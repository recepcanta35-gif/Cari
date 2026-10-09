from datetime import datetime
from decimal import Decimal

import pytest
from cari_custom.rules import (
	RuleViolation,
	Scope,
	assignment_balance,
	intervals_overlap,
	positive_quantity,
	redact_costs,
	task_transition,
)


@pytest.mark.parametrize("value", [0, -1, "NaN", "Infinity", "-Infinity", "bad", None])
def test_invalid_quantity_is_rejected(value):
	with pytest.raises(RuleViolation):
		positive_quantity(value)


def test_assignment_partial_return_sale_and_balance():
	assert assignment_balance(10, 2, 3) == (Decimal(5), "Kısmi İade")
	assert assignment_balance(10, 10, 0) == (Decimal(0), "İade Edildi")
	assert assignment_balance(10, 2, 8) == (Decimal(0), "Tükendi")
	with pytest.raises(RuleViolation):
		assignment_balance(10, 3, 8)
	with pytest.raises(RuleViolation):
		assignment_balance(10, 0, -1)


def test_fractional_quantity_keeps_precision():
	assert assignment_balance("1.0005", "0.0004", "0.0001")[0] == Decimal("1.0000")


@pytest.mark.parametrize(
	"source,target", [("Planlandı", "Sahada"), ("Sahada", "Tamamlandı"), ("Planlandı", "İptal")]
)
def test_task_valid_transitions(source, target):
	assert task_transition(source, target) == target


@pytest.mark.parametrize(
	"source,target",
	[("Planlandı", "Tamamlandı"), ("Tamamlandı", "Sahada"), ("İptal", "Planlandı"), ("unknown", "Sahada")],
)
def test_task_invalid_transitions(source, target):
	with pytest.raises(RuleViolation):
		task_transition(source, target)


def test_half_open_intervals():
	def at(hour):
		return datetime(2026, 10, 9, hour)

	assert not intervals_overlap(at(9), at(10), at(10), at(11))
	assert intervals_overlap(at(9), at(11), at(10), at(12))
	with pytest.raises(RuleViolation):
		intervals_overlap(at(9), at(9), at(10), at(11))


def test_scope_is_deny_by_default():
	scope = Scope(user="a@example.invalid", company="A", persona="Saha", employee="EMP-A")
	assert scope.permits_company("A")
	assert not scope.permits_company("B")
	assert not scope.permits_customer("CUS-A")
	assert not scope.permits_warehouse("WH-A")
	assert scope.permits_employee("EMP-A")
	assert not scope.permits_employee("EMP-B")
	assert not Scope(user="a", company="A", persona="Saha", enabled=False).permits_company("A")


def test_redaction_keeps_sales_price_but_removes_cost():
	data = {
		"rate": 250,
		"valuation_rate": 150,
		"stock_queue": "[[10,150]]",
		"items": [{"basic_rate": 150, "qty": 10, "amount": 2500}],
	}
	sales = redact_costs(data)
	assert sales["rate"] == 250
	assert "valuation_rate" not in sales and "stock_queue" not in sales
	quantity_only = redact_costs(data, quantity_only=True)
	assert quantity_only == {"items": [{"qty": 10}]}
