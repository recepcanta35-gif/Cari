"""Demo kabul kontrolleri — salt okuma, stok/muhasebe verilerini düzeltmez."""

import json
from decimal import Decimal

import frappe
from frappe.query_builder.functions import Count, Sum
from frappe.utils import getdate

from cari_custom.compat_patches import install
from cari_custom.sample_data import (
	BANK,
	COMPANY,
	CUSTOMER,
	DOCTYPES,
	EMPLOYEE,
	ITEMS,
	POSTING_DATE,
	SAHA,
	SALE_ITEMS,
	STORES,
	SUPPLIER,
	VEHICLE,
	load_manifest,
)


class DemoValidationError(AssertionError):
	pass


def _money(value):
	return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def verify(state=None):
	install()
	state = state or load_manifest()
	names = state["documents"]
	checks = []

	def check(label, condition, actual=None, expected=None):
		if not condition:
			raise DemoValidationError(f"{label}: gerçek={actual!r}, beklenen={expected!r}")
		checks.append(label)

	def equal(label, actual, expected):
		check(label, actual == expected, actual, expected)

	def money(label, actual, expected):
		equal(label, _money(actual), _money(expected))

	company = frappe.get_doc("Company", COMPANY)
	equal("Şirket para birimi", company.default_currency, "TRY")
	equal("Global varsayılan para birimi", frappe.defaults.get_global_default("currency"), "TRY")
	equal(
		"Global Defaults para birimi",
		frappe.db.get_single_value("Global Defaults", "default_currency"),
		"TRY",
	)
	employee = frappe.db.get_value("Employee", {"employee_name": EMPLOYEE, "company": COMPANY}, "name")
	check("Saha personeli mevcut", bool(employee))
	check(
		"İkinci personel mevcut",
		bool(frappe.db.exists("Employee", {"employee_name": "Mehmet Kaya", "company": COMPANY})),
	)
	check("İkinci müşteri mevcut", bool(frappe.db.exists("Customer", "Ahmet Yılmaz")))
	check("Araç mevcut", bool(frappe.db.exists("Vehicle", VEHICLE)))

	for code, item_name, buy, sell in ITEMS:
		item = frappe.get_doc("Item", code)
		equal(f"{code}: ürün adı", item.item_name, item_name)
		equal(f"{code}: birim", item.stock_uom, "Nos")
		check(f"{code}: stok ürünü", bool(item.is_stock_item))
		for price_list, price in [("Standard Selling", sell), ("Standard Buying", buy)]:
			row = frappe.db.get_value(
				"Item Price",
				{"item_code": code, "price_list": price_list, "uom": "Nos"},
				["currency", "price_list_rate"],
				as_dict=True,
			)
			check(f"{code}: {price_list} fiyat kaydı", bool(row))
			equal(f"{code}: {price_list} para birimi", row.currency, "TRY")
			money(f"{code}: {price_list} fiyat", row.price_list_rate, price)

	docs = {key: frappe.get_doc(DOCTYPES[key], name) for key, name in names.items()}
	for key in [
		"purchase_receipt",
		"stock_transfer",
		"quotation",
		"sales_order",
		"delivery_note",
		"sales_invoice",
		"payment_entry",
	]:
		equal(f"{DOCTYPES[key]}: onaylı", docs[key].docstatus, 1)
		equal(f"{DOCTYPES[key]}: şirket", docs[key].company, COMPANY)
	for key in ["purchase_receipt", "quotation", "sales_order", "delivery_note", "sales_invoice"]:
		equal(f"{DOCTYPES[key]}: TRY", docs[key].currency, "TRY")
		money(f"{DOCTYPES[key]}: kur", docs[key].conversion_rate, 1)

	receipt = docs["purchase_receipt"]
	equal("Stok girişi tedarikçisi", receipt.supplier, SUPPLIER)
	equal("Stok girişi kalem sayısı", len(receipt.items), 4)
	for row in receipt.items:
		money(f"Stok girişi {row.item_code}: miktar", row.qty, 50)
		equal(f"Stok girişi {row.item_code}: depo", row.warehouse, STORES)
	money("Satın alma net tutarı", receipt.net_total, 154000)

	transfer = docs["stock_transfer"]
	equal("Stok transferi türü", transfer.purpose, "Material Transfer")
	equal("Stok transferi kalem sayısı", len(transfer.items), 1)
	equal("Transfer kaynak deposu", transfer.items[0].s_warehouse, STORES)
	equal("Transfer hedef deposu", transfer.items[0].t_warehouse, SAHA)
	equal("Transfer ürün kodu", transfer.items[0].item_code, "ITEM-001")
	money("Saha deposuna transfer", transfer.items[0].transfer_qty, 10)

	assignment = docs["stock_assignment"]
	equal("Zimmet personeli", assignment.personel, employee)
	equal("Zimmet deposu", assignment.depo, SAHA)
	equal("Zimmet ürünü", assignment.urun, "ITEM-001")
	money("Zimmet miktarı", assignment.zimmet_miktar, 10)
	equal("Zimmet transfer bağlantısı", assignment.stok_hareketi, transfer.name)
	equal("Zimmet durumu", assignment.durum, "Aktif")

	assignment = docs["daily_assignment"]
	equal("Görev personeli", assignment.personel, employee)
	equal("Görev aracı", assignment.arac, VEHICLE)
	equal("Görev müşterisi", assignment.musteri, CUSTOMER)
	equal("Görev bölgesi", assignment.bolge, "Marmara")
	equal("Görev tarihi", getdate(assignment.tarih), getdate(POSTING_DATE))

	quote, order, delivery, invoice, payment = [
		docs[k] for k in ["quotation", "sales_order", "delivery_note", "sales_invoice", "payment_entry"]
	]
	equal("Teklif müşterisi", quote.party_name, CUSTOMER)
	for label, document in [("Sipariş", order), ("İrsaliye", delivery), ("Fatura", invoice)]:
		equal(f"{label} müşterisi", document.customer, CUSTOMER)
	for label, document in [
		("Teklif", quote),
		("Sipariş", order),
		("İrsaliye", delivery),
		("Fatura", invoice),
	]:
		equal(
			f"{label} kalemleri",
			sorted((r.item_code, float(r.qty), float(r.rate)) for r in document.items),
			sorted(SALE_ITEMS),
		)
		money(f"{label} net", document.net_total, 1800)
		money(f"{label} KDV", document.total_taxes_and_charges, 360)
		money(f"{label} genel toplam", document.grand_total, 2160)
		equal(f"{label} vergi satırı sayısı", len(document.taxes), 1)
		# Ürün vergi şablonu ERPNext'te başlık oranını override edebilir (başlık rate=0 olabilir).
		effective = json.loads(document.taxes[0].item_wise_tax_detail or "{}")
		for code, qty, price in SALE_ITEMS:
			check(f"{label} {code} etkin KDV kaydı", code in effective)
			money(f"{label} {code} etkin KDV %20", effective[code][0], 20)
			money(f"{label} {code} KDV tutarı", effective[code][1], qty * price * 0.2)
	for row in order.items:
		equal(f"{row.item_code}: teklif -> sipariş bağı", row.prevdoc_docname, quote.name)
		check(f"{row.item_code}: teklif kalemi bağı", row.quotation_item in [r.name for r in quote.items])
	for row in delivery.items:
		equal(f"{row.item_code}: sipariş -> irsaliye bağı", row.against_sales_order, order.name)
		check(f"{row.item_code}: sipariş kalemi bağı", row.so_detail in [r.name for r in order.items])
	for row in invoice.items:
		equal(f"{row.item_code}: sipariş -> fatura bağı", row.sales_order, order.name)
		check(f"{row.item_code}: fatura sipariş kalemi bağı", row.so_detail in [r.name for r in order.items])
		if row.delivery_note:
			equal(f"{row.item_code}: irsaliye -> fatura bağı", row.delivery_note, delivery.name)
	money("Sipariş sevkiyat yüzdesi", order.per_delivered, 100)
	money("Sipariş faturalama yüzdesi", order.per_billed, 100)
	equal("Sipariş durumu", order.status, "Completed")
	equal("Fatura durumu", invoice.status, "Paid")
	money("Fatura açık bakiye", invoice.outstanding_amount, 0)
	equal("Fatura stok ikinci kez düşürmez", invoice.update_stock, 0)
	equal("Tahsilat tipi", payment.payment_type, "Receive")
	equal("Tahsilat carisi", payment.party, CUSTOMER)
	equal("Tahsilat kanalı", payment.mode_of_payment, "Havale/EFT")
	equal("Tahsilat banka hesabı", payment.paid_to, BANK)
	money("Tahsilat ödenen tutar", payment.paid_amount, 2160)
	money("Tahsilat alınan tutar", payment.received_amount, 2160)
	equal("Tahsilat referans sayısı", len(payment.references), 1)
	equal("Tahsilat fatura referansı", payment.references[0].reference_name, invoice.name)
	money("Tahsilat fatura tahsisi", payment.references[0].allocated_amount, 2160)

	sle = frappe.qb.DocType("Stock Ledger Entry")
	entries = (
		frappe.qb.from_(sle)
		.select(
			sle.voucher_no,
			sle.item_code,
			sle.warehouse,
			Sum(sle.actual_qty).as_("qty"),
			Count(sle.name).as_("count"),
		)
		.where(
			(sle.voucher_no.isin([receipt.name, transfer.name, delivery.name, invoice.name]))
			& (sle.is_cancelled == 0)
		)
		.groupby(sle.voucher_no, sle.item_code, sle.warehouse)
	).run(as_dict=True)
	quantities = {(row.voucher_no, row.item_code, row.warehouse): _money(row.qty) for row in entries}
	for code, _name, _buy, _sell in ITEMS:
		money(f"Stok defteri giriş {code}", quantities.get((receipt.name, code, STORES)), 50)
	money("Stok defteri transfer merkez", quantities.get((transfer.name, "ITEM-001", STORES)), -10)
	money("Stok defteri transfer saha", quantities.get((transfer.name, "ITEM-001", SAHA)), 10)
	money("Stok defteri satış mouse", quantities.get((delivery.name, "ITEM-001", STORES)), -5)
	money("Stok defteri satış kablo", quantities.get((delivery.name, "ITEM-002", STORES)), -10)
	equal("Faturada ek stok hareketi yok", len([r for r in entries if r.voucher_no == invoice.name]), 0)

	stock = []
	for code, warehouse, expected in [
		("ITEM-001", STORES, 35),
		("ITEM-001", SAHA, 10),
		("ITEM-002", STORES, 40),
		("ITEM-003", STORES, 50),
		("ITEM-004", STORES, 50),
	]:
		qty = frappe.db.get_value("Bin", {"item_code": code, "warehouse": warehouse}, "actual_qty")
		money(f"Bin {code} / {warehouse}", qty, expected)
		stock.append({"item_code": code, "warehouse": warehouse, "qty": float(qty)})

	gl = frappe.qb.DocType("GL Entry")
	balances = (
		frappe.qb.from_(gl)
		.select(
			gl.voucher_type,
			gl.voucher_no,
			Sum(gl.debit).as_("debit"),
			Sum(gl.credit).as_("credit"),
			Count(gl.name).as_("count"),
		)
		.where(gl.voucher_no.isin(list(names.values())) & (gl.is_cancelled == 0))
		.groupby(gl.voucher_type, gl.voucher_no)
	).run(as_dict=True)
	for row in balances:
		money(f"Muhasebe borç/alacak eşit {row.voucher_no}", row.debit, row.credit)
	for key in ["purchase_receipt", "delivery_note", "sales_invoice", "payment_entry"]:
		check(
			f"Muhasebe fişi var {names[key]}",
			any(r.voucher_no == names[key] and r.count > 0 for r in balances),
		)
	party_balance = (
		frappe.qb.from_(gl)
		.select(Sum(gl.debit - gl.credit))
		.where(
			(gl.voucher_no.isin([invoice.name, payment.name]))
			& (gl.party_type == "Customer")
			& (gl.party == CUSTOMER)
			& (gl.is_cancelled == 0)
		)
	).run()[0][0]
	money("Bağımsız muhasebe cari bakiyesi", party_balance, 0)

	ple = frappe.qb.DocType("Payment Ledger Entry")
	balance = (
		frappe.qb.from_(ple)
		.select(Sum(ple.amount_in_account_currency))
		.where(
			(ple.against_voucher_type == "Sales Invoice")
			& (ple.against_voucher_no == invoice.name)
			& (ple.delinked == 0)
		)
	).run()[0][0]
	money("Ödeme defteri cari bakiyesi", balance, 0)
	from erpnext.accounts.utils import QueryPaymentLedger

	rows = QueryPaymentLedger().get_voucher_outstandings(
		vouchers=[frappe._dict(voucher_type="Sales Invoice", voucher_no=invoice.name)],
		common_filter=[ple.account == invoice.debit_to, ple.party_type == "Customer", ple.party == CUSTOMER],
	)
	equal("Cari sorgusu tek fatura", len(rows), 1)
	money("Cari sorgusu fatura tutarı", rows[0].invoice_amount_in_account_currency, 2160)
	money("Cari sorgusu bakiye", rows[0].outstanding_in_account_currency, 0)
	money("Cari sorgusu ödenen", rows[0].paid_amount_in_account_currency, 2160)
	check("Uyumsoft canlı bağlantı kapalı", not frappe.db.get_single_value("Uyumsoft Settings", "aktif"))

	return {
		"status": "PASS",
		"company": COMPANY,
		"posting_date": POSTING_DATE,
		"documents": names,
		"net_total": 1800,
		"vat_total": 360,
		"grand_total": 2160,
		"collected": 2160,
		"outstanding": 0,
		"stock": stock,
		"checks_passed": len(checks),
		"checks": checks,
	}
