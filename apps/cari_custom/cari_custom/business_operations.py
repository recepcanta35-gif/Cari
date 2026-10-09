"""Çek/senet, sevkiyat ve servis: stok/finans defterlerinin yerine geçmez."""

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, now_datetime, today

from cari_custom.rules import RuleViolation, positive_quantity
from cari_custom.security import (
	assert_scope,
	get_scope,
	internal_transition,
	is_system_manager,
	require_operations_manager,
)


def _locked(doc):
	doc.check_permission("write")
	assert_scope(doc)
	frappe.db.sql(f"SELECT name FROM `tab{doc.doctype}` WHERE name=%s FOR UPDATE", (doc.name,))
	doc.reload()
	if doc.docstatus != 1:
		frappe.throw("İşlem yalnız onaylı belgede yapılabilir")


def _finance():
	if not is_system_manager():
		scope = get_scope()
		if not scope or scope.persona not in {"Yönetici", "Muhasebe"}:
			frappe.throw("Muhasebe yetkisi gerekli", frappe.PermissionError)


def _guard_update(doc):
	before = doc.get_doc_before_save()
	if (
		before
		and before.docstatus == 1
		and before.status != doc.status
		and not getattr(frappe.local, "cari_internal_transition", False)
	):
		frappe.throw("Durum yalnız yetkili işlem uçlarıyla değiştirilir", frappe.PermissionError)


class CariPaymentInstrument(Document):
	"""Evrak alınması banka tahsilatı sayılmaz. Tahsilat yalnız collect ile oluşur."""

	def validate(self):
		try:
			positive_quantity(self.amount)
		except RuleViolation as exc:
			frappe.throw(str(exc))
		if self.invoice and not self.references:
			self.append("references", {"invoice": self.invoice, "allocated_amount": self.amount})
		seen, total = set(), 0.0
		for row in self.references:
			invoice = frappe.get_doc("Sales Invoice", row.invoice)
			if (
				invoice.docstatus != 1
				or invoice.company != self.company
				or invoice.customer != self.customer
				or invoice.currency != self.currency
			):
				frappe.throw("Fatura/cari/şirket/para birimi eşleşmesi geçersiz")
			if row.invoice in seen or flt(row.allocated_amount) <= 0:
				frappe.throw("Mükerrer veya geçersiz evrak tahsisi")
			seen.add(row.invoice)
			total += flt(row.allocated_amount)
		if total > flt(self.amount):
			frappe.throw("Fatura tahsisleri evrak tutarını aşıyor")
		if self.docstatus == 0 and self.payment_entry:
			frappe.throw("Tahsilat bağı sunucu tarafından oluşturulur")
		assert_scope(self)
		_guard_update(self)

	def before_update_after_submit(self):
		if not getattr(frappe.local, "cari_internal_transition", False):
			frappe.throw("Onaylı belge yalnız yetkili işlemlerle değişir", frappe.PermissionError)
		self.validate()

	def before_submit(self):
		_finance()
		self.status = "Alındı"

	@frappe.whitelist(methods=["POST"])
	def deposit(self):
		_finance()
		_locked(self)
		if self.status != "Alındı":
			frappe.throw("Yalnız alınmış evrak bankaya verilebilir")
		with internal_transition():
			self.status = "Bankada"
			self.save()
		return {"name": self.name, "status": self.status, "bank_collection": False}

	@frappe.whitelist(methods=["POST"])
	def collect(self, bank_account, reference_no, collection_date=None):
		_finance()
		_locked(self)
		if self.payment_entry and frappe.db.get_value("Payment Entry", self.payment_entry, "docstatus") == 1:
			return {"payment_entry": self.payment_entry, "status": self.status}
		if self.status not in {"Alındı", "Bankada"}:
			frappe.throw("Evrak bu durumdan tahsil edilemez")
		if not str(reference_no or "").strip():
			frappe.throw("Gerçek banka tahsilat referansı gerekir")
		bank = frappe.get_doc("Account", bank_account)
		if bank.company != self.company or bank.account_type != "Bank" or bank.is_group or bank.disabled:
			frappe.throw("Aynı şirketin etkin banka muhasebe hesabı gerekli")
		date = collection_date or today()
		if getdate(date) > getdate():
			frappe.throw("Gelecek tarihli gerçek tahsilat oluşturulamaz")
		for row in self.references:
			frappe.db.sql("SELECT name FROM `tabSales Invoice` WHERE name=%s FOR UPDATE", (row.invoice,))
			if flt(row.allocated_amount) > flt(
				frappe.db.get_value("Sales Invoice", row.invoice, "outstanding_amount")
			):
				frappe.throw("Tahsis güncel fatura bakiyesini aşıyor")
		from erpnext.accounts.party import get_party_account
		from erpnext.setup.utils import get_exchange_rate

		party_account = get_party_account("Customer", self.customer, self.company)
		party_currency = frappe.db.get_value("Account", party_account, "account_currency")
		if party_currency != self.currency:
			frappe.throw("Evrak para birimi cari hesabın para birimiyle uyuşmalıdır")
		company_currency = frappe.db.get_value("Company", self.company, "default_currency")
		source_rate = get_exchange_rate(party_currency, company_currency, date)
		target_rate = get_exchange_rate(bank.account_currency, company_currency, date)
		if not source_rate or not target_rate:
			frappe.throw("Geçerli muhasebe kur kaydı gerekli")
		payment = frappe.get_doc(
			{
				"doctype": "Payment Entry",
				"payment_type": "Receive",
				"party_type": "Customer",
				"party": self.customer,
				"company": self.company,
				"posting_date": date,
				"paid_from": party_account,
				"paid_to": bank.name,
				"paid_amount": self.amount,
				"received_amount": flt(self.amount) * source_rate / target_rate,
				"source_exchange_rate": source_rate,
				"target_exchange_rate": target_rate,
				"reference_no": reference_no,
				"reference_date": date,
				"mode_of_payment": self.instrument_type,
				"references": [
					{
						"reference_doctype": "Sales Invoice",
						"reference_name": r.invoice,
						"allocated_amount": r.allocated_amount,
					}
					for r in self.references
				],
			}
		)
		payment.insert()
		payment.submit()
		with internal_transition():
			self.status = "Tahsil Edildi"
			self.payment_entry = payment.name
			self.bank_account = bank_account
			self.collection_date = date
			self.save()
		return {"name": self.name, "payment_entry": payment.name, "status": self.status}

	@frappe.whitelist(methods=["POST"])
	def reject(self, reason):
		_finance()
		_locked(self)
		if self.status not in {"Alındı", "Bankada"} or not str(reason or "").strip():
			frappe.throw("Karşılıksız evrak için durum ve gerekçe geçersiz")
		with internal_transition():
			self.status, self.reason = "Karşılıksız", reason
			self.save()
		return {"name": self.name, "status": self.status}

	def before_cancel(self):
		_finance()
		if self.payment_entry and frappe.db.get_value("Payment Entry", self.payment_entry, "docstatus") == 1:
			frappe.throw("Önce gerçek tahsilat kaydı standart muhasebe süreciyle iptal edilmelidir")

	def on_cancel(self):
		self.db_set("status", "İptal")


class CariShipment(Document):
	def validate(self):
		delivery = frappe.get_doc("Delivery Note", self.delivery_note)
		if delivery.docstatus != 1 or delivery.is_return:
			frappe.throw("Sevkiyat için onaylı normal irsaliye gerekir")
		self.company, self.customer = delivery.company, delivery.customer
		if self.delivery_mode == "Kendi Araçlarımız" and not self.vehicle:
			frappe.throw("Yerel teslimat için araç gerekir")
		if self.delivery_proof:
			file = frappe.get_doc("File", self.delivery_proof)
			if (
				not file.is_private
				or file.attached_to_doctype != self.doctype
				or file.attached_to_name != self.name
			):
				frappe.throw("Teslim kanıtı bu sevkiyatın özel dosyası olmalıdır")
		assert_scope(self)
		_guard_update(self)

	def before_update_after_submit(self):
		if not getattr(frappe.local, "cari_internal_transition", False):
			frappe.throw("Onaylı belge yalnız yetkili işlemlerle değişir", frappe.PermissionError)
		self.validate()

	def before_submit(self):
		require_operations_manager()
		self.status = "Hazırlanıyor"

	@frappe.whitelist(methods=["POST"])
	def dispatch(self, carrier=None, tracking_number=None):
		require_operations_manager()
		_locked(self)
		if self.status != "Hazırlanıyor":
			frappe.throw("Yalnız hazırlanmakta olan sevkiyat çıkabilir")
		if self.delivery_mode == "Kargo" and (
			not str(carrier or "").strip() or not str(tracking_number or "").strip()
		):
			frappe.throw("Kargo firması ve takip numarası gerekli")
		with internal_transition():
			self.carrier, self.tracking_number = carrier, tracking_number
			self.status, self.dispatched_at = "Sevk Edildi", now_datetime()
			self.save()
		# Finans/stok tutarlarına dokunmadan sevkiyat metadata'sı eşitlenir.
		frappe.db.set_value(
			"Delivery Note", self.delivery_note, {"kargo_firma": carrier, "kargo_takip_no": tracking_number}
		)
		return {"name": self.name, "status": self.status}

	@frappe.whitelist(methods=["POST"])
	def deliver(self, note, proof=None):
		require_operations_manager()
		_locked(self)
		if self.status != "Sevk Edildi" or not str(note or "").strip():
			frappe.throw("Teslim durumu/gerekçesi geçersiz")
		with internal_transition():
			self.status, self.delivered_at, self.note, self.delivery_proof = (
				"Teslim Edildi",
				now_datetime(),
				note,
				proof,
			)
			self.save()
		return {"name": self.name, "status": self.status}

	def before_cancel(self):
		require_operations_manager()
		if self.status == "Teslim Edildi":
			frappe.throw("Teslim edilmiş sevkiyat iptal yerine iade süreciyle ele alınır")

	def on_cancel(self):
		self.db_set("status", "İptal")


class CariServiceRecord(Document):
	def validate(self):
		if self.serial_no:
			serial = frappe.get_doc("Serial No", self.serial_no)
			if (
				serial.item_code != self.item
				or serial.company != self.company
				or (serial.customer and serial.customer != self.customer)
			):
				frappe.throw("Seri no/ürün/şirket/müşteri uyuşmuyor")
			self.warranty_expires = serial.warranty_expiry_date
		if self.service_type == "Garanti" and (
			not self.serial_no
			or not self.warranty_expires
			or getdate(self.warranty_expires) < getdate(self.opened_on)
		):
			frappe.throw("Garanti servisi için geçerli seri no garantisi gerekir")
		if self.warranty_claim:
			claim = frappe.get_doc("Warranty Claim", self.warranty_claim)
			if claim.customer != self.customer or claim.serial_no != self.serial_no:
				frappe.throw("Garanti talebi servis kaydıyla uyuşmuyor")
		assert_scope(self)
		_guard_update(self)

	def before_update_after_submit(self):
		if not getattr(frappe.local, "cari_internal_transition", False):
			frappe.throw("Onaylı belge yalnız yetkili işlemlerle değişir", frappe.PermissionError)
		self.validate()

	def before_submit(self):
		self.status = "Açık"

	@frappe.whitelist(methods=["POST"])
	def begin(self):
		_locked(self)
		if self.status != "Açık":
			frappe.throw("Yalnız açık servis başlatılır")
		with internal_transition():
			self.status = "İşlemde"
			self.save()
		return {"name": self.name, "status": self.status}

	@frappe.whitelist(methods=["POST"])
	def complete(self, result):
		_locked(self)
		if self.status != "İşlemde" or not str(result or "").strip():
			frappe.throw("Servis tamamlanması için geçerli durum ve sonuç gerekir")
		with internal_transition():
			self.status, self.result, self.completed_on = "Tamamlandı", result, today()
			self.save()
		return {"name": self.name, "status": self.status}

	def before_cancel(self):
		if self.status == "Tamamlandı":
			frappe.throw("Tamamlanmış servis geçmişi iptal edilmez")

	def on_cancel(self):
		self.db_set("status", "İptal")
