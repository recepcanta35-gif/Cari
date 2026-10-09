import frappe
from frappe.model.document import Document


class CariSecurityEvent(Document):
	def validate(self):
		if not self.is_new():
			frappe.throw("Denetim kaydı değiştirilemez")

	def on_trash(self):
		frappe.throw("Denetim kaydı silinemez")
