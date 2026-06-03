"""The one-page web demo: form renders, and a POST returns a computed return."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from northstar_tax.branding import brand
from northstar_tax.main import app

client = TestClient(app)


@pytest.mark.functional
def test_healthz() -> None:
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.functional
def test_index_renders_form() -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert brand.name in r.text
    assert "box14" in r.text


@pytest.mark.functional
def test_assess_renders_result() -> None:
    r = client.post(
        "/assess",
        data={
            "box14": "70000",
            "box16": "3956.75",
            "box18": "1077.48",
            "box22": "12000",
            "rrsp": "5000",
        },
    )
    assert r.status_code == 200
    assert "Refund: $1985.40" in r.text
    assert "File it yourself" in r.text
