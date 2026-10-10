# Portions adapted from ERPNext v15.122.0.
# Copyright (c) Frappe Technologies Pvt. Ltd. and contributors.
# SPDX-License-Identifier: GPL-3.0-only

"""ERPNext v15 için hedefli PostgreSQL sorgu düzeltmeleri.

Yalnızca compat_patches.install() üzerinden PostgreSQL sitelerinde çağrılır.
Stok/muhasebe doğrulamaları atlanmaz; çekirdek uygulamalar değiştirilmez.
Kaynak: ERPNext v15.122.0 (stock_balance, inventory_dimension,
purchase_receipt, stock_reservation_entry, accounts.utils).
"""

import frappe
from frappe.query_builder import AliasedQuery, Case, Criterion
from frappe.query_builder.functions import Max, Min, Sum
from frappe.utils import cint, flt


def get_inventory_dimensions():
	if not getattr(frappe.local, "inventory_dimensions", None):
		frappe.local.inventory_dimensions = frappe.get_all(
			"Inventory Dimension",
			fields=[
				"distinct target_fieldname as fieldname",
				"source_fieldname",
				"reference_document as doctype",
				"validate_negative_stock",
			],
			order_by="target_fieldname",
		)
	return frappe.local.inventory_dimensions


def get_item_wise_returned_qty(pr_doc):
	return frappe._dict(
		frappe.get_all(
			"Purchase Receipt",
			fields=[
				"`tabPurchase Receipt Item`.purchase_receipt_item",
				"sum(abs(`tabPurchase Receipt Item`.qty)) as qty",
			],
			filters=[
				["Purchase Receipt", "docstatus", "=", 1],
				["Purchase Receipt", "is_return", "=", 1],
				["Purchase Receipt Item", "purchase_receipt_item", "in", [d.name for d in pr_doc.items]],
			],
			group_by="`tabPurchase Receipt Item`.purchase_receipt_item",
			order_by="`tabPurchase Receipt Item`.purchase_receipt_item",
			as_list=True,
		)
	)


def set_landed_cost_voucher_amount(self):
	lci = frappe.qb.DocType("Landed Cost Item")
	for item in self.get("items"):
		# Tüm masraflar toplanır; cost_center ile gruplamak toplamın bir kısmını kaybettirir.
		result = (
			frappe.qb.from_(lci)
			.select(Sum(lci.applicable_charges), Min(lci.cost_center))
			.where(
				(lci.docstatus == 1)
				& (lci.purchase_receipt_item == item.name)
				& (lci.receipt_document == self.name)
			)
		).run()
		item.landed_cost_voucher_amount = flt(result[0][0]) if result else 0.0
		if not item.cost_center and result and result[0][1]:
			item.db_set("cost_center", result[0][1])


def get_reserved_qty(item_code, warehouse):
	flag = cint(
		frappe.get_cached_value(
			"Selling Settings", "Selling Settings", "dont_reserve_sales_order_qty_on_sales_return"
		)
	)
	# ERPNext v15 sorgusu ile aynı kapsam: normal kalemler + Product Bundle bileşenleri.
	# MySQL IF(integer, ...) yerine PostgreSQL CASE WHEN integer = 1 kullanılır.
	result = frappe.db.sql(
		"""
		SELECT SUM(dnpi_qty * (
			(so_item_qty - so_item_delivered_qty -
			 CASE WHEN %(flag)s = 1 THEN so_item_returned_qty ELSE 0 END) / so_item_qty
		))
		FROM (
			SELECT packed.qty AS dnpi_qty, so_item.qty AS so_item_qty,
				so_item.delivered_qty AS so_item_delivered_qty,
				so_item.returned_qty AS so_item_returned_qty,
				packed.parent, packed.name
			FROM `tabPacked Item` packed
			INNER JOIN `tabSales Order Item` so_item ON so_item.name = packed.parent_detail_docname
			INNER JOIN `tabSales Order` so ON so.name = packed.parent
			WHERE packed.item_code = %(item)s AND packed.warehouse = %(warehouse)s
				AND packed.parenttype = 'Sales Order' AND packed.item_code != packed.parent_item
				AND (so_item.delivered_by_supplier IS NULL OR so_item.delivered_by_supplier = 0)
				AND so.docstatus = 1 AND so.status NOT IN ('On Hold', 'Closed')
			UNION
			SELECT so_item.stock_qty AS dnpi_qty, so_item.qty AS so_item_qty,
				so_item.delivered_qty AS so_item_delivered_qty,
				so_item.returned_qty AS so_item_returned_qty,
				so_item.parent, so_item.name
			FROM `tabSales Order Item` so_item
			INNER JOIN `tabSales Order` so ON so.name = so_item.parent
			WHERE so_item.item_code = %(item)s AND so_item.warehouse = %(warehouse)s
				AND (so_item.delivered_by_supplier IS NULL OR so_item.delivered_by_supplier = 0)
				AND so.docstatus = 1 AND so.status NOT IN ('On Hold', 'Closed')
		) reserved
		WHERE so_item_qty >= so_item_delivered_qty
		""",
		{"flag": flag, "item": item_code, "warehouse": warehouse},
	)
	return flt(result[0][0]) if result else 0.0


def get_sre_reserved_warehouses_for_voucher(voucher_type, voucher_no, voucher_detail_no=None):
	sre = frappe.qb.DocType("Stock Reservation Entry")
	query = (
		frappe.qb.from_(sre)
		.select(sre.warehouse)
		.where(
			(sre.docstatus == 1)
			& (sre.voucher_type == voucher_type)
			& (sre.voucher_no == voucher_no)
			& sre.status.notin(["Delivered", "Cancelled"])
		)
		.groupby(sre.warehouse)
		.orderby(Min(sre.creation), sre.warehouse)
	)
	if voucher_detail_no:
		query = query.where(sre.voucher_detail_no == voucher_detail_no)
	return [row[0] for row in query.run()]


def query_for_outstanding(self):
	"""QueryPaymentLedger: tam/kısmi ödemeleri aynı cari referansta toplar.

	Tarih/maliyet merkezi bazında GROUP BY eklemek ödemeleri parçalayarak yanlış
	bakiye üretir. Hesap + belge + cari anahtarları gruplanır; metadata aggregate
	edilir. CTE sonucundaki HAVING alias yerine WHERE kullanılır.
	"""
	qb = frappe.qb
	ple = self.ple
	voucher_filter = []
	against_filter = []
	if self.vouchers:
		types = {v.voucher_type for v in self.vouchers}
		names = {v.voucher_no for v in self.vouchers}
		voucher_filter.extend([ple.voucher_type.isin(types), ple.voucher_no.isin(names)])
		against_filter.extend([ple.against_voucher_type.isin(types), ple.against_voucher_no.isin(names)])
	if self.voucher_no:
		voucher_filter.append(ple.voucher_no.like(f"%{self.voucher_no}%"))
		against_filter.append(ple.against_voucher_no.like(f"%{self.voucher_no}%"))

	if self.limit and self.get_invoices:
		invoice_date = Max(
			Case().when(
				(ple.voucher_no == ple.against_voucher_no) & (ple.voucher_type == ple.against_voucher_type),
				ple.posting_date,
			)
		)
		eligible = (
			qb.from_(ple)
			.select(ple.against_voucher_no.as_("voucher_no"), invoice_date.as_("invoice_date"))
			.where(ple.delinked == 0)
			.where(
				Criterion.all(
					against_filter + self.common_filter + self.dimensions_filter + self.voucher_posting_date
				)
			)
			.groupby(ple.account, ple.against_voucher_type, ple.against_voucher_no, ple.party_type, ple.party)
			.having(Sum(ple.amount_in_account_currency) > 0)
			.orderby(qb.Field("invoice_date"), qb.Field("voucher_no"))
			.limit(self.limit)
		).run()
		if eligible:
			names = [row[0] for row in eligible]
			voucher_filter.append(ple.voucher_no.isin(names))
			against_filter.append(ple.against_voucher_no.isin(names))
		else:
			self.voucher_outstandings = []
			return

	voucher_amount = (
		qb.from_(ple)
		.select(
			ple.account,
			ple.voucher_type,
			ple.voucher_no,
			ple.party_type,
			ple.party,
			Min(ple.posting_date).as_("posting_date"),
			Max(ple.due_date).as_("due_date"),
			ple.account_currency.as_("currency"),
			Min(ple.cost_center).as_("cost_center"),
			Sum(ple.amount).as_("amount"),
			Sum(ple.amount_in_account_currency).as_("amount_in_account_currency"),
			Max(ple.remarks).as_("remarks"),
		)
		.where(ple.delinked == 0)
		.where(
			Criterion.all(
				voucher_filter + self.common_filter + self.dimensions_filter + self.voucher_posting_date
			)
		)
		.groupby(
			ple.account, ple.voucher_type, ple.voucher_no, ple.party_type, ple.party, ple.account_currency
		)
	)
	outstanding = (
		qb.from_(ple)
		.select(
			ple.account,
			ple.against_voucher_type.as_("voucher_type"),
			ple.against_voucher_no.as_("voucher_no"),
			ple.party_type,
			ple.party,
			Sum(ple.amount).as_("amount"),
			Sum(ple.amount_in_account_currency).as_("amount_in_account_currency"),
		)
		.where(ple.delinked == 0)
		.where(Criterion.all(against_filter + self.common_filter))
		.groupby(ple.account, ple.against_voucher_type, ple.against_voucher_no, ple.party_type, ple.party)
	)
	v = AliasedQuery("vouchers")
	o = AliasedQuery("outstanding")
	query = (
		qb.with_(voucher_amount, "vouchers")
		.with_(outstanding, "outstanding")
		.from_(AliasedQuery("vouchers"))
		.left_join(AliasedQuery("outstanding"))
		.on(
			(v.account == o.account)
			& (v.voucher_type == o.voucher_type)
			& (v.voucher_no == o.voucher_no)
			& (v.party_type == o.party_type)
			& (v.party == o.party)
		)
		.select(
			v.account,
			v.voucher_type,
			v.voucher_no,
			v.party_type,
			v.party,
			v.posting_date,
			v.amount.as_("invoice_amount"),
			v.amount_in_account_currency.as_("invoice_amount_in_account_currency"),
			o.amount.as_("outstanding"),
			o.amount_in_account_currency.as_("outstanding_in_account_currency"),
			(v.amount - o.amount).as_("paid_amount"),
			(v.amount_in_account_currency - o.amount_in_account_currency).as_(
				"paid_amount_in_account_currency"
			),
			v.due_date,
			v.currency,
			v.cost_center,
			v.remarks,
		)
	)
	for bound, upper in [(self.min_outstanding, False), (self.max_outstanding, True)]:
		if bound:
			query = query.where(
				o.amount_in_account_currency <= bound
				if (upper and bound > 0) or (not upper and bound < 0)
				else o.amount_in_account_currency >= bound
			)
	if self.get_invoices:
		query = query.where(o.amount_in_account_currency > 0)
	elif self.get_payments:
		query = query.where(o.amount_in_account_currency < 0)
	if self.limit:
		query = query.limit(self.limit)
	self.cte_query_voucher_amount_and_outstanding = query
	self.voucher_outstandings = query.run(as_dict=True)


def get_negative_outstanding_invoices(
	party_type,
	party,
	party_account,
	party_account_currency,
	company_currency,
	cost_center=None,
	condition=None,
):
	"""İade/alacak faturaları da tahsilat validasyonunda sorgulanır; atlanmaz."""
	if party_type not in ("Customer", "Supplier"):
		return []
	voucher_type = "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"
	account = "debit_to" if party_type == "Customer" else "credit_to"
	party_field = "customer" if party_type == "Customer" else "supplier"
	prefix = "base_" if party_account_currency == company_currency else ""
	rounded = prefix + "rounded_total"
	grand = prefix + "grand_total"
	supplier_condition = (
		"AND (release_date IS NULL OR release_date <= CURRENT_DATE)" if party_type == "Supplier" else ""
	)
	# condition, çekirdek get_outstanding_reference_documents tarafından escape edilerek üretilir.
	condition = (
		(condition or "").replace("voucher_type=", "%(voucher_type)s=").replace("voucher_no=", "name=")
	)
	return frappe.db.sql(
		f"""
		SELECT %(voucher_type)s AS voucher_type, name AS voucher_no, {account} AS account,
			CASE WHEN {rounded} != 0 THEN {rounded} ELSE {grand} END AS invoice_amount,
			outstanding_amount, posting_date, due_date, conversion_rate AS exchange_rate
		FROM `tab{voucher_type}`
		WHERE {party_field} = %(party)s AND {account} = %(account)s
			AND docstatus = 1 AND outstanding_amount < 0
			{supplier_condition} {condition}
		ORDER BY posting_date, name
		""",
		{"voucher_type": voucher_type, "party": party, "account": party_account},
		as_dict=True,
	)


def get_orders_to_be_billed(
	posting_date,
	party_type,
	party,
	company,
	party_account_currency,
	company_currency,
	cost_center=None,
	filters=None,
):
	from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_dimensions
	from erpnext.setup.utils import get_exchange_rate
	from frappe.query_builder.functions import Abs

	if party_type not in ("Customer", "Supplier"):
		return []
	voucher_type = "Sales Order" if party_type == "Customer" else "Purchase Order"
	party_field = "customer" if party_type == "Customer" else "supplier"
	filters = filters or {}
	order = frappe.qb.DocType(voucher_type)
	prefix = "base_" if party_account_currency == company_currency else ""
	rounded = order[prefix + "rounded_total"]
	grand = order[prefix + "grand_total"]
	amount = Case().when(rounded != 0, rounded).else_(grand)
	query = (
		frappe.qb.from_(order)
		.select(
			order.name.as_("voucher_no"),
			amount.as_("invoice_amount"),
			(amount - order.advance_paid).as_("outstanding_amount"),
			order.transaction_date.as_("posting_date"),
		)
		.where(
			(order[party_field] == party)
			& (order.docstatus == 1)
			& (order.company == company)
			& (order.status != "Closed")
			& (amount > order.advance_paid)
			& (Abs(100 - order.per_billed) > 0.01)
		)
		.orderby(order.transaction_date, order.name)
	)
	for dimension in get_dimensions(True)[0]:
		if filters.get(dimension.fieldname):
			query = query.where(order[dimension.fieldname] == filters[dimension.fieldname])
	result = []
	for row in query.run(as_dict=True):
		lower = filters.get("outstanding_amt_greater_than")
		upper = filters.get("outstanding_amt_less_than")
		if lower and upper and not (flt(lower) <= flt(row.outstanding_amount) <= flt(upper)):
			continue
		row.voucher_type = voucher_type
		row.exchange_rate = get_exchange_rate(party_account_currency, company_currency, posting_date)
		result.append(row)
	return result


def get_matched_payment_request_of_references(references=None):
	from frappe.query_builder.functions import Count
	from pypika.terms import Tuple

	if not references:
		return None
	refs = {
		(row.reference_doctype, row.reference_name, row.allocated_amount)
		for row in references
		if row.reference_doctype and row.reference_name and row.allocated_amount
	}
	if not refs:
		return None
	request = frappe.qb.DocType("Payment Request")
	matched = (
		frappe.qb.from_(request)
		.select(
			request.reference_doctype,
			request.reference_name,
			request.outstanding_amount.as_("allocated_amount"),
			Min(request.name).as_("payment_request"),
		)
		.where(
			Tuple(request.reference_doctype, request.reference_name, request.outstanding_amount).isin(refs)
		)
		.where((request.status != "Paid") & (request.docstatus == 1))
		.groupby(request.reference_doctype, request.reference_name, request.outstanding_amount)
		.having(Count("*") == 1)
	).run()
	return matched or None


def get_previous_sle_of_current_voucher(args, operator="<", exclude_current_voucher=False):
	"""Oluşturulma zamanı yalnızca eşit kayıt zamanı için tie-breaker'dır.

	v15 mevcut sorgusu creation filtresini bütün geçmişe uyguluyor. Saat dilimi
	değişiminden önceki kayıtlar bu nedenle yokmuş gibi değerlendirilebiliyor.
	Stok güvenliği korunur: önce posting_datetime, eşitse creation karşılaştırılır.
	"""
	from erpnext.stock.utils import get_combine_datetime
	from frappe.query_builder import Order

	if not args.get("posting_date"):
		args["posting_datetime"] = "1900-01-01 00:00:00"
	if not args.get("posting_datetime"):
		args["posting_datetime"] = get_combine_datetime(args["posting_date"], args["posting_time"])
	sle = frappe.qb.DocType("Stock Ledger Entry")
	at = args["posting_datetime"]
	operators = {
		"<": sle.posting_datetime < at,
		"<=": sle.posting_datetime <= at,
		">": sle.posting_datetime > at,
		">=": sle.posting_datetime >= at,
		"=": sle.posting_datetime == at,
	}
	if operator not in operators:
		raise ValueError("Desteklenmeyen stok defteri karşılaştırması")
	boundary = operators[operator]
	if (
		not exclude_current_voucher
		and args.get("creation")
		and args.get("sle_id")
		and not args.get("cancelled")
	):
		boundary = (sle.posting_datetime < at) | (
			(sle.posting_datetime == at) & (sle.creation < args["creation"])
		)
	query = (
		frappe.qb.from_(sle)
		.select("*", sle.posting_datetime.as_("timestamp"))
		.where(
			(sle.item_code == args.get("item_code"))
			& (sle.warehouse == args.get("warehouse"))
			& (sle.is_cancelled == 0)
			& boundary
		)
		.orderby(sle.posting_datetime, sle.creation, order=Order.desc)
		.limit(1)
		.for_update()
	)
	if exclude_current_voucher:
		query = query.where(sle.voucher_no != args.get("voucher_no"))
	rows = query.run(as_dict=True)
	return rows[0] if rows else frappe._dict()
