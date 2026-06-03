#!/usr/bin/env python3
"""Validate the tax-constants bundle (mirrors Northstar's validate_crosswalks.py).

Structural checks only — brackets are ascending and rates sane, the BPA taper
endpoints line up with real federal bracket thresholds, and the Ontario surtax
and health-premium tiers ascend. Exits non-zero on any issue so it gates CI and
pre-commit. Run: ``uv run python scripts/validate_constants.py``."""

from __future__ import annotations

from decimal import Decimal

from northstar_tax.constants import (
    FederalConstants,
    OntarioConstants,
    load_federal,
    load_ontario,
)

YEARS = (2025,)


def _check_brackets(name: str, brackets: object, issues: list[str]) -> None:
    bands = list(brackets)  # type: ignore[call-overload]
    bounds = [lo for lo, _ in bands]
    rates = [r for _, r in bands]
    if bounds != sorted(bounds) or len(set(bounds)) != len(bounds):
        issues.append(f"{name}: bracket lower bounds must strictly ascend: {bounds}")
    if bounds and bounds[0] != 0:
        issues.append(f"{name}: first bracket must start at 0 (got {bounds[0]})")
    if any(not (Decimal(0) < Decimal(r) < Decimal(1)) for r in rates):
        issues.append(f"{name}: every marginal rate must be in (0, 1): {rates}")
    if rates != sorted(rates):
        issues.append(f"{name}: marginal rates should be non-decreasing: {rates}")


def _check_federal(fed: FederalConstants, issues: list[str]) -> None:
    _check_brackets("federal", fed.brackets, issues)
    if not (fed.bpa_minimum <= fed.bpa_maximum):
        issues.append("federal: BPA minimum exceeds maximum")
    bounds = {lo for lo, _ in fed.brackets}
    if fed.bpa_taper_start not in bounds or fed.bpa_taper_end not in bounds:
        issues.append("federal: BPA taper endpoints must align with bracket thresholds")
    if not (Decimal(0) < Decimal(fed.credit_rate) < Decimal(1)):
        issues.append("federal: credit_rate out of range")


def _check_ontario(on: OntarioConstants, issues: list[str]) -> None:
    _check_brackets("ontario", on.brackets, issues)
    if on.surtax_tier1_threshold >= on.surtax_tier2_threshold:
        issues.append("ontario: surtax tier1 threshold must be below tier2")
    floors = [b.lower for b in on.health_premium_bands]
    if floors != sorted(floors):
        issues.append(f"ontario: health-premium band floors must ascend: {floors}")
    if on.health_premium_bands and on.health_premium_bands[0].lower != 0:
        issues.append("ontario: first health-premium band must start at 0")


def main() -> int:
    issues: list[str] = []
    for year in YEARS:
        fed = load_federal(year)
        on = load_ontario(year)
        print(
            f"{year}: federal {fed.vintage} ({len(fed.brackets)} brackets), "
            f"ontario {on.vintage} ({len(on.brackets)} brackets)"
        )
        _check_federal(fed, issues)
        _check_ontario(on, issues)

    if issues:
        print(f"\nFAILED with {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print("\nOK: tax constants are structurally consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
