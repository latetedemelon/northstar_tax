"""Immutable brand strings, built from settings at module load.

Brand is a variable, never a literal: reference ``brand.name`` / ``brand.slug``
in code, templates, and generated filenames. Generated artifacts are named from
``brand.slug`` (e.g. ``f"{brand.slug}-t1-2025.txt"``) so a rebrand never touches
a path. The capitalized default lives only in ``config.py``."""

from __future__ import annotations

from dataclasses import dataclass

from northstar_tax.config import settings


@dataclass(frozen=True)
class Brand:
    name: str
    name_possessive: str
    slug: str
    tagline: str
    short_description: str
    footer: str


brand = Brand(
    name=settings.app_name,
    name_possessive=f"{settings.app_name}'s",
    slug=settings.app_slug,
    tagline=settings.app_tagline,
    short_description=(
        f"{settings.app_name} prepares a complete Canadian personal income-tax "
        "return — every relevant line, federal and provincial, explained — and "
        "stops at the moment before filing. You review it and file it yourself."
    ),
    footer="© Bayview Industries Ltd.",
)
