import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime


class DailyAssignment(Document):
	"""Saha personelinin günlük görev planı (araç, bölge, müşteri)."""

	def validate(self):
		if (
			self.bitis_saati
			and self.baslangic_saati
			and get_datetime(self.bitis_saati) < get_datetime(self.baslangic_saati)
		):
			frappe.throw("Bitiş saati başlangıç saatinden önce olamaz")
