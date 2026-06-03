"""The CLI demo surface: `northstar-tax assess` prints a computed return."""

from __future__ import annotations

import pytest

from northstar_tax.cli import build_parser


@pytest.mark.functional
def test_assess_command_prints_return(capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "assess",
            "--box14",
            "70000",
            "--box16",
            "3956.75",
            "--box18",
            "1077.48",
            "--box22",
            "12000",
            "--rrsp",
            "5000",
        ]
    )
    assert args.func(args) == 0
    out = capsys.readouterr().out
    assert "Refund: $1985.40" in out
    assert "tax year 2025" in out


@pytest.mark.functional
def test_assess_command_html_format(capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    args = parser.parse_args(["assess", "--box14", "40000", "--box22", "4500", "--format", "html"])
    assert args.func(args) == 0
    assert "<section>" in capsys.readouterr().out
