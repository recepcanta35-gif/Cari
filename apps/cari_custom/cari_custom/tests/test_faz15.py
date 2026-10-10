"""Bağlı bir demo sitesinde çalıştırılır; regresyon kayıtları rollback edilir.

Çalıştırıcı: scripts/run_faz15_tests.py (bench env Python'u ile).
"""

import unittest
from decimal import Decimal
from uuid import uuid4

import frappe
from frappe.utils import add_days

from cari_custom.compat_patches import install
from cari_custom.sample_data import (
	BANK,
	COMPANY,
	CUSTOMER,
	DOCTYPES,
	POSTING_DATE,
	SAHA,
	SALE_ITEMS,
	STORES,
	load_manifest,
	run,
	tax_template,
)
from cari_custom.sample_validation import verify


def amount(value):
	return Decimal(str(value or 0)).quantize(Decimal("0.01"))


class Faz15Tests(unittest.TestCase):
	def setUp(self):
		install()
		self.state = load_manifest()
		self.old_mute = frappe.flags.mute_emails
		frappe.flags.mute_emails = True
		frappe.local.lang = "tr"

	def tearDown(self):
		frappe.db.rollback()
		frappe.flags.mute_emails = self.old_mute

	def _counts(self):
		return {
			dt: frappe.db.count(dt)
			for dt in [
				*DOCTYPES.values(),
				"Item",
				"Item Price",
				"Customer",
				"Supplier",
				"Employee",
				"Vehicle",
				"Stock Ledger Entry",
				"GL Entry",
				"Payment Ledger Entry",
			]
		}

	def _insert_submit(self, doc, label):
		doc.insert(set_name=f"CARI-TEST-15-{label}-{uuid4().hex[:10]}")
		doc.submit()
		return doc

	def _invoice_chain(self):
		from erpnext.selling.doctype.quotation.quotation import make_sales_order
		from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
		from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice

		quote = frappe.new_doc("Quotation")
		quote.company = COMPANY
		quote.quotation_to = "Customer"
		quote.party_name = CUSTOMER
		quote.transaction_date = POSTING_DATE
		quote.valid_till = add_days(POSTING_DATE, 14)
		quote.currency = "TRY"
		quote.selling_price_list = "Standard Selling"
		quote.taxes_and_charges = tax_template()
		quote.set_taxes()
		for code, qty, rate in SALE_ITEMS:
			quote.append("items", {"item_code": code, "qty": qty, "rate": rate})
		self._insert_submit(quote, "QTN")
		order = make_sales_order(quote.name)
		order.delivery_date = add_days(POSTING_DATE, 3)
		for row in order.items:
			row.warehouse = STORES
		self._insert_submit(order, "SO")
		delivery = make_delivery_note(order.name)
		delivery.set_posting_time = 1
		delivery.posting_date = POSTING_DATE
		delivery.posting_time = "18:00:00"
		self._insert_submit(delivery, "DN")
		invoice = make_sales_invoice(delivery.name)
		invoice.set_posting_time = 1
		invoice.posting_date = POSTING_DATE
		invoice.posting_time = "18:01:00"
		invoice.due_date = add_days(POSTING_DATE, 30)
		self._insert_submit(invoice, "SI")
		return quote, order, delivery, invoice

	def _payment(self, invoice, value):
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

		invoice.reload()
		payment = get_payment_entry("Sales Invoice", invoice.name, party_amount=value, bank_account=BANK)
		payment.mode_of_payment = "Havale/EFT"
		payment.reference_no = "DEMO-REGRESYON"
		payment.reference_date = POSTING_DATE
		payment.posting_date = POSTING_DATE
		return self._insert_submit(payment, "PE")

	def _outstanding(self, invoice, **kwargs):
		from erpnext.accounts.utils import QueryPaymentLedger

		ple = frappe.qb.DocType("Payment Ledger Entry")
		return QueryPaymentLedger().get_voucher_outstandings(
			vouchers=[frappe._dict(voucher_type="Sales Invoice", voucher_no=invoice.name)],
			common_filter=[
				ple.account == invoice.debit_to,
				ple.party_type == "Customer",
				ple.party == CUSTOMER,
			],
			**kwargs,
		)

	def test_persisted_demo_acceptance(self):
		result = verify(self.state)
		self.assertEqual(result["status"], "PASS")
		self.assertGreaterEqual(result["checks_passed"], 190)
		self.assertEqual(result["outstanding"], 0)

	def test_seed_idempotency_no_duplicate_documents_or_ledgers(self):
		before = self._counts()
		result = run(allow_demo=True)
		self.assertEqual(result["documents"], self.state["documents"])
		self.assertEqual(self._counts(), before)

	def test_demo_requires_explicit_opt_in(self):
		before = self._counts()
		with self.assertRaises(frappe.ValidationError):
			run()
		self.assertEqual(self._counts(), before)

	def test_demo_refuses_production_mode(self):
		previous = frappe.conf.developer_mode
		try:
			frappe.conf.developer_mode = 0
			with self.assertRaises(frappe.ValidationError):
				run(allow_demo=True)
		finally:
			frappe.conf.developer_mode = previous

	def test_stock_assignment_quantity_and_date_validation(self):
		original = frappe.get_doc("Stock Assignment", self.state["documents"]["stock_assignment"])
		for qty in [0, -1]:
			doc = frappe.copy_doc(original)
			doc.zimmet_miktar = qty
			with self.assertRaises(frappe.ValidationError):
				doc.validate()
		doc = frappe.copy_doc(original)
		doc.atama_tarihi = POSTING_DATE
		doc.iade_tarihi = "2026-10-08"
		with self.assertRaises(frappe.ValidationError):
			doc.validate()
		doc.iade_tarihi = "2026-10-10"
		doc.validate()

	def test_daily_assignment_datetime_validation(self):
		doc = frappe.copy_doc(frappe.get_doc("Daily Assignment", self.state["documents"]["daily_assignment"]))
		doc.baslangic_saati = "2026-10-09 10:00:00"
		doc.bitis_saati = "2026-10-09 09:00:00"
		with self.assertRaises(frappe.ValidationError):
			doc.validate()
		doc.bitis_saati = "2026-10-09 11:00:00"
		doc.validate()

	def test_standard_mappers_and_partial_then_full_collection(self):
		quote, order, delivery, invoice = self._invoice_chain()
		self.assertEqual(amount(invoice.net_total), amount(1800))
		self.assertEqual(amount(invoice.total_taxes_and_charges), amount(360))
		self.assertEqual(amount(invoice.outstanding_amount), amount(2160))
		self.assertTrue(all(r.delivery_note == delivery.name for r in invoice.items))
		self.assertTrue(all(r.sales_order == order.name for r in invoice.items))
		self.assertTrue(all(r.prevdoc_docname == quote.name for r in order.items))
		first = self._payment(invoice, 1080)
		self.assertEqual(amount(first.references[0].allocated_amount), amount(1080))
		invoice.reload()
		self.assertEqual(amount(invoice.outstanding_amount), amount(1080))
		rows = self._outstanding(invoice, get_invoices=True, limit=10)
		self.assertEqual(len(rows), 1)
		self.assertEqual(amount(rows[0].invoice_amount_in_account_currency), amount(2160))
		self.assertEqual(amount(rows[0].outstanding_in_account_currency), amount(1080))
		self.assertEqual(amount(rows[0].paid_amount_in_account_currency), amount(1080))
		self.assertEqual(self._outstanding(invoice, get_invoices=True, min_outstanding=1100), [])
		self.assertEqual(self._outstanding(invoice, get_invoices=True, max_outstanding=1000), [])
		self._payment(invoice, 1080)
		invoice.reload()
		self.assertEqual(amount(invoice.outstanding_amount), amount(0))
		self.assertEqual(invoice.status, "Paid")
		self.assertEqual(self._outstanding(invoice, get_invoices=True, limit=10), [])
		self.assertEqual(amount(self._outstanding(invoice)[0].paid_amount_in_account_currency), amount(2160))

	def test_overallocation_is_rejected(self):
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

		invoice = self._invoice_chain()[-1]
		payment = get_payment_entry("Sales Invoice", invoice.name, party_amount=2161, bank_account=BANK)
		payment.paid_amount = 2161
		payment.received_amount = 2161
		payment.references[0].allocated_amount = 2161
		payment.mode_of_payment = "Havale/EFT"
		payment.reference_no = "DEMO-EXCESS"
		payment.reference_date = POSTING_DATE
		with self.assertRaises(frappe.ValidationError):
			payment.insert()

	def test_insufficient_stock_is_rejected(self):
		from erpnext.stock.stock_ledger import NegativeStockError

		if not frappe.db.exists("Stock Entry Type", "Material Issue"):
			frappe.get_doc({"doctype": "Stock Entry Type", "purpose": "Material Issue"}).insert(
				set_name="Material Issue"
			)
		doc = frappe.new_doc("Stock Entry")
		doc.company = COMPANY
		doc.stock_entry_type = "Material Issue"
		doc.purpose = "Material Issue"
		doc.set_posting_time = 1
		doc.posting_date = POSTING_DATE
		doc.posting_time = "19:00:00"
		doc.append(
			"items",
			{"item_code": "ITEM-001", "qty": 1000, "s_warehouse": SAHA, "uom": "Nos", "conversion_factor": 1},
		)
		with self.assertRaises(NegativeStockError):
			doc.insert()
			doc.submit()

	def test_landed_cost_sums_all_cost_centers(self):
		from cari_custom.postgres_queries import set_landed_cost_voucher_amount

		# Yalnız sorgu regresyonu için izolasyonlu child-table fixture; commit edilmez.
		for value, center in [(12, "TEST-CENTER-A"), (8, "TEST-CENTER-B")]:
			doc = frappe.get_doc(
				{
					"doctype": "Landed Cost Item",
					"name": f"CARI-TEST-LCI-{uuid4().hex[:10]}",
					"parent": "CARI-TEST-LCV",
					"parenttype": "Landed Cost Voucher",
					"parentfield": "items",
					"docstatus": 1,
					"purchase_receipt_item": "CARI-TEST-PR-ITEM",
					"receipt_document": "CARI-TEST-PR",
					"cost_center": center,
					"applicable_charges": value,
				}
			)
			doc.db_insert()
		item = frappe._dict(name="CARI-TEST-PR-ITEM", cost_center="Main - CARI")
		parent = frappe._dict(name="CARI-TEST-PR", items=[item])
		set_landed_cost_voucher_amount(parent)
		self.assertEqual(amount(item.landed_cost_voucher_amount), amount(20))

	def test_stock_history_uses_creation_only_for_equal_posting_time(self):
		from erpnext.stock.stock_ledger import get_previous_sle_of_current_voucher

		result = get_previous_sle_of_current_voucher(
			frappe._dict(
				item_code="ITEM-001",
				warehouse=STORES,
				posting_date=POSTING_DATE,
				posting_time="23:00:00",
				creation="2026-01-01 00:00:00",
				sle_id="CARI-TEST-SLE",
			)
		)
		expected = frappe.get_all(
			"Stock Ledger Entry",
			filters={"item_code": "ITEM-001", "warehouse": STORES, "is_cancelled": 0},
			fields=["voucher_no", "qty_after_transaction"],
			order_by="posting_datetime desc, creation desc",
			limit_page_length=1,
		)[0]
		self.assertEqual(result.voucher_no, expected.voucher_no)
		self.assertEqual(amount(result.qty_after_transaction), amount(expected.qty_after_transaction))
		self.assertEqual(amount(result.qty_after_transaction), amount(35))

	def test_permission_rules_preserve_manager_access_and_field_creation(self):
		for dt in ["Stock Assignment", "Daily Assignment"]:
			self.assertTrue(
				frappe.db.get_value("Custom DocPerm", {"parent": dt, "role": "System Manager"}, "read")
			)
		for dt in ["Sales Order", "Quotation", "Delivery Note"]:
			permissions = frappe.db.get_value(
				"Custom DocPerm",
				{"parent": dt, "role": "Saha Personeli", "permlevel": 0},
				["read", "write", "create"],
			)
			self.assertEqual(tuple(permissions), (1, 1, 1))

	def test_adapters_are_site_scoped_and_idempotent(self):
		from types import SimpleNamespace
		from unittest.mock import patch

		from cari_custom.compat_patches import _wrap

		target = SimpleNamespace(query=lambda: "core")
		_wrap(target, "query", lambda: "postgres")
		wrapped = target.query
		_wrap(target, "query", lambda: "wrong-second-wrapper")
		self.assertIs(target.query, wrapped)
		with patch("cari_custom.compat_patches._postgres_site", return_value=False):
			self.assertEqual(target.query(), "core")
		with patch("cari_custom.compat_patches._postgres_site", return_value=True):
			self.assertEqual(target.query(), "postgres")
		self.assertEqual(frappe.get_all.__name__, "get_all")
		self.assertEqual(frappe.get_list.__name__, "get_list")
