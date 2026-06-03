"""Review layer — pure, non-blocking diagnostics (cf. Northstar's ``review.py``).

Informational checks on the inputs that catch common slip-entry mistakes. They
never block the assessment; they surface notes for the user to verify before
filing."""

from __future__ import annotations

from northstar_tax.constants import FederalConstants
from northstar_tax.model import Diagnostic, TaxReturnInput
from northstar_tax.money import ZERO, money


def input_diagnostics(data: TaxReturnInput, fed: FederalConstants) -> list[Diagnostic]:
    notes: list[Diagnostic] = []
    cpp_max = money((fed.cpp.ympe - fed.cpp.basic_exemption) * fed.cpp.base_rate) + money(
        (fed.cpp.ympe - fed.cpp.basic_exemption) * fed.cpp.enhanced_rate
        + (fed.cpp.yampe - fed.cpp.ympe) * fed.cpp.cpp2_rate
    )

    for i, t4 in enumerate(data.t4s, start=1):
        label = t4.employer or f"T4 #{i}"
        if t4.box_14_employment_income < ZERO:
            notes.append(Diagnostic("negative_income", "warning", f"{label}: box 14 is negative."))
        if t4.box_16_cpp_contrib > cpp_max + money(5):
            notes.append(
                Diagnostic(
                    "cpp_over_max",
                    "warning",
                    f"{label}: box 16 CPP (${t4.box_16_cpp_contrib}) exceeds the 2025 maximum "
                    f"(~${cpp_max}).",
                )
            )
        if t4.box_18_ei_premiums > fed.ei.max_premium + money(5):
            notes.append(
                Diagnostic(
                    "ei_over_max",
                    "warning",
                    f"{label}: box 18 EI (${t4.box_18_ei_premiums}) exceeds the 2025 maximum "
                    f"(${fed.ei.max_premium}).",
                )
            )

    if data.taxpayer.rrsp_deduction < ZERO:
        notes.append(Diagnostic("negative_rrsp", "warning", "RRSP deduction is negative."))
    return notes
