import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate


class StockAssignment(Document):
	"""Personel stok zimmeti. Fiziksel hareket ayrı bir Stock Entry'dir.

	stok_hareketi, zimmeti destekleyen transferi gösterir; bu fazda otomatik
	stok hareketi üretilmez. Gerçek transfer seed/test tarafından ayrıca yapılır.
	"""

	def validate(self):
		if flt(self.zimmet_miktar) <= 0:
			frappe.throw("Zimmet miktarı sıfırdan büyük olmalıdır")
		if self.iade_tarihi and self.atama_tarihi and getdate(self.iade_tarihi) < getdate(self.atama_tarihi):
			frappe.throw("İade tarihi atama tarihinden önce olamaz")
