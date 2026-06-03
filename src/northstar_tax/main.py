"""FastAPI application entrypoint for the web demo."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from northstar_tax.branding import brand
from northstar_tax.web import router

app = FastAPI(title=brand.name, description=brand.short_description, version="0.1.0.dev0")
app.include_router(router)


@app.get("/healthz")
def healthz() -> JSONResponse:
    """Liveness probe."""
    return JSONResponse({"status": "ok", "app": brand.name})
