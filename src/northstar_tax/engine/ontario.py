"""Ontario stage (Form ON428): tax before credits, non-refundable credits (at
5.05%), surtax (after credits, before the health premium), and the Ontario Health
Premium. Returns the total Ontario tax payable."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from northstar_tax.constants import OntarioConstants
from northstar_tax.engine.tax_math import progressive_tax
from northstar_tax.money import ZERO, Money, money


def ontario_surtax(tax_after_credits: Money, on: OntarioConstants) -> Money:
    """20% of Ontario tax over tier1 plus an additional 36% over tier2."""
    tier1 = max(ZERO, tax_after_credits - on.surtax_tier1_threshold) * Decimal(on.surtax_tier1_rate)
    tier2 = max(ZERO, tax_after_credits - on.surtax_tier2_threshold) * Decimal(on.surtax_tier2_rate)
    return money(tier1 + tier2)


def ontario_health_premium(taxable_income: Money, on: OntarioConstants) -> Money:
    """Piecewise base + min(cap, rate × (taxable_income − band floor))."""
    premium = ZERO
    for band in on.health_premium_bands:
        if taxable_income <= band.lower:
            break
        marginal = min(band.cap, money((taxable_income - band.lower) * Decimal(band.rate)))
        premium = money(band.base + marginal)
    return min(premium, on.health_premium_maximum)


@dataclass(frozen=True)
class OntarioResult:
    tax_before_credits: Money
    bpa: Money
    credit_base: Money
    credit_value: Money
    tax_after_credits: Money
    surtax: Money
    health_premium: Money
    total: Money  # Ontario tax + surtax + health premium


def compute_ontario(
    *,
    taxable_income: Money,
    cpp_base_credit: Money,
    ei_credit: Money,
    on: OntarioConstants,
) -> OntarioResult:
    tax_before = progressive_tax(taxable_income, on.brackets)
    credit_base = money(on.bpa_amount + cpp_base_credit + ei_credit)
    credit_value = money(credit_base * Decimal(on.credit_rate))
    after_credits = max(ZERO, money(tax_before - credit_value))
    surtax = ontario_surtax(after_credits, on)
    premium = ontario_health_premium(taxable_income, on)
    total = money(after_credits + surtax + premium)
    return OntarioResult(
        tax_before_credits=tax_before,
        bpa=on.bpa_amount,
        credit_base=credit_base,
        credit_value=credit_value,
        tax_after_credits=after_credits,
        surtax=surtax,
        health_premium=premium,
        total=total,
    )
