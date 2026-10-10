"""MariaDB üzerinde gerçek izin, stok, iptal ve görev kabul testleri."""

import unittest
from contextlib import contextmanager
from uuid import uuid4

import frappe
from frappe.utils import today

from cari_custom.sample_data import COMPANY, CUSTOMER, SAHA, STORES, VEHICLE


class DeliveryTests(unittest.TestCase):
	def setUp(self):
		from cari_custom.security import install_query_guard

		install_query_guard()
		frappe.set_user("Administrator")
		frappe.flags.mute_emails = True
		frappe.local.lang = "tr"
		self.employee = frappe.db.get_value(
			"Employee", {"employee_name": "Ayşe Demir", "company": COMPANY}, "name"
		)

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()
		frappe.flags.mute_emails = False

	@contextmanager
	def actor(self, user):
		previous = frappe.session.user
		frappe.set_user(user)
		try:
			yield
		finally:
			frappe.set_user(previous)

	def user(self, persona="Saha", *, scope=True, customers=None):
		name = f"cari-test-{uuid4().hex[:12]}@example.invalid"
		frappe.get_doc(
			{
				"doctype": "User",
				"email": name,
				"first_name": "Kabul",
				"send_welcome_email": 0,
				"enabled": 1,
				"role_profile_name": f"Cari {persona}",
				"user_type": "System User",
			}
		).insert(ignore_permissions=True)
		employee = None
		if persona == "Saha":
			original = frappe.get_doc("Employee", self.employee)
			doc = frappe.copy_doc(original)
			doc.first_name = f"Kabul-{uuid4().hex[:5]}"
			doc.user_id = name
			doc.insert(ignore_permissions=True)
			employee = doc.name
		if scope:
			frappe.get_doc(
				{
					"doctype": "Cari User Scope",
					"user": name,
					"company": COMPANY,
					"persona": persona,
					"employee": employee,
					"enabled": 1,
					"customers": [
						{"customer": n} for n in (customers if customers is not None else [CUSTOMER])
					],
					"warehouses": [{"warehouse": STORES}, {"warehouse": SAHA}],
				}
			).insert(ignore_permissions=True)
		return name, employee

	def loan(self, employee=None, qty=2):
		doc = frappe.get_doc(
			{
				"doctype": "Stock Assignment",
				"personel": employee or self.employee,
				"kaynak_depo": STORES,
				"depo": SAHA,
				"urun": "ITEM-001",
				"zimmet_miktar": qty,
				"birim": "Nos",
				"atama_tarihi": today(),
			}
		)
		doc.insert()
		doc.submit()
		return doc

	def return_loan(self, loan, qty):
		doc = frappe.get_doc(
			{
				"doctype": "Stock Assignment Return",
				"assignment": loan.name,
				"quantity": qty,
				"posting_date": today(),
				"reason": "Kabul testi",
			}
		)
		doc.insert()
		doc.submit()
		return doc

	def qty(self, warehouse):
		return float(
			frappe.db.get_value("Bin", {"item_code": "ITEM-001", "warehouse": warehouse}, "actual_qty") or 0
		)

	def test_loan_approval_creates_one_real_transfer(self):
		before = self.qty(STORES), self.qty(SAHA)
		loan = self.loan(qty=2)
		self.assertEqual((self.qty(STORES), self.qty(SAHA)), (before[0] - 2, before[1] + 2))
		loan.reload()
		self.assertEqual(loan.kalan_miktar, 2)
		count = frappe.db.count("Stock Entry")
		loan.on_submit()  # Yan etki idempotency'si; standart ikinci submit zaten engellenir.
		self.assertEqual(frappe.db.count("Stock Entry"), count)
		self.assertEqual(frappe.get_doc("Stock Entry", loan.stok_hareketi).docstatus, 1)

	def test_partial_full_return_and_cancellation(self):
		before = self.qty(STORES), self.qty(SAHA)
		loan = self.loan(qty=4)
		first = self.return_loan(loan, 1)
		loan.reload()
		self.assertEqual((loan.kalan_miktar, loan.iade_miktar, loan.durum), (3, 1, "Kısmi İade"))
		with self.assertRaises(frappe.ValidationError):
			loan.cancel()
		first.cancel()
		loan.reload()
		self.assertEqual((loan.kalan_miktar, loan.iade_miktar), (4, 0))
		last = self.return_loan(loan, 4)
		loan.reload()
		self.assertEqual((loan.kalan_miktar, loan.durum), (0, "İade Edildi"))
		self.assertEqual((self.qty(STORES), self.qty(SAHA)), before)
		last.cancel()
		loan.reload()
		loan.cancel()
		self.assertEqual((self.qty(STORES), self.qty(SAHA)), before)

	def test_return_cannot_exceed_current_remaining(self):
		loan = self.loan(qty=2)
		self.return_loan(loan, 1)
		with self.assertRaises(frappe.ValidationError):
			self.return_loan(loan, 2)

	def test_linked_stock_entry_cannot_be_cancelled_outside_loan(self):
		loan = self.loan()
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc("Stock Entry", loan.stok_hareketi).cancel()

	def test_saha_list_direct_id_and_share_isolation(self):
		user_a, employee_a = self.user()
		_user_b, employee_b = self.user()
		own, other = self.loan(employee_a), self.loan(employee_b)
		frappe.share.add("Stock Assignment", other.name, user=user_a, read=1)
		with self.actor(user_a):
			names = frappe.get_list("Stock Assignment", pluck="name")
			self.assertIn(own.name, names)
			self.assertNotIn(other.name, names)
			with self.assertRaises(frappe.PermissionError):
				frappe.get_doc("Stock Assignment", other.name).check_permission("read")

	def test_missing_scope_returns_no_records(self):
		user, _employee = self.user(scope=False)
		with self.actor(user):
			self.assertEqual(frappe.get_list("Customer", pluck="name"), [])
			with self.assertRaises(frappe.PermissionError):
				frappe.get_doc("Customer", CUSTOMER).check_permission("read")

	def test_customer_empty_scope_does_not_mean_all(self):
		user, _employee = self.user(customers=[])
		with self.actor(user):
			self.assertEqual(frappe.get_list("Customer", pluck="name"), [])

	def test_depot_cannot_read_cost_or_create_financial_document(self):
		user, _employee = self.user("Depo")
		with self.actor(user):
			doc = frappe.get_doc("Item", "ITEM-001")
			doc.check_permission("read")
			doc.apply_fieldlevel_read_permissions()
			self.assertIn(doc.get("valuation_rate"), (None, ""))
			self.assertFalse(frappe.has_permission("Payment Entry", "create"))
			self.assertFalse(frappe.has_permission("Stock Entry", "create"))

	def test_depot_can_approve_controlled_loan_without_cost_permissions(self):
		user, _employee = self.user("Depo")
		with self.actor(user):
			loan = self.loan()
			self.assertEqual(loan.docstatus, 1)
			self.assertTrue(loan.stok_hareketi)

	def task(self, start="09:00:00", end="10:00:00"):
		doc = frappe.get_doc(
			{
				"doctype": "Daily Assignment",
				"personel": self.employee,
				"arac": VEHICLE,
				"tarih": today(),
				"musteri": CUSTOMER,
				"bolge": "Marmara",
				"baslangic_saati": f"{today()} {start}",
				"bitis_saati": f"{today()} {end}",
				"gorev": "Kabul testi",
			}
		)
		doc.insert()
		doc.submit()
		return doc

	def test_task_conflict_and_valid_adjacent_interval(self):
		self.task()
		with self.assertRaises(frappe.ValidationError):
			self.task("09:30:00", "10:30:00")
		self.assertEqual(self.task("10:00:00", "11:00:00").docstatus, 1)

	def test_task_start_finish_and_arbitrary_update_is_rejected(self):
		doc = self.task()
		self.assertEqual(doc.start()["status"], "Sahada")
		with self.assertRaises(frappe.ValidationError):
			doc.start()
		self.assertEqual(doc.finish("Müşteri ziyareti tamamlandı")["status"], "Tamamlandı")
		self.assertTrue(doc.actual_end)
		doc.durum = "Planlandı"
		with self.assertRaises(frappe.PermissionError):
			doc.save()

	def test_user_creation_is_disabled_until_secure_invitation(self):
		from cari_custom.user_management import provision_user

		name = f"new-cari-{uuid4().hex[:10]}@example.invalid"
		result = provision_user(name, "Kabul", COMPANY, "Satış", reason="Kabul testi")
		self.assertFalse(result["enabled"])
		self.assertNotIn("password", result)
		self.assertEqual(frappe.db.get_value("User", name, "enabled"), 0)
		self.assertTrue(frappe.db.exists("Cari Security Event", {"target_user": name}))

	def test_user_manager_cannot_grant_elevated_profiles(self):
		from cari_custom.user_management import provision_user

		user, _employee = self.user("Kullanıcı Yöneticisi")
		with self.actor(user), self.assertRaises(frappe.PermissionError):
			provision_user(
				f"priv-{uuid4().hex[:10]}@example.invalid",
				"Kabul",
				COMPANY,
				"Yönetici",
				reason="Yükseltme testi",
			)
