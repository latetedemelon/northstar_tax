# northstar_tax — limitations & boundaries

> The honest edges of the tool. Modelled on Northstar's `docs/limitations.md` and
> its "informational, not advisory" stance. Two boundaries define this module:
> the **filing boundary** (we complete, you file) and the **advisory boundary**
> (we compute, we don't advise). Status: `t0.0` design.

## The filing boundary: we complete, we do not file

This is the defining decision of the module, so it is stated plainly and
defended.

**northstar_tax prepares a complete T1 return and stops.** It does not transmit
anything to the Canada Revenue Agency. There is no NETFILE, no ReFILE, no Express
NOA, no EFILE. You take the finished return — printable PDF, structured export,
and step-by-step filing instructions — and file it yourself.

Why this is a deliberate design, not a missing feature:

1. **NETFILE certification is structurally incompatible with us.** The CRA
   certifies a *specific vendor's specific software build* for a *specific tax
   year*, after annual conformance testing, and re-certifies every year. A
   self-hosted, open-source (AGPL) tool that any user can fork, modify, and
   recompile cannot meaningfully be "the certified build." Rather than
   compromise the open-source, self-hosted model to chase a certification that
   doesn't fit it, we design the product around *not* transmitting.

2. **It is the strongest form of Northstar's privacy promise.** Northstar's
   defining claims are "self-hosted, no telemetry, no third-party data sharing."
   Your tax return is the most sensitive financial document you own. A tool that
   never sends it anywhere — not to us, not to a SaaS, not even to the CRA except
   by your own hand through your own CRA My Account — is the most private design
   available.

3. **It keeps the advisory boundary clean.** "We prepared this return; review it
   and file it" is an honest, defensible position. "We filed your taxes for you"
   carries representations a volunteer/open-source project should not be making.

4. **The hand-off is first-class.** The finished return is fully explained,
   line-numbered, and accompanied by jurisdiction-aware filing instructions. We
   invest in making *you filing it* easy, rather than hiding the return behind a
   Submit button.

What this means in practice: you can file the prepared return through CRA My
Account (entering the figures or following the guide), on paper, or by importing
the structured export into a NETFILE-certified product to transmit. The
arithmetic is done; only the transmission is yours.

## The advisory boundary: computation, not advice

northstar_tax computes a tax return from the inputs you give it and the published
rules for the year. It is **not** a tax advisor, accountant, or preparer.

- The output is a **computed return for you to review**, not professional advice
  and not a guarantee of CRA assessment.
- It does not make planning recommendations beyond the explicit, transparent
  optimizers (credit transfer, pension splitting, pooling, RRSP what-if), each of
  which shows its arithmetic.
- For complex, contested, or high-stakes situations, consult a CPA or tax lawyer.
  The structured export (every line with its provenance) is designed to hand
  cleanly to such an advisor.

## Accuracy, garbage-in, and the "refuse rather than approximate" rule

- **Garbage in, garbage out.** The return is only as correct as the slips and
  answers entered. The Review diagnostics catch common omissions and
  inconsistencies, but cannot know about income or facts you never entered.
- **We refuse rather than approximate.** For any `(jurisdiction, tax_year)` we do
  not have a vetted, vintage-tagged constant set, the engine raises
  `ConstantsUnavailable` rather than guessing. For situations a release does not
  model, it raises `UnsupportedSituation` with a clear reason. A wrong number is
  worse than an honest "we don't handle this."
- **Constants are pinned and dated.** Every assessment records the exact
  `constants_vintage` used, so it is reproducible — and so a constant error is
  traceable and correctable. See [`data-and-vintage.md`](data-and-vintage.md).

## Out of scope (and why)

- **Filing/transmission** — by design; see above.
- **Quebec TP1** before `t1.0` — Quebec's separate provincial return is a second
  full engine; English-Canada T1 ships first. The engine refuses QC residency
  until then rather than producing a federal-only half-answer.
- **Corporate (T2) and trust-as-filer (T3) returns** — this is a *personal* (T1)
  module. (We *consume* T3 slips as income; we do not file the trust's return.)
- **Non-resident / emigrant / newcomer part-year edge returns** — initially out;
  these carry significant special rules. Refused honestly until modelled.
- **Human services** — expert review, audit representation, live support. We are
  software, not a firm. We do provide a full provenance/audit-trail export for
  your own advisor.
- **Brokerage/issuer auto-import** — we have no financial-institution
  relationship, so we cannot pull an issuer's own slips the way a bank-affiliated
  product can. (Read-only CRA Auto-fill import is the substitute, if feasible.)

## Things that will never change

- No transmission to the CRA. The filing seam is intentionally, and *testably*,
  empty.
- No telemetry, no third-party data sharing — inherited from Northstar.
- The engine never guesses a tax constant and never silently approximates an
  unmodelled situation.
