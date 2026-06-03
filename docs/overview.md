# northstar_tax — what we're building

> A navigable, plain-language map of the tax module. The detailed engineering
> spec lives in the sibling docs (`architecture.md`, `feature-parity.md`,
> `roadmap.md`, `limitations.md`, `data-and-vintage.md`); this page is the hub
> that ties them together. Last updated: `t0.0` design, June 2026.

## In one sentence

**northstar_tax turns a shoebox of slips into a finished, defensible T1 return —
and then hands you the pen.** It computes a complete Canadian personal income-tax
return (federal + provincial, every common slip, deduction, and credit) with the
same arithmetic CloudTax and Wealthsimple Tax run, but it stops at the moment
before transmission: **it completes the return; it does not file it.**

## Why this module exists

Northstar already gets a user 90% of the way to the door. Its Review layer
(`src/northstar/review.py`) surfaces *eligibility flags* — "you may qualify for
the GST/HST credit; here's the official page" — but, by deliberate design, it
does **no dollar calculations**; the architecture document parks "the full rules
engine with estimates" as a future module (§7.10). `northstar_tax` **is** that
module, scoped to its highest-value instance: the T1 return itself.

The same person Northstar serves — someone facing a blank page, asking "am I
normal?" and "what am I leaving on the table?" — faces the identical wall at tax
time. The incumbents answer it, but they answer it as **filers**: their business
model and their CRA certification are built around pressing *Submit*. That
framing carries baggage Northstar's audience explicitly opted out of when they
chose a self-hosted, open-source, no-telemetry budgeting tool.

## The thesis: complete, don't file

This is the one decision that defines the module, so it leads. (Full treatment in
[`limitations.md`](limitations.md); the short version:)

- **What we do.** Ingest slips and answers, run the full T1 computation for the
  tax year, optimize the splits a couple makes between them, and produce a
  complete return: every line filled, every schedule computed, a plain-language
  explanation of each number, and the bottom line (refund or balance owing).
- **What we don't do.** Transmit to the CRA. No NETFILE, no ReFILE, no Express
  NOA round-trip. The user files the finished return themselves.
- **Why that's coherent, not a cop-out.**
  1. **NETFILE certification is per-build and per-year**, granted by the CRA to a
     specific vendor's specific software release after annual conformance
     testing. A self-hosted, user-modifiable, AGPL codebase that anyone can fork
     and recompile is fundamentally the wrong shape for that certification model.
     Rather than fight it, we design *around* it.
  2. **It keeps the privacy promise whole.** Northstar's pitch is "no telemetry,
     no third-party data sharing." A tool that never transmits your return to
     anyone — not even the CRA, except by your own hand through your own CRA My
     Account — is the strongest possible version of that promise.
  3. **It keeps the advisory boundary clean.** Northstar is careful to be
     "informational, not advisory" (`docs/limitations.md`). "We prepared this;
     you review and file it" is a defensible, honest line. "We filed it for you"
     is not a line a self-hosted open-source project should be standing on.
- **The hand-off is a first-class feature, not an afterthought.** See the Output
  layer below: a clean print/PDF of the return, a structured export, and explicit
  "how to file this" guidance are part of the deliverable.

## Where the feature set comes from

CloudTax and Wealthsimple Tax define the bar for "what a Canadian DIY return must
handle." We take their *coverage* as the target and drop only the *filing* step.
[`feature-parity.md`](feature-parity.md) is the line-by-line map; the headline
groupings:

| Capability group | Examples | Our stance |
|---|---|---|
| **Income slips** | T4, T4A, T4A(P)/CPP, T4A(OAS), T4E, T5, T3, T5008, T5007, T4RSP, T4RIF, T2125, T776 | Core — this is the bulk of a return |
| **Deductions** | RRSP/FHSA, union/professional dues, child care (T778), moving, carrying charges, CCB-clawback items | Core |
| **Non-refundable credits** | BPA, spouse, age, pension, CPP/EI, Canada employment, tuition (T2202), medical, donations, disability (T2201) | Core |
| **Refundable credits / benefits** | GST/HST credit, CWB, CCB, provincial trillium-type credits, climate action | Computed where on-return; flagged where benefit-system-side |
| **Investment / capital** | Capital gains & losses, ACB tracking, loss carryforwards, crypto, foreign income (T1135), foreign tax credit | Core (P1) |
| **Self-employment** | T2125, home-office, vehicle/mileage, CCA | Core (P1) |
| **Optimization** | Spousal/partner credit transfers, pension splitting, donation pooling, RRSP "what-if" | A differentiator we lean into |
| **Convenience** | CRA Auto-fill My Return (AFR) import, AI slip OCR, prior-year returns | Import: yes (read-only). OCR: later. |
| **Filing** | NETFILE, ReFILE, Express NOA | **Out of scope, by design** |
| **Human services** | Expert review, audit protection | Out of scope (not a service business) |

## How it maps onto Northstar's layers

Northstar is organized as nine clean layers (see Northstar `docs/overview.md`).
`northstar_tax` reuses that mental model and the same stage-4 seams (repository +
`tenant_id`, `RequestContext`, `AuthProvider`, `JobQueue`, feature flags). It
adds a tax-specific spine:

| Northstar layer | Tax-module analogue |
|---|---|
| **Data** | Tax-year *constants* (brackets, BPA, credit rates, indexation factors), each tagged with a tax-year vintage — same discipline as the COICOP crosswalks. See [`data-and-vintage.md`](data-and-vintage.md). |
| **Question** | An interview/wizard that gathers residency, marital status, dependants, and which slips apply — detail-gated like the budgeting wizard. |
| **Inference** | Slip ingestion + Auto-fill import: turn raw slips into typed line items. |
| **(Healthcare)** | Folded into the medical-expense credit (METC) rules rather than a separate layer. |
| **Tweaking** | The optimizer: interactive "who claims the kids / how much pension to split / RRSP what-if," with live recompute. |
| **Framework** | The **T1 calculation engine**: a pure, ordered function from `TaxReturnInput` → `TaxAssessment`. This is the heart of the module. |
| **Review** | Diagnostics: missing-slip warnings, "you forgot to claim X," carryforward reminders, sanity checks before hand-off. Mirrors Northstar's Review layer. |
| **Output** | A `TaxReturnTarget` interface (cf. `BudgetTarget`): a printable T1 PDF/HTML, a structured JSON/`.tax`-style export, and "how to file this yourself" guidance. **No transmitter implementation.** |
| **Cross-cutting** | Config, persistence, audit/provenance (every number traceable to its source line and the constant vintage that produced it). |

## What's in scope vs. out (the one-screen version)

**In:** A complete, accurate, explainable T1 for the common-to-moderately-complex
resident filer — employment, investment, retirement, rental, and
self-employment income; the deductions and credits most filers actually use; all
provinces/territories except Quebec's TP1 in the first cycle; couples optimization;
read-only Auto-fill import; prior-year computations for supported years.

**Out:** Filing/transmission of any kind (the thesis). Quebec TP1 in cycle one
(English-Canada T1 first; QC is a sizeable second engine). Corporate (T2) and
trust (T3-as-filer) returns. Non-resident/emigrant edge returns initially. Human
expert review and audit-protection *services* (we are software, not a firm). AI
slip OCR is a convenience deferred behind correct manual + AFR entry.

## Roadmap at a glance

Mirrors Northstar's release cadence; full detail in [`roadmap.md`](roadmap.md).

| Release | What it adds |
|---|---|
| **t0.0 Design** (now) | These documents. No code. |
| **t0.1 Engine core** | Federal T1 + one province (ON), T4-only, BPA + core credits; golden-case tests vs. CRA examples. |
| **t0.2 Slips & credits** | T5/T3/T4A income, RRSP/FHSA, medical, donations, tuition; the interview. |
| **t0.3 Couples & optimization** | Spousal credit transfers, pension splitting, donation pooling. |
| **t0.4 Investments & self-employment** | Capital gains/ACB, T5008, T2125, T776, CCA. |
| **t0.5 Coverage** | Remaining provinces/territories; AFR import; carryforwards. |
| **t0.6 Output & hand-off** | Printable T1 PDF, structured export, "how to file" flow. |
| **t1.0 Full** | Quebec TP1; OCR slip capture; multi-year. |

## Document index

- [`architecture.md`](architecture.md) — domain model, the calculation engine,
  seams, error taxonomy, testing.
- [`feature-parity.md`](feature-parity.md) — the full CloudTax/WS feature matrix.
- [`roadmap.md`](roadmap.md) — phased releases with acceptance criteria.
- [`limitations.md`](limitations.md) — advisory + filing boundaries, NETFILE
  stance, accuracy disclaimers.
- [`data-and-vintage.md`](data-and-vintage.md) — tax-constant sourcing and the
  annual refresh discipline.

## Sources

Feature scope is grounded in the two reference products' own descriptions:

- [Wealthsimple Tax](https://www.wealthsimple.com/en-ca/tax) — auto-fill, NETFILE/RQ
  certification, 400+ credit/deduction search, spousal optimization, audit
  protection tiers.
- [CloudTax](https://www.cloudtax.ca/) and
  [CloudTax Free](https://www.cloudtax.ca/free) — supported income types, AI slip
  extraction, self-employment (T2125), prior-year returns, service tiers.
- [CRA — find certified (NETFILE) software](https://www.canada.ca/en/services/taxes/income-tax/personal-income-tax/how-file/tax-software/find-software.html)
  — the certification model the "don't file" boundary is designed around.
