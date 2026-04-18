# Preference Detection Patterns

Patterns and heuristics for detecting when the user has expressed a preference,
correction, rule, or style directive worth capturing for `CLAUDE.md`.

Inspired by [claude-reflect](https://github.com/BayramAnnakov/claude-reflect)
but extended with confidence scoring and model-based disambiguation.

---

## Pattern Categories

### 1. Explicit Corrections (confidence 0.90–0.95)

The user tells you something you did was wrong, and what to do instead.

Regex cues:
```
no,?\s+(?:use|do|say|write|it's|that's)\s+...
don't\s+(?:use|do|say|write)\s+...
stop\s+(?:using|doing|saying|writing)\s+...
\bnot\s+(?:that|this),?\s+(?:use|do)\s+...
```

Example triggers:
- "no, use `X` instead"
- "don't add emojis"
- "stop summarizing at the end"
- "not that — call it `Y`"

---

### 2. Absolute Rules (confidence 0.85–0.90)

Declarative rules with absolute quantifiers.

Regex cues:
```
\b(?:always|never)\s+...
\b(?:do not|don't)\s+...
every\s+time\s+you\s+...
```

Example triggers:
- "always spell my brand name lowercase"
- "never commit without running tests"
- "every time you write a project page, include a status field"

---

### 3. Soft Preferences (confidence 0.70–0.80)

Stated preference without absolute language.

Regex cues:
```
I\s+(?:prefer|like|want|expect)\s+...
(?:can you|could you)\s+(?:always|usually)\s+...
I'd\s+rather\s+...
```

Example triggers:
- "I prefer concise responses"
- "can you always link related pages"
- "I'd rather you ask first before creating new sections"

---

### 4. Implicit Signals (confidence 0.60–0.70)

Reaction-based. The user didn't state a rule but expressed displeasure or
approval in a way that implies one.

Cues (no clean regex — model judgment):
- "ugh that's too much"
- "perfect, keep doing that"
- "why did you add X" (implies: don't add X)

Only capture if the signal is unambiguous in context. Prefer to skip than to
over-capture.

---

## Confidence Scoring Rubric

| Confidence | Meaning |
|------------|---------|
| 0.95 | Explicit correction, repeated or emphatic |
| 0.90 | Explicit correction, single occurrence |
| 0.85 | Absolute rule, clearly stated |
| 0.80 | Strong preference with specific scope |
| 0.70 | General preference |
| 0.60 | Inferred from reaction, unambiguous |
| <0.60 | **Skip** — too uncertain to queue |

---

## What NOT to Capture

- One-off decisions for *this* task only (e.g., "let's not touch that file for
  now") — these are task scope, not durable preferences.
- Restatements of things already in `CLAUDE.md` — Grep `CLAUDE.md` first to
  avoid duplicates.
- Your own reasoning dressed as a preference (don't put words in the user's
  mouth).
- Code style preferences that belong in lint config, not `CLAUDE.md`.

---

## Disambiguation

When a statement could be either a one-off or a durable preference, lean toward
**skip**. The queue + review workflow is lossy-safe: a missed preference can be
re-captured next time it comes up. A false-positive preference lives in
`CLAUDE.md` forever and biases every future response.

When confidence is in the 0.60–0.75 range, add a `"note"` field to the queue
entry explaining why you're uncertain, so the user can make the call at review
time.
