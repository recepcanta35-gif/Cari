"""Barkodsuz katalog ve kendi müşterisine bağlı portal siparişi.

İstemci fiyat/şirket/müşteri/hesap bilgisi gönderemez. Sipariş draft'tır;
stok tahsisi ve finans onayı işletmenin standart ERPNext akışında yapılır.
"""

from hashlib import sha256
from uuid import UUID

import frappe
from frappe.query_builder import Order
from frappe.rate_limiter import rate_limit
from frappe.utils import add_days, flt, today

from cari_custom.rules import RuleViolation, positive_quantity
from cari_custom.security import get_scope, is_system_manager


def settings_for_catalog():
	settings = frappe.get_single("Cari Settings")
	if not settings.portal_enabled:
		frappe.throw("Portal yapılandırılmamış/kapalı", frappe.PermissionError)
	if frappe.session.user == "Guest":
		if not settings.public_catalog:
			frappe.throw("Katalog için oturum gerekli", frappe.PermissionError)
	elif not is_system_manager():
		scope = get_scope()
		if not scope or scope.company != settings.company:
			frappe.throw("Portal şirketi kapsam dışında", frappe.PermissionError)
	return settings


def portal_context():
	if frappe.session.user == "Guest":
		frappe.throw("Müşteri oturumu gerekli", frappe.PermissionError)
	scope = get_scope()
	if not scope or scope.persona != "Portal" or len(scope.customers) != 1:
		frappe.throw("Tek müşteriye bağlı portal profili gerekli", frappe.PermissionError)
	settings = settings_for_catalog()
	return settings, scope, next(iter(scope.customers))


def price_for(item, settings):
	price = frappe.qb.DocType("Item Price")
	query = (
		frappe.qb.from_(price)
		.select(price.price_list_rate, price.currency)
		.where(
			(price.item_code == item.name)
			& (price.price_list == settings.selling_price_list)
			& (price.uom == item.stock_uom)
			& (price.customer.isnull() | (price.customer == ""))
			& (price.valid_from.isnull() | (price.valid_from <= today()))
			& (price.valid_upto.isnull() | (price.valid_upto >= today()))
		)
		.orderby(price.valid_from, price.creation, order=Order.desc)
		.limit(1)
	)
	rows = query.run(as_dict=True)
	if not rows or flt(rows[0].price_list_rate) <= 0:
		frappe.throw("Ürünün etkin satış fiyatı yok")
	return rows[0]


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=120, seconds=60)
def catalog(search="", category=None, offset=0, limit=24):
	settings = settings_for_catalog()
	limit, offset = min(48, max(1, int(limit))), max(0, int(offset))
	item = frappe.qb.DocType("Item")
	query = (
		frappe.qb.from_(item)
		.select(item.name, item.item_name, item.item_group, item.stock_uom, item.image)
		.where((item.disabled == 0) & (item.is_sales_item == 1))
	)
	if search:
		text = "%" + str(search)[:80] + "%"
		query = query.where(item.name.like(text) | item.item_name.like(text))
	if category:
		query = query.where(item.item_group == category)
	rows = query.orderby(item.item_name).offset(offset).limit(limit).run(as_dict=True)
	result = []
	for row in rows:
		try:
			price = price_for(row, settings)
		except frappe.ValidationError:
			frappe.clear_messages()
			continue
		qty = flt(
			frappe.db.get_value(
				"Bin", {"item_code": row.name, "warehouse": settings.portal_warehouse}, "actual_qty"
			)
		)
		result.append(
			{
				"item_code": row.name,
				"name": row.item_name,
				"category": row.item_group,
				"uom": row.stock_uom,
				"image": row.image if (row.image or "").startswith(("/files/", "/assets/")) else None,
				"price": flt(price.price_list_rate),
				"currency": price.currency,
				"in_stock": qty > 0,
			}
		)
	return {"items": result, "prices_exclude_vat": True, "offset": offset, "limit": limit}


@frappe.whitelist(methods=["POST"])
@rate_limit(limit=20, seconds=3600)
def place_order(items, request_id):
	settings, scope, customer = portal_context()
	try:
		request_id = str(UUID(str(request_id)))
	except ValueError:
		frappe.throw("Sipariş istek kimliği UUID olmalıdır")
	key = sha256(f"{scope.user}:{request_id}".encode()).hexdigest()
	existing = frappe.db.get_value("Sales Order", {"cari_portal_request": key}, "name")
	if existing:
		doc = frappe.get_doc("Sales Order", existing)
		if doc.company != scope.company or doc.customer != customer:
			frappe.throw("İstek anahtarı kapsam dışında", frappe.PermissionError)
		return {
			"name": doc.name,
			"status": doc.status,
			"grand_total": doc.grand_total,
			"currency": doc.currency,
			"reused": True,
		}
	items = frappe.parse_json(items)
	if not isinstance(items, list) or not 1 <= len(items) <= 100:
		frappe.throw("Sepet 1–100 ürün satırı içermelidir")
	doc = frappe.new_doc("Sales Order")
	doc.company, doc.customer = scope.company, customer
	doc.transaction_date, doc.delivery_date = today(), add_days(today(), 3)
	doc.currency = frappe.db.get_value("Company", scope.company, "default_currency")
	doc.selling_price_list = settings.selling_price_list
	doc.cari_portal_request = key
	seen = set()
	for row in sorted(items, key=lambda x: str(x.get("item_code", "")) if isinstance(x, dict) else ""):
		if (
			not isinstance(row, dict)
			or set(row) != {"item_code", "qty"}
			or not isinstance(row["item_code"], str)
		):
			frappe.throw("İstemci sadece ürün kodu ve miktar gönderebilir; fiyat kabul edilmez")
		if row["item_code"] in seen:
			frappe.throw("Mükerrer sepet kalemi")
		seen.add(row["item_code"])
		try:
			qty = positive_quantity(row["qty"])
		except RuleViolation as exc:
			frappe.throw(str(exc))
		item = frappe.get_doc("Item", row["item_code"])
		if item.disabled or not item.is_sales_item:
			frappe.throw("Ürün satışa kapalı")
		price = price_for(item, settings)
		if price.currency != doc.currency:
			frappe.throw("Portal fiyat listesi şirket para biriminde olmalıdır")
		if item.is_stock_item:
			frappe.db.sql(
				"SELECT name FROM `tabBin` WHERE item_code=%s AND warehouse=%s FOR UPDATE",
				(item.name, settings.portal_warehouse),
			)
			bin_values = frappe.db.get_value(
				"Bin",
				{"item_code": item.name, "warehouse": settings.portal_warehouse},
				["actual_qty", "reserved_qty"],
			)
			available = flt(bin_values[0] - bin_values[1]) if bin_values else 0
			if float(qty) > available:
				frappe.throw(
					"İstenen miktar mevcut stoktan fazla; sipariş onayı öncesi tekrar kontrol edilir"
				)
		doc.append(
			"items",
			{
				"item_code": item.name,
				"qty": float(qty),
				"rate": price.price_list_rate,
				"warehouse": settings.portal_warehouse,
			},
		)
	# Core fiyat/iskonto/vergi/risk kuralları korunur; portal submit hakkı kazanmaz.
	doc.insert(ignore_permissions=True)
	return {
		"name": doc.name,
		"status": doc.status,
		"grand_total": doc.grand_total,
		"currency": doc.currency,
		"reused": False,
		"stock_reserved": False,
	}


@frappe.whitelist()
def my_records(kind="Sales Order"):
	_settings, scope, customer = portal_context()
	definitions = {
		"Sales Order": (
			["name", "transaction_date", "status", "grand_total", "currency"],
			{"customer": customer},
		),
		"Quotation": (
			["name", "transaction_date", "status", "grand_total", "currency"],
			{"quotation_to": "Customer", "party_name": customer},
		),
		"Sales Invoice": (
			["name", "posting_date", "status", "grand_total", "outstanding_amount", "currency"],
			{"customer": customer, "docstatus": 1},
		),
		"Cari Shipment": (
			["name", "status", "carrier", "tracking_number", "delivered_at"],
			{"customer": customer, "docstatus": 1},
		),
		"Cari Service Record": (
			["name", "status", "item", "opened_on", "completed_on"],
			{"customer": customer, "docstatus": 1},
		),
	}
	if kind not in definitions:
		frappe.throw("Portal kayıt türü geçersiz")
	fields, filters = definitions[kind]
	filters["company"] = scope.company
	return frappe.get_all(
		kind, filters=filters, fields=fields, order_by="modified desc", limit_page_length=100
	)
