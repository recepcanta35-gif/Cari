"""Faz 1: Türkiye temel yapılandırması (idempotent — tekrar çalıştırılabilir).

Kapsam: şirket + hesap planı, KDV şablonları, temel tanımlar (UOM, ürün/müşteri
grupları, bölge, vade/ödeme şartları, ödeme tipleri, depo), rol/yetki matrisi,
e-posta hatırlatması.

Çalıştırma: bench --site cari.local console << 'EOF'
import cari_custom.setup_turkey as st
st.run()
EOF
"""

import frappe

COMPANY = "Cari A.Ş."
ABBR = "CARI"


def _exists(doctype, name):
	return frappe.db.exists(doctype, name)


def _ensure_warehouse_types():
	"""ERPNext company kurulumunun transit deposu için gerekli."""
	for wt in ["Transit", "Stores"]:
		if not _exists("Warehouse Type", wt):
			d = frappe.new_doc("Warehouse Type")
			d.warehouse_type = wt
			d.name = wt  # autoname: Prompt — isim manuel verilir
			d.insert(ignore_permissions=True)


def _ensure_root_groups():
	"""ERPNext after_install default'ları (root gruplar + birim) oluşmamışsa kurar."""
	if not _exists("UOM", "Nos"):
		d = frappe.new_doc("UOM")
		d.uom_name = "Nos"
		d.insert(ignore_permissions=True)
	if not _exists("Item Group", "All Item Groups"):
		d = frappe.new_doc("Item Group")
		d.item_group_name = "All Item Groups"
		d.is_group = 1
		d.insert(ignore_permissions=True)
	if not _exists("Customer Group", "All Customer Groups"):
		d = frappe.new_doc("Customer Group")
		d.customer_group_name = "All Customer Groups"
		d.is_group = 1
		d.insert(ignore_permissions=True)
	if not _exists("Supplier Group", "All Supplier Groups"):
		d = frappe.new_doc("Supplier Group")
		d.supplier_group_name = "All Supplier Groups"
		d.is_group = 1
		d.insert(ignore_permissions=True)
	if not _exists("Territory", "All Territories"):
		d = frappe.new_doc("Territory")
		d.territory_name = "All Territories"
		d.is_group = 1
		d.insert(ignore_permissions=True)


def _create_company():
	if _exists("Company", COMPANY):
		return frappe.get_doc("Company", COMPANY)
	c = frappe.new_doc("Company")
	c.company_name = COMPANY
	c.abbr = ABBR
	c.country = "Turkey"
	c.default_currency = "TRY"
	c.insert(ignore_permissions=True)
	frappe.db.commit()
	frappe.logger("cari_custom").info(
		f"Company oluşturuldu: {COMPANY} (chart of accounts + varsayılan tanımlar otomatik)"
	)
	return c


def _vat_account(company):
	"""Jenerik chart of accounts içinden KDV hesabını bulur; yoksa oluşturur."""
	name = frappe.db.get_value(
		"Account", {"company": company.name, "account_type": "Tax", "is_group": 0}, "name"
	)
	if name:
		return name
	parent = frappe.db.get_value(
		"Account", {"company": company.name, "account_name": "Duties and Taxes", "is_group": 1}, "name"
	)
	if not parent:
		cl = frappe.db.get_value(
			"Account", {"company": company.name, "account_name": "Current Liabilities", "is_group": 1}, "name"
		)
		p = frappe.new_doc("Account")
		p.account_name = "Duties and Taxes"
		p.company = company.name
		p.parent_account = cl
		p.is_group = 1
		p.insert(ignore_permissions=True)
		parent = p.name
	a = frappe.new_doc("Account")
	a.account_name = "Ödenecek KDV"
	a.company = company.name
	a.parent_account = parent
	a.account_type = "Tax"
	a.insert(ignore_permissions=True)
	return a.name


def _setup_taxes(company):
	"""KDV %1/%10/%20 — satış, alış ve ürün vergi şablonları."""
	vat = _vat_account(company)
	for rate, title in [(20, "KDV %20"), (10, "KDV %10"), (1, "KDV %1")]:
		legacy_title = f"{title} - {ABBR}"
		for doctype in ["Sales Taxes and Charges Template", "Purchase Taxes and Charges Template"]:
			if not frappe.db.exists(
				doctype, {"company": company.name, "title": ["in", [title, legacy_title]]}
			):
				template = frappe.new_doc(doctype)
				template.title = title  # ERPNext şirket kısaltmasını kendisi ekler.
				template.company = company.name
				template.is_default = 1 if rate == 20 else 0
				template.append(
					"taxes",
					{
						"charge_type": "On Net Total",
						"account_head": vat,
						"rate": rate,
						"description": title,
						"category": "Total",
						"add_deduct_tax": "Add",
					},
				)
				template.insert(ignore_permissions=True)
		if not frappe.db.exists(
			"Item Tax Template", {"company": company.name, "title": ["in", [title, legacy_title]]}
		):
			it = frappe.new_doc("Item Tax Template")
			it.title = title
			it.company = company.name
			it.append("taxes", {"tax_type": vat, "tax_rate": rate})
			it.insert(ignore_permissions=True)


def _setup_master_data(company):
	# Birimler (ürün seçimi birim üzerinden de yapılacak)
	for uom in ["Kg", "m", "Koli"]:
		if not _exists("UOM", uom):
			d = frappe.new_doc("UOM")
			d.uom_name = uom
			d.insert(ignore_permissions=True)

	# Ürün grupları (ürün seçimi kategori üzerinden — kapsam kuralı)
	if not _exists("Item Group", "Genel"):
		d = frappe.new_doc("Item Group")
		d.item_group_name = "Genel"
		d.parent_item_group = "All Item Groups"
		d.insert(ignore_permissions=True)

	# Müşteri grupları
	for g in ["Bireysel", "Kurumsal"]:
		if not _exists("Customer Group", g):
			d = frappe.new_doc("Customer Group")
			d.customer_group_name = g
			d.parent_customer_group = "All Customer Groups"
			d.insert(ignore_permissions=True)

	# Tedarikçi grubu
	if not _exists("Supplier Group", "Yerli Tedarikçi"):
		d = frappe.new_doc("Supplier Group")
		d.supplier_group_name = "Yerli Tedarikçi"
		d.parent_supplier_group = "All Supplier Groups"
		d.insert(ignore_permissions=True)

	# Bölgeler (saha görevlendirme/rota için)
	if not _exists("Territory", "Türkiye"):
		d = frappe.new_doc("Territory")
		d.territory_name = "Türkiye"
		d.is_group = 1
		d.parent_territory = "All Territories"
		d.insert(ignore_permissions=True)
	for t in ["Marmara", "İç Anadolu", "Ege", "Akdeniz", "Karadeniz", "Doğu Anadolu", "Güneydoğu Anadolu"]:
		if not _exists("Territory", t):
			d = frappe.new_doc("Territory")
			d.territory_name = t
			d.parent_territory = "Türkiye"
			d.insert(ignore_permissions=True)

	# Vade şartları (cari hesap / tahsilat takibi için)
	for name, days in [("Peşin", 0), ("30 Gün Vadeli", 30), ("60 Gün Vadeli", 60)]:
		if not _exists("Payment Terms Template", name):
			d = frappe.new_doc("Payment Terms Template")
			d.template_name = name  # v15 alan adı (autoname: field:template_name)
			d.append(
				"terms",
				{"invoice_portion": 100, "credit_days": days, "description": name},
			)
			d.insert(ignore_permissions=True)

	# Banka hesabı (yoksa) — havale/KK/çek/senet için
	bank = frappe.db.get_value(
		"Account", {"company": company.name, "account_type": "Bank", "is_group": 0}, "name"
	)
	if not bank:
		ca = frappe.db.get_value(
			"Account", {"company": company.name, "account_name": "Current Assets", "is_group": 1}, "name"
		)
		a = frappe.new_doc("Account")
		a.account_name = "Banka - TRY"
		a.company = company.name
		a.parent_account = ca
		a.account_type = "Bank"
		a.insert(ignore_permissions=True)
		bank = a.name
	cash = frappe.db.get_value(
		"Account", {"company": company.name, "account_name": "Cash", "is_group": 0}, "name"
	)

	# Ödeme tipleri (tahsilat modülü — kapsam 8)
	for mode, acc, typ in [
		("Nakit", cash, "Cash"),
		("Kredi Kartı", bank, "Bank"),
		("Havale/EFT", bank, "Bank"),
		("Çek", bank, "Bank"),
		("Senet", bank, "Bank"),
	]:
		if not _exists("Mode of Payment", mode):
			d = frappe.new_doc("Mode of Payment")
			d.mode_of_payment = mode
			d.type = typ
			d.enabled = 1
			d.append("accounts", {"company": company.name, "default_account": acc})
			d.insert(ignore_permissions=True)

	# Ek depo: saha deposu (personel zimmet/saha satış için)
	wh = f"Saha Deposu - {ABBR}"
	if not _exists("Warehouse", wh):
		d = frappe.new_doc("Warehouse")
		d.warehouse_name = "Saha Deposu"
		d.company = company.name
		d.insert(ignore_permissions=True)


def _setup_roles():
	"""Kapsam modülü 16 — rol/yetki matrisi.

	Hazır ERPNext rolleri: Sales/Purchase/Accounts/Stock/HR User+Manager, System Manager.
	Ek: 'Saha Personeli' (saha satış + zimmet + görevlendirme).
	"""
	if not _exists("Role", "Saha Personeli"):
		r = frappe.new_doc("Role")
		r.role_name = "Saha Personeli"
		r.desk_access = 1
		r.insert(ignore_permissions=True)

	# Saha Personeli — çekirdek doctype erişimleri
	perms = {
		"Sales Order": {"read": 1, "write": 1, "create": 1},
		"Quotation": {"read": 1, "write": 1, "create": 1},
		"Delivery Note": {"read": 1, "write": 1, "create": 1},
		"Customer": {"read": 1},
		"Item": {"read": 1},
		"Warehouse": {"read": 1},
		"Employee": {"read": 1},
		"Vehicle": {"read": 1},
	}
	for dt, p in perms.items():
		_grant_permissions(dt, "Saha Personeli", p)

	# Custom izinler standart izinleri gölgeler; System Manager erişimi korunur.
	for dt in ["Stock Assignment", "Daily Assignment"]:
		_grant_permissions(
			dt, "System Manager", {"read": 1, "write": 1, "create": 1, "delete": 1, "print": 1}
		)
		_grant_permissions(
			dt, "Saha Personeli", {"read": 1, "write": 1, "create": 1, "delete": 1, "print": 1}
		)


def _grant_permissions(doctype, role, permissions):
	from frappe.permissions import add_permission, update_permission_property

	if not frappe.db.exists(
		"Custom DocPerm", {"parent": doctype, "role": role, "permlevel": 0, "if_owner": 0}
	):
		add_permission(doctype, role, 0, "read")
	# add_permission mevcut kuralı güncellemez; haklar ayrı ayrı uygulanır.
	for right, value in permissions.items():
		update_permission_property(doctype, role, 0, right, value)
	frappe.clear_cache(doctype=doctype)


def _setup_notifications():
	"""Kapsam modülü 15 — e-posta hatırlatması (Notification, v15).

	SMTP (Email Account) ayarlanınca gönderim başlar; bu aşamada kayıt aktif.
	"""
	if not _exists("Notification", "Tahsilat Vadesi Yaklaşıyor"):
		d = frappe.new_doc("Notification")
		d.name = "Tahsilat Vadesi Yaklaşıyor"  # autoname: Prompt
		d.document_type = "Sales Invoice"
		d.event = "Days Before"
		d.date_changed = "due_date"
		d.days_in_advance = 7
		d.condition = "doc.docstatus == 1 and doc.outstanding_amount > 0"
		d.channel = "Email"
		d.enabled = 1
		d.append("recipients", {"receiver_by_role": "Accounts Manager"})
		d.subject = "Vadesi yaklaşan fatura: {{ doc.name }}"
		d.message = (
			"Merhaba,\n\n{{ doc.customer_name }} müşterisine kesilen "
			"{{ doc.name }} numaralı faturanın vadesi 7 gün içinde doluyor."
		)
		d.insert(ignore_permissions=True)
	else:
		d = frappe.get_doc("Notification", "Tahsilat Vadesi Yaklaşıyor")
		expected = "doc.docstatus == 1 and doc.outstanding_amount > 0"
		if d.condition != expected:
			d.condition = expected
			d.save(ignore_permissions=True)


def _setup_system_defaults():
	settings = frappe.get_doc("System Settings")
	settings.language = "tr"
	settings.time_zone = "Europe/Istanbul"
	settings.save(ignore_permissions=True)
	defaults = frappe.get_doc("Global Defaults")
	defaults.default_company = COMPANY
	defaults.country = "Turkey"
	defaults.default_currency = "TRY"
	defaults.save(ignore_permissions=True)
	frappe.defaults.set_global_default("currency", "TRY")
	frappe.local.lang = "tr"


def run():
	from cari_custom.compat_patches import install

	install()
	_ensure_warehouse_types()
	_ensure_root_groups()
	company = _create_company()
	_setup_system_defaults()
	_setup_taxes(company)
	_setup_master_data(company)
	_setup_roles()
	_setup_notifications()
	from cari_custom.bootstrap import run as setup_access
	from cari_custom.bootstrap import setup_defaults

	setup_access()
	if frappe.db.exists("Price List", "Standard Selling"):
		setup_defaults(company.name)
	frappe.db.commit()
	print("FAZ1_TAMAM:", company.name)
