"""Tax-year constants — versioned, validated data, never magic numbers.

Each ``(jurisdiction, tax_year)`` resolves to one immutable constants object,
loaded from the checked-in TOML bundle under ``data/constants/``. The engine
records the exact vintage it used and **refuses years it has no vetted file for**
(``ConstantsUnavailable``) rather than guessing. See ``docs/data-and-vintage.md``.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from northstar_tax.config import settings
from northstar_tax.money import Money, money

Bracket = tuple[Money, Decimal]  # (lower_bound, marginal_rate)


class ConstantsUnavailable(Exception):
    """No vetted constant set exists for the requested jurisdiction/tax year."""


@dataclass(frozen=True)
class CppConstants:
    basic_exemption: Money
    ympe: Money
    yampe: Money
    base_rate: Decimal
    enhanced_rate: Decimal
    cpp2_rate: Decimal


@dataclass(frozen=True)
class EiConstants:
    rate: Decimal
    max_insurable: Money
    max_premium: Money


@dataclass(frozen=True)
class FederalConstants:
    tax_year: int
    vintage: str
    credit_rate: Decimal
    brackets: tuple[Bracket, ...]
    bpa_maximum: Money
    bpa_minimum: Money
    bpa_taper_start: Money
    bpa_taper_end: Money
    canada_employment_amount: Money
    cpp: CppConstants
    ei: EiConstants


@dataclass(frozen=True)
class HealthPremiumBand:
    lower: Money
    base: Money
    rate: Decimal
    cap: Money


@dataclass(frozen=True)
class OntarioConstants:
    tax_year: int
    vintage: str
    credit_rate: Decimal
    brackets: tuple[Bracket, ...]
    bpa_amount: Money
    surtax_tier1_threshold: Money
    surtax_tier1_rate: Decimal
    surtax_tier2_threshold: Money
    surtax_tier2_rate: Decimal
    health_premium_bands: tuple[HealthPremiumBand, ...]
    health_premium_maximum: Money


def _load_toml(jurisdiction: str, tax_year: int) -> dict[str, Any]:
    path = Path(settings.constants_dir) / f"{jurisdiction}_{tax_year}.toml"
    if not path.exists():
        raise ConstantsUnavailable(
            f"No vetted constants for {jurisdiction} {tax_year} (looked for {path.name}). "
            "We never guess tax constants."
        )
    with path.open("rb") as fh:
        return tomllib.load(fh)


def _brackets(raw: list[list[float]]) -> tuple[Bracket, ...]:
    return tuple((money(lo), Decimal(str(rate))) for lo, rate in raw)


def load_federal(tax_year: int = 2025) -> FederalConstants:
    d = _load_toml("ca_federal", tax_year)
    return FederalConstants(
        tax_year=d["tax_year"],
        vintage=d["vintage"],
        credit_rate=Decimal(str(d["credit_rate"])),
        brackets=_brackets(d["brackets"]),
        bpa_maximum=money(d["bpa"]["maximum"]),
        bpa_minimum=money(d["bpa"]["minimum"]),
        bpa_taper_start=money(d["bpa"]["taper_start"]),
        bpa_taper_end=money(d["bpa"]["taper_end"]),
        canada_employment_amount=money(d["canada_employment_amount"]),
        cpp=CppConstants(
            basic_exemption=money(d["cpp"]["basic_exemption"]),
            ympe=money(d["cpp"]["ympe"]),
            yampe=money(d["cpp"]["yampe"]),
            base_rate=Decimal(str(d["cpp"]["base_rate"])),
            enhanced_rate=Decimal(str(d["cpp"]["enhanced_rate"])),
            cpp2_rate=Decimal(str(d["cpp"]["cpp2_rate"])),
        ),
        ei=EiConstants(
            rate=Decimal(str(d["ei"]["rate"])),
            max_insurable=money(d["ei"]["max_insurable"]),
            max_premium=money(d["ei"]["max_premium"]),
        ),
    )


def load_ontario(tax_year: int = 2025) -> OntarioConstants:
    d = _load_toml("ca_on", tax_year)
    bands = tuple(
        HealthPremiumBand(money(lo), money(base), Decimal(str(rate)), money(cap))
        for lo, base, rate, cap in d["health_premium"]["bands"]
    )
    return OntarioConstants(
        tax_year=d["tax_year"],
        vintage=d["vintage"],
        credit_rate=Decimal(str(d["credit_rate"])),
        brackets=_brackets(d["brackets"]),
        bpa_amount=money(d["bpa"]["amount"]),
        surtax_tier1_threshold=money(d["surtax"]["tier1_threshold"]),
        surtax_tier1_rate=Decimal(str(d["surtax"]["tier1_rate"])),
        surtax_tier2_threshold=money(d["surtax"]["tier2_threshold"]),
        surtax_tier2_rate=Decimal(str(d["surtax"]["tier2_rate"])),
        health_premium_bands=bands,
        health_premium_maximum=money(d["health_premium"]["maximum"]),
    )


_SUPPORTED_PROVINCES = {"ON"}


def supported_province(province: str) -> bool:
    return province in _SUPPORTED_PROVINCES
