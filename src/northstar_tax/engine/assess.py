"""``assess()`` — the single pure entry point. Composes the ordered T1 stages
into a complete, line-numbered, explained :class:`TaxAssessment`. No I/O."""

from __future__ import annotations

from decimal import Decimal

from northstar_tax.constants import (
    FederalConstants,
    OntarioConstants,
    load_federal,
    load_ontario,
    supported_province,
)
from northstar_tax.engine.federal import compute_federal
from northstar_tax.engine.ontario import compute_ontario
from northstar_tax.engine.payroll import cpp_split, ei_premium
from northstar_tax.errors import UnsupportedSituation
from northstar_tax.model import Diagnostic, LineResult, TaxAssessment, TaxReturnInput
from northstar_tax.money import ZERO, Money, money
from northstar_tax.review import input_diagnostics


def _pct(rate: Decimal) -> str:
    return f"{float(rate) * 100:g}%"


def assess(
    data: TaxReturnInput,
    fed: FederalConstants | None = None,
    on: OntarioConstants | None = None,
) -> TaxAssessment:
    taxpayer = data.taxpayer
    province = taxpayer.province_of_residence
    if not supported_province(province):
        raise UnsupportedSituation(
            f"Province {province!r} is not modelled in this release (Ontario only at t0.1). "
            "We refuse rather than compute a wrong number."
        )

    fed = fed or load_federal(taxpayer.tax_year)
    on = on or load_ontario(taxpayer.tax_year)

    lines: list[LineResult] = []
    diagnostics: list[Diagnostic] = list(input_diagnostics(data, fed))

    # --- 1. Total income (line 15000) -----------------------------------------
    employment_income = money(sum((t.box_14_employment_income for t in data.t4s), ZERO))
    tax_withheld = money(sum((t.box_22_income_tax_deducted for t in data.t4s), ZERO))
    cpp_box16 = money(sum((t.box_16_cpp_contrib for t in data.t4s), ZERO))
    total_income = employment_income
    lines.append(
        LineResult(
            "15000",
            "Total income",
            total_income,
            f"Employment income from {len(data.t4s)} T4 slip(s), box 14.",
            tuple(t.employer or "T4" for t in data.t4s),
        )
    )

    # --- 2. CPP split (Schedule 8): base -> credit, enhanced -> deduction ------
    cpp_base_credit, cpp_enhanced_deduction = cpp_split(employment_income, fed.cpp)
    ei_credit = ei_premium(employment_income, fed.ei)
    if cpp_box16 > ZERO and abs(cpp_box16 - (cpp_base_credit + cpp_enhanced_deduction)) > money(2):
        diagnostics.append(
            Diagnostic(
                "cpp_box16_mismatch",
                "warning",
                f"T4 box 16 CPP (${cpp_box16}) differs from the amount expected for "
                f"${employment_income} of pensionable earnings — check the slip.",
            )
        )

    # --- 3. Deductions -> Net income (line 23600) -----------------------------
    rrsp = taxpayer.rrsp_deduction
    if rrsp > ZERO:
        lines.append(
            LineResult("20800", "RRSP deduction", rrsp, "Reported RRSP/PRPP contributions.")
        )
    lines.append(
        LineResult(
            "22215",
            "Deduction for CPP enhanced contributions",
            cpp_enhanced_deduction,
            "Employee first-additional (enhanced) CPP plus CPP2 — deductible, not a credit.",
        )
    )
    net_income = money(total_income - rrsp - cpp_enhanced_deduction)
    lines.append(
        LineResult(
            "23600",
            "Net income",
            net_income,
            "Total income less RRSP and the enhanced-CPP deduction.",
        )
    )

    # --- 4. Taxable income (line 26000) ---------------------------------------
    taxable_income = net_income  # no Division-C deductions in the T4-only MVP
    lines.append(
        LineResult(
            "26000",
            "Taxable income",
            taxable_income,
            "Equals net income (no Division-C deductions modelled at t0.1).",
        )
    )

    # --- 5-7. Federal tax and credits -> net federal tax (line 42000) ---------
    fr = compute_federal(
        taxable_income=taxable_income,
        net_income=net_income,
        employment_income=employment_income,
        cpp_base_credit=cpp_base_credit,
        ei_credit=ei_credit,
        fed=fed,
    )
    lines.append(
        LineResult(
            "30000-35000",
            "Federal non-refundable credit amounts",
            fr.credit_base,
            f"BPA ${fr.bpa} + CPP base ${fr.cpp_base_credit} + EI ${fr.ei_credit} "
            f"+ Canada employment ${fr.canada_employment_amount}.",
        )
    )
    lines.append(
        LineResult(
            "35000",
            f"Federal credit value (at {_pct(fed.credit_rate)})",
            fr.credit_value,
            f"Credit amounts valued at the 2025 effective lowest rate, {_pct(fed.credit_rate)}.",
        )
    )
    lines.append(
        LineResult(
            "42000",
            "Net federal tax",
            fr.net_federal_tax,
            f"Federal tax ${fr.tax_before_credits} less credits ${fr.credit_value} (floored at 0).",
        )
    )

    # --- 8-11. Ontario (Form ON428) -------------------------------------------
    onr = compute_ontario(
        taxable_income=taxable_income,
        cpp_base_credit=cpp_base_credit,
        ei_credit=ei_credit,
        on=on,
    )
    lines.append(
        LineResult(
            "ON428-tax",
            "Ontario tax after non-refundable credits",
            onr.tax_after_credits,
            f"Ontario tax ${onr.tax_before_credits} less credits ${onr.credit_value} "
            f"(BPA ${onr.bpa}, valued at {_pct(on.credit_rate)}).",
        )
    )
    if onr.surtax > ZERO:
        lines.append(
            LineResult(
                "ON428-surtax",
                "Ontario surtax",
                onr.surtax,
                "20% of Ontario tax over the first threshold, +36% over the second.",
            )
        )
    if onr.health_premium > ZERO:
        lines.append(
            LineResult(
                "ON428-ohp",
                "Ontario Health Premium",
                onr.health_premium,
                "From the taxable-income schedule (nil under $20,000, max $900).",
            )
        )
    lines.append(
        LineResult(
            "ON428-total", "Ontario tax payable", onr.total, "Tax + surtax + health premium."
        )
    )

    # --- 12-13. Reconciliation ------------------------------------------------
    total_payable = money(fr.net_federal_tax + onr.total)
    lines.append(
        LineResult("43500", "Total payable", total_payable, "Net federal tax plus Ontario tax.")
    )
    lines.append(
        LineResult("43700", "Total income tax deducted", tax_withheld, "T4 box 22 withholding.")
    )
    refund_or_balance: Money = money(tax_withheld - total_payable)
    if refund_or_balance >= ZERO:
        lines.append(
            LineResult("48400", "Refund", refund_or_balance, "Withholding exceeded total payable.")
        )
    else:
        lines.append(
            LineResult(
                "48500",
                "Balance owing",
                -refund_or_balance,
                "Total payable exceeded withholding.",
            )
        )

    return TaxAssessment(
        tax_year=taxpayer.tax_year,
        province=province,
        constants_vintage=fed.vintage,
        total_income=total_income,
        net_income=net_income,
        taxable_income=taxable_income,
        federal_tax=fr.net_federal_tax,
        provincial_tax=onr.total,
        total_payable=total_payable,
        tax_withheld=tax_withheld,
        refund_or_balance=refund_or_balance,
        lines=tuple(lines),
        diagnostics=tuple(diagnostics),
    )
