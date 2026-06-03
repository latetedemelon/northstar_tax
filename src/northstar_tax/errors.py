"""Error taxonomy. The guiding principle: a wrong number is worse than an honest
"we don't handle this." The engine refuses rather than approximates."""

from __future__ import annotations


class TaxInputError(ValueError):
    """Malformed or contradictory input (caught before it reaches the engine)."""


class UnsupportedSituation(Exception):
    """A case this release does not model (e.g. a non-Ontario province at t0.1).
    Carries a human-readable reason; we fail loudly rather than compute a wrong
    number."""
