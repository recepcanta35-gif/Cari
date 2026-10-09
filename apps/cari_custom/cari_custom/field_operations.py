"""Onaylı zimmet, kısmi iade, satış tüketimi ve günlük saha planı.

Gerçek stok hareketleri ERPNext Stock Entry/Delivery Note ile üretilir.
Tüm miktar sınırları kilitli zimmet satırı üzerinde değerlendirilir.
"""

from datetime import datetime, time

import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import flt, get_datetime, getdate, now_datetime

from cari_custom.rules import (
	RuleViolation,
	assignment_balance,
	intervals_overlap,
	positive_quantity,
	task_transition,
)
from cari_custom.security import (
	assert_scope,
	get_scope,
	internal_transition,
	require_operations_manager,
)


def lock_assignment(name):
	# MariaDB ve PostgreSQL'de parametreli satır kilidi; işlem sonuna kadar tutulur.
	frappe.db.sql("SELECT name FROM `tabStock Assignment` WHERE name=%s FOR UPDATE", (name,))
	return frappe.get_doc("Stock Assignment", name)


def totals(assignment, *, exclude_return=None, exclude_sale=None):
	returns = frappe.qb.DocType("Stock Assignment Return")
	query = (
		frappe.qb.from_(returns)
		.select(Sum(returns.quantity))
		.where((returns.assignment == assignment) & (returns.docstatus == 1))
	)
	if exclude_return:
		query = query.where(returns.name != exclude_return)
	returned = flt(query.run()[0][0])
	sold = 0.0
	for parent_type, child_type, stock_condition in [
		("Delivery Note", "Delivery Note Item", None),
		("Sales Invoice", "Sales Invoice Item", "update_stock"),
	]:
		parent, child = frappe.qb.DocType(parent_type), frappe.qb.DocType(child_type)
		query = (
			frappe.qb.from_(parent)
			.join(child)
			.on(child.parent == parent.name)
			.select(Sum(child.stock_qty))
			.where((parent.docstatus == 1) & (child.cari_zimmet == assignment))
		)
		if stock_condition:
			query = query.where(parent[stock_condition] == 1)
		if exclude_sale and exclude_sale[0] == parent_type:
			query = query.where(parent.name != exclude_sale[1])
		sold += flt(query.run()[0][0])
	return returned, sold


def recompute(name):
	assignment = lock_assignment(name)
	returned, sold = totals(name)
	try:
		remaining, status = assignment_balance(assignment.zimmet_miktar, returned, sold)
	except RuleViolation as exc:
		frappe.throw(str(exc))
	assignment.db_set(
		{"iade_miktar": returned, "satilan_miktar": sold, "kalan_miktar": float(remaining), "durum": status},
		update_modified=False,
	)
	return assignment


def _check_warehouse(name, company):
	warehouse = frappe.get_doc("Warehouse", name)
	if warehouse.company != company or warehouse.disabled or warehouse.is_group:
		frappe.throw("Stok hareketi aynı şirketin etkin yaprak depoları arasında olmalıdır")
	scope = get_scope()
	if scope and scope.persona in {"Saha", "Depo"} and not scope.permits_warehouse(name):
		frappe.throw("Depo erişim kapsamı dışında", frappe.PermissionError)


def _transfer(company, item, qty, source, target, posting_date, *, serial_no=None, batch_no=None, remark=""):
	_check_warehouse(source, company)
	_check_warehouse(target, company)
	if source == target:
		frappe.throw("Kaynak ve hedef depo aynı olamaz")
	if not frappe.db.exists("Stock Entry Type", "Material Transfer"):
		frappe.get_doc({"doctype": "Stock Entry Type", "purpose": "Material Transfer"}).insert(
			set_name="Material Transfer", ignore_permissions=True
		)
	doc = frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"company": company,
			"stock_entry_type": "Material Transfer",
			"purpose": "Material Transfer",
			"posting_date": posting_date,
			"remarks": remark,
			"items": [
				{
					"item_code": item,
					"qty": qty,
					"uom": frappe.db.get_value("Item", item, "stock_uom"),
					"conversion_factor": 1,
					"s_warehouse": source,
					"t_warehouse": target,
					"serial_no": serial_no,
					"batch_no": batch_no,
					"use_serial_batch_fields": 1 if serial_no or batch_no else 0,
				}
			],
		}
	)
	# Dar kapsamlı sistem yan etkisi: fiyat/maliyet istemciden alınmaz. Depocuya
	# finansal belge düzenleme yetkisi vermeden çekirdek stok validasyonları çalışır.
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc


class StockAssignment(Document):
	def validate(self):
		try:
			positive_quantity(self.zimmet_miktar)
		except RuleViolation as exc:
			frappe.throw(str(exc))
		if self.iade_tarihi and self.atama_tarihi and getdate(self.iade_tarihi) < getdate(self.atama_tarihi):
			frappe.throw("İade tarihi atama tarihinden önce olamaz")
		if not self.depo or not self.urun or not self.personel:
			frappe.throw("Personel, ürün ve hedef depo zorunlu")
		company = frappe.db.get_value("Warehouse", self.depo, "company")
		if self.company and self.company != company:
			frappe.throw("Şirket ile hedef depo uyuşmuyor")
		self.company = company
		if frappe.db.get_value("Employee", self.personel, "company") != company:
			frappe.throw("Personel ve depo farklı şirkete ait")
		item = frappe.get_doc("Item", self.urun)
		if not item.is_stock_item or item.disabled:
			frappe.throw("Etkin stok ürünü gerekli")
		if item.has_serial_no and not str(self.serial_no or "").strip():
			frappe.throw("Serili üründe zimmet seri numaraları açıkça seçilmelidir")
		if item.has_batch_no and not self.batch_no:
			frappe.throw("Partili üründe parti açıkça seçilmelidir")
		self.birim = self.birim or item.stock_uom
		if self.birim != item.stock_uom:
			frappe.throw("Zimmet stok biriminde tutulur; farklı birim önce stok birimine çevrilmelidir")
		if self.stok_hareketi:
			entry = frappe.get_doc("Stock Entry", self.stok_hareketi)
			matching = [
				r
				for r in entry.items
				if r.item_code == self.urun
				and r.t_warehouse == self.depo
				and flt(r.transfer_qty) == flt(self.zimmet_miktar)
			]
			if (
				entry.docstatus != 1
				or entry.company != company
				or entry.purpose != "Material Transfer"
				or len(entry.items) != 1
				or len(matching) != 1
			):
				frappe.throw("Zimmet stok transferi uyuşmuyor")
			self.kaynak_depo = self.kaynak_depo or matching[0].s_warehouse
			if self.kaynak_depo != matching[0].s_warehouse:
				frappe.throw("Zimmet kaynak deposu transferle uyuşmuyor")
		if self.kaynak_depo:
			_check_warehouse(self.kaynak_depo, company)
		_check_warehouse(self.depo, company)
		assert_scope(self)
		if self.docstatus == 0:
			self.kalan_miktar = flt(self.zimmet_miktar)

	def before_submit(self):
		require_operations_manager()
		if not self.kaynak_depo:
			frappe.throw("Onay için kaynak depo gerekli")
		if getdate(self.atama_tarihi) > getdate():
			frappe.throw("Gelecek tarihli zimmet onaylanamaz")

	def on_submit(self):
		if not self.stok_hareketi:
			entry = _transfer(
				self.company,
				self.urun,
				self.zimmet_miktar,
				self.kaynak_depo,
				self.depo,
				self.atama_tarihi,
				serial_no=self.serial_no,
				batch_no=self.batch_no,
				remark=f"Zimmet: {self.name}",
			)
			self.db_set("stok_hareketi", entry.name)
		recompute(self.name)

	def before_cancel(self):
		require_operations_manager()
		parent = lock_assignment(self.name)
		returned, sold = totals(parent.name)
		if returned or sold:
			frappe.throw("Önce ilgili satış/iadelerin iptal veya ters kayıtları tamamlanmalıdır")

	def on_cancel(self):
		if self.stok_hareketi:
			entry = frappe.get_doc("Stock Entry", self.stok_hareketi)
			if entry.docstatus == 1:
				entry.flags.ignore_permissions = True
				entry.cancel()
		self.db_set("durum", "İptal")


class StockAssignmentReturn(Document):
	def validate(self):
		try:
			qty = positive_quantity(self.quantity)
		except RuleViolation as exc:
			frappe.throw(str(exc))
		assignment = lock_assignment(self.assignment)
		if assignment.docstatus != 1:
			frappe.throw("Yalnız onaylı zimmet iade edilebilir")
		self.company = assignment.company
		if assignment.serial_no:
			serials = {v.strip() for v in (self.serial_no or "").splitlines() if v.strip()}
			original = {v.strip() for v in assignment.serial_no.splitlines() if v.strip()}
			if len(serials) != qty or not serials.issubset(original):
				frappe.throw("İade seri numaraları zimmetle ve miktarla uyuşmuyor")
		if assignment.batch_no and self.batch_no != assignment.batch_no:
			frappe.throw("İade partisi zimmetle uyuşmuyor")
		assert_scope(assignment)
		if getdate(self.posting_date) < getdate(assignment.atama_tarihi):
			frappe.throw("İade tarihi zimmetten önce olamaz")
		returned, sold = totals(self.assignment, exclude_return=self.name)
		try:
			remaining, _status = assignment_balance(assignment.zimmet_miktar, returned, sold)
			if qty > remaining:
				raise RuleViolation("İade miktarı kalan zimmeti aşıyor")
		except RuleViolation as exc:
			frappe.throw(str(exc))

	def before_submit(self):
		require_operations_manager()
		if self.stock_entry:
			frappe.throw("İade transferi sunucu tarafından oluşturulur")

	def on_submit(self):
		assignment = lock_assignment(self.assignment)
		entry = _transfer(
			self.company,
			assignment.urun,
			self.quantity,
			assignment.depo,
			assignment.kaynak_depo,
			self.posting_date,
			serial_no=self.serial_no,
			batch_no=self.batch_no,
			remark=f"Zimmet iadesi: {self.name}",
		)
		self.db_set("stock_entry", entry.name)
		recompute(self.assignment)

	def before_cancel(self):
		require_operations_manager()
		lock_assignment(self.assignment)

	def on_cancel(self):
		if self.stock_entry:
			entry = frappe.get_doc("Stock Entry", self.stock_entry)
			entry.flags.ignore_permissions = True
			entry.cancel()
		recompute(self.assignment)


def before_stock_entry_cancel(doc, method=None):
	if frappe.db.exists("Stock Assignment", {"stok_hareketi": doc.name, "docstatus": 1}):
		frappe.throw("Bağlı zimmet üzerinden iptal edilmelidir")
	if frappe.db.exists("Stock Assignment Return", {"stock_entry": doc.name, "docstatus": 1}):
		frappe.throw("Bağlı zimmet iadesi üzerinden iptal edilmelidir")


def validate_sale(doc, method=None):
	if doc.doctype == "Sales Invoice" and not doc.update_stock:
		return
	grouped = {}
	scope = get_scope()
	for row in doc.items:
		if (
			scope
			and scope.persona == "Saha"
			and frappe.get_cached_value("Item", row.item_code, "is_stock_item")
		) and (not row.cari_zimmet or not scope.permits_warehouse(row.warehouse)):
			frappe.throw("Saha stok satışında kapsamlı depo ve zimmet bağı zorunlu", frappe.PermissionError)
		if row.cari_zimmet:
			grouped.setdefault(row.cari_zimmet, []).append(row)
	# Sabit kilit sırası birden çok zimmetli satışlarda deadlock riskini düşürür.
	for name in sorted(grouped):
		assignment = lock_assignment(name)
		assert_scope(assignment)
		if assignment.docstatus != 1 or assignment.company != doc.company:
			frappe.throw("Zimmet onaylı değil veya farklı şirkete ait")
		for row in grouped[name]:
			if row.item_code != assignment.urun or row.warehouse != assignment.depo:
				frappe.throw("Satış ürünü/deposu zimmetle uyuşmuyor")
			if doc.is_return:
				original_detail = (
					row.get("dn_detail") if doc.doctype == "Delivery Note" else row.get("sales_invoice_item")
				)
				child_type = "Delivery Note Item" if doc.doctype == "Delivery Note" else "Sales Invoice Item"
				if (
					not original_detail
					or frappe.db.get_value(child_type, original_detail, "cari_zimmet") != name
				):
					frappe.throw("Satış iadesi özgün zimmet kalemine bağlı olmalıdır")
		returned, sold = totals(name, exclude_sale=(doc.doctype, doc.name))
		try:
			assignment_balance(
				assignment.zimmet_miktar, returned, sold + sum(flt(r.stock_qty) for r in grouped[name])
			)
		except RuleViolation as exc:
			frappe.throw(str(exc))


def after_sale(doc, method=None):
	if doc.doctype == "Sales Invoice" and not doc.update_stock:
		return
	for name in sorted({r.cari_zimmet for r in doc.items if r.cari_zimmet}):
		recompute(name)


class DailyAssignment(Document):
	def validate(self):
		if (
			self.baslangic_saati
			and self.bitis_saati
			and get_datetime(self.bitis_saati) <= get_datetime(self.baslangic_saati)
		):
			frappe.throw("Bitiş saati başlangıçtan sonra olmalıdır")
		if bool(self.baslangic_saati) != bool(self.bitis_saati):
			frappe.throw("Başlangıç ve bitiş birlikte girilmelidir")
		if self.baslangic_saati and getdate(self.baslangic_saati) != getdate(self.tarih):
			frappe.throw("Görev başlangıcı görev tarihinde olmalıdır")
		company = frappe.db.get_value("Employee", self.personel, "company")
		if self.company and self.company != company:
			frappe.throw("Görev/personel şirketi uyuşmuyor")
		self.company = company
		assert_scope(self)
		before = self.get_doc_before_save()
		if (
			before
			and before.docstatus == 1
			and before.durum != self.durum
			and not getattr(frappe.local, "cari_internal_transition", False)
		):
			frappe.throw("Görev durumunu başlat/bitir işlemleriyle değiştirin", frappe.PermissionError)

	def before_submit(self):
		require_operations_manager()
		for doctype, name in [("Employee", self.personel), ("Vehicle", self.arac)]:
			if name:
				frappe.db.sql(f"SELECT name FROM `tab{doctype}` WHERE name=%s FOR UPDATE", (name,))
		start, end = self.interval()
		other = frappe.get_all(
			"Daily Assignment",
			filters={
				"company": self.company,
				"docstatus": 1,
				"name": ["!=", self.name],
				"durum": ["not in", ["Tamamlandı", "İptal"]],
			},
			fields=["name", "personel", "arac", "tarih", "baslangic_saati", "bitis_saati"],
		)
		for row in other:
			if row.personel != self.personel and (not self.arac or row.arac != self.arac):
				continue
			other_start = (
				get_datetime(row.baslangic_saati)
				if row.baslangic_saati
				else datetime.combine(getdate(row.tarih), time.min)
			)
			other_end = (
				get_datetime(row.bitis_saati)
				if row.bitis_saati
				else datetime.combine(getdate(row.tarih), time.max)
			)
			if intervals_overlap(start, end, other_start, other_end):
				frappe.throw(f"Personel veya araç başka görevle çakışıyor: {row.name}")
		self.durum = "Planlandı"

	def interval(self):
		return (
			get_datetime(self.baslangic_saati)
			if self.baslangic_saati
			else datetime.combine(getdate(self.tarih), time.min),
			get_datetime(self.bitis_saati)
			if self.bitis_saati
			else datetime.combine(getdate(self.tarih), time.max),
		)

	@frappe.whitelist(methods=["POST"])
	def start(self):
		return self._transition("Sahada")

	@frappe.whitelist(methods=["POST"])
	def finish(self, note):
		if not str(note or "").strip():
			frappe.throw("Görev sonuç notu gerekli")
		return self._transition("Tamamlandı", note=note)

	def _transition(self, target, note=None):
		self.check_permission("write")
		assert_scope(self)
		if self.docstatus != 1:
			frappe.throw("Yalnız onaylı görev başlatılabilir/bitirilebilir")
		frappe.db.sql("SELECT name FROM `tabDaily Assignment` WHERE name=%s FOR UPDATE", (self.name,))
		self.reload()
		try:
			task_transition(self.durum, target)
		except RuleViolation as exc:
			frappe.throw(str(exc))
		with internal_transition():
			self.durum = target
			if target == "Sahada":
				self.actual_start = now_datetime()
			else:
				self.actual_end = now_datetime()
				self.completion_note = note
			self.save()
		return {"name": self.name, "status": self.durum}

	def before_cancel(self):
		require_operations_manager()
		if self.durum == "Tamamlandı":
			frappe.throw("Tamamlanmış görevin geçmişi iptal edilmez; düzeltme kaydı gerekir")

	def on_cancel(self):
		self.db_set("durum", "İptal")
