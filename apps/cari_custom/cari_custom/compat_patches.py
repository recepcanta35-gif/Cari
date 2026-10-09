"""ERPNext v15/PostgreSQL için dar kapsamlı, siteye göre çalışan adaptörler.

Genel frappe.get_all/get_list/sql veya muhasebe validasyonları değiştirilmez.
İçe aktarımda DB/konfigürasyon okunmaz. install() istek/job/migrate hook'larında
ve demo/test girişinde çağrılır; tekrar çağırmak güvenlidir. MariaDB ve v16+
yolları çekirdekte kalır. Üretim tercihi v15 + MariaDB'dir.
"""

import sys
from functools import wraps
from importlib import import_module

import frappe


def _postgres_site():
	return getattr(frappe.local, "conf", {}).get("db_type") == "postgres"


def _wrap(target, name, replacement, aliases=(), *, always=False):
	original = getattr(target, name)
	if getattr(original, "_cari_pg_adapter", False):
		return

	@wraps(original)
	def adapted(*args, **kwargs):
		if always or _postgres_site():
			return replacement(*args, **kwargs)
		return original(*args, **kwargs)

	adapted._cari_pg_adapter = True
	# Bir whitelist endpoint'i sarılırsa aynı erişim/HTTP yöntemleri korunur.
	if original in frappe.whitelisted:
		frappe.whitelisted.append(adapted)
		frappe.allowed_http_methods_for_whitelisted_func[adapted] = (
			frappe.allowed_http_methods_for_whitelisted_func[original]
		)
		if original in frappe.guest_methods:
			frappe.guest_methods.append(adapted)
		if original in frappe.xss_safe_methods:
			frappe.xss_safe_methods.append(adapted)
	setattr(target, name, adapted)
	# Önceden yapılmış from-import bağları da aynı fonksiyona yönlenir.
	loaded = [m for n, m in list(sys.modules.items()) if n.startswith("erpnext.") and m is not None]
	for alias in [*aliases, *loaded]:
		if getattr(alias, name, None) is original:
			setattr(alias, name, adapted)


def install(**_kwargs):
	"""Request/job hook'ları kwargs gönderebilir. Fonksiyon DB işlemi yapmaz."""
	import erpnext

	if erpnext.__version__.split(".", 1)[0] != "15":
		return
	from cari_custom import postgres_queries as queries

	inventory = import_module("erpnext.stock.doctype.inventory_dimension.inventory_dimension")
	stock_ledger_entry = import_module("erpnext.stock.doctype.stock_ledger_entry.stock_ledger_entry")
	purchase_receipt = import_module("erpnext.stock.doctype.purchase_receipt.purchase_receipt")
	buying = import_module("erpnext.controllers.buying_controller")
	stock_balance = import_module("erpnext.stock.stock_balance")
	stock_ledger = import_module("erpnext.stock.stock_ledger")
	sales_order = import_module("erpnext.selling.doctype.sales_order.sales_order")
	reservation = import_module("erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry")
	account_utils = import_module("erpnext.accounts.utils")
	payment_entry = import_module("erpnext.accounts.doctype.payment_entry.payment_entry")

	_wrap(inventory, "get_inventory_dimensions", queries.get_inventory_dimensions, [stock_ledger_entry])
	_wrap(purchase_receipt, "get_item_wise_returned_qty", queries.get_item_wise_returned_qty)
	_wrap(buying.BuyingController, "set_landed_cost_voucher_amount", queries.set_landed_cost_voucher_amount)
	_wrap(stock_balance, "get_reserved_qty", queries.get_reserved_qty, [sales_order])
	_wrap(
		reservation,
		"get_sre_reserved_warehouses_for_voucher",
		queries.get_sre_reserved_warehouses_for_voucher,
	)
	_wrap(account_utils.QueryPaymentLedger, "query_for_outstanding", queries.query_for_outstanding)
	_wrap(payment_entry, "get_negative_outstanding_invoices", queries.get_negative_outstanding_invoices)
	_wrap(payment_entry, "get_orders_to_be_billed", queries.get_orders_to_be_billed)
	_wrap(
		payment_entry,
		"get_matched_payment_request_of_references",
		queries.get_matched_payment_request_of_references,
	)
	_wrap(
		stock_ledger,
		"get_previous_sle_of_current_voucher",
		queries.get_previous_sle_of_current_voucher,
		always=True,
	)
