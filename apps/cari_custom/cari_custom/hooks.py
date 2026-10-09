app_name = "cari_custom"
app_title = "Cari Custom"
app_publisher = "Cari"
app_description = "Personel stok zimmeti, gunluk gorevlendirme ve kargo takibi ozel gelistirmeleri"
app_email = "info@cari.local"
app_license = "GPL-3.0"

# Kapsam disi: barkod ve SMS modulu yoktur (is kuralı)

fixtures = [
	{
		"dt": "Custom Field",
		"filters": [["name", "in", ["Delivery Note-kargo_firma", "Delivery Note-kargo_takip_no"]]],
	}
]

# Geliştirme sitelerinde v15/PostgreSQL adaptörleri (MariaDB/v16 çekirdeğe yönlenir).
before_request = ["cari_custom.compat_patches.install"]
before_job = ["cari_custom.compat_patches.install"]
before_migrate = ["cari_custom.compat_patches.install"]

# Sahaya/portala verilen erişim ön yüzde değil sunucuda uygulanır.
required_apps = ["erpnext"]
after_install = "cari_custom.bootstrap.run"
after_migrate = ["cari_custom.bootstrap.run"]
before_request += ["cari_custom.security.before_request"]
after_request = ["cari_custom.security.after_request"]
has_permission = {"*": "cari_custom.security.has_permission"}
doc_events = {
	"*": {"validate": "cari_custom.security.validate_document"},
	"Delivery Note": {
		"validate": "cari_custom.field_operations.validate_sale",
		"on_submit": "cari_custom.field_operations.after_sale",
		"on_cancel": "cari_custom.field_operations.after_sale",
	},
	"Sales Invoice": {
		"validate": "cari_custom.field_operations.validate_sale",
		"on_submit": "cari_custom.field_operations.after_sale",
		"on_cancel": "cari_custom.field_operations.after_sale",
	},
	"Stock Entry": {"before_cancel": "cari_custom.field_operations.before_stock_entry_cancel"},
}
permission_query_conditions = {
	"Company": "cari_custom.permission_queries.company",
	"Customer": "cari_custom.permission_queries.customer",
	"Supplier": "cari_custom.permission_queries.supplier",
	"Vehicle": "cari_custom.permission_queries.vehicle",
	"Employee": "cari_custom.permission_queries.employee",
	"Item Price": "cari_custom.permission_queries.item_price",
	"Address": "cari_custom.permission_queries.address",
	"Contact": "cari_custom.permission_queries.contact",
	"Quotation": "cari_custom.permission_queries.quotation",
	"Stock Assignment": "cari_custom.permission_queries.stock_assignment",
	"Stock Assignment Return": "cari_custom.permission_queries.stock_assignment_return",
	"Daily Assignment": "cari_custom.permission_queries.daily_assignment",
	"Warehouse": "cari_custom.permission_queries.warehouse",
	"Stock Entry": "cari_custom.permission_queries.stock_entry",
	"Stock Ledger Entry": "cari_custom.permission_queries.stock_ledger_entry",
	"Sales Order": "cari_custom.permission_queries.sales_order",
	"Sales Invoice": "cari_custom.permission_queries.sales_invoice",
	"Delivery Note": "cari_custom.permission_queries.delivery_note",
	"Purchase Order": "cari_custom.permission_queries.purchase_order",
	"Purchase Receipt": "cari_custom.permission_queries.purchase_receipt",
	"Purchase Invoice": "cari_custom.permission_queries.purchase_invoice",
	"Payment Entry": "cari_custom.permission_queries.payment_entry",
	"GL Entry": "cari_custom.permission_queries.gl_entry",
	"Cari Payment Instrument": "cari_custom.permission_queries.cari_payment_instrument",
	"Cari Shipment": "cari_custom.permission_queries.cari_shipment",
	"Cari Service Record": "cari_custom.permission_queries.cari_service_record",
	"Warranty Claim": "cari_custom.permission_queries.warranty_claim",
}

doctype_js = dict.fromkeys(
	["Stock Assignment", "Daily Assignment", "Cari Shipment", "Cari Service Record"],
	"public/js/operations.js",
)

before_job += ["cari_custom.security.install_query_guard"]

scheduler_events = {"daily": ["cari_custom.notifications.daily"]}
