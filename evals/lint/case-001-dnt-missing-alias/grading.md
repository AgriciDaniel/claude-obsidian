# Grading — case-001-dnt-missing-alias

Fully deterministic. The runner handles this case automatically.

## Expected output

Two findings:
- **ERROR missing-alias** on `concepts/AGB.md` (only 1 alias, needs ≥ 2)
- **WARN termbase-drift** on `concepts/Vorstand.md` (DNT but not in termbase index)

## Should NOT emit

- Any finding on `concepts/AGB.md` for termbase-drift (it IS in the termbase).
- Any finding on `concepts/Vorstand.md` for missing-alias (it has 2 aliases).
- Any orphan-termbase-entry findings (termbase only links to existing DNT pages).
- Any invalid-dnt-class findings.
