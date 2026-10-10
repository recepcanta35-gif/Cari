"""SMTP varsa çalışan, şirket/kayıt kapsamlı ve tekilleştirilmiş hatırlatmalar."""

from hashlib import sha256

import frappe
from frappe.utils import add_days, today

from cari_custom.security import get_scope, record_allowed


def _enabled():
	return (
		frappe.db.get_single_value("Cari Settings", "email_notifications_enabled")
		and not frappe.flags.mute_emails
		and frappe.db.exists("Email Account", {"enable_outgoing": 1})
	)


def _queue(recipient, doctype, name, event, subject, text, discriminator):
	key = sha256(f"{recipient}:{doctype}:{name}:{event}:{discriminator}".encode()).hexdigest()
	if frappe.db.exists("Cari Reminder Log", key):
		return
	doc = frappe.get_doc(
		{
			"doctype": "Cari Reminder Log",
			"key": key,
			"recipient": recipient,
			"reference_doctype": doctype,
			"reference_name": name,
			"notification_type": event,
			"status": "Kuyrukta",
		}
	)
	doc.insert(ignore_permissions=True)
	# now=False: SMTP arka plan kuyruğunda; bu kayıt teslim edildi anlamına gelmez.
	frappe.sendmail(
		recipients=[recipient],
		subject=subject,
		message=frappe.utils.escape_html(text),
		reference_doctype=doctype,
		reference_name=name,
		now=False,
	)


def daily():
	if not _enabled():
		return {"status": "DISABLED"}
	users = frappe.get_all(
		"Cari User Scope", filters={"enabled": 1}, fields=["user", "persona", "company", "employee"]
	)
	for row in frappe.get_all(
		"Sales Invoice",
		filters={"docstatus": 1, "outstanding_amount": [">", 0], "due_date": add_days(today(), 7)},
		pluck="name",
	):
		invoice = frappe.get_doc("Sales Invoice", row)
		for user in users:
			if user.persona not in {"Yönetici", "Muhasebe"} or user.company != invoice.company:
				continue
			scope = get_scope(user.user, required=False)
			if not scope or not record_allowed(invoice, scope):
				continue
			_queue(
				user.user,
				"Sales Invoice",
				invoice.name,
				"Vade-7",
				f"Vadesi yaklaşan fatura: {invoice.name}",
				f"{invoice.customer_name} — {invoice.outstanding_amount} {invoice.currency}; vade {invoice.due_date}",
				invoice.due_date,
			)
	for name in frappe.get_all(
		"Daily Assignment", filters={"docstatus": 1, "tarih": today(), "durum": "Planlandı"}, pluck="name"
	):
		task = frappe.get_doc("Daily Assignment", name)
		for user in users:
			if user.persona != "Saha" or user.employee != task.personel or user.company != task.company:
				continue
			scope = get_scope(user.user, required=False)
			if scope and record_allowed(task, scope):
				_queue(
					user.user,
					"Daily Assignment",
					task.name,
					"Görev",
					f"Günlük görev: {task.name}",
					f"Bölge: {task.bolge or ''}. Görev: {task.gorev or ''}",
					task.tarih,
				)
	return {"status": "QUEUED_NOT_DELIVERED"}
