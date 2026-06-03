# northstar_tax — architecture

> Engineering design for the tax module: the domain model, the pure-function T1
> calculation engine, how it plugs into Northstar's seams, the error taxonomy,
> and the testing strategy. Companion to [`overview.md`](overview.md). Status:
> `t0.0` design — nothing here is built yet; this is the contract the build
> targets.

This document follows Northstar's house conventions deliberately, so a Northstar
contributor finds it familiar:

- **Pure functions and frozen dataclasses** for all domain logic (cf.
  `review.py`, `framework.py`). The calculation engine has no I/O.
- **Every tax constant is tagged with a tax-year vintage** and refreshed
  annually, exactly as the COICOP/benefit thresholds are (cf.
  `THRESHOLDS_VINTAGE` in `review.py`).
- **Stage-4 seams are reused, not reinvented**: repository + `tenant_id`,
  `RequestContext`, `AuthProvider`, `JobQueue`, feature flags.
- **Brand is a variable.** Generated artifacts are named from `brand.slug`
  (e.g. `f"{brand.slug}-t1-2025.pdf"`), never a literal. No brand in any path.

## Packaging & relationship to Northstar

`northstar_tax` is a standalone repository and Python package that depends on
`northstar` as a library (for `config`, `branding`, `db`, `context`, `auth`, and
the infra seams). It does **not** vendor or fork those; it imports them. The
public surface it adds:

```
src/northstar_tax/
  constants/        # tax-year data: brackets, BPA, credit rates, indexation
    __init__.py     # registry: load_year(2025) -> YearConstants (frozen)
    ca_federal_2025.py
    ca_on_2025.py
    ...
  model.py          # domain dataclasses: TaxReturnInput, slips, TaxAssessment
  slips/            # typed slip ingestion (T4, T5, T3, T2125, ...)
  engine/           # the calculation engine (pure)
    federal.py      # ordered T1 federal computation
    provincial/     # one module per province/territory
    credits.py      # non-refundable credit machinery
    optimize.py     # couples/pension-split/donation-pool optimizers
  review.py         # diagnostics & pre-hand-off checks
  targets/          # TaxReturnTarget implementations (PDF/HTML, export)
  interview/        # the question layer (web + state)
```

Why a separate repo (vs. a `src/northstar/tax/` subpackage): tax has a different
release cadence (it is pinned to the CRA's annual cycle, not the budgeting
roadmap), a heavier and more frequently-churning data layer, and a correctness
bar that benefits from its own CI gate and its own golden-case suite. The seam
to Northstar is a normal library dependency, kept narrow.

## The domain model (`model.py`)

All inputs and outputs are immutable. The engine never mutates; it derives.

### Inputs

```python
@dataclass(frozen=True)
class Taxpayer:
    tax_year: int
    province_of_residence: str        # "ON", "BC", ... (Dec 31 residency)
    marital_status: str               # "single", "married", "common_law", ...
    birth_date: date
    is_resident_full_year: bool = True
    dependants: tuple[Dependant, ...] = ()

@dataclass(frozen=True)
class TaxReturnInput:
    taxpayer: Taxpayer
    slips: tuple[Slip, ...]           # T4, T5, T3, T2125, ... (typed below)
    deductions: tuple[Deduction, ...] # RRSP, child care, carrying charges, ...
    credit_claims: tuple[CreditClaim, ...]  # medical, donations, tuition, ...
    carryforwards: Carryforwards = Carryforwards()  # losses, tuition, donations
    partner: "TaxReturnInput | None" = None         # for couple optimization
```

Slips are a closed, typed hierarchy — one frozen dataclass per slip box-set, with
field names that track the CRA box numbers so provenance is auditable:

```python
@dataclass(frozen=True)
class T4(Slip):
    box_14_employment_income: Decimal
    box_16_cpp_contrib: Decimal = Decimal(0)
    box_18_ei_premiums: Decimal = Decimal(0)
    box_22_income_tax_deducted: Decimal = Decimal(0)
    box_44_union_dues: Decimal = Decimal(0)
    box_46_charitable_donations: Decimal = Decimal(0)
    # ... rpp, pension adjustment, etc.
```

**Money is `Decimal`, never `float`.** This is the one hard departure from
Northstar's budgeting code (which uses `float`, because a budget is an estimate).
A tax return is an exact arithmetic artifact; rounding rules are prescribed
(CRA rounds most lines to the nearest dollar at defined points), and `float`
rounding drift is unacceptable. A `Money` newtype wraps `Decimal` with the CRA
rounding helpers (`round_line`, `half_up`).

### Outputs

```python
@dataclass(frozen=True)
class LineResult:
    line: str            # CRA line number, e.g. "30000" (federal BPA)
    label: str
    amount: Money
    explain: str         # plain-language: where this number came from
    sources: tuple[str, ...]  # slip ids / constant vintage that produced it

@dataclass(frozen=True)
class TaxAssessment:
    tax_year: int
    constants_vintage: str            # e.g. "2025-cra-v1"
    total_income: Money               # line 15000
    net_income: Money                 # line 23600
    taxable_income: Money             # line 26000
    federal_tax: Money
    provincial_tax: Money
    total_payable: Money              # line 43500
    total_credits_and_withholding: Money
    refund_or_balance: Money          # +refund / -owing
    lines: tuple[LineResult, ...]     # the full, ordered, explained worksheet
    diagnostics: tuple[Diagnostic, ...]  # from review.py
```

Every assessment is fully **explainable**: `lines` is the ordered worksheet, each
entry carrying its plain-language `explain` string and the `sources` that fed it.
This is what makes "you review it before you file" real — the user can see *why*
every number is what it is.

## The calculation engine (`engine/`)

The engine is one pure function with a strict, documented order of operations
that mirrors the T1 itself:

```python
def assess(input: TaxReturnInput, constants: YearConstants) -> TaxAssessment: ...
```

Ordered stages (each a small pure function; this ordering *is* the T1):

1. **Total income (line 15000).** Sum employment, investment, pension,
   self-employment, capital-gains (taxable half), other income from the slips.
2. **Net income (line 23600).** Apply deductions: RRSP/FHSA, union/professional
   dues, child care (T778), carrying charges, capital/non-capital loss
   application, etc.
3. **Taxable income (line 26000).** Apply division-C deductions.
4. **Federal tax before credits.** Apply the federal bracket schedule from
   `constants`.
5. **Federal non-refundable credits (Schedule 1 logic).** BPA, age, spouse,
   pension, CPP/EI, Canada employment, tuition (current + transferred + carried),
   medical (METC), donations, disability — each computed by `credits.py`, summed,
   multiplied by the lowest-bracket rate, and netted against federal tax.
6. **Provincial tax.** Dispatch to `provincial/<prov>.py`: provincial brackets,
   provincial non-refundable credits (analogous machinery, different rates and
   amounts), surtaxes (ON, PE), health premiums (ON), and provincial refundable
   credits that live on the return.
7. **Other federal items.** CPP on self-employment, EI, the refundable items
   that appear *on* the T1 (e.g. CWB via Schedule 6, climate action where
   applicable), foreign tax credit.
8. **Reconciliation.** Total payable − (withholding from box 22 + instalments +
   refundable credits) = refund or balance owing.

Non-goals of the engine: it does not decide *who* claims what (that is the
optimizer, stage below), it does not do I/O, and it does not know about slips' raw
formats (that is `slips/`). It consumes typed line items and constants and
returns an assessment.

### Constants & vintage (`constants/`)

Each `(jurisdiction, tax_year)` is a frozen `YearConstants` object: bracket
thresholds and rates, the BPA (including the federal BPA's high-income taper),
each credit's base amount and rate, the indexation factor, CPP/EI maximums,
prescribed mileage rates, etc. The registry exposes `load_year(2025)`. Full
sourcing and refresh discipline: [`data-and-vintage.md`](data-and-vintage.md).
The assessment records the exact `constants_vintage` it used, so a return is
reproducible years later.

### The optimizer (`engine/optimize.py`)

This is the layer where we beat a naïve port of the incumbents, and it is pure
"search over assessments":

- **Spousal credit transfers** — assign transferable credits (age, pension,
  disability, tuition) to the partner that minimizes combined tax.
- **Pension income splitting** — solve for the split (0–50%) that minimizes the
  couple's total, respecting eligibility.
- **Donation & medical pooling** — pool to the higher-benefit partner; carry the
  donation portion that crosses the first-tier threshold.
- **RRSP what-if** — marginal-rate readout: "$1,000 more to your RRSP saves
  roughly $X at your bracket."

Each optimizer calls `assess()` repeatedly over candidate allocations and returns
the winning `TaxReturnInput` mutation plus an explanation. Because `assess()` is
pure and fast, brute-force-with-pruning is fine for the small search spaces
involved.

## Slip ingestion (`slips/`)

Three entry paths, all producing the same typed slip objects:

1. **Manual entry** — the interview collects box values; the canonical path.
2. **CRA Auto-fill My Return (AFR) import** — *read-only*. AFR is a download API:
   with the user's authorization it returns the slips the CRA has on file. We
   consume it to pre-fill; we never use it to transmit. This needs CRA
   developer access and is gated behind a feature flag and a clear consent step
   (reuses Northstar's `Consent` model and `AuthProvider`).
3. **OCR / AI slip extraction** — deferred to `t1.0`. When it lands it is a
   pre-fill convenience that always lands the user on an editable, manually
   verifiable slip form; we never file numbers a human hasn't seen.

## Review / diagnostics (`review.py`)

Mirrors Northstar's Review layer in spirit: pure functions producing
informational, non-blocking `Diagnostic` items, e.g.:

- Missing-slip heuristics ("you had a T4 last year from this employer — none this
  year?").
- Unclaimed credits ("you entered medical expenses below the threshold; pooling
  them on your partner may help").
- Carryforward reminders (unused tuition, capital losses, donations).
- Sanity checks (negative income lines, CPP/EI over the annual max, RRSP over
  deduction limit).

Diagnostics never block; they inform the review-before-you-file step.

## Output / hand-off (`targets/`)

A `TaxReturnTarget` interface modelled on Northstar's `BudgetTarget` (interface +
shared conformance suite every implementation must pass). v1 implementations:

- **`PrintableT1`** — a clean, paginated HTML/PDF of the return and its
  worksheets, named `f"{brand.slug}-t1-{year}.pdf"`.
- **`StructuredExport`** — JSON of the full `TaxAssessment` (line-numbered),
  suitable for re-import, archival, or feeding a certified filer.
- **`FilingGuide`** — generated, jurisdiction-aware "how to file this yourself"
  instructions (CRA My Account, paper, or hand-off to a certified product).

There is **no** `NetfileTransmitter` implementation, and the conformance suite
asserts the package ships none. That is the architectural expression of the
thesis: the seam where filing *would* go is intentionally empty.

## Error taxonomy

A small exception hierarchy (cf. Northstar's `budget_targets` error taxonomy):

- `TaxInputError` — malformed/contradictory input (e.g. province not a valid
  code, negative box where impossible). Surfaced in the interview, never reaches
  the engine.
- `UnsupportedSituation` — a case the current release does not model (e.g. Quebec
  TP1 before `t1.0`, non-resident return). Carries a human-readable reason and,
  where possible, a pointer to a product that does handle it. We fail loudly and
  honestly rather than computing a wrong number.
- `ConstantsUnavailable` — no vetted constant set for the requested
  `(jurisdiction, tax_year)`. We never guess constants.

The guiding principle: **a wrong number is worse than an honest "we don't handle
this."** The engine refuses rather than approximates.

## Testing strategy

Three layers, gated like Northstar's harness, but with tax-specific rigor:

- **Unit** — pure-function tests on each engine stage and each credit, including
  property-based tests (monotonicity: more income never decreases tax within a
  bracket; symmetry of couple optimization).
- **Golden-case conformance** — the centrepiece. A corpus of complete returns
  with CRA-published or hand-verified expected line values (drawn from CRA's own
  worked examples, the T1 guide, and certified-software test scenarios). The
  engine must reproduce every line to the cent/dollar per the prescribed
  rounding. Each golden case is pinned to a `constants_vintage`.
- **Functional** — interview → assessment → output round-trips, and the
  `TaxReturnTarget` conformance suite (including the assertion that no
  transmitter exists).

CI gate: the golden-case suite is **red-bar-means-stop**. A change that moves a
golden line without a corresponding, reviewed constant/vintage update fails the
build. Correctness here is not negotiable, because a person is going to file
these numbers.

## Open questions (to resolve before `t0.1`)

- **AFR access**: CRA developer onboarding for a self-hosted tool — feasible for
  individual users, or does it require per-deployment credentials? Affects whether
  AFR is `t0.5` or later.
- **Decimal vs. integer cents** for the `Money` newtype (rounding-point fidelity
  vs. ergonomics).
- **Constant authorship workflow**: hand-curated Python modules vs. a checked-in
  data file + validator (like the COICOP crosswalk validator). Leaning toward the
  latter for auditability.
