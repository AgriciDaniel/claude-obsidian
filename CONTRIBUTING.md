# Contributing to claude-obsidian

Thanks for your interest in improving this plugin. claude-obsidian is a small, focused project; contributions that match its philosophy land quickly.

## Philosophy

Three constraints shape every change:

1. **Read before write.** Every contribution starts by reading the affected files, their tests, and their callers. Removals break assumptions as often as additions.
2. **Smallest unit that works.** No speculative abstraction. Complexity is earned, not anticipated. Three real callers minimum before an abstraction lands.
3. **Failure is the spec.** Every new failure mode needs explicit handling. Untrusted input, network calls, and state changes need an explicit blast-radius answer.

The full kernel lives in [`/best-practices`](https://github.com/AgriciDaniel/best-practices) (composable Claude Code skill). The pre-commit verifier agent at [`agents/verifier.md`](agents/verifier.md) enforces it for non-trivial changes.

## Workflow

### 1. Open an issue first (for non-trivial changes)

For typo fixes, doc clarifications, or single-line changes, skip straight to a PR. For anything bigger:

- Open an issue using the bug-report or feature-request template
- Describe the problem, the proposed change, and the blast radius
- Wait for a thumbs-up before investing time

### 2. Fork + branch

Contributions are accepted on the public canonical repo. Fork [`AgriciDaniel/claude-obsidian`](https://github.com/AgriciDaniel/claude-obsidian) on GitHub, then:

```bash
git clone https://github.com/<your-username>/claude-obsidian.git
cd claude-obsidian
git checkout -b your-feature-name
```

> ℹ️ AI Marketing Hub Pro members working from the early-access mirror (`AI-Marketing-Hub/claude-obsidian`) should also raise PRs against the public canonical — community work lands there first and gets backported.

Branch names: `fix/...`, `feat/...`, `docs/...`, `refactor/...`.

### 3. Set up locally

The plugin runs anywhere Claude Code runs. For development:

```bash
# Run the hermetic test suite — required before submitting a PR
make test

# Optionally provision the v1.7 retrieval pipeline (requires consent for API egress)
bash bin/setup-retrieve.sh

# Optionally pick a methodology mode for testing the v1.8 routing
bash bin/setup-mode.sh
```

### 4. Make the change

Follow the six-cut kernel:
- Read every file you're touching
- Name new identifiers like the next reader is hostile
- Smallest unit that works
- Delete more than you add (when superseding)
- Evidence over intuition (tests for new behavior)
- Failure-mode + undo plan documented

If you add a new skill, agent, script, or hook, also add a test under `tests/`. The 8 hermetic test suites are the project's safety net.

### 5. Run the tests

```bash
make test
```

All 8 suites must pass (~1234 assertions). Tests are hermetic: no network, no ollama, no Anthropic API. If your change adds a network call, gate it behind a `--consent`/`--allow-egress`/env-var pattern matching `scripts/contextual-prefix.py` or `scripts/tiling-check.py`.

### 6. Run the verifier (optional but recommended)

For multi-file changes:

```bash
# After git add, before git commit, dispatch the verifier agent
# (Claude Code: invoke agents/verifier.md on the staged diff)
```

The verifier applies the six-cut + agent kernel to your staged diff and returns findings in BLOCKER / HIGH / MEDIUM / LOW tiers. Address BLOCKER + HIGH before committing.

### 7. Commit

Commit message convention (Conventional Commits):

```
<type>(<scope>): <short description>

<longer body if needed>
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `style`.

Example:
```
fix(wiki-mode): close path-traversal in route_path safe_name

Sanitize routing input via safe_name() before string-concat into
the vault-relative path. Adds 9 hermetic test assertions for traversal
vectors. Closes audit finding S1.
```

### 8. Update CHANGELOG.md

Add an entry under `## [Unreleased]` (create the section if needed). Follow the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format:

```markdown
## [Unreleased]

### Added
- Description of new feature

### Fixed
- Description of bug fix
```

The maintainer will move your entry to a versioned section at release time.

### 9. Open a PR

Use the PR template. Required fields:
- What changed
- Why
- How it was tested (paste `make test` output if relevant)
- Audit/verifier results if applicable

PRs are reviewed against the kernel. Expect feedback on naming, scope, and failure-mode coverage.

## Testing standards

- **Hermetic.** No network, no external services, no user-specific environment.
- **Fast.** The full suite runs in under a minute.
- **Deterministic.** Same input → same output, every time.
- **Documented.** Every test asserts a named behavior, not a coincidence.

If you can't make your test hermetic, ask in the issue whether a mocked alternative is acceptable.

## What we will NOT merge

- Code without tests for new behavior
- Speculative abstractions (no real callers yet)
- Network calls without an explicit consent gate
- Path construction from user input without sanitization (see `scripts/wiki-mode.py:safe_name`)
- Skills/agents that shell out without documenting the failure mode
- Anything that breaks the existing test suite without a documented reason

## Security

Found a vulnerability? Do NOT open a public issue. See [SECURITY.md](SECURITY.md) for disclosure.

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).

## Code of Conduct

Participation is governed by the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
