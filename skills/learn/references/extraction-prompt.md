# Extraction Prompt: Walk the Transcript Category-by-Category

Use this framework to review the conversation. It prevents recency bias —
without it, models tend to only capture what happened in the last few turns.

---

## Sweep 1 — Facts and State

Scan the transcript and note anything that looks like a **fact about the user's
life, work, or plans** that isn't already in the wiki.

- Did they mention a new project, side project, or idea?
- Did they share an update on an existing project (progress, blockers, pivots)?
- Did they talk about health (sleep, training, food, substances)?
- Did they mention money, income, spending, business decisions?
- Did they mention creative work, aesthetics, references, inspirations?
- Did they set or revise a goal, deadline, or commitment?

---

## Sweep 2 — People

List every named person mentioned. For each:

- Who are they to the user? (friend, colleague, mentor, client, etc.)
- What context was shared? (owes money, recommended X, collaborating on Y)
- Any follow-up implied? (need to reply, meeting scheduled, etc.)

Cross-check against `wiki/people/_index.md` before adding.

---

## Sweep 3 — Resources

List every tool, book, app, framework, URL, course, or external resource
mentioned. For each:

- What is it?
- Why did it come up? (using it, considering it, recommended by someone)
- Does it belong on `wiki/resources/_index.md`?

---

## Sweep 4 — Learning

Look for "I learned X", "I now understand Y", "it turns out Z", or any concept
the user engaged with seriously.

- Is this a new concept page (`wiki/learning/[concept].md`) or a row in the
  index?
- What's the key insight in one sentence?

---

## Sweep 5 — Reflections

Read emotional tone. Did the user:

- Express frustration, excitement, doubt, clarity?
- Have a realization about themselves or their work?
- Journal-style ramble about where they're at?

These go in `wiki/journal/YYYY-MM-DD — [theme].md`.

---

## Sweep 6 — Preferences

Run the transcript against [preference-patterns.md](preference-patterns.md).
For every match, score confidence. For everything ≥0.60, prepare a queue entry.

---

## Sweep 7 — Decisions and Rationale

Things the user *decided* during the conversation (e.g., "let's go with
approach B", "I'll drop that project"). Decisions shape future work — capture
them with the *why*, not just the outcome.

Decisions about a specific project → append to that project's page.
Cross-cutting decisions → `wiki/journal/`.

---

## Output Format (for your own working memory)

Before writing any files, list the captures you intend to make:

```
CAPTURES:
1. [project] Add new page for "X" — rationale: mentioned side project
2. [person] Update <person>'s row — recommended a book
3. [resource] Add "<book title>" — book, reading now
4. [journal] Create "YYYY-MM-DD — <theme>" — emotional reflection
5. [preference:queue] "No em dashes" (conf 0.90)
```

Then execute them. Having the plan on paper prevents partial captures.
