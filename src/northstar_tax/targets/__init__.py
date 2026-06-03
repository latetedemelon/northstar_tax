"""Output targets — the hand-off seam, modelled on Northstar's ``BudgetTarget``
Protocol + shared conformance suite.

The defining invariant of this module: **no target may transmit a return.** A
target renders the finished assessment for the user to file themselves. The seam
where a NETFILE transmitter *would* go is intentionally, and testably, empty
(see ``tests/functional/test_target_conformance.py``). ``TRANSMIT`` is not a
permitted capability."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from northstar_tax.model import TaxAssessment

# Capabilities a target may advertise. Note the deliberate absence of any
# "transmit"/"netfile"/"efile" capability — that is the architectural thesis.
RENDER = "render"
ALLOWED_CAPABILITIES = frozenset({RENDER})
FORBIDDEN_CAPABILITIES = frozenset({"transmit", "netfile", "efile", "file", "submit"})


class TaxReturnTargetError(Exception):
    """Base class for output-target failures."""


class RenderError(TaxReturnTargetError):
    """The assessment could not be rendered into the target format."""


@dataclass(frozen=True)
class TargetInfo:
    name: str
    version: str
    capabilities: frozenset[str] = field(default_factory=frozenset)


@runtime_checkable
class TaxReturnTarget(Protocol):
    """The output contract. Render the finished return; never file it."""

    def describe(self) -> TargetInfo:
        """Static metadata about this target."""
        ...

    def render(self, assessment: TaxAssessment) -> str:
        """Produce the target's representation of the finished return."""
        ...


def available_targets() -> tuple[TaxReturnTarget, ...]:
    """Every output target this package ships. The conformance suite asserts none
    of them can transmit a return."""
    from northstar_tax.targets.printable import PrintableSummary

    return (PrintableSummary(fmt="text"), PrintableSummary(fmt="html"))
