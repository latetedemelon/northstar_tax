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

**Status:** `t0.0` — design only. This repository currently contains the
architecture and scope documents; no calculation code has been written yet. The
implementation roadmap is in [`docs/roadmap.md`](docs/roadmap.md).

**License:** AGPL-3.0-only, matching Northstar.

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
