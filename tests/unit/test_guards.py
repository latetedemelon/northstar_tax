"""The engine refuses rather than approximates."""

from __future__ import annotations

import pytest

from northstar_tax.constants import ConstantsUnavailable, load_federal
from northstar_tax.engine import assess
from northstar_tax.errors import UnsupportedSituation
from northstar_tax.model import T4, Taxpayer, TaxReturnInput
from northstar_tax.money import money


@pytest.mark.unit
def test_unsupported_province_refused() -> None:
    data = TaxReturnInput(
        taxpayer=Taxpayer(province_of_residence="BC"),
        t4s=(T4(box_14_employment_income=money(50000)),),
    )
    with pytest.raises(UnsupportedSituation):
        assess(data)


@pytest.mark.unit
def test_unknown_year_refused() -> None:
    with pytest.raises(ConstantsUnavailable):
        load_federal(1999)
