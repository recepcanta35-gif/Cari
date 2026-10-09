"""UBL-TR (e-Fatura / e-Arşiv / e-İrsaliye) eşleme taslağı.

GİB UBL-TR 1.2 zorunlu alanlari (kaynak: entegrasyon kilavuzlari):
- Taraf VKN/TCKN (10/11 hane), vergi dairesi
- Belge no: 3 hane önek + yıl + seri no
- KDV: TaxTypeCode 0015, oran bazinda TaxSubtotal
- Tevkifat senaryolari, iade faturasi iliskisi
"""

KDV_TAX_TYPE_CODE = "0015"


def invoice_to_ubltr(sales_invoice):
	"""Sales Invoice -> UBL-TR Invoice dict taslagi."""
	raise NotImplementedError("UBL-TR eşleme Faz 5'te (Uyumsoft onayı sonrası) tamamlanacak")
