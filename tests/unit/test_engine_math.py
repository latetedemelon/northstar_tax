"""Unit tests for the engine's building blocks + property-based invariants."""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from northstar_tax.constants import load_federal, load_ontario
from northstar_tax.engine import assess, progressive_tax
from northstar_tax.engine.federal import basic_personal_amount
from northstar_tax.engine.ontario import ontario_health_premium, ontario_surtax
from northstar_tax.engine.payroll import cpp_split, ei_premium
from northstar_tax.model import T4, Taxpayer, TaxReturnInput
from northstar_tax.money import money

FED = load_federal(2025)
ON = load_ontario(2025)


@pytest.mark.unit
def test_progressive_tax_first_bracket() -> None:
    # 14.5% on the first bracket only.
    assert progressive_tax(money(10000), FED.brackets) == money(1450)


@pytest.mark.unit
def test_progressive_tax_zero_and_negative() -> None:
    assert progressive_tax(money(0), FED.brackets) == money(0)
    assert progressive_tax(money(-100), FED.brackets) == money(0)


@pytest.mark.unit
def test_cpp_split_maxed_employee() -> None:
    base_credit, enhanced = cpp_split(money(130000), FED.cpp)
    assert base_credit == money(67800 * 0.0495)  # 3356.10
    assert enhanced == money(67800 * 0.01 + 9900 * 0.04)  # 678 + 396 = 1074.00


@pytest.mark.unit
def test_ei_premium_capped() -> None:
    assert ei_premium(money(200000), FED.ei) == FED.ei.max_premium


@pytest.mark.unit
def test_bpa_taper_endpoints() -> None:
    assert basic_personal_amount(money(100000), FED) == FED.bpa_maximum
    assert basic_personal_amount(money(300000), FED) == FED.bpa_minimum
    mid = basic_personal_amount(money(215648), FED)  # midpoint of the taper
    assert FED.bpa_minimum < mid < FED.bpa_maximum


@pytest.mark.unit
def test_ontario_surtax_tiers() -> None:
    assert ontario_surtax(money(5000), ON) == money(0)  # below tier1
    # Just above tier2: 20% over tier1 + 36% over tier2.
    val = ontario_surtax(money(8000), ON)
    assert val == money((8000 - 5710) * 0.20 + (8000 - 7307) * 0.36)


@pytest.mark.unit
def test_ontario_health_premium_bands() -> None:
    assert ontario_health_premium(money(15000), ON) == money(0)
    assert ontario_health_premium(money(40000), ON) == money(450)
    assert ontario_health_premium(money(500000), ON) == ON.health_premium_maximum


@pytest.mark.unit
@given(income=st.integers(min_value=0, max_value=500_000))
def test_total_payable_is_monotonic_in_income(income: int) -> None:
    """More employment income never decreases total tax payable."""
    step = 1000

    def payable(amount: int) -> Decimal:
        data = TaxReturnInput(
            taxpayer=Taxpayer(),
            t4s=(T4(box_14_employment_income=money(amount)),),
        )
        return assess(data, FED, ON).total_payable

    assert payable(income + step) >= payable(income)
