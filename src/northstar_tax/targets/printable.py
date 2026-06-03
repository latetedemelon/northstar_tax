"""A printable summary of the finished return — plain text or simple HTML.

This is the MVP hand-off: a clean, line-numbered worksheet the user reads, then
files themselves. Generated-artifact names come from ``brand.slug``, never a
literal."""

from __future__ import annotations

from northstar_tax.branding import brand
from northstar_tax.model import TaxAssessment
from northstar_tax.targets import RENDER, RenderError, TargetInfo


def artifact_name(assessment: TaxAssessment, ext: str) -> str:
    """Brand-free, slug-based filename, e.g. ``northstar-tax-t1-2025.txt``."""
    return f"{brand.slug}-t1-{assessment.tax_year}.{ext}"


class PrintableSummary:
    """Renders an assessment as text or HTML. Renders only — it cannot file."""

    def __init__(self, fmt: str = "text") -> None:
        if fmt not in ("text", "html"):
            raise RenderError(f"unknown format {fmt!r}")
        self._fmt = fmt

    def describe(self) -> TargetInfo:
        return TargetInfo(
            name=f"printable-{self._fmt}",
            version="1",
            capabilities=frozenset({RENDER}),
        )

    def render(self, assessment: TaxAssessment) -> str:
        return (
            self._render_html(assessment) if self._fmt == "html" else self._render_text(assessment)
        )

    def _bottom_line(self, a: TaxAssessment) -> str:
        return (
            f"Refund: ${a.refund_or_balance}"
            if a.is_refund
            else f"Balance owing: ${-a.refund_or_balance}"
        )

    def _render_text(self, a: TaxAssessment) -> str:
        out = [
            f"{brand.name} — {a.province} T1, tax year {a.tax_year}",
            f"(constants {a.constants_vintage}) — prepared, NOT filed.",
            "-" * 64,
        ]
        for ln in a.lines:
            out.append(f"  {ln.line:<12} {ln.label:<44} ${ln.amount:>12}")
        out.append("-" * 64)
        out.append(f"  {self._bottom_line(a)}")
        if a.diagnostics:
            out.append("")
            out.append("Notes:")
            out.extend(f"  - [{d.severity}] {d.message}" for d in a.diagnostics)
        out.append("")
        out.append("This return was prepared for your review. File it yourself.")
        return "\n".join(out)

    def _render_html(self, a: TaxAssessment) -> str:
        rows = "".join(
            f"<tr><td>{ln.line}</td><td>{ln.label}</td><td class='amt'>${ln.amount}</td></tr>"
            for ln in a.lines
        )
        return (
            f"<section><h2>{brand.name} — {a.province} T1 {a.tax_year}</h2>"
            f"<p>Constants {a.constants_vintage} — prepared, not filed.</p>"
            f"<table>{rows}</table>"
            f"<p class='bottom'>{self._bottom_line(a)}</p></section>"
        )
