"""Web layer — a one-page demo: a T4 form that renders a computed return.

Mirrors Northstar's wizard→result pattern (Jinja2, server-rendered)."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from northstar_tax.branding import brand
from northstar_tax.engine import assess
from northstar_tax.errors import UnsupportedSituation
from northstar_tax.model import T4, Taxpayer, TaxReturnInput
from northstar_tax.money import money

_TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
_TEMPLATES.env.globals["brand"] = brand

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return _TEMPLATES.TemplateResponse(request, "index.html", {})


@router.post("/assess", response_class=HTMLResponse)
def do_assess(
    request: Request,
    box14: str = Form("0"),
    box16: str = Form("0"),
    box18: str = Form("0"),
    box22: str = Form("0"),
    rrsp: str = Form("0"),
) -> HTMLResponse:
    data = TaxReturnInput(
        taxpayer=Taxpayer(rrsp_deduction=money(rrsp or 0)),
        t4s=(
            T4(
                box_14_employment_income=money(box14 or 0),
                box_16_cpp_contrib=money(box16 or 0),
                box_18_ei_premiums=money(box18 or 0),
                box_22_income_tax_deducted=money(box22 or 0),
            ),
        ),
    )
    try:
        assessment = assess(data)
    except UnsupportedSituation as exc:
        return _TEMPLATES.TemplateResponse(
            request, "index.html", {"error": str(exc)}, status_code=422
        )
    bottom = (
        f"Refund: ${assessment.refund_or_balance}"
        if assessment.is_refund
        else f"Balance owing: ${-assessment.refund_or_balance}"
    )
    return _TEMPLATES.TemplateResponse(
        request,
        "result.html",
        {"a": assessment, "bottom": bottom, "is_refund": assessment.is_refund},
    )
