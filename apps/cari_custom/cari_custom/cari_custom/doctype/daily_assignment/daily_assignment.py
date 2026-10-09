from frappe.model.document import Document


class DailyAssignment(Document):
	"""Gunluk gorevlendirme (kapsam modulu 10).

	ERPNext Delivery Trip sevkiyat rotalarina yoneliktir; bu DocType
	saha personelinin gunluk gorev planini (arac, bolge, musteri) tutar.
	"""

	def validate(self):
		if self.bitis_saati and self.baslangic_saati and self.bitis_saati < self.baslangic_saati:
			frappe.throw("Bitiş saati başlangıç saatinden önce olamaz")
