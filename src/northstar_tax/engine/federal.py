"""Federal stage of the T1: tax before credits, non-refundable credits (valued at
the 2025 effective lowest rate, 14.5%), and net federal tax (line 42000)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from northstar_tax.constants import FederalConstants
from northstar_tax.engine.tax_math import progressive_tax
from northstar_tax.money import ZERO, Money, money


def basic_personal_amount(net_income: Money, fed: FederalConstants) -> Money:
    """BPA with the high-income taper (enhanced → minimum across the top brackets)."""
    if net_income <= fed.bpa_taper_start:
        return fed.bpa_maximum
    if net_income >= fed.bpa_taper_end:
        return fed.bpa_minimum
    span = fed.bpa_taper_end - fed.bpa_taper_start
    reduction = (fed.bpa_maximum - fed.bpa_minimum) * (net_income - fed.bpa_taper_start) / span
    return money(fed.bpa_maximum - reduction)


@dataclass(frozen=True)
class FederalResult:
    tax_before_credits: Money
    bpa: Money
    cpp_base_credit: Money
    ei_credit: Money
    canada_employment_amount: Money
    credit_base: Money
    credit_value: Money
    net_federal_tax: Money  # line 42000


def compute_federal(
    *,
    taxable_income: Money,
    net_income: Money,
    employment_income: Money,
    cpp_base_credit: Money,
    ei_credit: Money,
    fed: FederalConstants,
) -> FederalResult:
    tax_before = progressive_tax(taxable_income, fed.brackets)
    bpa = basic_personal_amount(net_income, fed)
    cea = min(fed.canada_employment_amount, employment_income)
    credit_base = money(bpa + cpp_base_credit + ei_credit + cea)
    credit_value = money(credit_base * Decimal(fed.credit_rate))
    net_federal = max(ZERO, money(tax_before - credit_value))
    return FederalResult(
        tax_before_credits=tax_before,
        bpa=bpa,
        cpp_base_credit=cpp_base_credit,
        ei_credit=ei_credit,
        canada_employment_amount=cea,
        credit_base=credit_base,
        credit_value=credit_value,
        net_federal_tax=net_federal,
    )
