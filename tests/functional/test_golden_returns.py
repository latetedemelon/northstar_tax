"""Golden-case conformance — the centrepiece gate.

Each case is a complete Ontario 2025 return whose expected line values were
derived by hand following the T1 / Form ON428 method (CPP Schedule 8 split,
14.5% federal credit rate, BPA taper, ON surtax, ON Health Premium) and the
primary-sourced 2025 constants. Cases A, B and C were verified to the cent
independently of the engine. A change that moves any of these without a reviewed
constant/vintage update must fail the build.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from northstar_tax.engine import assess
from northstar_tax.model import T4, Taxpayer, TaxReturnInput
from northstar_tax.money import money


def _return(box14, box16, box18, box22, rrsp=0) -> TaxReturnInput:
    return TaxReturnInput(
        taxpayer=Taxpayer(rrsp_deduction=money(rrsp)),
        t4s=(
            T4(
                box_14_employment_income=money(box14),
                box_16_cpp_contrib=money(box16),
                box_18_ei_premiums=money(box18),
                box_22_income_tax_deducted=money(box22),
            ),
        ),
    )


# name -> (input, expected line values)
GOLDEN = {
    "A_40k_balance_owing": (
        _return(40000, 2171.75, 656.00, 4500),
        {
            "net_income": "39635.00",
            "taxable_income": "39635.00",
            "federal_tax": "2837.98",
            "provincial_tax": "1683.48",
            "total_payable": "4521.46",
            "refund_or_balance": "-21.46",  # balance owing
        },
    ),
    "B_70k_rrsp_refund": (
        _return(70000, 3956.75, 1077.48, 12000, rrsp=5000),
        {
            "net_income": "64335.00",
            "taxable_income": "64335.00",
            "federal_tax": "6560.64",
            "provincial_tax": "3453.96",
            "total_payable": "10014.60",
            "refund_or_balance": "1985.40",  # refund
        },
    ),
    "C_130k_surtax": (
        _return(130000, 4430.10, 1077.48, 30000),
        {
            "net_income": "128926.00",
            "taxable_income": "128926.00",
            "federal_tax": "20572.14",
            "provincial_tax": "11370.23",  # includes surtax + health premium
            "total_payable": "31942.37",
            "refund_or_balance": "-1942.37",
        },
    ),
    "D_250k_bpa_taper": (
        _return(250000, 4430.10, 1077.48, 80000),
        {
            "net_income": "248926.00",
            "taxable_income": "248926.00",
            "federal_tax": "54120.45",
            "provincial_tax": "34406.24",
            "total_payable": "88526.69",
            "refund_or_balance": "-8526.69",
        },
    ),
}


@pytest.mark.functional
@pytest.mark.parametrize("name", list(GOLDEN), ids=list(GOLDEN))
def test_golden_return(name: str) -> None:
    data, expected = GOLDEN[name]
    a = assess(data)
    for field, want in expected.items():
        got = getattr(a, field)
        assert got == Decimal(want), f"{name}.{field}: got {got}, want {want}"


@pytest.mark.functional
def test_balance_and_refund_signs() -> None:
    assert not assess(GOLDEN["A_40k_balance_owing"][0]).is_refund
    assert assess(GOLDEN["B_70k_rrsp_refund"][0]).is_refund


@pytest.mark.functional
def test_worksheet_is_explained() -> None:
    a = assess(GOLDEN["C_130k_surtax"][0])
    assert any(line.line == "15000" for line in a.lines)
    assert any(line.line == "42000" for line in a.lines)
    assert all(line.explain for line in a.lines)  # every line carries a why
