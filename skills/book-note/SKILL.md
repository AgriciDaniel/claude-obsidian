---
name: book-note
description: >
  Create or update a RIA-format book note in wiki/books/. Follows the three-section
  RIA structure (Reading / Interpretation / Appropriation). Enforces A-segment
  quality: verb + completion-criterion + deadline. Integrates with Ember agent.
allowed-tools: Read Write Edit Glob Grep
---

# book-note: RIA Book Notes

## Workflow

1. Ask for the book title (if not provided).
2. Check if wiki/books/<Title>.md already exists: read it or create from template.
3. Guide through RIA sections.
4. Validate A-segment: verb + measurable criterion + deadline.
5. Write to wiki/books/<Title>.md.
6. Update wiki/index.md and wiki/log.md.

## A-Segment Validation

Reject: vague ("read more"), missing deadline, missing criterion.
Accept: starts with verb ("Write", "Build"), specific outcome, time boundary.
