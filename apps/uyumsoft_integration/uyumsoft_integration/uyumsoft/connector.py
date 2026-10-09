"""Uyumsoft REST/SOAP istemcisi (taslak).

UYARI: Uyumsoft baglantisi; urun, surum ve erisim yetkilerine baglidir
(kapsam dokumani). Canli entegrasyon bu kosullar saglanmadan acilmaz.
"""

import frappe
import requests


class UyumsoftConnector:
	def __init__(self, settings=None):
		settings = settings or frappe.get_single("Uyumsoft Settings")
		self.base_url = settings.base_url
		self.kullanici = settings.kullanici_adi
		self.sifre = settings.sifre
		self.sirket_kodu = settings.sirket_kodu

	def test_connection(self):
		"""Baglanti testi — urun/surum/yetki onayi sonrasi implement edilecek."""
		raise NotImplementedError("Uyumsoft entegrasyonu henüz aktif değil (ürün/sürüm/yetki onayı bekleniyor)")

	def send_payload(self, endpoint, payload):
		"""Genel POST — UBL-TR veya proprietary format payload gönderimi."""
		raise NotImplementedError
