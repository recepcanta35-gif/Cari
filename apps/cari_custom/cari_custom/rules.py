"""Çerçeveden bağımsız iş kuralları; birim testleri Frappe/DB gerektirmez."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation


class RuleViolation(ValueError):
	pass


def quantity(value):
	try:
		result = Decimal(str(value))
	except (InvalidOperation, TypeError, ValueError) as exc:
		raise RuleViolation("Geçersiz miktar") from exc
	if not result.is_finite():
		raise RuleViolation("Miktar sonlu bir sayı olmalıdır")
	return result


def positive_quantity(value):
	result = quantity(value)
	if result <= 0:
		raise RuleViolation("Miktar sıfırdan büyük olmalıdır")
	return result


def assignment_balance(assigned, returned=0, net_sold=0):
	assigned, returned, net_sold = map(quantity, (assigned, returned, net_sold))
	if assigned <= 0 or returned < 0 or net_sold < 0:
		raise RuleViolation("Zimmet miktarları geçersiz")
	remaining = assigned - returned - net_sold
	if remaining < 0:
		raise RuleViolation("Satış ve iade toplamı zimmeti aşıyor")
	if returned == assigned:
		status = "İade Edildi"
	elif remaining == 0:
		status = "Tükendi"
	elif returned > 0:
		status = "Kısmi İade"
	else:
		status = "Aktif"
	return remaining, status


def task_transition(current, target):
	transitions = {
		"Planlandı": {"Sahada", "İptal"},
		"Sahada": {"Tamamlandı", "İptal"},
		"Tamamlandı": set(),
		"İptal": set(),
	}
	if target not in transitions.get(current, set()):
		raise RuleViolation(f"Geçersiz görev geçişi: {current} → {target}")
	return target


def intervals_overlap(start, end, other_start, other_end):
	if not all(isinstance(v, datetime) for v in (start, end, other_start, other_end)):
		raise RuleViolation("Zaman aralığı tarih/saat olmalıdır")
	if end <= start or other_end <= other_start:
		raise RuleViolation("Bitiş başlangıçtan sonra olmalıdır")
	# Bitişi diğer görevin başlangıcına eşit olan aralık çakışmaz.
	return start < other_end and other_start < end


COST_FIELDS = frozenset(
	{
		"valuation_rate",
		"stock_value",
		"stock_value_difference",
		"incoming_rate",
		"outgoing_rate",
		"stock_queue",
		"basic_rate",
		"basic_amount",
		"base_basic_rate",
		"base_basic_amount",
		"total_incoming_value",
		"total_outgoing_value",
		"total_additional_costs",
		"total_amount",
		"difference_amount",
		"additional_cost",
		"landed_cost_voucher_amount",
		"buying_price_list",
		"last_purchase_rate",
		"item_valuation_rate",
		"purchase_rate",
		"expense_account",
		"stock_adjustment_account",
	}
)


def redact_costs(value, *, quantity_only=False):
	"""RPC sözlük çıktılarında ek savunma; field-level izinlerin yerine geçmez."""
	blocked = COST_FIELDS | (
		frozenset(
			{
				"rate",
				"price_list_rate",
				"standard_rate",
				"amount",
				"base_rate",
				"base_amount",
				"total",
				"base_total",
				"net_total",
				"base_net_total",
				"grand_total",
				"base_grand_total",
				"rounded_total",
				"base_rounded_total",
				"in_words",
				"base_in_words",
			}
		)
		if quantity_only
		else frozenset()
	)
	if isinstance(value, dict):
		return {k: redact_costs(v, quantity_only=quantity_only) for k, v in value.items() if k not in blocked}
	if isinstance(value, (list, tuple)):
		return [redact_costs(v, quantity_only=quantity_only) for v in value]
	return value


@dataclass(frozen=True)
class Scope:
	user: str
	company: str
	persona: str
	employee: str | None = None
	customers: frozenset[str] = field(default_factory=frozenset)
	warehouses: frozenset[str] = field(default_factory=frozenset)
	enabled: bool = True

	def permits_company(self, company):
		return self.enabled and bool(self.company) and company == self.company

	def permits_customer(self, customer):
		return self.enabled and bool(customer) and customer in self.customers

	def permits_warehouse(self, warehouse):
		return self.enabled and bool(warehouse) and warehouse in self.warehouses

	def permits_employee(self, employee):
		return self.enabled and bool(self.employee) and employee == self.employee
