"""Application settings. Mirrors Northstar's config pattern: load once, inject
everywhere. Self-contained for the MVP (no import dependency on ``northstar``;
that integration is a documented follow-up)."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """All configuration. Branding copy lives in ``branding.py``."""

    # Branding (the rename pivots; see branding.py).
    app_name: str = Field(default="Northstar Tax")
    app_slug: str = Field(default="northstar-tax")
    app_tagline: str = Field(default="Prepare your return. Review it. File it yourself.")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    log_level: str = Field(default="INFO")

    # Reference data (tax-year constants, vintage-tagged).
    constants_dir: Path = Field(default=_REPO_ROOT / "data" / "constants")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",  # bare names: APP_NAME, PORT, ...
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
