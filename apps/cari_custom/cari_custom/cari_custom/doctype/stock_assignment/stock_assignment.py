from frappe.model.document import Document


class StockAssignment(Document):
	"""Personel stok zimmeti (kapsam modulu 4).

	Personel/zimmet mantigi ERPNext'te yerlesik degildir; bu DocType,
	saha personeline zimmetlenen stoklari takip eder. Stok dusumu/cikisi
	ayri Stock Entry ile yapilir; burada zimmet kaydi tutulur.
	"""

	def validate(self):
		if self.iade_tarihi and self.atama_tarihi and self.iade_tarihi < self.atama_tarihi:
			frappe.throw("İade tarihi atama tarihinden önce olamaz")
