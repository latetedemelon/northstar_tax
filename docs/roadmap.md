# northstar_tax — roadmap

> Phased releases, each with a clear "done when" gate. Mirrors Northstar's
> release cadence and its red-bar-means-stop discipline. Versions are `tN.M`
> (the `t` distinguishes the tax module's CRA-pinned cycle from Northstar's
> budgeting releases). Status: `t0.0` design.

The ordering principle: **prove the arithmetic on the narrowest real return
first, then widen.** Every release ends green on the golden-case conformance
suite ([`architecture.md`](architecture.md) → Testing).

## t0.0 — Design (this release)

The documents in this repo. No code.

**Done when:** scope, architecture, feature map, and boundaries are reviewed and
agreed. ✅ (this PR)

## t0.1 — Engine core

The thinnest end-to-end T1 that produces a correct number.

- `Money`/`Decimal` foundation and CRA rounding helpers.
- Federal computation: total → net → taxable income, federal brackets.
- Ontario only, with surtax and health premium.
- Credits: BPA (with federal taper), spouse amount, CPP/EI, Canada employment.
- Income: T4 only.
- `TaxAssessment` with fully line-numbered, explained worksheet output.

**Done when:** a single-T4 Ontario return reproduces every line of a set of
hand-verified / CRA-example golden cases to the prescribed rounding.

## t0.2 — Slips & credits

The credits and income types most filers actually have.

- Income: T5, T3, T4A, T4A(P)/(OAS), T4E, T4RSP/RIF, T5007.
- Deductions: RRSP, FHSA, union/professional dues, child care (T778), carrying
  charges.
- Credits: age, pension, eligible-dependant, tuition (T2202, current +
  carryforward), medical (METC), donations.
- The interview (Question layer): residency, marital status, dependants,
  slip-applicability gating.

**Done when:** a moderately complex single-filer return (multiple slips, RRSP,
medical, donations, tuition) is golden-green.

## t0.3 — Couples & optimization

The differentiator.

- Partner-linked returns.
- Optimizers: spousal credit transfers, pension income splitting, donation &
  medical pooling, RRSP what-if / marginal-rate readout.
- Review diagnostics: unclaimed-credit and pooling suggestions.

**Done when:** for a couple golden case, the optimizer's allocation provably
minimizes combined tax (verified against an exhaustive search in tests), and the
suggestions are explained.

## t0.4 — Investments & self-employment

- Capital gains/losses with ACB tracking; T5008.
- Crypto gains (capital vs. business characterization prompt).
- Foreign income + foreign tax credit; T1135 computation.
- Self-employment: T2125 with expenses, CCA, vehicle/mileage; rental T776.

**Done when:** investment and self-employment golden cases (including
loss-carryforward application) are green.

## t0.5 — Coverage

Breadth and import.

- Remaining provinces/territories (all except Quebec).
- Provincial-specific credits (trillium-type, climate, etc.).
- Carryforward engine (tuition, capital/non-capital losses, donations) across
  years.
- CRA Auto-fill My Return (read-only, consent-gated) — *if* CRA developer access
  is feasible for the self-hosted model (open question in `architecture.md`);
  otherwise slips remain manual + structured import.

**Done when:** every non-Quebec province has a golden case; AFR import (if
shipped) round-trips into editable, verifiable slip forms.

## t0.6 — Output & hand-off

The "complete, don't file" promise made tangible.

- `PrintableT1` PDF/HTML of the return + worksheets (`f"{brand.slug}-t1-{year}"`).
- `StructuredExport` JSON of the full assessment.
- `FilingGuide`: jurisdiction-aware "how to file this yourself" instructions
  (CRA My Account, paper, or hand-off to a certified product).
- `TaxReturnTarget` conformance suite, including the assertion that **no
  transmitter ships**.

**Done when:** a user can take the generated artifacts and file the return
themselves with no further computation, and the conformance suite passes.

## t1.0 — Full

- Quebec **TP1** (the second provincial engine) + Revenu Québec auto-fill.
- OCR / AI slip extraction (always landing on an editable, verifiable form).
- Multi-year support across all available constant vintages.

**Done when:** Quebec golden cases are green and the module covers the full
feature-parity matrix's in-scope rows.

## Standing gates (every release)

- Golden-case conformance is **red-bar-means-stop**. No line moves without a
  reviewed constant/vintage change.
- Every shipped tax year has a vetted, vintage-tagged constant set
  ([`data-and-vintage.md`](data-and-vintage.md)); the engine refuses years it
  has no constants for rather than guessing.
- No `NetfileTransmitter`, ever. The empty filing seam is a tested invariant.
