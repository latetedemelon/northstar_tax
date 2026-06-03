"""Money is ``Decimal``, never ``float``.

A tax return is exact arithmetic with prescribed rounding, so float drift is
unacceptable (this is the one deliberate departure from Northstar's budgeting
code, which uses float because a budget is an estimate). Everything flows through
:func:`money`, which quantizes to cents with banker-free half-up rounding (the
CRA's convention)."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

Money = Decimal

_CENT = Decimal("0.01")
ZERO: Money = Decimal("0.00")


def money(value: object) -> Money:
    """Coerce a number/string to a cent-quantized :data:`Money` (half-up)."""
    return Decimal(str(value)).quantize(_CENT, rounding=ROUND_HALF_UP)


def round_dollar(value: Money) -> Money:
    """Round to the nearest dollar (half-up), as the CRA does on tax lines."""
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP).quantize(_CENT)


def clamp(value: Money, low: Money, high: Money) -> Money:
    """Clamp ``value`` into ``[low, high]``."""
    return max(low, min(value, high))
