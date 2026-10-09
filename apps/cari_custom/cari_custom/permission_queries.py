from cari_custom.security import query_condition


def company(user=None):
	return query_condition("Company", user)


def customer(user=None):
	return query_condition("Customer", user)


def supplier(user=None):
	return query_condition("Supplier", user)


def vehicle(user=None):
	return query_condition("Vehicle", user)


def employee(user=None):
	return query_condition("Employee", user)


def item_price(user=None):
	return query_condition("Item Price", user)


def address(user=None):
	return query_condition("Address", user)


def contact(user=None):
	return query_condition("Contact", user)


def quotation(user=None):
	return query_condition("Quotation", user)


def stock_assignment(user=None):
	return query_condition("Stock Assignment", user)


def stock_assignment_return(user=None):
	return query_condition("Stock Assignment Return", user)


def daily_assignment(user=None):
	return query_condition("Daily Assignment", user)


def warehouse(user=None):
	return query_condition("Warehouse", user)


def stock_entry(user=None):
	return query_condition("Stock Entry", user)


def stock_ledger_entry(user=None):
	return query_condition("Stock Ledger Entry", user)


def sales_order(user=None):
	return query_condition("Sales Order", user)


def sales_invoice(user=None):
	return query_condition("Sales Invoice", user)


def delivery_note(user=None):
	return query_condition("Delivery Note", user)


def purchase_order(user=None):
	return query_condition("Purchase Order", user)


def purchase_receipt(user=None):
	return query_condition("Purchase Receipt", user)


def purchase_invoice(user=None):
	return query_condition("Purchase Invoice", user)


def payment_entry(user=None):
	return query_condition("Payment Entry", user)


def gl_entry(user=None):
	return query_condition("GL Entry", user)


def cari_payment_instrument(user=None):
	return query_condition("Cari Payment Instrument", user)


def cari_shipment(user=None):
	return query_condition("Cari Shipment", user)


def cari_service_record(user=None):
	return query_condition("Cari Service Record", user)


def warranty_claim(user=None):
	return query_condition("Warranty Claim", user)


def item(user=None):
	return query_condition("Item", user)
