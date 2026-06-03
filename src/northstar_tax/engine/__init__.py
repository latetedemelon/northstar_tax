"""The calculation engine — pure functions, no I/O.

``assess()`` is the single entry point; the rest of this package is the ordered
T1 computation it composes. See ``docs/architecture.md`` for the stage order.
"""

from __future__ import annotations

from northstar_tax.engine.assess import assess
from northstar_tax.engine.tax_math import progressive_tax

__all__ = ["assess", "progressive_tax"]
