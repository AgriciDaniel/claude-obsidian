# Pull request

## Summary
One-paragraph description of what this PR changes and why.

## Type
- [ ] Bug fix (`fix:`)
- [ ] New feature (`feat:`)
- [ ] Documentation (`docs:`)
- [ ] Refactor (`refactor:`)
- [ ] Test coverage (`test:`)
- [ ] Chore / build / maintenance (`chore:`)

## Related issue
Closes #<issue-number> (if applicable)

## Changes
List the files and surfaces touched:
- `skills/<name>/SKILL.md` — what changed
- `scripts/<name>.py` — what changed
- ...

## Six-cut self-review
- [ ] Read every file before changing it
- [ ] New identifiers named for the next reader
- [ ] Smallest unit that works (no speculative abstraction)
- [ ] Deletions kept up with additions where applicable
- [ ] New behavior has hermetic test coverage
- [ ] New failure modes have explicit handling + undo plan

## Testing
```
make test
```
Paste the tail of the output here (or a summary if too long):

```
All tests passed.
```

## Verifier
For non-trivial changes, dispatch `agents/verifier.md` on the staged diff and paste its verdict:

- Verdict: SHIP / HOLD-FIX-FIRST / NEEDS-REWORK
- BLOCKER: N / HIGH: N / MEDIUM: N / LOW: N

## CHANGELOG
- [ ] Added an entry under `## [Unreleased]` in `CHANGELOG.md`

## Screenshots / output
If the change affects user-visible output, paste a before/after example.

## Notes for reviewer
Anything specific the reviewer should focus on, or context that's not obvious from the diff.
