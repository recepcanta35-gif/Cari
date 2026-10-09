"""Faz 1.5 demo verisi: tekrar çalıştırılabilir, yalnızca geliştirme sitesi.

bench --site cari.local execute cari_custom.sample_data.run --kwargs '{"allow_demo": True}'

Belge kimlikleri sitenin private/files/cari-faz15-demo.json dosyasında tutulur.
Yeni belgeler CARI-DEMO-15-* adlarıyla tekilleştirilir. Önceki demo belgeleri
existing_documents ile açıkça benimsenebilir; müşterinin rastgele belgesi seçilmez.
Önce setup_turkey.run() çalışmalıdır. Hiçbir validasyon atlanmaz, dışarı e-posta
veya Uyumsoft aktarımı yapılmaz. Hata halinde DB rollback edilir.
"""

import json
from datetime import timedelta
from pathlib import Path

import frappe
from frappe.utils import add_days, cint, flt, get_datetime

from cari_custom.compat_patches import install

COMPANY = "Cari A.Ş."
ABBR = "CARI"
STORES = f"Stores - {ABBR}"
SAHA = f"Saha Deposu - {ABBR}"
BANK = f"Banka - TRY - {ABBR}"
POSTING_DATE = "2026-10-09"
CUSTOMER = "ABC Teknoloji Ltd."
SUPPLIER = "Tedarikçi A.Ş."
VEHICLE = "34 ABC 123"
EMPLOYEE = "Ayşe Demir"
MARKER = "Cari Faz 1.5 — DEMO / gerçek mali belge değildir"

ITEMS = [
	("ITEM-001", "Kablosuz Mouse", 150, 250),
	("ITEM-002", "USB-C Kablo 2m", 30, 55),
	("ITEM-003", '27" Monitör', 2500, 4200),
	("ITEM-004", "Mekanik Klavye", 400, 700),
]
SALE_ITEMS = [("ITEM-001", 5, 250), ("ITEM-002", 10, 55)]
DOCTYPES = {
	"purchase_receipt": "Purchase Receipt",
	"stock_transfer": "Stock Entry",
	"stock_assignment": "Stock Assignment",
	"daily_assignment": "Daily Assignment",
	"quotation": "Quotation",
	"sales_order": "Sales Order",
	"delivery_note": "Delivery Note",
	"sales_invoice": "Sales Invoice",
	"payment_entry": "Payment Entry",
}
DEFAULT_NAMES = {
	key: f"CARI-DEMO-15-{suffix}"
	for key, suffix in [
		("purchase_receipt", "PRE"),
		("stock_transfer", "TRANSFER"),
		("stock_assignment", "ZIMMET"),
		("daily_assignment", "GOREV"),
		("quotation", "QTN"),
		("sales_order", "SO"),
		("delivery_note", "DN"),
		("sales_invoice", "SI"),
		("payment_entry", "PE"),
	]
}


def _require_demo(allow_demo):
	frappe.only_for("System Manager")
	if allow_demo is not True or not cint(frappe.conf.get("developer_mode")):
		frappe.throw("Demo verisi için developer_mode=1 ve allow_demo=true açık onayı gerekir.")


def _manifest_path():
	return Path(frappe.get_site_path("private", "files", "cari-faz15-demo.json"))


def load_manifest(existing_documents=None):
	path = _manifest_path()
	if path.exists():
		state = json.loads(path.read_text())
		if state.get("version") != 1 or state.get("company") != COMPANY:
			frappe.throw("Demo manifest sürümü/şirketi uyumsuz.")
		if existing_documents and any(state["documents"].get(k) != v for k, v in existing_documents.items()):
			frappe.throw("Mevcut demo kimlikleri değiştirilemez; yanlış belgenin benimsenmesi engellendi.")
	else:
		state = {
			"version": 1,
			"company": COMPANY,
			"posting_date": POSTING_DATE,
			"documents": dict(DEFAULT_NAMES),
		}
		for key, name in (existing_documents or {}).items():
			if key not in DOCTYPES or not isinstance(name, str) or not frappe.db.exists(DOCTYPES[key], name):
				frappe.throw(f"Benimsenecek demo belgesi bulunamadı: {key} / {name}")
			state["documents"][key] = name
	if set(state["documents"]) != set(DOCTYPES) or state.get("posting_date") != POSTING_DATE:
		frappe.throw("Demo manifest içeriği uyumsuz.")
	return state


def _save_manifest(state):
	path = _manifest_path()
	path.parent.mkdir(parents=True, exist_ok=True)
	temporary = path.with_suffix(".tmp")
	temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
	temporary.chmod(0o600)
	temporary.replace(path)


def tax_template(doctype="Sales Taxes and Charges Template"):
	name = frappe.db.get_value(
		doctype,
		{"company": COMPANY, "title": ["in", ["KDV %20", f"KDV %20 - {ABBR}"]]},
		"name",
	)
	if not name:
		frappe.throw(f"KDV %20 şablonu eksik: {doctype}. Önce Türkiye kurulumunu çalıştırın.")
	return name


def _ensure_reference_data():
	company = frappe.get_doc("Company", COMPANY)
	if company.default_currency != "TRY":
		frappe.throw("Demo şirket para birimi TRY olmalıdır.")
	from cari_custom.setup_turkey import _setup_system_defaults

	_setup_system_defaults()
	if not frappe.db.exists("Fiscal Year", "2026"):
		frappe.get_doc(
			{
				"doctype": "Fiscal Year",
				"year": "2026",
				"year_start_date": "2026-01-01",
				"year_end_date": "2026-12-31",
				"companies": [{"company": COMPANY}],
			}
		).insert()
	for name, selling, buying in [("Standard Selling", 1, 0), ("Standard Buying", 0, 1)]:
		if not frappe.db.exists("Price List", name):
			frappe.get_doc(
				{
					"doctype": "Price List",
					"price_list_name": name,
					"currency": "TRY",
					"enabled": 1,
					"selling": selling,
					"buying": buying,
				}
			).insert()
		elif frappe.db.get_value("Price List", name, "currency") != "TRY":
			frappe.throw(f"{name} başka para biriminde; demo gerçek fiyat listesini değiştirmez.")
	for unit in ["Nos", "Km"]:
		if not frappe.db.exists("UOM", unit):
			frappe.get_doc({"doctype": "UOM", "uom_name": unit}).insert()
	# sunucu API'sinde stock_entry_type atamak purpose default'unu değiştirmez.
	if not frappe.db.exists("Stock Entry Type", "Material Transfer"):
		frappe.get_doc({"doctype": "Stock Entry Type", "purpose": "Material Transfer"}).insert(
			set_name="Material Transfer"
		)


def _create_items():
	item_tax = tax_template("Item Tax Template")
	for code, name, buy, sell in ITEMS:
		if not frappe.db.exists("Item", code):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": code,
					"item_name": name,
					"item_group": "Genel",
					"stock_uom": "Nos",
					"is_stock_item": 1,
					"description": f"Örnek ürün: {name}",
					"item_defaults": [{"company": COMPANY, "default_warehouse": STORES}],
					"taxes": [{"item_tax_template": item_tax}],
				}
			).insert()
		else:
			doc = frappe.get_doc("Item", code)
			if doc.item_name != name or doc.stock_uom != "Nos" or not doc.is_stock_item:
				frappe.throw(f"{code} başka ürüne ait; demo kartı değiştirilmedi.")
		# Mevcut Item bulunması fiyatların da mevcut olduğunu varsaydırmaz.
		for price_list, rate in [("Standard Selling", sell), ("Standard Buying", buy)]:
			filters = {"item_code": code, "price_list": price_list, "uom": "Nos"}
			if not frappe.db.exists("Item Price", filters):
				frappe.get_doc(
					{
						"doctype": "Item Price",
						**filters,
						"price_list_rate": rate,
						"currency": "TRY",
						"valid_from": POSTING_DATE,
					}
				).insert()
			else:
				existing = frappe.db.get_value(
					"Item Price", filters, ["currency", "price_list_rate"], as_dict=True
				)
				if existing.currency != "TRY" or flt(existing.price_list_rate) != rate:
					frappe.throw(f"{code} / {price_list} fiyatı farklı; demo gerçek fiyatı değiştirmez.")


def _create_parties():
	for name, ctype, group, territory, terms in [
		(CUSTOMER, "Company", "Kurumsal", "Marmara", "30 Gün Vadeli"),
		("Ahmet Yılmaz", "Individual", "Bireysel", "İç Anadolu", "Peşin"),
	]:
		if not frappe.db.exists("Customer", name):
			frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": name,
					"customer_type": ctype,
					"customer_group": group,
					"territory": territory,
					"payment_terms": terms,
					"default_currency": "TRY",
				}
			).insert(set_name=name)
	if not frappe.db.exists("Supplier", SUPPLIER):
		frappe.get_doc(
			{
				"doctype": "Supplier",
				"supplier_name": SUPPLIER,
				"supplier_group": "Yerli Tedarikçi",
				"default_currency": "TRY",
			}
		).insert(set_name=SUPPLIER)


def _create_employees_and_vehicle():
	for gender in ["Female", "Male"]:
		if not frappe.db.exists("Gender", gender):
			frappe.get_doc({"doctype": "Gender", "gender": gender}).insert()
	for first, last, department, designation, gender, birthday in [
		("Ayşe", "Demir", f"Sales - {ABBR}", "Satış Temsilcisi", "Female", "1990-05-15"),
		("Mehmet", "Kaya", f"Operations - {ABBR}", "Depo Sorumlusu", "Male", "1985-03-20"),
	]:
		if not frappe.db.exists("Designation", designation):
			frappe.get_doc({"doctype": "Designation", "designation_name": designation}).insert()
		if not frappe.db.exists("Employee", {"employee_name": f"{first} {last}", "company": COMPANY}):
			frappe.get_doc(
				{
					"doctype": "Employee",
					"first_name": first,
					"last_name": last,
					"gender": gender,
					"date_of_birth": birthday,
					"company": COMPANY,
					"department": department,
					"designation": designation,
					"date_of_joining": POSTING_DATE,
					"naming_series": "EMP-.#####",
				}
			).insert()
	if not frappe.db.exists("Vehicle", VEHICLE):
		frappe.get_doc(
			{
				"doctype": "Vehicle",
				"license_plate": VEHICLE,
				"make": "Ford",
				"model": "Transit",
				"last_odometer": 45000,
				"uom": "Km",
			}
		).insert()
	return frappe.db.get_value("Employee", {"employee_name": EMPLOYEE, "company": COMPANY}, "name")


def _same_items(doc, expected):
	actual = sorted(
		(row.item_code, flt(row.qty), flt(row.get("rate", row.get("basic_rate")))) for row in doc.items
	)
	if actual != sorted(expected):
		frappe.throw(f"Demo belge kalemleri farklı: {doc.doctype} / {doc.name}")


def _submitted(state, key, factory, expected_items=None, party_field=None, party=None):
	name = state["documents"][key]
	if frappe.db.exists(DOCTYPES[key], name):
		doc = frappe.get_doc(DOCTYPES[key], name)
	else:
		doc = factory()
		doc.insert(set_name=name)
	if doc.company != COMPANY or doc.docstatus == 2 or (party_field and doc.get(party_field) != party):
		frappe.throw(f"Demo belgesi farklı şirkete/cariye ait veya iptal edilmiş: {name}")
	if expected_items is not None:
		_same_items(doc, expected_items)
	if doc.docstatus == 0:
		doc.submit()
	return doc


def _timestamp(doc, timestamp):
	doc.set_posting_time = 1
	doc.posting_date = timestamp.date()
	doc.posting_time = timestamp.time()


def _stock_receipt(state):
	def factory():
		doc = frappe.new_doc("Purchase Receipt")
		doc.supplier = SUPPLIER
		doc.company = COMPANY
		_timestamp(doc, get_datetime(f"{POSTING_DATE} 09:00:00"))
		doc.currency = "TRY"
		doc.conversion_rate = 1
		doc.buying_price_list = "Standard Buying"
		doc.taxes_and_charges = tax_template("Purchase Taxes and Charges Template")
		doc.remarks = MARKER
		for code, _name, buy, _sell in ITEMS:
			doc.append("items", {"item_code": code, "qty": 50, "rate": buy, "warehouse": STORES})
		return doc

	return _submitted(
		state, "purchase_receipt", factory, [(c, 50, b) for c, _, b, _ in ITEMS], "supplier", SUPPLIER
	)


def _field_stock_and_assignment(state, employee, receipt):
	at = get_datetime(f"{receipt.posting_date} {receipt.posting_time}")
	# Önceki demo sevkiyatı varsa transferi ondan sonra yap; onaylı belgeyi/repost'u değiştirme.
	if frappe.db.exists("Delivery Note", state["documents"]["delivery_note"]):
		delivery = frappe.get_doc("Delivery Note", state["documents"]["delivery_note"])
		at = max(at, get_datetime(f"{delivery.posting_date} {delivery.posting_time}"))
	at += timedelta(minutes=1)

	def factory():
		doc = frappe.new_doc("Stock Entry")
		doc.company = COMPANY
		doc.stock_entry_type = "Material Transfer"
		doc.purpose = "Material Transfer"
		_timestamp(doc, at)
		doc.append(
			"items",
			{
				"item_code": "ITEM-001",
				"qty": 10,
				"uom": "Nos",
				"conversion_factor": 1,
				"s_warehouse": STORES,
				"t_warehouse": SAHA,
			},
		)
		doc.remarks = MARKER
		return doc

	transfer = _submitted(state, "stock_transfer", factory)
	if transfer.purpose != "Material Transfer" or len(transfer.items) != 1:
		frappe.throw("Demo stok transferi farklı.")
	row = transfer.items[0]
	if (row.item_code, row.s_warehouse, row.t_warehouse, flt(row.qty)) != ("ITEM-001", STORES, SAHA, 10):
		frappe.throw("Demo stok transfer kalemi farklı.")
	name = state["documents"]["stock_assignment"]
	if frappe.db.exists("Stock Assignment", name):
		assignment = frappe.get_doc("Stock Assignment", name)
		if (assignment.personel, assignment.depo, assignment.urun, flt(assignment.zimmet_miktar)) != (
			employee,
			SAHA,
			"ITEM-001",
			10,
		):
			frappe.throw("Mevcut zimmet örnek veriyle eşleşmiyor.")
		if assignment.stok_hareketi and assignment.stok_hareketi != transfer.name:
			frappe.throw("Zimmet başka stok transferine bağlı.")
		if not assignment.stok_hareketi:
			assignment.stok_hareketi = transfer.name
			assignment.save()
	else:
		frappe.get_doc(
			{
				"doctype": "Stock Assignment",
				"personel": employee,
				"depo": SAHA,
				"urun": "ITEM-001",
				"zimmet_miktar": 10,
				"birim": "Nos",
				"atama_tarihi": POSTING_DATE,
				"durum": "Aktif",
				"stok_hareketi": transfer.name,
				"aciklama": MARKER,
			}
		).insert(set_name=name)
	return get_datetime(f"{transfer.posting_date} {transfer.posting_time}")


def _daily_assignment(state, employee):
	name = state["documents"]["daily_assignment"]
	if frappe.db.exists("Daily Assignment", name):
		doc = frappe.get_doc("Daily Assignment", name)
		if doc.personel != employee or doc.arac != VEHICLE or str(doc.tarih) != POSTING_DATE:
			frappe.throw("Mevcut görevlendirme örnek veriyle eşleşmiyor.")
		if doc.musteri and doc.musteri != CUSTOMER:
			frappe.throw("Görev başka müşteriye ait.")
		if not doc.musteri:
			doc.musteri = CUSTOMER
			doc.save()
	else:
		frappe.get_doc(
			{
				"doctype": "Daily Assignment",
				"tarih": POSTING_DATE,
				"personel": employee,
				"arac": VEHICLE,
				"bolge": "Marmara",
				"musteri": CUSTOMER,
				"gorev": "Demo müşteri ziyareti + tahsilat",
				"durum": "Planlandı",
			}
		).insert(set_name=name)


def _sales_flow(state, at):
	from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
	from erpnext.selling.doctype.quotation.quotation import make_sales_order
	from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
	from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice

	def quote_factory():
		doc = frappe.new_doc("Quotation")
		doc.quotation_to = "Customer"
		doc.party_name = CUSTOMER
		doc.company = COMPANY
		doc.transaction_date = POSTING_DATE
		doc.valid_till = add_days(POSTING_DATE, 14)
		doc.currency = "TRY"
		doc.selling_price_list = "Standard Selling"
		doc.taxes_and_charges = tax_template()
		doc.set_taxes()
		for code, qty, rate in SALE_ITEMS:
			doc.append("items", {"item_code": code, "qty": qty, "rate": rate})
		return doc

	quote = _submitted(state, "quotation", quote_factory, SALE_ITEMS, "party_name", CUSTOMER)

	def order_factory():
		doc = make_sales_order(quote.name)
		doc.delivery_date = add_days(POSTING_DATE, 3)
		for row in doc.items:
			row.warehouse = STORES
		return doc

	order = _submitted(state, "sales_order", order_factory, SALE_ITEMS, "customer", CUSTOMER)

	def delivery_factory():
		doc = make_delivery_note(order.name)
		_timestamp(doc, at + timedelta(minutes=1))
		return doc

	delivery = _submitted(state, "delivery_note", delivery_factory, SALE_ITEMS, "customer", CUSTOMER)

	def invoice_factory():
		doc = make_sales_invoice(delivery.name)
		_timestamp(doc, at + timedelta(minutes=2))
		doc.due_date = add_days(doc.posting_date, 30)
		return doc

	invoice = _submitted(state, "sales_invoice", invoice_factory, SALE_ITEMS, "customer", CUSTOMER)

	def payment_factory():
		invoice.reload()
		if flt(invoice.outstanding_amount) != 2160:
			frappe.throw("Beklenen demo faturası 2.160 TL açık bakiyede değil; tahsilat yinelenmedi.")
		doc = get_payment_entry("Sales Invoice", invoice.name, bank_account=BANK)
		_timestamp(doc, at + timedelta(minutes=3))
		doc.mode_of_payment = "Havale/EFT"
		doc.reference_no = "DEMO-TRF-0001"
		doc.reference_date = POSTING_DATE
		return doc

	_submitted(state, "payment_entry", payment_factory, party_field="party", party=CUSTOMER)


def _complete_demo_setup():
	# Kabul kontrollerinden sonra, programatik kurulumu tamamlanmış demo Desk'i aç.
	from frappe.desk.page.setup_wizard.setup_wizard import enable_setup_wizard_complete

	for app in ("frappe", "erpnext"):
		enable_setup_wizard_complete(app)
	settings = frappe.get_doc("System Settings")
	if not settings.setup_complete:
		settings.setup_complete = 1
		settings.save()
	frappe.clear_cache()


def run(allow_demo=False, existing_documents=None):
	_require_demo(allow_demo)
	install()
	state = load_manifest(existing_documents)
	old_mute = frappe.flags.mute_emails
	old_lang = frappe.local.lang
	frappe.flags.mute_emails = True
	frappe.local.lang = "tr"
	try:
		_ensure_reference_data()
		_create_items()
		_create_parties()
		employee = _create_employees_and_vehicle()
		receipt = _stock_receipt(state)
		at = _field_stock_and_assignment(state, employee, receipt)
		_daily_assignment(state, employee)
		_sales_flow(state, at)
		from cari_custom.sample_validation import verify

		result = verify(state)
		_complete_demo_setup()
		frappe.db.commit()
		_save_manifest(state)
		return result
	except Exception:
		frappe.db.rollback()
		raise
	finally:
		frappe.flags.mute_emails = old_mute
		frappe.local.lang = old_lang
