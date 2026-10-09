"""Kayıt/şirket/depo/müşteri izolasyonu ve kontrollü kullanıcı yaşam döngüsü."""

import json
from contextlib import contextmanager

import frappe
from frappe.model.document import Document
from frappe.utils import cint

from cari_custom.rules import Scope, redact_costs

PERSONA_ROLES = {
	"Yönetici": "Cari Yönetici",
	"Kullanıcı Yöneticisi": "Cari Kullanıcı Yöneticisi",
	"Muhasebe": "Cari Muhasebe",
	"Satış": "Cari Satış",
	"Saha": "Saha Personeli",
	"Depo": "Depo Personeli",
	"Servis": "Cari Servis",
	"İnsan Kaynakları": "Cari İK",
	"Portal": "Cari Portal",
}
MANAGED_ROLES = frozenset(PERSONA_ROLES.values())
RESTRICTED_PERSONAS = {"Saha", "Depo", "Portal"}
SENSITIVE_PERSONAS = {"Yönetici", "Kullanıcı Yöneticisi", "Muhasebe", "İnsan Kaynakları"}
COMPANY_DOCTYPES = {
	"Quotation",
	"Sales Order",
	"Delivery Note",
	"Sales Invoice",
	"Purchase Order",
	"Purchase Receipt",
	"Purchase Invoice",
	"Payment Entry",
	"Stock Entry",
	"Stock Ledger Entry",
	"GL Entry",
	"Warehouse",
	"Stock Assignment",
	"Stock Assignment Return",
	"Daily Assignment",
	"Cari Payment Instrument",
	"Cari Shipment",
	"Cari Service Record",
}
CUSTOMER_DOCTYPES = {
	"Sales Order",
	"Delivery Note",
	"Sales Invoice",
	"Cari Payment Instrument",
	"Cari Shipment",
	"Cari Service Record",
	"Warranty Claim",
}
GLOBAL_READ = {
	"Item",
	"Item Group",
	"UOM",
	"Territory",
	"Country",
	"Currency",
	"Brand",
	"Item Tax Template",
	"Sales Taxes and Charges Template",
	"Mode of Payment",
	"Payment Terms Template",
}


def is_system_manager(user=None):
	user = user or frappe.session.user
	return user == "Administrator" or "System Manager" in frappe.get_roles(user)


def is_managed(user=None):
	return bool(MANAGED_ROLES.intersection(frappe.get_roles(user or frappe.session.user)))


def get_scope(user=None, *, required=True):
	user = user or frappe.session.user
	if is_system_manager(user) or not is_managed(user):
		return None
	if not frappe.db.exists("DocType", "Cari User Scope"):
		if required:
			frappe.throw("Kullanıcı kapsamı kurulmamış", frappe.PermissionError)
		return None
	if not frappe.db.exists("Cari User Scope", user):
		if required:
			frappe.throw("Kullanıcı kapsamı tanımlanmamış", frappe.PermissionError)
		return None
	doc = frappe.get_doc("Cari User Scope", user)
	if not doc.enabled or not frappe.db.get_value("User", user, "enabled"):
		if required:
			frappe.throw("Kullanıcı kapsamı pasif", frappe.PermissionError)
		return None
	if PERSONA_ROLES.get(doc.persona) not in frappe.get_roles(user):
		frappe.throw("Kullanıcı rolü ile erişim kapsamı uyuşmuyor", frappe.PermissionError)
	return Scope(
		user=user,
		company=doc.company,
		persona=doc.persona,
		employee=doc.employee,
		customers=frozenset(r.customer for r in doc.customers),
		warehouses=frozenset(r.warehouse for r in doc.warehouses),
	)


def _customer_in_company(customer, company):
	if not customer:
		return False
	if frappe.db.get_value("Customer", customer, "cari_company") == company:
		return True
	return bool(
		frappe.db.exists("Party Account", {"parenttype": "Customer", "parent": customer, "company": company})
	)


def record_allowed(doc, scope):
	kind = doc.doctype
	if kind in COMPANY_DOCTYPES and not scope.permits_company(doc.get("company")):
		return False
	if kind == "Company":
		return scope.permits_company(doc.name)
	if kind == "Customer":
		return (
			scope.permits_customer(doc.name)
			if scope.persona in {"Saha", "Portal"}
			else _customer_in_company(doc.name, scope.company)
		)
	if kind == "Payment Entry" and scope.persona in {"Saha", "Portal"}:
		return doc.party_type == "Customer" and scope.permits_customer(doc.party)
	if kind == "Supplier":
		return doc.cari_company == scope.company
	if kind == "Vehicle":
		return doc.cari_company == scope.company
	if kind == "Quotation" and scope.persona in {"Saha", "Portal"}:
		return doc.quotation_to == "Customer" and scope.permits_customer(doc.party_name)
	if kind in CUSTOMER_DOCTYPES and scope.persona in {"Saha", "Portal"}:
		return scope.permits_customer(doc.get("customer"))
	if kind == "Warehouse":
		return scope.permits_warehouse(doc.name) if scope.persona in {"Saha", "Depo"} else True
	if kind == "Employee":
		return (
			scope.permits_employee(doc.name)
			if scope.persona == "Saha"
			else scope.permits_company(doc.company)
		)
	if kind in {"Stock Assignment", "Daily Assignment"} and scope.persona == "Saha":
		return scope.permits_employee(doc.personel)
	if kind == "Stock Assignment Return":
		parent = frappe.get_doc("Stock Assignment", doc.assignment)
		return record_allowed(parent, scope)
	if kind == "Stock Entry" and scope.persona in {"Saha", "Depo"}:
		return all(
			scope.permits_warehouse(w) for row in doc.items for w in (row.s_warehouse, row.t_warehouse) if w
		)
	if kind == "Stock Ledger Entry" and scope.persona in {"Saha", "Depo"}:
		return scope.permits_warehouse(doc.warehouse)
	if kind == "Item Price" and scope.persona in {"Saha", "Satış", "Portal"}:
		return doc.price_list == frappe.db.get_single_value("Cari Settings", "selling_price_list")
	if kind in {"Address", "Contact"} and scope.persona in {"Saha", "Portal"}:
		return any(r.link_doctype == "Customer" and scope.permits_customer(r.link_name) for r in doc.links)
	return True


def assert_scope(doc, user=None):
	user = user or frappe.session.user
	if not is_managed(user) or is_system_manager(user):
		return
	scope = get_scope(user)
	if not record_allowed(doc, scope):
		# False döndürmek bazı Frappe sürümlerinde DocShare fallback'ine izin verir.
		# Açık hata ile kapsam dışındaki paylaşım da reddedilir.
		frappe.throw("Kayıt erişim kapsamınız dışında", frappe.PermissionError)


def has_permission(doc, ptype=None, user=None, **_kwargs):
	assert_scope(doc, user)
	return None  # Rol hakları hâlâ Frappe tarafından değerlendirilir; hak yükseltmez.


def validate_document(doc, method=None):
	if doc.doctype in {"Customer", "Supplier", "Vehicle"} and is_managed() and not is_system_manager():
		scope = get_scope()
		if not doc.cari_company:
			doc.cari_company = scope.company
	if doc.doctype in COMPANY_DOCTYPES | CUSTOMER_DOCTYPES | {
		"Customer",
		"Supplier",
		"Vehicle",
		"Employee",
		"Company",
		"Quotation",
	}:
		if (
			doc.doctype in {"Quotation", "Sales Order", "Delivery Note", "Sales Invoice"}
			and is_managed()
			and not is_system_manager()
		):
			scope = get_scope()
			for row in doc.get("items", []):
				if (
					row.get("warehouse")
					and scope.persona == "Saha"
					and not scope.permits_warehouse(row.warehouse)
				):
					frappe.throw("Satış deposu erişim kapsamı dışında", frappe.PermissionError)
		assert_scope(doc)


def _in(values):
	return "(" + ", ".join(frappe.db.escape(v) for v in sorted(values)) + ")" if values else "(NULL)"


def query_condition(doctype, user=None):
	user = user or frappe.session.user
	if is_system_manager(user) or not is_managed(user):
		return ""
	scope = get_scope(user, required=False)
	if scope is None:
		return "1=0"
	table = f"`tab{doctype}`"
	conditions = []
	if doctype in COMPANY_DOCTYPES:
		conditions.append(f"{table}.company = {frappe.db.escape(scope.company)}")
	if doctype == "Company":
		conditions.append(f"{table}.name = {frappe.db.escape(scope.company)}")
	if doctype == "Customer":
		if scope.persona in {"Saha", "Portal"}:
			conditions.append(f"{table}.name IN {_in(scope.customers)}")
		else:
			company = frappe.db.escape(scope.company)
			conditions.append(
				f"({table}.cari_company = {company} OR EXISTS (SELECT 1 FROM `tabParty Account` pa WHERE pa.parent = {table}.name AND pa.parenttype='Customer' AND pa.company={company}))"
			)
	if doctype == "Payment Entry" and scope.persona in {"Saha", "Portal"}:
		conditions.append(f"{table}.party_type='Customer' AND {table}.party IN {_in(scope.customers)}")
	if doctype in {"Supplier", "Vehicle"}:
		conditions.append(f"{table}.cari_company={frappe.db.escape(scope.company)}")
	if doctype == "Quotation" and scope.persona in {"Saha", "Portal"}:
		conditions.append(f"{table}.quotation_to='Customer' AND {table}.party_name IN {_in(scope.customers)}")
	if doctype in CUSTOMER_DOCTYPES and scope.persona in {"Saha", "Portal"}:
		conditions.append(f"{table}.customer IN {_in(scope.customers)}")
	if doctype == "Employee":
		conditions.append(
			f"{table}.name = {frappe.db.escape(scope.employee or '')}"
			if scope.persona == "Saha"
			else f"{table}.company={frappe.db.escape(scope.company)}"
		)
	if doctype in {"Stock Assignment", "Daily Assignment"} and scope.persona == "Saha":
		conditions.append(f"{table}.personel={frappe.db.escape(scope.employee or '')}")
	if doctype == "Stock Assignment Return" and scope.persona == "Saha":
		conditions.append(
			f"EXISTS (SELECT 1 FROM `tabStock Assignment` sa WHERE sa.name={table}.assignment AND sa.personel={frappe.db.escape(scope.employee or '')})"
		)
	if doctype in {"Warehouse", "Stock Ledger Entry"} and scope.persona in {"Saha", "Depo"}:
		conditions.append(
			f"{table}.{'name' if doctype == 'Warehouse' else 'warehouse'} IN {_in(scope.warehouses)}"
		)
	if doctype == "Stock Entry" and scope.persona in {"Saha", "Depo"}:
		allowed = _in(scope.warehouses)
		conditions.append(
			f"NOT EXISTS (SELECT 1 FROM `tabStock Entry Detail` sed WHERE sed.parent={table}.name AND ((COALESCE(sed.s_warehouse,'')!='' AND sed.s_warehouse NOT IN {allowed}) OR (COALESCE(sed.t_warehouse,'')!='' AND sed.t_warehouse NOT IN {allowed})))"
		)
	if doctype == "Item Price" and scope.persona in {"Saha", "Satış", "Portal"}:
		price_list = frappe.db.get_single_value("Cari Settings", "selling_price_list") or ""
		conditions.append(f"{table}.price_list={frappe.db.escape(price_list)}")
	if doctype in {"Address", "Contact"} and scope.persona in {"Saha", "Portal"}:
		conditions.append(
			f"EXISTS (SELECT 1 FROM `tabDynamic Link` dl WHERE dl.parent={table}.name AND dl.parenttype={frappe.db.escape(doctype)} AND dl.link_doctype='Customer' AND dl.link_name IN {_in(scope.customers)})"
		)
	return " AND ".join(f"({c})" for c in conditions)


@contextmanager
def internal_transition():
	old = getattr(frappe.local, "cari_internal_transition", False)
	frappe.local.cari_internal_transition = True
	try:
		yield
	finally:
		frappe.local.cari_internal_transition = old


def require_operations_manager():
	if is_system_manager():
		return
	scope = get_scope()
	if scope.persona not in {"Yönetici", "Depo"}:
		frappe.throw("Stok/görev onay yetkisi gerekli", frappe.PermissionError)


def audit(action, target_user=None, reason=None, details=None):
	# Parola/token/payload kabul etmez; yalnız operasyonel metadata kaydeder.
	allowed = {"profile", "company", "enabled", "document", "doctype", "persona"}
	clean = {k: v for k, v in (details or {}).items() if k in allowed}
	frappe.get_doc(
		{
			"doctype": "Cari Security Event",
			"actor": frappe.session.user,
			"action": action,
			"target_user": target_user,
			"reason": reason,
			"details": json.dumps(clean, ensure_ascii=False),
		}
	).insert(ignore_permissions=True)


class CariUserScope(Document):
	def validate(self):
		if self.persona not in PERSONA_ROLES:
			frappe.throw("Geçersiz kullanıcı profili")
		if not is_system_manager():
			actor = get_scope()
			if (
				actor.persona not in {"Yönetici", "Kullanıcı Yöneticisi"}
				or actor.company != self.company
				or self.persona in SENSITIVE_PERSONAS
			):
				frappe.throw("Kapsam yönetimi yetkisi yok", frappe.PermissionError)
		if self.persona == "Saha" and not self.employee:
			frappe.throw("Saha kullanıcısı için personel bağı zorunlu")
		if self.persona == "Portal" and len(self.customers) != 1:
			frappe.throw("Portal kullanıcısı tam bir müşteriyle eşleşmelidir")
		if self.employee:
			employee = frappe.get_doc("Employee", self.employee)
			if employee.company != self.company or employee.user_id != self.user:
				frappe.throw("Personel/kullanıcı/şirket eşleşmesi geçersiz")
		for row in self.warehouses:
			warehouse = frappe.get_doc("Warehouse", row.warehouse)
			if warehouse.company != self.company or warehouse.is_group or warehouse.disabled:
				frappe.throw("Kapsama sadece aynı şirketin etkin yaprak deposu atanabilir")
		for row in self.customers:
			if not _customer_in_company(row.customer, self.company):
				frappe.throw("Müşteri bu şirketle ilişkilendirilmemiş")
		if len({r.customer for r in self.customers}) != len(self.customers) or len(
			{r.warehouse for r in self.warehouses}
		) != len(self.warehouses):
			frappe.throw("Mükerrer kapsam satırı")
		if self.persona in {"Depo", "Saha"} and not self.warehouses:
			frappe.throw("Depo/saha kullanıcısına en az bir depo atanmalıdır")

	def on_update(self):
		frappe.clear_cache(user=self.user)
		for row in frappe.get_all(
			"User Permission",
			filters={"user": self.user, "allow": "Company", "for_value": ["!=", self.company]},
			pluck="name",
		):
			frappe.delete_doc("User Permission", row, ignore_permissions=True)
		# Resmî Company User Permission; metadata/raporlar için ikinci katman.
		if not frappe.db.exists(
			"User Permission", {"user": self.user, "allow": "Company", "for_value": self.company}
		):
			frappe.get_doc(
				{
					"doctype": "User Permission",
					"user": self.user,
					"allow": "Company",
					"for_value": self.company,
					"apply_to_all_doctypes": 1,
				}
			).insert(ignore_permissions=True)


def before_request():
	install_query_guard()
	request = getattr(frappe.local, "request", None)
	if not request:
		return
	form = frappe.form_dict
	path = request.path
	command = str(form.get("cmd") or (path.split("/api/method/", 1)[1] if "/api/method/" in path else ""))
	# Kapsam dışı kanallar yalnız gizlenmez; dış çağrı da engellenir.
	if "sms_settings" in command or command.endswith(".send_sms"):
		frappe.throw("SMS bu projenin kapsamında değildir", frappe.PermissionError)
	if frappe.session.user == "Guest" or is_system_manager() or not is_managed():
		return
	scope = get_scope()
	if command.startswith("frappe.desk.query_report"):
		filters = frappe.parse_json(form.get("filters") or {})
		if filters.get("company") and not scope.permits_company(filters["company"]):
			frappe.throw("Rapor şirketi erişim kapsamı dışında", frappe.PermissionError)
		filters["company"] = scope.company
		form["filters"] = json.dumps(filters)
	if scope.persona == "Portal" and command.startswith("erpnext."):
		frappe.throw("Portal yalnız kendi Cari müşteri servislerini kullanabilir", frappe.PermissionError)
	if scope.persona in RESTRICTED_PERSONAS:
		if scope.persona == "Depo" and path.startswith("/private/files/"):
			frappe.throw("Özel dosya indirmeleri bu miktar profiline kapalıdır", frappe.PermissionError)
		if command.startswith("erpnext.accounts.") and (
			command != "erpnext.accounts.party.get_party_details"
			or form.get("party_type", "Customer") != "Customer"
			or not scope.permits_customer(form.get("party"))
		):
			frappe.throw("Finansal servis erişimi kapsam dışında", frappe.PermissionError)
		if command.startswith("erpnext.stock.") and command not in {
			"erpnext.stock.utils.get_stock_balance",
			"erpnext.stock.get_item_details.get_item_details",
			"erpnext.stock.get_item_details.get_conversion_factor",
		}:
			frappe.throw("Bu profil kapsamlı Cari stok servislerini kullanmalıdır", frappe.PermissionError)
		if command.startswith(
			(
				"frappe.desk.query_report",
				"frappe.desk.reportview.export",
				"erpnext.accounts.report",
				"erpnext.stock.report",
			)
		):
			frappe.throw("Bu profil yalnız Cari kapsamlı raporlarını kullanabilir", frappe.PermissionError)
		if command.startswith("erpnext.stock.utils."):
			if (
				command != "erpnext.stock.utils.get_stock_balance"
				or cint(form.get("with_valuation_rate"))
				or cint(form.get("with_serial_no"))
			):
				frappe.throw("Stok değerleme servisine erişim yok", frappe.PermissionError)
			if not scope.permits_warehouse(form.get("warehouse")):
				frappe.throw("Depo kapsam dışında", frappe.PermissionError)
		if command == "erpnext.stock.get_item_details.get_item_details":
			args = frappe.parse_json(form.get("args") or {})
			if args.get("company") and not scope.permits_company(args["company"]):
				frappe.throw("Şirket kapsam dışında", frappe.PermissionError)
			if args.get("warehouse") and not scope.permits_warehouse(args["warehouse"]):
				frappe.throw("Depo kapsam dışında", frappe.PermissionError)
			if args.get("customer") and not scope.permits_customer(args["customer"]):
				frappe.throw("Müşteri kapsam dışında", frappe.PermissionError)
		if scope.persona == "Depo" and (path == "/printview" or "download_pdf" in command):
			frappe.throw("Maliyet içeren standart belge çıktısı bu profile kapalıdır", frappe.PermissionError)


def after_request(response, request=None):
	# Genel sözlük RPC'leri field-level izinleri uygulamayabilir. Ham stok-değerleme
	# tuple servisleri before_request'te reddedilir; sözlükler ikinci kez filtrelenir.
	if is_system_manager() or not is_managed() or not response.is_json:
		return
	scope = get_scope(required=False)
	if scope and scope.persona in {"Saha", "Depo", "Portal"}:
		data = response.get_json()
		data = redact_costs(data, quantity_only=scope.persona == "Depo")
		response.set_data(json.dumps(data, ensure_ascii=False, default=str))
		response.headers["Content-Type"] = "application/json"


def install_query_guard(**_kwargs):
	"""PQC'yi paylaşım OR koşulunun dışında da uygular; hiçbir rol hakkı vermez.

	Frappe v15, User Permission + özel PQC toplamına DocShare'ı OR ile ekler.
	Yalnız yönetilen Cari kullanıcıları için en dışta kapsam AND'i gerekir.
	get_all(ignore_permissions) ve sistem/üçüncü taraf kullanıcıları etkilenmez.
	"""
	from functools import wraps

	from frappe.model.db_query import DatabaseQuery

	original = DatabaseQuery.build_match_conditions
	if getattr(original, "_cari_scope_guard", False):
		return

	@wraps(original)
	def scoped(query, as_condition=True):
		result = original(query, as_condition=as_condition)
		if (
			not as_condition
			or query.flags.ignore_permissions
			or is_system_manager(query.user)
			or not is_managed(query.user)
		):
			return result
		strict = query_condition(query.doctype, query.user)
		if strict:
			return f"({result}) AND ({strict})" if result else strict
		return result

	scoped._cari_scope_guard = True
	DatabaseQuery.build_match_conditions = scoped
