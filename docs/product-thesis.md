# Product Thesis (living document)

**One line:** The "counsel-ready, drift-monitored" compliance layer for securities offerings.
Vanta-for-securities-counsel. The product makes an issuer *counsel-ready* and monitors for
*drift*; the lawyer still opines. It assembles and flags. **It never opines.**

> Status: v0.2 (2026-06-29). This is THE goal this repo serves, not a side note. It is a
> living document, meant to be **constantly refined**. See the Self-Refinement Protocol
> directly below. Keep it honest: mark what's conviction vs. open question.

---

## Self-Refinement Protocol (how this doc improves without being asked)

This is the standing instruction, modeled on the repo's Operating Principles (capture the
fix; the goal steers the work). **Any session that does substantive work touching this
repo must, without waiting to be prompted:**

1. **Read this doc first** when the work is product-relevant (CLAUDE.md points here).
2. **Fold new understanding back in proactively.** If research, a data pull, a user remark,
   or an implementation detail sharpens, contradicts, or answers anything here - update the
   relevant section, move items between "open" and "resolved," and **bump the Revision Log**.
   Do this as part of the work, not as a separate chore the user has to request.
3. **Point the research at the open questions.** The autoresearch loop's backlog should be
   derived from this doc's Open Questions and the control-set it needs (bad-actor §506(d),
   §502 conditions, blue-sky, accreditation verification, precedent mining). The loop exists
   to *retire open questions here*, so each pass should generate the next refinement.
4. **Stay honest about confidence.** Tag conviction vs. hypothesis vs. open. Never let the
   doc drift into wishful certainty - same discipline the wiki uses.

> The honest boundary (Operating Principle #3, applied to myself): I do not think between
> sessions. "Without prompting" works because this instruction lives in always-loaded memory
> and future sessions reload it - the persistence is external, not autonomous cognition. It
> fires in sessions that load this repo's memory; merging to `main` makes it canonical
> everywhere. That is the mechanism, stated plainly.

## The positioning (why this is the defensible spot)

Most "AI for law" tries to **replace the authority** (be the lawyer, give the opinion). That
is the malpractice trap and where these products die. This product builds the **layer
underneath the authority**:

- **Vanta** does not replace the auditor. It makes you continuously audit-ready and
  monitored; the CPA still signs.
- **This product** does not replace counsel. It makes you continuously counsel-ready and
  drift-monitored; the lawyer still opines.

The author is the issuer. The authority is counsel. We are the substrate they both stand on.

## The non-negotiable discipline (this is the whole moat's foundation)

A question/output in this system **never resolves to a legal conclusion.** It resolves to one
of three states:

- `satisfied + evidence attached`
- `open`
- `escalate to counsel` (a genuine facts-and-circumstances judgment call)

Never "✅ Compliant" or "Yes, 506(c) is available." Always "9/11 controls evidenced · 2 open ·
1 needs counsel," each with a rule citation and the evidence behind it. The conclusion is
always counsel's. The moment our UI reads as a conclusion, we've stepped into the lawyer's
chair and lost the defensible position.

## The four loops (Vanta's skeleton, securities edition)

1. **Requirement map** - decompose an offering type into a control checklist with rule
   citations (e.g., 506(c) -> accredited verification on every purchaser, Form D in 15 days,
   no Rule 506(d) bad actor, state notice filings, integration analysis). The SEC wiki in
   this repo IS this layer.
2. **Gap check** - current state vs. the map; readiness %. Reconcile the **Form D on EDGAR**
   against the cap table and the PPM. Disclosure-consistency across documents.
3. **Drift monitor** (the subscription engine - a lawyer checks once at closing, we check
   continuously):
   - Exemption drift (506(b) + a public solicitation act blows the exemption)
   - Threshold drift (non-accredited count >35; raise approaching Reg CF $5M / Reg A $75M)
   - Bad-actor drift (Rule 506(d): a new SEC/state order against an officer/director/20%
     holder silently disqualifies the exemption)
   - Deadline drift (Form D 15 days, Form C-AR annual, Reg A ongoing, state blue-sky)
   - Regulatory drift (a rule a *live deal* depends on changed - our autoresearch machine)
4. **Counsel-ready record** - assemble the exemption-analysis memo skeleton: every control,
   its evidence, its citation, open judgment calls flagged. Counsel opines on the residual
   ~10% instead of building the 90%. That billable-hour compression is the sale.

## Architecture (v0.2 - the control model, axes, and drift engine)

### The atom: a Control

A control is one atomic, citable, testable, owned obligation. The count per offering is an
**output of the rule text**, not a choice: for 506(b), decompose 17 CFR 230.501 / 230.502(a-d)
/ 230.503 / 230.506(b)(d)(e) into ~12-18 atoms. (The 8-row demo collapsed several.)

```
Control {
  id
  offering_type            # e.g., "506(b)"
  obligation               # one atomic duty, plain language
  authority {              # POLYMORPHIC - see drift layer C
    type                   # CFR_section | FR_document | release | CDI | no_action_letter
    citation               # e.g., "17 CFR 230.502(c)"
    pinned_version         # eCFR amendment_date or text_hash | FR doc number | release no.
  }
  state                    # satisfied | open | runnable | escalate_to_counsel | n/a
  locus                    # public | private | hybrid
  owner                    # issuer | counsel | system | third_party
  cadence                  # point_in_time | continuous
  severity                 # exemption_fatal | curable_procedural | informational
  evidence[]               # pointers (Form D accession, verification record, board consent)
  drift_conditions[]       # the change(s) that flip this control's state
  last_verified
}
```

### The five axes (a gap is a matrix, not a list)

"Open" is meaningless until tagged. Each control carries all five; useful views are slices:

| Axis | Values | Example slice |
|---|---|---|
| State | satisfied / open / runnable / escalate / n/a | "what still needs evidence?" |
| Locus | public / private / hybrid | "what can we auto-check vs. must the issuer give us?" |
| Owner | issuer / counsel / system / third_party | "what's on the founder's plate this week?" |
| Cadence | point_in_time / continuous | "what do we monitor forever?" |
| Severity | exemption_fatal / curable_procedural / informational | "what could blow the exemption?" |

The high-value default view = `exemption_fatal AND private AND point_in_time AND open` (the
issuer's urgent homework) and `continuous AND public` (what the system watches on its own).

### The three-layer drift engine (verified against live APIs 2026-06-29)

Drift has three sources, matched to where the truth lives:

- **Layer A - Private-state drift** (the *facts* change): new investor, a marketing/solicitation
  act, an officer change, raise-amount change. Source: customer integrations + uploads.
- **Layer B - Public-state drift** (the *world* changes around a fixed fact): a related person
  gets a new SEC order (506(d) bad-actor drift); a conflicting nearby offering appears; Form D
  reconciliation. Source: EDGAR + enforcement/admin-proceeding polling (`sec-fetch.sh`,
  data.sec.gov, getcurrent feeds).
- **Layer C - Regulatory drift** (the *rule itself* moves). Pin each control to its authority +
  version; diff on a schedule; any change -> flag every citing control **stale -> re-verify ->
  escalate to counsel** (NEVER "now non-compliant"). Verified endpoints:
  - **eCFR versioner** - per-section amendment dates:
    `GET https://www.ecfr.gov/api/versioner/v1/versions/title-17.json?part=230`
    (confirmed: §230.506 amendment history `2016-11-21 / 2021-01-14 / 2021-03-15 / 2021-06-09`).
    Pin `{citation, amendment_date, text_hash}`; a new date -> stale flag. ("git for the
    control's legal basis.")
  - **Federal Register API** - the SEC rulemaking pipeline (early warning before codification):
    `GET https://www.federalregister.gov/api/v1/documents.json?conditions[agencies][]=securities-and-exchange-commission&conditions[type][]=RULE`
    (confirmed: 1,020 SEC final rules; surfaced the FDTA final rule).
  - **Autoresearch loop** - the SOFT-LAW watcher. **Critical caveat, with live proof:** a pure
    CFR diff MISSES non-codified authority. The April 2026 tender-offer change came via an
    **exemptive order**, not a CFR amendment; C&DIs, no-action letters, and staff guidance never
    touch the CFR. So `authority.type` must be polymorphic and each type gets its own watcher;
    the autoresearch loop covers orders/guidance/no-action (it already caught that April order).

## The moat questions (public data answers these; a solo human cannot)

- **Bad-actor + rule-change monitoring** - continuous, data-grounded, across a whole client
  book. Grounded in SEC enforcement / administrative-proceeding data + the rule corpus.
- **Precedent benchmarking** - mine *qualified/accepted* filings on EDGAR so an issuer's
  draft is already "market" before counsel sees it ("here's what good looks like").

## Data boundaries (be honest about what we can and can't ground)

- **Public / EDGAR (we have direct access via `scripts/sec-fetch.sh` + data.sec.gov):**
  Form D verification, precedent disclosure mining, bad-actor lookups (enforcement data),
  rule-change monitoring, the rule corpus.
- **Private / internal (customer must provide; not on EDGAR):** cap table, subscription docs,
  accreditation-verification records, board consents, the PPM/deck. Most "counsel-ready"
  evidence is here. The product's integrations live here.
- **Out of scope (don't let the system answer these - they're conclusions or unknowable):**
  "Are we compliant?" (conclusion), "is the exemption available?" (legal conclusion),
  management intent, anything forward-looking.

## How this connects to what's already built in this repo

- The **SEC/EDGAR wiki** (~87 pages, cited, lint-clean) = the **controls framework** / rule
  model. Each concept page (Reg D, Reg A, Rule 144, bad-actor disqualification, Form D, etc.)
  is a candidate control definition.
- **`scripts/sec-fetch.sh` + data.sec.gov** = the **verification / monitoring / precedent**
  layer.
- The **autoresearch loop** = the **regulatory-drift monitor** prototype (it already caught
  the Apr 2026 tender-offer change and the climate-rule rescission).

## Open questions to refine (the point of this being a living doc)

**Resolved in v0.2:**
- ~~Control data model~~ -> defined (the Control atom + five axes).
- ~~Rule-change-monitor mechanism~~ -> defined + endpoints verified (eCFR versioner + Federal
  Register API + autoresearch for soft law; codified-only diff is insufficient).

**Still open:**
- ICP: who is the first buyer - the issuer (founder/CFO) or the law firm itself (a tool that
  makes associates faster)? Different products.
- Wedge offering type: start with Reg D 506(c) (cleanest, highest volume, verification-heavy)?
- Build vs. partner for accreditation verification.
- How to source/normalize the private evidence (integrations vs. upload).
- What's the minimum defensible "counsel-ready package" a lawyer will actually accept?
- Control-set authoring: hand-curate from the wiki, or auto-generate atoms from CFR text then
  human-review? (Likely the latter, with counsel sign-off on the template.)
- Bad-actor matching: how to disambiguate a name hit against enforcement data to an acceptable
  false-positive rate (this is itself an "escalate to counsel," never an auto-conclusion).

## Revision Log

- **v0.2 (2026-06-29):** Added the Architecture (Control atom schema; the five axes -
  state/locus/owner/cadence/severity; the three-layer drift engine). Verified the
  rule-change-monitor endpoints live: eCFR versioner (per-section amendment dates for 17 CFR
  Part 230) and the Federal Register API (SEC rulemaking). Established the polymorphic
  `authority` field and the soft-law caveat (CFR diff alone misses exemptive orders / C&DIs /
  no-action - proven by the Apr 2026 tender-offer order). Added the Self-Refinement Protocol
  so this doc updates itself as a default behavior. Promoted the doc to "THE goal."
- **v0.1 (2026-06-29):** Initial capture from conversation. Positioning (layer underneath
  authority / Vanta-for-counsel), the never-opine discipline, four loops, moat questions,
  data boundaries. Author: issuer; authority: counsel; us: substrate.
