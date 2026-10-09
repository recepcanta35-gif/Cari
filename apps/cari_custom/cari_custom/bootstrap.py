"""Sürümlenmiş DB özelleştirmeleri; çekirdek dosyaları değiştirmeden kurulur."""

import frappe

from cari_custom.rules import COST_FIELDS
from cari_custom.security import PERSONA_ROLES

PROFILES = {
	"Yönetici": [
		"Cari Yönetici",
		"Sales Manager",
		"Purchase Manager",
		"Stock Manager",
		"Accounts Manager",
		"Maintenance Manager",
	],
	"Kullanıcı Yöneticisi": ["Cari Kullanıcı Yöneticisi"],
	"Muhasebe": ["Cari Muhasebe", "Accounts Manager"],
	"Satış": ["Cari Satış", "Sales Manager"],
	"Saha": ["Saha Personeli"],
	"Depo": ["Depo Personeli"],
	"Servis": ["Cari Servis", "Maintenance User"],
	"İnsan Kaynakları": ["Cari İK", "HR Manager"],
	"Portal": ["Cari Portal"],
}


def _permission(doctype, role, *, level=0, **rights):
	from frappe.permissions import add_permission, update_permission_property

	filters = {"parent": doctype, "role": role, "permlevel": level, "if_owner": 0}
	if not frappe.db.exists("Custom DocPerm", filters):
		add_permission(doctype, role, level, "read")
	for key, value in rights.items():
		update_permission_property(doctype, role, level, key, value, validate=False)
	frappe.clear_cache(doctype=doctype)


def _property(doctype, fieldname, key, value, kind):
	from frappe.custom.doctype.property_setter.property_setter import make_property_setter

	meta = frappe.get_meta(doctype)
	if not meta.has_field(fieldname):
		return
	if str(meta.get_field(fieldname).get(key) or 0) == str(value):
		return
	make_property_setter(doctype, fieldname, key, str(value), kind, validate_fields_for_doctype=False)


def _fields():
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	custom = {
		"Customer": [
			{
				"fieldname": "cari_company",
				"label": "Cari Şirket Bağı",
				"fieldtype": "Link",
				"options": "Company",
				"insert_after": "customer_group",
			}
		],
		"Supplier": [
			{
				"fieldname": "cari_company",
				"label": "Cari Şirket Bağı",
				"fieldtype": "Link",
				"options": "Company",
				"insert_after": "supplier_group",
			}
		],
		"Vehicle": [
			{
				"fieldname": "cari_company",
				"label": "Şirket",
				"fieldtype": "Link",
				"options": "Company",
				"insert_after": "license_plate",
			}
		],
		"Sales Order": [
			{
				"fieldname": "cari_portal_request",
				"label": "Portal İstek Anahtarı",
				"fieldtype": "Data",
				"read_only": 1,
				"unique": 1,
				"no_copy": 1,
			}
		],
	}
	for dt in ["Quotation Item", "Sales Order Item", "Delivery Note Item", "Sales Invoice Item"]:
		custom[dt] = [
			{
				"fieldname": "cari_zimmet",
				"label": "Stok Zimmeti",
				"fieldtype": "Link",
				"options": "Stock Assignment",
				"insert_after": "warehouse" if dt != "Quotation Item" else "item_code",
			}
		]
	create_custom_fields(custom)


def _roles():
	for role in set(PERSONA_ROLES.values()) | {"Cari Kapsamlı"}:
		if not frappe.db.exists("Role", role):
			frappe.get_doc(
				{"doctype": "Role", "role_name": role, "desk_access": 0 if role == "Cari Portal" else 1}
			).insert(ignore_permissions=True)
	for persona, roles in PROFILES.items():
		name = f"Cari {persona}"
		doc = (
			frappe.get_doc("Role Profile", name)
			if frappe.db.exists("Role Profile", name)
			else frappe.new_doc("Role Profile")
		)
		doc.role_profile = name
		doc.set("roles", [{"role": r} for r in roles + (["Cari Kapsamlı"] if persona != "Portal" else [])])
		doc.save(ignore_permissions=True)


def _permissions():
	read_only = {
		"read": 1,
		"write": 0,
		"create": 0,
		"delete": 0,
		"submit": 0,
		"cancel": 0,
		"share": 0,
		"export": 0,
		"print": 0,
	}
	for role in ["Saha Personeli", "Depo Personeli", "Cari Servis"]:
		for dt in [
			"Item",
			"Item Group",
			"UOM",
			"Company",
			"Warehouse",
			"Employee",
			"Vehicle",
			"Customer",
			"Territory",
			"Country",
			"Currency",
		]:
			_permission(dt, role, **read_only)
	for dt in ["Stock Entry", "Stock Ledger Entry", "Supplier"]:
		_permission(dt, "Depo Personeli", **read_only)
	for dt in ["Quotation", "Sales Order", "Delivery Note"]:
		_permission(dt, "Saha Personeli", **{**read_only, "create": 1, "write": 1})
	for dt in [
		"Sales Invoice",
		"Payment Entry",
		"Item Price",
		"Sales Taxes and Charges Template",
		"Item Tax Template",
		"Payment Terms Template",
		"Mode of Payment",
		"Address",
		"Contact",
	]:
		_permission(dt, "Saha Personeli", **read_only)
	for dt in ["Stock Assignment", "Stock Assignment Return", "Daily Assignment"]:
		_permission(
			dt,
			"Saha Personeli",
			**{
				**read_only,
				"write": 1 if dt == "Daily Assignment" else 0,
				"create": 1 if dt == "Stock Assignment Return" else 0,
			},
		)
		for role in ["Depo Personeli", "Cari Yönetici"]:
			_permission(
				dt,
				role,
				read=1,
				create=1,
				write=1,
				submit=1,
				cancel=1,
				amend=1,
				delete=0,
				share=0,
				export=0,
				print=0,
			)
	for dt in [
		"Customer",
		"Sales Order",
		"Quotation",
		"Sales Invoice",
		"Delivery Note",
		"Cari Service Record",
	]:
		if frappe.db.exists("DocType", dt):
			_permission(dt, "Cari Portal", **read_only)
	# Yetki seviyeleri: stok değerleri 1, personel özel bilgileri 2.
	financial = {
		"System Manager",
		"Cari Yönetici",
		"Cari Muhasebe",
		"Accounts Manager",
		"Stock Manager",
		"Purchase Manager",
	}
	for dt in [
		"Item",
		"Stock Entry",
		"Stock Ledger Entry",
		"Purchase Receipt",
		"Purchase Invoice",
		"Delivery Note",
		"Sales Invoice",
	]:
		for role in financial:
			_permission(
				dt,
				role,
				level=1,
				read=1,
				write=1
				if role
				in {
					"System Manager",
					"Cari Yönetici",
					"Stock Manager",
					"Purchase Manager",
					"Accounts Manager",
				}
				else 0,
			)
	for role in ["System Manager", "HR Manager", "Cari İK"]:
		_permission("Employee", role, level=2, read=1, write=1)


def _protected_fields():
	money_fields = COST_FIELDS | {
		"stock_queue",
		"stock_value",
		"total",
		"base_total",
		"net_total",
		"base_net_total",
		"grand_total",
		"base_grand_total",
		"rounded_total",
		"base_rounded_total",
		"in_words",
		"base_in_words",
		"base_rate",
		"base_amount",
		"amount",
		"rate",
		"price_list_rate",
		"standard_rate",
	}
	for dt in [
		"Item",
		"Stock Entry",
		"Stock Entry Detail",
		"Stock Ledger Entry",
		"Purchase Receipt",
		"Purchase Receipt Item",
		"Purchase Invoice",
		"Purchase Invoice Item",
	]:
		for f in frappe.get_meta(dt).fields:
			if f.fieldname in money_fields:
				_property(dt, f.fieldname, "permlevel", 1, "Int")
	# Satış fiyatı değil, maliyet alanları korunur.
	for dt in ["Delivery Note", "Delivery Note Item", "Sales Invoice", "Sales Invoice Item"]:
		for f in frappe.get_meta(dt).fields:
			if f.fieldname in COST_FIELDS:
				_property(dt, f.fieldname, "permlevel", 1, "Int")
	for key in [
		"date_of_birth",
		"personal_email",
		"passport_number",
		"bank_ac_no",
		"salary_mode",
		"ctc",
		"pan_number",
	]:
		_property("Employee", key, "permlevel", 2, "Int")
	for dt in [
		"Item",
		"Stock Entry",
		"Delivery Note",
		"Sales Invoice",
		"Sales Order",
		"Purchase Receipt",
		"Purchase Invoice",
	]:
		for fieldname in ["barcodes", "barcode", "scan_barcode", "scan_barcode_section"]:
			_property(dt, fieldname, "hidden", 1, "Check")


def _legacy_metadata():
	# Stok/finans defterine dokunmaz; özel draft kayıtlara eksik şirket bilgisi ekler.
	for row in frappe.get_all(
		"Stock Assignment",
		fields=["name", "depo", "stok_hareketi", "kaynak_depo", "company"],
		filters={"company": ["is", "not set"]},
	):
		values = {"company": frappe.db.get_value("Warehouse", row.depo, "company")}
		if row.stok_hareketi and not row.kaynak_depo:
			values["kaynak_depo"] = frappe.db.get_value(
				"Stock Entry Detail", {"parent": row.stok_hareketi}, "s_warehouse"
			)
		frappe.db.set_value("Stock Assignment", row.name, values, update_modified=False)
	for row in frappe.get_all(
		"Daily Assignment", fields=["name", "personel"], filters={"company": ["is", "not set"]}
	):
		frappe.db.set_value(
			"Daily Assignment",
			row.name,
			"company",
			frappe.db.get_value("Employee", row.personel, "company"),
			update_modified=False,
		)


def run():
	from cari_custom.security import install_query_guard

	install_query_guard()
	_fields()
	_roles()
	_permissions()
	_protected_fields()
	_legacy_metadata()
	if frappe.db.exists("Notification", "Tahsilat Vadesi Yaklaşıyor"):
		frappe.db.set_value("Notification", "Tahsilat Vadesi Yaklaşıyor", "enabled", 0)
	frappe.clear_cache()


def setup_defaults(company, selling_price_list="Standard Selling"):
	doc = frappe.get_single("Cari Settings")
	if not doc.company:
		doc.company = company
	if not doc.selling_price_list:
		doc.selling_price_list = selling_price_list
	doc.save(ignore_permissions=True)
