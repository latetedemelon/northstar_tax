"""Domain model — all inputs and outputs are immutable frozen dataclasses.

The engine never mutates; it derives. Slip field names track CRA box numbers so
every computed number is auditable back to its source. See ``docs/architecture.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from northstar_tax.money import ZERO, Money


@dataclass(frozen=True)
class T4:
    """Statement of Remuneration Paid. MVP subset of boxes."""

    box_14_employment_income: Money
    box_16_cpp_contrib: Money = ZERO
    box_18_ei_premiums: Money = ZERO
    box_22_income_tax_deducted: Money = ZERO
    employer: str = ""


@dataclass(frozen=True)
class Taxpayer:
    """Who is filing. MVP: Ontario residents, full-year, tax year 2025."""

    tax_year: int = 2025
    province_of_residence: str = "ON"
    rrsp_deduction: Money = ZERO  # line 20800


@dataclass(frozen=True)
class TaxReturnInput:
    """Everything needed to assess a return. MVP: one taxpayer, T4 income only."""

    taxpayer: Taxpayer
    t4s: tuple[T4, ...] = ()


@dataclass(frozen=True)
class LineResult:
    """One line of the computed return: its CRA line number, value, and *why*."""

    line: str  # CRA line number, e.g. "15000"
    label: str
    amount: Money
    explain: str = ""
    sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class Diagnostic:
    """An informational, non-blocking note (cf. Northstar's Review layer)."""

    id: str
    severity: str  # "info" | "warning"
    message: str


@dataclass(frozen=True)
class TaxAssessment:
    """The finished return — a complete, explained, line-numbered worksheet."""

    tax_year: int
    province: str
    constants_vintage: str
    total_income: Money  # line 15000
    net_income: Money  # line 23600
    taxable_income: Money  # line 26000
    federal_tax: Money  # line 42000 (net federal tax)
    provincial_tax: Money  # ON 428 total (incl. surtax + health premium)
    total_payable: Money  # line 43500
    tax_withheld: Money  # line 43700
    refund_or_balance: Money  # +refund / -balance owing
    lines: tuple[LineResult, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = field(default_factory=tuple)

    @property
    def is_refund(self) -> bool:
        return self.refund_or_balance >= 0
