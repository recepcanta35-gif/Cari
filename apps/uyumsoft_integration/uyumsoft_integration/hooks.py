app_name = "uyumsoft_integration"
app_title = "Uyumsoft Integration"
app_publisher = "Cari"
app_description = "Uyumsoft veri aktarimi ve e-belge (UBL-TR) entegrasyonu"
app_email = "info@cari.local"
app_license = "MIT"

doc_events = {
	"Sales Invoice": {
		"on_submit": "uyumsoft_integration.uyumsoft.sync.sync_on_invoice_submit",
		"on_cancel": "uyumsoft_integration.uyumsoft.sync.sync_on_invoice_cancel",
	},
	"Item": {
		"on_update": "uyumsoft_integration.uyumsoft.sync.sync_on_item_update",
	},
	"Customer": {
		"on_update": "uyumsoft_integration.uyumsoft.sync.sync_on_customer_update",
	},
}

scheduler_events = {
	"hourly": ["uyumsoft_integration.uyumsoft.sync.process_pending_transfers"],
}
