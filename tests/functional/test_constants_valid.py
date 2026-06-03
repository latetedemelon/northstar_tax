"""Mirror of scripts/validate_constants.py so a broken constant fails the suite,
not just the standalone gate."""

from __future__ import annotations

import pytest
from scripts.validate_constants import main as validate


@pytest.mark.functional
def test_constants_bundle_is_valid() -> None:
    assert validate() == 0
