"""TaxReturnTarget conformance suite (modelled on Northstar's BudgetTarget suite)
— plus the module's defining invariant: **no target may transmit a return.**"""

from __future__ import annotations

import pytest

from northstar_tax.engine import assess
from northstar_tax.model import T4, Taxpayer, TaxReturnInput
from northstar_tax.money import money
from northstar_tax.targets import (
    FORBIDDEN_CAPABILITIES,
    TargetInfo,
    TaxReturnTarget,
    available_targets,
)
from northstar_tax.targets.printable import PrintableSummary, artifact_name

_ASSESSMENT = assess(
    TaxReturnInput(taxpayer=Taxpayer(), t4s=(T4(box_14_employment_income=money(70000)),))
)


class TaxReturnTargetConformance:
    """Behaviours every target must satisfy. Subclasses provide a `target`."""

    @pytest.fixture
    def target(self) -> TaxReturnTarget:
        raise NotImplementedError

    def test_satisfies_protocol(self, target: TaxReturnTarget) -> None:
        assert isinstance(target, TaxReturnTarget)

    def test_describe_returns_info(self, target: TaxReturnTarget) -> None:
        info = target.describe()
        assert isinstance(info, TargetInfo)
        assert info.name

    def test_render_returns_text(self, target: TaxReturnTarget) -> None:
        out = target.render(_ASSESSMENT)
        assert isinstance(out, str) and out

    def test_target_cannot_transmit(self, target: TaxReturnTarget) -> None:
        # The architectural thesis, enforced: a target may not advertise any
        # filing/transmission capability.
        assert target.describe().capabilities.isdisjoint(FORBIDDEN_CAPABILITIES)


@pytest.mark.functional
class TestPrintableTextConformance(TaxReturnTargetConformance):
    @pytest.fixture
    def target(self) -> TaxReturnTarget:
        return PrintableSummary(fmt="text")


@pytest.mark.functional
class TestPrintableHtmlConformance(TaxReturnTargetConformance):
    @pytest.fixture
    def target(self) -> TaxReturnTarget:
        return PrintableSummary(fmt="html")


@pytest.mark.functional
def test_no_shipped_target_can_transmit() -> None:
    for target in available_targets():
        assert target.describe().capabilities.isdisjoint(FORBIDDEN_CAPABILITIES)


@pytest.mark.functional
def test_package_ships_no_transmitter() -> None:
    # There is no NETFILE/transmitter class anywhere in the targets package.
    import northstar_tax.targets as targets_pkg

    names = dir(targets_pkg)
    assert not any(any(bad in n.lower() for bad in ("netfile", "transmit", "efile")) for n in names)


@pytest.mark.functional
def test_artifact_name_is_slug_based() -> None:
    name = artifact_name(_ASSESSMENT, "txt")
    assert name.endswith("-t1-2025.txt")
