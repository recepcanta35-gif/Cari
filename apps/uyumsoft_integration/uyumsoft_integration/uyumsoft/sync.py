"""Olay güdümlü aktarım kuyruğu.

Sales Invoice submit/cancel, Item/Customer update olaylarinda
Uyumsoft Transfer Log kaydi olusturur; saatlik scheduler bekleyenleri isler.
"""

import frappe


def _enqueue(transfer_tipi, ref_doctype, ref_name):
	settings = frappe.get_single("Uyumsoft Settings")
	if not settings.aktif:
		return  # Kapsam kosulu: baglanti urun/surum/yetki onayina bagli
	frappe.get_doc(
		{
			"doctype": "Uyumsoft Transfer Log",
			"transfer_tipi": transfer_tipi,
			"referans_doctype": ref_doctype,
			"referans_adi": ref_name,
			"durum": "Bekliyor",
		}
	).insert(ignore_permissions=True)


def sync_on_invoice_submit(doc, method=None):
	_enqueue("Fatura", "Sales Invoice", doc.name)


def sync_on_invoice_cancel(doc, method=None):
	_enqueue("Fatura", "Sales Invoice", doc.name)


def sync_on_item_update(doc, method=None):
	_enqueue("Ürün", "Item", doc.name)


def sync_on_customer_update(doc, method=None):
	_enqueue("Cari", "Customer", doc.name)


def process_pending_transfers():
	"""Saatlik scheduler — Bekliyor durumundaki kayitlari Uyumsoft'a gönderir.

	Uyumsoft onayi (urun/surum/yetki) sonrasi connector devreye alinacak.
	"""
	pending = frappe.get_all(
		"Uyumsoft Transfer Log", filters={"durum": "Bekliyor"}, limit_page_length=50
	)
	if not pending:
		return
	frappe.logger("uyumsoft").info(f"{len(pending)} aktarım kuyrukta (connector henüz aktif değil)")
