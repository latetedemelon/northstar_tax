"""Shared, pure tax arithmetic used by the federal and provincial stages."""

from __future__ import annotations

from decimal import Decimal

from northstar_tax.constants import Bracket
from northstar_tax.money import ZERO, Money, money


def progressive_tax(taxable: Money, brackets: tuple[Bracket, ...]) -> Money:
    """Tax on ``taxable`` under a progressive ``[(lower_bound, rate), ...]``
    schedule (assumed sorted ascending by lower bound)."""
    if taxable <= ZERO:
        return ZERO
    total: Money = ZERO
    for i, (lower, rate) in enumerate(brackets):
        if taxable <= lower:
            break
        upper = brackets[i + 1][0] if i + 1 < len(brackets) else None
        top = taxable if upper is None else min(taxable, upper)
        total += (top - lower) * Decimal(rate)
    return money(total)
