---
name: deep-review
description: "Build a rigorously cited, single-page HTML reference document on a scientific, pharmacological or mechanism-heavy topic. Verifies every mechanistic claim against primary literature via web search before writing it, keeps technical vocabulary while glossing it inline, and researches until no further verifiable primary sources turn up rather than stopping at a fixed length. Can start from an existing document, verify and extend it, and add a fast-scan Key Quotes section. Triggers on: deep review, make a review document, research this compound, research this topic in depth, pharmacology review, mechanism review with citations, summarize these studies into a document, build a reference doc, extend this document with more research, add a quotes section, pull key quotes with sources."
---

# deep-review: Cited Mechanism/Pharmacology Reference Documents

Turns a scientific or pharmacological topic — a compound, a receptor system, a
pathway, a comparison of several agents — into a single, self-contained HTML
document at genuine depth, with every non-obvious claim traceable to a real,
checkable source. Not a blog post, not a Wikipedia summary. The test for whether a
claim belongs: *would a specialist reading this nod, or wince?*

`references/template.html` is the starting skeleton for the page itself — copy it,
don't rebuild the CSS from scratch. This file governs the research, writing, and
validation process that fills it in.

Good fits: a single compound or receptor system, a signaling pathway, a comparison of
several related compounds, a disease mechanism, a "state of the evidence" writeup on
a contested question, or extending/re-sourcing a document that already exists. Not a
good fit: news, opinion, anything without a real evidence base, anything where the
point is persuasion rather than explanation.

---

## Default depth: research until exhausted

Unless told otherwise for a specific task, **keep researching and extending the
document until no further verifiable primary sources can be found for the claims in
scope** — not until it "feels long enough." This is the confirmed default. Signs
you've actually hit the ceiling (stop here, don't pad past it):
- New searches return the same handful of papers already cited, or only
  secondary/aggregator restatements of them.
- The remaining candidate claims can't be pinned to a specific, checkable source
  after a reasonable search effort.
- You're reaching for topics increasingly tangential to what was actually asked
  rather than deeper on the same thread.

At that point, say plainly that you've hit the research ceiling rather than quietly
downshifting into weaker or unverified material. If the user then says "continue"
anyway, treat that as their call and keep going on whatever thread is left — don't
re-litigate whether to stop a second time.

---

## 1. Source modes — work out which one you're in

**A — Research from scratch.** The default when the user names a topic without
supplying material. Follow the full research discipline in §2.

**B — User supplies the research**, in any of these forms: papers, notes, a set of
PDFs, a set of URLs, their own draft, **or an existing document — including one
Claude produced in an earlier session.** Read everything provided first. Extract
claims and attribute them to the specific source that made them — don't silently
blend supplied material with anything recalled from training. If a claim seems
wrong, outdated, or unsupported by what they gave you, say so rather than laundering
it into the document uncritically. Independent searches are still fine to fill
genuine gaps or verify a surprising claim — just say when you've done that versus
when a claim comes straight from what was handed to you. **A prior Claude-authored
document is not pre-verified just because Claude wrote it** — an earlier session may
not have followed this skill's research discipline, so re-check its load-bearing
claims the same way you would for anything else in this mode; see §4 for the specific
workflow for extending a ready-made document.

**C — Combined.** User supplies a core (their own research, a draft, a set of
compounds they care about), the skill fills in and verifies around it. Treat the
user's material as the spine; research extends and checks it, not replaces it.

State which mode applies at the start of the work, in one line.

---

## 2. Research discipline (mode A, and the "fill in" half of mode C)

This is what makes the document trustworthy. It is more work than writing what's
already known, and that extra work is the entire point.

- **Never state a specific mechanistic claim (a number, a binding site, a gene name,
  a "study X found Y") from memory alone.** Search for it. Training-data recall of
  specific papers is unreliable — author lists, years, and even findings get
  misremembered or blended with adjacent papers. Confirm before writing it down.
- **Get the real citation**: authors, journal, year, volume/pages where confirmable.
  If a detail (exact page range, a co-author's initials) doesn't surface confidently
  after a reasonable search, **omit it rather than invent it**. A citation with a
  missing page number is honest; a citation with a fabricated one is not.
- **Prefer primary literature over secondary aggregation.** A drug-info site or a
  peptide-vendor blog restating a mechanism is a lead to the real paper, not a
  citable source itself.
- **Chase the surprising claim hardest.** Anything that contradicts the "obvious"
  story (a hormone that *doesn't* correlate with what you'd expect, a mechanism that
  failed to replicate, a drug that worked in theory and killed people in the trial)
  deserves an extra search pass to confirm it's real and not a misread abstract.
- **Batch searches.** Fire multiple `WebSearch` calls in parallel per round rather
  than one at a time — this is a throughput problem, not a reasoning problem.
- **Build in a self-correction pass.** After a section's first draft exists,
  deliberately search for evidence that complicates or contradicts what was just
  written. Some of the most valuable material comes from this pass — a replication
  failure, a corrected mechanism, "more recent work complicates this." Mark
  corrections as corrections; don't quietly rewrite over the original claim.
- **Track every citation number by hand and validate before publishing** — §7.

---

## 3. Document architecture

Reuse this skeleton (see `references/template.html`):

1. **Masthead** — title, one-sentence italic subtitle, a short abstract box
   summarizing the whole argument, a meta row (scope / level / reading time).
2. **Sticky side nav (rail)** — numbered links to every major section.
3. **Lede paragraph** — one sentence per numbered section, so a reader gets the
   whole argument before committing to reading it.
4. **Numbered sections ("Pillars")** — one per major claim or sub-topic, each with a
   kicker label, a large ghost-outline number, and prose broken up by `h3`/`h4`
   sub-headers, callout boxes (§5), compound cards, tables, and inline SVG figures
   only where a diagram genuinely earns its place (§9).
5. **Key Quotes (optional)** — a fast-scan excerpt layer, directly before
   References. Build this when the user wants quick-reference lookup rather than
   (or in addition to) narrative reading. See §4.
6. **References** — numbered in order of first citation, full author list where
   confirmed, with a one-line note on how they were sourced (see the `refs-note`
   pattern in the template: *"Located through targeted literature search rather
   than recalled from general training knowledge."*).
7. **Footer** — one line identifying the document, one line pointing to companion
   volumes if any exist.

Don't force a diagram, a compound-card layout, a Key Quotes section, or a table where
the topic doesn't need one — the skeleton is a toolbox, not a checklist every
document must exhaust.

**When to split into a series instead of one document:** split when the topic has
two or more genuinely distinct sub-systems that don't share much surface area (e.g.
"this hormone's effect on bone" vs "this hormone's effect on muscle receptor
signaling"). Keep it as one document when it's one throughline at increasing depth.
If split: give each volume its own accent color within the shared palette (§8),
cross-link them explicitly in masthead and footer, and keep each volume's lede
paragraph current as sections get added.

---

## 4. Key Quotes section, and extending a ready-made document

### The Key Quotes section

When the goal is quick-reference lookup — the user wants to scan the load-bearing
evidence fast without reading full narrative prose — add a **Key Quotes** section,
placed directly before References so a reader can jump from an excerpt straight to
its full citation.

Format: one short, genuinely verbatim excerpt per entry — a sentence or a key clause
from the source, not a paragraph — immediately followed by a compact byline that
names the source and links to its number in the References list below. See
`references/template.html` for the markup (`.quotes-list` / `.quote-item`).

Rules:
- **Verbatim means verbatim.** Copy the exact wording from the source (title,
  abstract, or body text actually read) — never reconstruct a quote from memory or
  approximate it. If the exact wording can't be confirmed, don't present it as a
  direct quote — paraphrase it in the body prose instead and cite it there.
- **Short.** One sentence or a key clause per entry — long enough to carry the
  finding, short enough to scan in a few seconds. This is an index into the source,
  not a substitute for reading it.
- **Spread across sources, not concentrated in one.** A handful of lines pulled from
  a single paper reads as excerpting that paper at length rather than surveying the
  evidence — cap it at one, or at most a small handful, of the sharpest lines per
  source.
- **Every entry links back to the same numbered reference** used in the main
  bibliography — don't create a second, parallel citation system.
- Order quotes either grouped under the pillar they support, or by citation number —
  pick whichever makes this particular document easier to scan, and be consistent.

### Extending a ready-made document

If the user hands over a document that already exists — their own writing, a paper,
or something Claude produced earlier — this is source mode B (§1) with one extra
step: **verify before you extend.** Re-check the existing document's load-bearing
claims the same way you would for brand-new material (an earlier document, even a
Claude one, may not have followed this discipline). Keep what holds up, flag or fix
what doesn't, then research further per the default-depth rule and add genuinely new
sections/pillars — extending the document rather than starting over. If a Key Quotes
section is wanted and the source document didn't have one, build it from the sources
now verified (existing citations plus anything newly added), following the rules
above.

---

## 5. Callout boxes — pick by function, not aesthetics

- **`.box.mechanism`** (coral) — what's physically/biochemically happening.
- **`.box.evidence`** (accent color) — a specific study's finding, attributed.
- **`.box.update`** (violet) — a correction, or a newer finding that complicates an
  earlier claim in the same document.
- **`.box.plain`** ("in plain terms") — see §6.

---

## 6. The plain-language convention

Keep the real pharmacological/technical vocabulary — don't replace "IGF binding
protein" with a vaguer paraphrase — but make sure a non-specialist reader isn't lost
by it.

**Rule: gloss on first use, in the same sentence, then use the real term freely
afterward.**

> **IGF binding proteins (IGFBPs)** — a family of carrier proteins that latch onto
> circulating IGF-1 and hold it in reserve rather than letting it act immediately —
> sequester, transport, and protect IGF-1 in blood and tissue...

Not a separate glossary the reader has to break flow to consult. Not replacing the
term with something vaguer and never giving the real name — that fails the "keep the
vocabulary" half just as much as an unglossed jargon dump fails the "explain it"
half.

For a passage that's dense even with individual terms glossed (a multi-step
mechanism, several acronyms in one paragraph), use a `.box.plain` ("in plain terms")
aside directly under the technical paragraph, restating the mechanism's shape in one
or two sentences without the jargon. Keep it short — a handhold, not a rewrite. Never
simplify by omitting the mechanism; "in plain terms" means fewer unexplained nouns,
not less content.

---

## 7. Pre-publish validation checklist

Run before every publish/republish, not just once at the end — each edit is a chance
to introduce a mismatched tag or a citation typo.

1. **Tag balance** — count open vs. close tags for every tag type used (`em`, `b`,
   `i`, `sup`, `p`, `div`, `section`, `table`, etc.) with a quick Python
   `re.findall` pass on the saved file. (Note: a naive regex also matches example
   tags written out inside HTML comments — if a mismatch traces to a comment, that's
   a false positive, not a bug; confirm with `grep -n` before "fixing" anything.)
2. **Citation ↔ reference consistency** — every `[n]` used in the body must have a
   matching numbered reference, and every reference should either be cited at least
   once or be explicitly flagged in the references intro as general/background
   reading.
3. **Quote accuracy** — if a Key Quotes section exists, spot-check that each excerpt
   matches the source's actual wording rather than a paraphrase that drifted into
   quotation marks.
4. **No stray characters** — check for zero-width spaces and other invisible
   characters that sneak in from copy-paste; they silently break tags like
   `</em​>`.
5. **One visual look, not zero** — on first publish, take the one permitted look at
   the rendered page; spend it checking layout and diagrams, not re-reading prose
   already written carefully.

---

## 8. Design system

Full CSS lives in `references/template.html` — copy it, then only change the accent
color block when starting a new topic/volume. Don't redesign the type system or
spacing per document; consistency across documents built with this skill is part of
what makes the format recognizable.

- **Typefaces**: STIX Two Text (body — scientific-journal serif, handles italic gene
  names cleanly), Archivo (headings/nav/labels), IBM Plex Mono (data, units, section
  numbers, gene/protein symbols in tables).
- **Fixed color roles** (same meaning in every document): `--coral` = active local
  signaling / key mechanism emphasis; `--violet` = receptor biology, transcriptional
  machinery, and corrections. The one swappable value is `--accent` — pick something
  grounded in the subject's own material (a histology stain, a real convention from
  that field), not a generic brand color.
- Gene symbols italic, protein/receptor names upright. Tabular numerals wherever
  digits line up in a column. Section numbers as two-digit mono — real structure (an
  actual sequence), not decoration; don't number something that isn't a sequence.
- Body copy max-width ~68ch, never full-bleed. `overflow-x: auto` on wide-content
  wrappers, never on the page body. Full light/dark token coverage — never a color
  defined for only one theme.
- The Key Quotes markup (`.quotes-list` / `.quote-item`) uses these same tokens —
  don't introduce a new color for it.

---

## 9. Diagrams

Hand-authored inline SVG only — no chart libraries, no external images, no photos.
One figure = one claim. Draw one only when it shows a mechanism a reader would
otherwise have to assemble from prose (a receptor conformational change, a branching
pathway, a before/after comparison). If a sentence says it as fast, skip it.

- `viewBox` sized to content, not a fixed preset.
- Strokes/text in `currentColor` by default; reserve accent colors for the one
  element that carries meaning.
- Arrowheads via `<marker>`, never an image.
- Legible label size (~11–13px at drawn scale); explanatory sentences belong in the
  `<figcaption>`, not crammed into the drawing.
- Every figure wrapped in `<figure>` with a `<figcaption>` stating the one claim, and
  `role="img"` + `aria-label` on the `<svg>` carrying the same claim.

---

## 10. Tone and scope guardrails

- **Mechanistic, not instructive.** Explain how something works and what the
  evidence shows. Never drift into dosing guidance, "how to use," stacking advice, or
  anything read naturally as encouragement to use a controlled or dangerous
  substance — regardless of how technical or "just science" the framing feels. The
  register should read like an endocrinology/pharmacology textbook throughout, even
  when covering compounds that are also used non-medically in practice. Reporting an
  actual clinical trial's dosing arm as part of describing what the study did (e.g.
  "letrozole 2.5mg daily" in a trial summary) is fine; a dosing *recommendation* is
  not — keep that line explicit.
- **State uncertainty as uncertainty.** "One study found X; a later, larger study
  found a smaller effect" is more useful and more honest than picking the version
  that makes a cleaner narrative.
- **Say when a claim is an inference, not a citation.** ("The mechanism predicts X;
  no study has directly measured it" is a real, useful sentence.)
- **Never fabricate a citation detail to fill a gap.** Missing is fine; wrong is not.
- **Quote sparingly and accurately (§4).** Short, verbatim, attributed, spread across
  many sources — never long excerpts from a single copyrighted work.

---

## 11. Quick-start

1. Copy `references/template.html` to a new working file, pick a title (short noun
   phrase, 2–4 words, no appended explainer — match a "The ___ ___" pattern if it's
   part of a series).
2. Pick the subject-grounded accent color (§8) and swap the CSS custom properties.
3. State the source mode (§1) and, if mode A/C, start the research pass (§2) before
   writing final prose — build the reference list's spine first, then write into it.
   If mode B is a ready-made document, verify it first (§4) before extending it.
4. Build section by section using the architecture in §3, glossing terms per §6.
5. Add diagrams only where §9's test is met; add a Key Quotes section (§4) only if
   quick-reference lookup is actually the goal.
6. Run the validation checklist (§7) before every publish.
7. Keep researching per the default in the opening section until the ceiling is
   actually hit, not until the document "feels done."
8. If part of a series, cross-link companion volumes in masthead and footer, and
   keep the lede paragraph's section list current as sections get added.
9. Publish via the `Artifact` tool (or save as a local file if the user prefers
   that instead) — either way, hand the user the finished, working document, not a
   description of what it would contain.
