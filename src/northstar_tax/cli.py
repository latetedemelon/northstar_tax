"""CLI entry point (installed as ``northstar-tax``).

``northstar-tax assess ...`` prints a computed return; ``northstar-tax serve``
boots the one-page web demo."""

from __future__ import annotations

import argparse
import sys

from northstar_tax.branding import brand
from northstar_tax.engine import assess
from northstar_tax.model import T4, Taxpayer, TaxReturnInput
from northstar_tax.money import money
from northstar_tax.targets.printable import PrintableSummary


def _build_input(args: argparse.Namespace) -> TaxReturnInput:
    t4 = T4(
        box_14_employment_income=money(args.box14),
        box_16_cpp_contrib=money(args.box16),
        box_18_ei_premiums=money(args.box18),
        box_22_income_tax_deducted=money(args.box22),
        employer=args.employer,
    )
    taxpayer = Taxpayer(
        tax_year=args.year,
        province_of_residence=args.province,
        rrsp_deduction=money(args.rrsp),
    )
    return TaxReturnInput(taxpayer=taxpayer, t4s=(t4,))


def _cmd_assess(args: argparse.Namespace) -> int:
    assessment = assess(_build_input(args))
    print(PrintableSummary(fmt=args.format).render(assessment))
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run("northstar_tax.main:app", host=args.host, port=args.port, reload=False)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=brand.slug, description=brand.tagline)
    sub = parser.add_subparsers(dest="command")

    a = sub.add_parser("assess", help="compute a return from T4 inputs and print it")
    a.add_argument("--box14", required=True, help="employment income (T4 box 14)")
    a.add_argument("--box16", default="0", help="CPP contributions (box 16)")
    a.add_argument("--box18", default="0", help="EI premiums (box 18)")
    a.add_argument("--box22", default="0", help="income tax deducted (box 22)")
    a.add_argument("--rrsp", default="0", help="RRSP deduction (line 20800)")
    a.add_argument("--year", type=int, default=2025)
    a.add_argument("--province", default="ON")
    a.add_argument("--employer", default="")
    a.add_argument("--format", choices=("text", "html"), default="text")
    a.set_defaults(func=_cmd_assess)

    s = sub.add_parser("serve", help="run the one-page web demo")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.set_defaults(func=_cmd_serve)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, "command", None):
        parser.print_help()
        raise SystemExit(0)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    sys.exit(0)
