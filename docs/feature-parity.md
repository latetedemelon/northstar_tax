# northstar_tax — feature parity with CloudTax & Wealthsimple Tax

> The line-by-line map. We take CloudTax and Wealthsimple Tax as the definition of
> "what a Canadian DIY personal return must handle," and commit to which tier each
> capability lands in — **minus filing, which is out by design.** Status: `t0.0`
> scope. Grounded in the products' own published feature descriptions (sourced at
> the foot of [`overview.md`](overview.md)).

## Coverage tiers

| Tier | Meaning |
|---|---|
| **P0** | First engine release (`t0.1`). The skeleton that proves the arithmetic. |
| **P1** | Core parity (`t0.2`–`t0.4`). The return a typical filer actually needs. |
| **P2** | Full coverage (`t0.5`–`t1.0`). Breadth, convenience, edge cases. |
| **Out** | Deliberately not built. Reason given. |

A capability being "Out" is a *decision*, not a backlog gap — see the reasons.

## Income slips & income types

| Capability | CloudTax | WS Tax | northstar_tax | Tier |
|---|:--:|:--:|---|:--:|
| T4 employment | ✓ | ✓ | ✓ | P0 |
| T4A (pension, other) | ✓ | ✓ | ✓ | P1 |
| T4A(P) CPP / T4A(OAS) | ✓ | ✓ | ✓ | P1 |
| T4E (EI) | ✓ | ✓ | ✓ | P1 |
| T4RSP / T4RIF | ✓ | ✓ | ✓ | P1 |
| T5 investment income | ✓ | ✓ | ✓ | P1 |
| T3 trust income | ✓ | ✓ | ✓ | P1 |
| T5008 securities | ✓ | ✓ | ✓ | P1 |
| T5007 social assistance / WCB | ✓ | ✓ | ✓ | P1 |
| T2125 self-employment / gig | ✓ | ✓ | ✓ | P1 |
| T776 rental income | ✓ | ✓ | ✓ | P1 |
| Capital gains/losses + ACB | ✓ | ✓ | ✓ | P1 |
| Cryptocurrency gains | ✓ | ✓ | ✓ (as capital/business gains) | P1 |
| Foreign income + FTC | ✓ | ✓ | ✓ | P1 |
| T1135 foreign property reporting | ✓ | ✓ | ✓ (computed; user files) | P2 |
| Scholarships / bursaries (T4A box 105) | ✓ | ✓ | ✓ | P1 |

## Deductions

| Capability | CloudTax | WS Tax | northstar_tax | Tier |
|---|:--:|:--:|---|:--:|
| RRSP contributions | ✓ | ✓ | ✓ | P1 |
| FHSA contributions | ✓ | ✓ | ✓ | P1 |
| Union / professional dues | ✓ | ✓ | ✓ | P1 |
| Child care expenses (T778) | ✓ | ✓ | ✓ | P1 |
| Carrying charges / investment expenses | ✓ | ✓ | ✓ | P1 |
| Moving expenses | ✓ | ✓ | ✓ | P2 |
| Home-office (employment, T2200) | ✓ | ✓ | ✓ | P2 |
| Self-employment expenses (incl. CCA, vehicle, mileage) | ✓ | ✓ | ✓ | P1 |
| Capital / non-capital loss carryforwards | ✓ | ✓ | ✓ | P2 |

## Non-refundable credits

| Capability | CloudTax | WS Tax | northstar_tax | Tier |
|---|:--:|:--:|---|:--:|
| Basic personal amount (incl. federal taper) | ✓ | ✓ | ✓ | P0 |
| Spouse / common-law partner amount | ✓ | ✓ | ✓ | P0 |
| Eligible dependant amount | ✓ | ✓ | ✓ | P1 |
| Age amount | ✓ | ✓ | ✓ | P1 |
| Pension income amount | ✓ | ✓ | ✓ | P1 |
| CPP/QPP & EI contributions | ✓ | ✓ | ✓ | P0 |
| Canada employment amount | ✓ | ✓ | ✓ | P0 |
| Tuition (T2202) + transfer + carryforward | ✓ | ✓ | ✓ | P1 |
| Student-loan interest | ✓ | ✓ | ✓ | P2 |
| Medical expenses (METC) | ✓ | ✓ | ✓ | P1 |
| Charitable donations (+ pooling/carry) | ✓ | ✓ | ✓ | P1 |
| Disability amount (T2201) + transfer | ✓ | ✓ | ✓ | P2 |
| Canada caregiver amount | ✓ | ✓ | ✓ | P2 |

## Refundable credits & benefits

| Capability | CloudTax | WS Tax | northstar_tax | Tier |
|---|:--:|:--:|---|:--:|
| Canada Workers Benefit (Sch. 6, on-return) | ✓ | ✓ | ✓ | P2 |
| GST/HST credit | ✓ (auto-determined) | ✓ | ✓ (eligibility + estimate) | P2 |
| Canada Child Benefit | ✓ | ✓ | Estimate + flag (benefit-side, not on T1) | P2 |
| Climate Action Incentive (where applicable) | ✓ | ✓ | ✓ | P2 |
| Provincial trillium-type / refundable credits | ✓ | ✓ | ✓ | P2 |

> Note: GST/HST credit, CCB, and similar are *benefit-system* outputs the CRA
> computes from the filed return, not lines the taxpayer remits on the T1. We
> compute estimates and surface them (extending Northstar's existing
> `review.benefit_flags` from flags to figures), clearly labelled as estimates.

## Provincial / territorial

| Capability | CloudTax | WS Tax | northstar_tax | Tier |
|---|:--:|:--:|---|:--:|
| Ontario (incl. surtax, health premium) | ✓ | ✓ | ✓ | P0 (ON is first) |
| BC, AB, MB, SK | ✓ | ✓ | ✓ | P1 |
| Atlantic provinces + territories | ✓ | ✓ | ✓ | P2 |
| Quebec **TP1** (separate provincial return) | ✓ (Basic/Plus) | ✓ (Basic/Plus) | ✓ | t1.0 |
| Provincial-specific credits (e.g. ON trillium, BC climate) | ✓ | ✓ | ✓ | P2 |

## Optimization (where we lean in)

| Capability | CloudTax | WS Tax | northstar_tax | Tier |
|---|:--:|:--:|---|:--:|
| Spousal/partner credit transfer optimization | ✓ | ✓ ("who should claim what") | ✓ | P1 |
| Pension income splitting | ✓ | ✓ | ✓ | P1 |
| Donation / medical pooling | ✓ | ✓ | ✓ | P1 |
| RRSP "what-if" / marginal-rate readout | partial | partial | ✓ (first-class) | P1 |
| Credit/deduction completeness search ("400+") | ✓ | ✓ | ✓ (rule-driven diagnostics) | P1 |

## Convenience & data import

| Capability | CloudTax | WS Tax | northstar_tax | Tier |
|---|:--:|:--:|---|:--:|
| CRA Auto-fill My Return (read-only import) | ✓ | ✓ | ✓ (consent-gated, read-only) | P2 |
| Revenu Québec auto-fill | ✓ | ✓ | with Quebec (t1.0) | t1.0 |
| AI / OCR slip extraction from photos/PDFs | ✓ | — | ✓ (deferred convenience) | t1.0 |
| Prior-year returns | ✓ (2018–) | ✓ | ✓ (per available constant vintages) | P2 |
| Auto-import of issuer's own slips (WS clients) | — | ✓ | n/a (no brokerage relationship) | Out |

## Filing & transmission — **out by design**

| Capability | CloudTax | WS Tax | northstar_tax | Reason |
|---|:--:|:--:|---|---|
| NETFILE transmission | ✓ | ✓ | **Out** | Per-build/per-year CRA certification is incompatible with a self-hosted, forkable AGPL build. See [`limitations.md`](limitations.md). |
| ReFILE (amend a filed return) | ✓ | ✓ | **Out** | Depends on NETFILE. We support recomputing; the user re-files. |
| Express NOA | ✓ | ✓ | **Out** | A NETFILE round-trip feature. |
| EFILE (preparer filing on behalf) | — | — | **Out** | We are not a preparer/firm. |

We replace this column with a **FilingGuide**: a clean printable return + a
structured export + jurisdiction-aware instructions for the user to file through
their own CRA My Account, on paper, or by importing into a certified product.

## Human services — out (we are software, not a firm)

| Capability | CloudTax | WS Tax | northstar_tax | Reason |
|---|:--:|:--:|---|---|
| Expert/CPA review & preparation tier | ✓ (Pro) | ✓ (Pro) | **Out** | Not a service business; no humans in the loop. |
| Audit protection / representation | ✓ | ✓ | **Out** | Same. We do provide an audit-trail export (every line's provenance) the user can hand to their own advisor. |
| Priority live chat / phone support | ✓ | ✓ | **Out** | Self-hosted OSS; community support only. |

## Net read

We commit to **the full return-preparation surface** of both products — slips,
deductions, credits, provinces, investment and self-employment income, and
couple-level optimization — and intentionally drop **only the two things that
make them businesses rather than calculators**: transmission to the CRA, and
paid human services. That subtraction is the product, not a shortfall.
