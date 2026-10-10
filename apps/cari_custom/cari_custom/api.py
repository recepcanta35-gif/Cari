"""Cari iş merkezi için kapsamlı, miktar/finans ayrımlı API'lar."""

import csv
from io import StringIO

import frappe
from frappe.query_builder.functions import Sum

from cari_custom.security import audit, get_scope, is_managed, is_system_manager


def context(company=None):
	if frappe.session.user == "Guest":
		frappe.throw("Oturum gerekli", frappe.PermissionError)
	if is_system_manager():
		company = company or frappe.db.get_single_value("Cari Settings", "company")
		if not company or not frappe.db.exists("Company", company):
			frappe.throw("Şirket seçilmelidir")
		return company, None
	if not is_managed():
		frappe.throw("Cari kullanıcı profili gerekir", frappe.PermissionError)
	scope = get_scope()
	if company and company != scope.company:
		frappe.throw("Şirket kapsam dışında", frappe.PermissionError)
	return scope.company, scope


@frappe.whitelist()
def quantity_stock(company=None):
	company, scope = context(company)
	warehouse, bin_table, item = [frappe.qb.DocType(n) for n in ["Warehouse", "Bin", "Item"]]
	query = (
		frappe.qb.from_(bin_table)
		.join(warehouse)
		.on(warehouse.name == bin_table.warehouse)
		.join(item)
		.on(item.name == bin_table.item_code)
		.select(
			item.name.as_("item_code"),
			item.item_name,
			item.stock_uom,
			warehouse.name.as_("warehouse"),
			bin_table.actual_qty,
			bin_table.reserved_qty,
		)
		.where((warehouse.company == company) & (warehouse.disabled == 0))
		.orderby(item.name, warehouse.name)
	)
	if scope and scope.persona in {"Saha", "Depo"}:
		if not scope.warehouses:
			return []
		query = query.where(warehouse.name.isin(scope.warehouses))
	elif scope and scope.persona == "Portal":
		frappe.throw("Portal stok raporu kullanamaz", frappe.PermissionError)
	return query.run(as_dict=True)


@frappe.whitelist()
def dashboard(company=None):
	company, scope = context(company)
	persona = scope.persona if scope else "Teknik Yönetici"
	result = {
		"company": company,
		"persona": persona,
		"currency": frappe.db.get_value("Company", company, "default_currency"),
	}
	if not scope or persona in {"Yönetici", "Depo", "Saha"}:
		stock = quantity_stock(company)
		result["stock_rows"] = len(stock)
		result["stock_units_by_uom"] = {}
		for row in stock:
			result["stock_units_by_uom"][row.stock_uom] = result["stock_units_by_uom"].get(
				row.stock_uom, 0
			) + float(row.actual_qty)
		result["open_tasks"] = len(
			frappe.get_list(
				"Daily Assignment",
				filters={"company": company, "docstatus": 1, "durum": ["in", ["Planlandı", "Sahada"]]},
				pluck="name",
				limit_page_length=0,
			)
		)
	if not scope or persona in {"Yönetici", "Muhasebe", "Satış", "Saha"}:
		invoice = frappe.qb.DocType("Sales Invoice")
		query = (
			frappe.qb.from_(invoice)
			.select(Sum(invoice.base_grand_total))
			.where((invoice.company == company) & (invoice.docstatus == 1))
		)
		if scope and persona == "Saha":
			query = query.where(invoice.customer.isin(scope.customers or {"__no_customer__"}))
		result["sales_base_total"] = float(query.run()[0][0] or 0)
		gl, account = frappe.qb.DocType("GL Entry"), frappe.qb.DocType("Account")
		query = (
			frappe.qb.from_(gl)
			.join(account)
			.on(account.name == gl.account)
			.select(Sum(gl.debit - gl.credit))
			.where(
				(gl.company == company)
				& (gl.is_cancelled == 0)
				& (gl.party_type == "Customer")
				& (account.account_type == "Receivable")
			)
		)
		if scope and persona == "Saha":
			query = query.where(gl.party.isin(scope.customers or {"__no_customer__"}))
		result["customer_balance_base"] = float(query.run()[0][0] or 0)
	return result


@frappe.whitelist()
def export_quantity_stock(company=None):
	rows = quantity_stock(company)
	company, _scope = context(company)
	out = StringIO()
	writer = csv.writer(out)
	writer.writerow(["Ürün Kodu", "Ürün", "Birim", "Depo", "Miktar", "Rezerve"])

	def safe(value):
		text = str(value or "")
		return "'" + text if text.startswith(("=", "+", "-", "@", "\t", "\r")) else text

	for row in rows:
		writer.writerow(
			[
				safe(row.item_code),
				safe(row.item_name),
				safe(row.stock_uom),
				safe(row.warehouse),
				row.actual_qty,
				row.reserved_qty,
			]
		)
	audit("Miktar raporu dışa aktarıldı", reason="Kapsamlı CSV", details={"company": company})
	frappe.local.response.filename = "cari-stok-miktar.csv"
	frappe.local.response.filecontent = out.getvalue().encode("utf-8-sig")
	frappe.local.response.type = "download"


@frappe.whitelist()
def managed_users():
	company, scope = context()
	if scope and scope.persona not in {"Yönetici", "Kullanıcı Yöneticisi"}:
		frappe.throw("Kullanıcı yönetim yetkisi gerekli", frappe.PermissionError)
	filters = {"company": company}
	if scope:
		filters["persona"] = ["not in", ["Yönetici", "Kullanıcı Yöneticisi", "Muhasebe", "İnsan Kaynakları"]]
	return frappe.get_all(
		"Cari User Scope",
		filters=filters,
		fields=["user", "company", "persona", "employee", "enabled"],
		limit_page_length=500,
	)
