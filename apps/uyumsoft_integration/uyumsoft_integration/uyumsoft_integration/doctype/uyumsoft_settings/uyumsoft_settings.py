from frappe.model.document import Document


class UyumsoftSettings(Document):
	"""Uyumsoft baglanti ayarlari (Singleton).

	Kapsam kosulu: baglanti; Uyumsoft urun, surum ve erisim yetkilerine baglidir.
	"""

	def validate(self):
		if self.aktif and not self.base_url:
			frappe.throw("Aktif bağlantı için base URL zorunludur")
