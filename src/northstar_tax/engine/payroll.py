"""CPP/EI arithmetic (Schedule 8 logic), computed from pensionable/insurable
earnings rather than trusting the slip totals — so the base-vs-enhanced split is
correct and any disagreement with the slip can be flagged as a diagnostic.

For a T4 employee the CPP *base* contribution is a non-refundable credit
(line 30800) while the *enhanced* (first-additional) portion plus CPP2 are a
deduction (line 22215). Conflating the two would visibly mis-match the CRA, so
the split is modelled explicitly even in the MVP."""

from __future__ import annotations

from decimal import Decimal

from northstar_tax.constants import CppConstants, EiConstants
from northstar_tax.money import ZERO, Money, clamp, money


def cpp_split(employment_income: Money, cpp: CppConstants) -> tuple[Money, Money]:
    """Return ``(base_credit_amount, enhanced_deduction)`` for the employee.

    * base credit (line 30800)   = base_rate × (pensionable up to YMPE − exemption)
    * enhanced deduction (22215) = enhanced_rate × that base + cpp2_rate × CPP2 earnings
    """
    base_pensionable = max(ZERO, clamp(employment_income, ZERO, cpp.ympe) - cpp.basic_exemption)
    cpp2_earnings = max(ZERO, clamp(employment_income, ZERO, cpp.yampe) - cpp.ympe)
    base_credit = money(base_pensionable * Decimal(cpp.base_rate))
    enhanced_deduction = money(
        base_pensionable * Decimal(cpp.enhanced_rate) + cpp2_earnings * Decimal(cpp.cpp2_rate)
    )
    return base_credit, enhanced_deduction


def ei_premium(employment_income: Money, ei: EiConstants) -> Money:
    """Required EI premium (line 31200 credit base) from insurable earnings."""
    insurable = clamp(employment_income, ZERO, ei.max_insurable)
    return min(money(insurable * Decimal(ei.rate)), ei.max_premium)
