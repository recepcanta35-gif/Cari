import unittest
from uuid import uuid4

import frappe
from frappe.utils import today

from cari_custom.sample_data import BANK, COMPANY, CUSTOMER, STORES
from cari_custom.tests.test_delivery import DeliveryTests
from cari_custom.tests.test_faz15 import Faz15Tests


class BusinessTests(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		frappe.flags.mute_emails = True
		frappe.local.lang = "tr"

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()
		frappe.flags.mute_emails = False

	def test_cheque_is_not_bank_money_until_collection_and_is_idempotent(self):
		invoice = Faz15Tests()._invoice_chain()[-1]
		before = frappe.db.count("Payment Entry")
		doc = frappe.get_doc(
			{
				"doctype": "Cari Payment Instrument",
				"company": COMPANY,
				"customer": CUSTOMER,
				"instrument_type": "Çek",
				"instrument_number": f"CI-{uuid4().hex[:10]}",
				"invoice": invoice.name,
				"amount": invoice.grand_total,
				"currency": invoice.currency,
				"received_date": today(),
				"due_date": today(),
			}
		)
		doc.insert()
		doc.submit()
		self.assertEqual(frappe.db.count("Payment Entry"), before)
		self.assertFalse(doc.deposit()["bank_collection"])
		result = doc.collect(BANK, "CI-GERCEK-TAHSILAT")
		self.assertEqual(frappe.db.count("Payment Entry"), before + 1)
		self.assertEqual(doc.collect(BANK, "CI-RETRY")["payment_entry"], result["payment_entry"])
		invoice.reload()
		self.assertEqual(invoice.outstanding_amount, 0)

	def test_shipment_status_and_carrier_metadata(self):
		delivery = Faz15Tests()._invoice_chain()[2]
		doc = frappe.get_doc(
			{"doctype": "Cari Shipment", "delivery_note": delivery.name, "delivery_mode": "Kargo"}
		)
		doc.insert()
		doc.submit()
		with self.assertRaises(frappe.ValidationError):
			doc.dispatch()
		self.assertEqual(doc.dispatch("Demo Kargo", "CI-TRACK")["status"], "Sevk Edildi")
		self.assertEqual(frappe.db.get_value("Delivery Note", delivery.name, "kargo_takip_no"), "CI-TRACK")
		self.assertEqual(doc.deliver("Teslim kanıtı kabul notu")["status"], "Teslim Edildi")

	def test_service_history_requires_result_and_valid_state(self):
		doc = frappe.get_doc(
			{
				"doctype": "Cari Service Record",
				"company": COMPANY,
				"customer": CUSTOMER,
				"item": "ITEM-001",
				"service_type": "Ücretli",
				"opened_on": today(),
				"complaint": "Demo arıza",
			}
		)
		doc.insert()
		doc.submit()
		with self.assertRaises(frappe.ValidationError):
			doc.complete("Önce başlatılmalı")
		doc.begin()
		self.assertEqual(doc.complete("Servis işlemi tamamlandı")["status"], "Tamamlandı")

	def test_portal_uses_server_price_and_no_automatic_stock_or_financial_posting(self):
		from cari_custom.portal import place_order

		settings = frappe.get_single("Cari Settings")
		settings.portal_warehouse, settings.portal_enabled = STORES, 1
		settings.save()
		fixture = DeliveryTests()
		fixture.setUp()
		user, _employee = fixture.user("Portal")
		request_id = str(uuid4())
		with fixture.actor(user):
			with self.assertRaises(frappe.ValidationError):
				place_order([{"item_code": "ITEM-001", "qty": 1, "rate": 1}], str(uuid4()))
			result = place_order([{"item_code": "ITEM-001", "qty": 1}], request_id)
			self.assertFalse(result["stock_reserved"])
			self.assertEqual(
				place_order([{"item_code": "ITEM-001", "qty": 1}], request_id)["name"], result["name"]
			)
		order = frappe.get_doc("Sales Order", result["name"])
		self.assertEqual(order.docstatus, 0)
		self.assertEqual(order.items[0].rate, 250)
		self.assertEqual(order.customer, CUSTOMER)

	def test_quantity_dashboard_has_no_financial_payload_for_depot(self):
		from cari_custom.api import dashboard, quantity_stock

		fixture = DeliveryTests()
		fixture.setUp()
		user, _employee = fixture.user("Depo")
		with fixture.actor(user):
			data = dashboard()
			self.assertNotIn("sales_base_total", data)
			self.assertNotIn("customer_balance_base", data)
			self.assertTrue(
				all("valuation_rate" not in r and "stock_value" not in r for r in quantity_stock())
			)
