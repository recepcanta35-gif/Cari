"""Kullanıcıları ayrıcalık yükseltmeden oluştur/davet et/pasifleştir."""

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import validate_email_address

from cari_custom.bootstrap import PROFILES
from cari_custom.security import SENSITIVE_PERSONAS, audit, get_scope, is_system_manager


def _authorize(company, persona, target=None):
	if persona not in PROFILES:
		frappe.throw("Bilinmeyen profil")
	if target in {"Administrator", "Guest"}:
		frappe.throw("Sistem hesabı bu servisle değiştirilemez", frappe.PermissionError)
	if is_system_manager():
		return
	actor = get_scope()
	if (
		actor.persona not in {"Yönetici", "Kullanıcı Yöneticisi"}
		or actor.company != company
		or persona in SENSITIVE_PERSONAS
	):
		frappe.throw("Kullanıcı/profil yönetimi yetkisi yok", frappe.PermissionError)
	if target and frappe.db.exists("User", target):
		if "System Manager" in frappe.get_roles(target):
			frappe.throw("Teknik yönetici değiştirilemez", frappe.PermissionError)
		old = frappe.db.get_value("Cari User Scope", target, ["company", "persona"], as_dict=True)
		if not old or old.company != company or old.persona in SENSITIVE_PERSONAS:
			frappe.throw("Hedef kullanıcı yönetim kapsamı dışında", frappe.PermissionError)


@frappe.whitelist(methods=["POST"])
@rate_limit(key="email", limit=30, seconds=3600)
def provision_user(
	email, first_name, company, persona, employee=None, customers=None, warehouses=None, reason=None
):
	email = validate_email_address(str(email).strip().lower(), throw=True)
	_authorize(company, persona, email)
	if not str(reason or "").strip():
		frappe.throw("Kullanıcı oluşturma/değiştirme gerekçesi gerekli")
	customers = frappe.parse_json(customers or [])
	warehouses = frappe.parse_json(warehouses or [])
	if (
		not isinstance(customers, list)
		or not isinstance(warehouses, list)
		or len(customers) > 500
		or len(warehouses) > 100
	):
		frappe.throw("Kapsam listeleri geçersiz")
	if any(not isinstance(v, str) for v in customers + warehouses):
		frappe.throw("Kapsam listeleri kayıt kimlikleri içermelidir")
	user = frappe.get_doc("User", email) if frappe.db.exists("User", email) else frappe.new_doc("User")
	if user.name and user.name == frappe.session.user and user.role_profile_name != f"Cari {persona}":
		frappe.throw("Kendi profiliniz bu servisle değiştirilemez")
	new = user.is_new()
	user.email = email
	user.first_name = first_name
	user.user_type = "Website User" if persona == "Portal" else "System User"
	user.role_profile_name = f"Cari {persona}"
	user.send_welcome_email = 0
	if new:
		user.enabled = 0  # SMTP daveti olmadan etkin/parolası bilinmeyen hesap oluşturma.
	user.save(ignore_permissions=True)
	if employee:
		doc = frappe.get_doc("Employee", employee)
		if doc.company != company or (doc.user_id and doc.user_id != email):
			frappe.throw("Personel başka şirket veya kullanıcıya bağlı")
		doc.user_id = email
		doc.save(ignore_permissions=True)
	scope = (
		frappe.get_doc("Cari User Scope", email)
		if frappe.db.exists("Cari User Scope", email)
		else frappe.new_doc("Cari User Scope")
	)
	scope.user, scope.company, scope.persona, scope.employee = email, company, persona, employee
	scope.enabled = user.enabled
	scope.notes = reason
	scope.set("customers", [{"customer": value} for value in customers])
	scope.set("warehouses", [{"warehouse": value} for value in warehouses])
	scope.save(ignore_permissions=True)
	frappe.clear_cache(user=email)
	audit(
		"Kullanıcı oluşturuldu" if new else "Kullanıcı kapsamı değiştirildi",
		email,
		reason,
		{"profile": user.role_profile_name, "company": company},
	)
	return {
		"user": email,
		"profile": user.role_profile_name,
		"enabled": bool(user.enabled),
		"invitation_required": not user.enabled,
	}


@frappe.whitelist(methods=["POST"])
@rate_limit(key="user", limit=5, seconds=3600)
def invite_user(user, reason):
	scope = frappe.get_doc("Cari User Scope", user)
	_authorize(scope.company, scope.persona, user)
	if not str(reason or "").strip():
		frappe.throw("Davet gerekçesi gerekli")
	if not frappe.db.exists("Email Account", {"enable_outgoing": 1}):
		frappe.throw("Davet için SMTP hesabı yapılandırılmalıdır")
	doc = frappe.get_doc("User", user)
	doc.enabled = 1
	doc.save(ignore_permissions=True)
	scope.enabled = 1
	scope.save(ignore_permissions=True)
	# Link/anahtar asla API yanıtında veya denetim kaydında döndürülmez.
	doc._reset_password(send_email=True)
	audit("Kullanıcı davet edildi", user, reason, {"company": scope.company})
	return {"user": user, "invitation": "queued"}


@frappe.whitelist(methods=["POST"])
def deactivate_user(user, reason):
	if user == frappe.session.user:
		frappe.throw("Kendi hesabınız pasifleştirilemez")
	scope = frappe.get_doc("Cari User Scope", user)
	_authorize(scope.company, scope.persona, user)
	if not str(reason or "").strip():
		frappe.throw("Pasifleştirme gerekçesi gerekli")
	doc = frappe.get_doc("User", user)
	doc.enabled = 0
	doc.save(ignore_permissions=True)
	scope.enabled = 0
	scope.save(ignore_permissions=True)
	from frappe.sessions import clear_sessions

	clear_sessions(user=user, keep_current=False, force=True)
	frappe.clear_cache(user=user)
	audit(
		"Kullanıcı pasifleştirildi ve oturumlar sonlandırıldı",
		user,
		reason,
		{"enabled": False, "company": scope.company},
	)
	return {"user": user, "enabled": False}
