# northstar_tax

> Prepare a complete, defensible Canadian personal income-tax return. Review it.
> File it yourself.

`northstar_tax` is a companion module to **[Northstar](https://github.com/latetedemelon/northstar)**
— the demographic-anchored budgeting tool. Where Northstar's Review layer today
only *flags* the benefits and credits you might qualify for (with links to the
official pages, no dollar figures), `northstar_tax` does the arithmetic: it
prepares a full T1 General return — every relevant slip, deduction, and credit,
federal plus provincial — and tells you the number.

It deliberately stops one step short of the products it draws its feature set
from (CloudTax, Wealthsimple Tax): **it completes the return but does not file
it.** No NETFILE transmission. You review the finished return and file it
yourself through CRA My Account, by exporting to a certified filer, or on paper.
See [`docs/limitations.md`](docs/limitations.md) for why that boundary is a
feature, not a gap.

**Status:** `t0.1` — the first runnable slice. A pure-function T1 engine computes a
complete **federal + Ontario, 2025, T4-only** return (CPP base/enhanced split, the
14.5% federal credit rate, BPA taper, Ontario surtax and health premium), with
golden-case tests verified to the cent against Form ON428. Two demo surfaces: a
`northstar-tax` CLI and a one-page web form. The phased roadmap to full coverage
is in [`docs/roadmap.md`](docs/roadmap.md).

**License:** AGPL-3.0-only, matching Northstar.

## Run the demo

```bash
uv sync --all-extras

# CLI: print a computed return
uv run northstar-tax assess --box14 70000 --box16 3956.75 --box18 1077.48 \
  --box22 12000 --rrsp 5000

# Web: a one-page T4 form -> computed return
uv run northstar-tax serve            # then open http://127.0.0.1:8000

# Quality gates
uv run ruff check . && uv run mypy
uv run python scripts/validate_constants.py
uv run pytest
```

---

## Start here

- **[`docs/overview.md`](docs/overview.md)** — what we're building, the
  "complete-but-don't-file" thesis, and how it maps onto Northstar's layers.
- [`docs/feature-parity.md`](docs/feature-parity.md) — the CloudTax /
  Wealthsimple Tax feature set, mapped item-by-item to our coverage tiers.
- [`docs/architecture.md`](docs/architecture.md) — domain model, the pure-function
  T1 calculation engine, data/vintage strategy, seams, and testing approach.
- [`docs/roadmap.md`](docs/roadmap.md) — the phased releases (`t0.1` → `t1.0`).
- [`docs/limitations.md`](docs/limitations.md) — the advisory and filing
  boundaries, NETFILE stance, and what we will never do.
- [`docs/data-and-vintage.md`](docs/data-and-vintage.md) — how tax constants are
  sourced, versioned by tax year, and refreshed annually.

---

© Bayview Industries Ltd.
