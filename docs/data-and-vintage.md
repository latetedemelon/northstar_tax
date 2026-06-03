# northstar_tax — tax constants & the vintage discipline

> How the numbers behind the arithmetic — brackets, amounts, rates, limits — are
> sourced, versioned by tax year, and refreshed. This mirrors Northstar's
> treatment of its reference data (the COICOP crosswalks with a CI-gated
> validator) and its benefit-threshold vintage tagging (`THRESHOLDS_VINTAGE` in
> `review.py`). Status: `t0.0` design.

## The core idea: constants are data, pinned to a tax year

A tax return is arithmetic over a large set of jurisdiction-and-year-specific
constants. Get one wrong and the answer is wrong. So we treat them the way
Northstar treats reference data: **as versioned, validated, dated data — never as
magic numbers scattered through the code.**

Each `(jurisdiction, tax_year)` resolves to one immutable `YearConstants` object,
loaded by `constants.load_year(2025, jurisdiction="ca_federal")`. The set
includes, at minimum:

- **Bracket schedule** — thresholds and marginal rates.
- **Basic personal amount** — including the federal BPA's high-income taper
  (it phases from the enhanced to the base amount across the top brackets).
- **Non-refundable credit base amounts** — spouse, age, pension, Canada
  employment, eligible dependant, caregiver, disability, etc.
- **Credit rate** — the lowest-bracket rate non-refundable credits are valued at
  (federal and each provincial equivalent).
- **Indexation factor** — the year's CRA indexation adjustment.
- **Payroll maximums** — CPP/QPP and EI pensionable/insurable maximums, rates,
  and the basic exemption.
- **Provincial specifics** — surtax thresholds/rates (ON, PE), health premium
  (ON), provincial credit amounts and rates, refundable provincial credits.
- **Prescribed rates** — e.g. the per-kilometre vehicle allowance rate.
- **Medical (METC) threshold** — the lesser-of dollar amount and the income
  percentage.

## Sourcing

All constants derive from primary CRA / Department of Finance / provincial
sources, each recorded with a citation in the constant file:

- **CRA** — the federal and provincial tax packages (T1 General + Schedule and
  Form 428 for each province), the annual indexation announcement, and the CPP/EI
  rate notices.
- **Department of Finance Canada** — budget/announcement changes to brackets,
  BPA, and credit rules.
- **Provincial finance ministries / Revenu Québec** — provincial brackets,
  surtaxes, health premiums, and provincial credits.

We use **official figures only**. Third-party summaries (including the reference
products) may inform *what to look for*, but the value committed is always traced
to a primary source cited inline.

## Vintage tagging & reproducibility

- Every `YearConstants` carries a `vintage` string, e.g. `"2025-cra-v1"`. The `v`
  suffix increments if a mid-season correction lands (e.g. a Finance change
  enacted after first publication).
- Every `TaxAssessment` records the exact `constants_vintage` it used. A return
  computed today is reproducible years later, and any constant error is
  traceable to the assessments it touched.
- The engine **refuses years it has no vetted constants for** — it raises
  `ConstantsUnavailable` rather than extrapolating last year's numbers. Indexed
  amounts change every year; guessing is not allowed.

## The annual refresh

Tax constants change every year, on the CRA's calendar, not ours. The refresh is
a bounded, scheduled, reviewed task:

1. New `(jurisdiction, year)` constant files are authored from primary sources,
   each value cited.
2. The **constants validator** (a CI gate, modelled on Northstar's
   `scripts/validate_crosswalks.py`) checks structural integrity: brackets are
   monotonic and contiguous, rates are in `(0, 1)`, no required field is missing,
   indexation is internally consistent, and the federal-BPA taper endpoints line
   up with the top brackets.
3. New golden cases for the year (CRA worked examples / certified-software test
   scenarios) are added and must pass before the year is marked shippable.
4. The year is released; the assessment vintage reflects it.

Because constants are isolated data with a validator and a golden-case gate, the
annual refresh is mechanical and auditable — the same property that makes a
Northstar rebrand a bounded change makes a tax-year roll-forward a bounded change.

## Authoring format (open question, leaning data-file)

Two candidate forms, same as the trade-off Northstar weighed for its crosswalks:

- **Python modules** (`ca_federal_2025.py`) — typed, ergonomic, but values are
  buried in code.
- **Checked-in data files** (TOML/JSON) + a loader + the validator — auditable,
  diff-friendly, reviewable by a non-programmer tax checker, and validated in CI.

We lean toward the **data-file + validator** form for exactly the reasons
Northstar gates its crosswalks that way: a reviewer can read the numbers and their
citations without reading code, and CI enforces structural correctness. Final
decision lands with `t0.1`.

## Relationship to Northstar's benefit thresholds

Northstar's `review.py` already carries approximate, vintage-tagged benefit
*thresholds* (`THRESHOLDS_VINTAGE = "2026-approx"`) used for *flags only*, with
"no dollar calculations in v1." northstar_tax is where those approximate flags
graduate into exact, sourced, on-return figures. The two stay consistent: the tax
module's vetted constants are the authoritative source, and Northstar's flag
thresholds can be derived from them rather than maintained twice.
