"""Canlı teslim kapısı: demo başarıları üretim kanıtı sayılmaz."""

from urllib.parse import urlparse

import frappe
from frappe.model.document import Document
from frappe.utils import cint

from cari_custom.security import is_system_manager


class CariSettings(Document):
	def validate(self):
		self.delivery_ready = 0  # Onay kutusu ile ürünün hazır sayılması engellenir.
		if self.accounting_approved and not str(self.accounting_approval_ref or "").strip():
			frappe.throw("Muhasebe onayı için kabul referansı gerekir")
		if self.uat_approved and not str(self.uat_approval_ref or "").strip():
			frappe.throw("Kullanıcı kabulü için tutanak referansı gerekir")
		if self.portal_enabled:
			warehouse = frappe.get_doc("Warehouse", self.portal_warehouse)
			if warehouse.company != self.company or warehouse.disabled or warehouse.is_group:
				frappe.throw("Portal için aynı şirketin etkin yaprak deposu gerekir")
		if self.selling_price_list:
			price_list = frappe.get_doc("Price List", self.selling_price_list)
			if not price_list.enabled or not price_list.selling:
				frappe.throw("Etkin satış fiyat listesi gerekir")
		if self.production_url and urlparse(self.production_url).scheme != "https":
			frappe.throw("Üretim adresi HTTPS olmalıdır")
		if self.email_notifications_enabled and not frappe.db.exists("Email Account", {"enable_outgoing": 1}):
			frappe.throw("Bildirimler için SMTP hesabı gerekir")


@frappe.whitelist()
def readiness():
	if not is_system_manager():
		frappe.throw("Teslim kontrolü teknik yöneticiye açıktır", frappe.PermissionError)
	settings = frappe.get_single("Cari Settings")
	checks = []

	def add(key, passed, message):
		checks.append({"id": key, "passed": bool(passed), "message": message})

	add("db", frappe.conf.get("db_type", "mariadb") == "mariadb", "Üretimde desteklenen MariaDB gerekir")
	add("debug", not cint(frappe.conf.get("developer_mode")), "Developer mode kapalı olmalıdır")
	add("csrf", not cint(frappe.conf.get("ignore_csrf")), "CSRF kapatılamaz")
	add("cors", frappe.conf.get("allow_cors") not in ("*", ["*"]), "Wildcard CORS yasaktır")
	add(
		"secrets",
		bool(frappe.conf.get("encryption_key")),
		"Sırların şifreleme anahtarı ve güvenli yedeği gerekir",
	)
	add(
		"tls",
		bool(settings.production_url and urlparse(settings.production_url).scheme == "https"),
		"Gerçek HTTPS adresi gerekir",
	)
	add(
		"smtp",
		bool(frappe.db.exists("Email Account", {"enable_outgoing": 1})),
		"SMTP uçtan uca kabulü gerekir",
	)
	add(
		"accounting",
		settings.accounting_approved and settings.accounting_approval_ref,
		"Muhasebeci onay referansı gerekir",
	)
	add("uat", settings.uat_approved and settings.uat_approval_ref, "Kullanıcı kabul referansı gerekir")
	add(
		"restore",
		bool(settings.restore_test_ref),
		"Dosya/encryption_key dahil geri yükleme tatbikatı gerekir",
	)
	# Bunlar yalnız sürümün bütün modül testleri ve gerçek ortam kanıtları eklendiğinde açılır.
	add("modules", False, "18 modülün son kabulü ve güncel sürüm test kanıtı henüz tamamlanmadı")
	add("uyumsoft", False, "Ürün/sürüm/sözleşme/sandbox-canlı sağlayıcı kabulü bekleniyor")
	return {"decision": "NO-GO", "checks": checks, "blockers": [c["id"] for c in checks if not c["passed"]]}
