# Privacy

## Data Handling

claude-obsidian is a Claude Code plugin and Obsidian vault that runs entirely on
your local machine. Your vault is plain Markdown on your own filesystem. The core
skill does not collect, transmit, or store any personal data, and there is no
telemetry, analytics, or usage tracking.

## What Stays Local

- Ingesting sources, answering queries, linting, and updating the hot cache all
  run inside your local Claude Code session.
- All wiki content (`wiki/`) is plain Markdown saved to your local filesystem.
- The `/wiki-retrieve` BM25 index and optional ollama-based reranking run fully
  locally. Without an explicit opt-in flag, retrieval never leaves your machine.

## Optional Network Egress (opt-in, consent-gated)

Network calls happen only when you explicitly enable them. By default everything
is local.

| Feature | Service | Data sent | Gate |
|---------|---------|-----------|------|
| `/wiki-retrieve` contextual prefix | Anthropic API | Wiki page chunks (for prefix generation) | Off by default. Requires the `--allow-egress` consent flag on `scripts/contextual-prefix.py`; without it, the tier falls back to `claude` on PATH or a fully local synthetic prefix. |
| `/autoresearch` | Web search + fetch | Your research query and fetched URLs | Opt-in; only runs when you invoke the research loop. |
| `/defuddle` | Web fetch | URLs you ask it to extract | Opt-in; only runs when you invoke it. |
| ollama rerank | `localhost` only | Query + candidate chunks | Local by default. Remote ollama hosts are refused unless you pass `--allow-remote-ollama`. |

## Credentials

- API keys (such as `ANTHROPIC_API_KEY`) are read from environment variables or
  your local `.env`, never hard-coded.
- Credentials are never committed to the repository (blocked by `.gitignore`).
- The included demo vault and configuration ship with placeholder values only.

## Security Disclosure

To report a security or privacy issue, see [`SECURITY.md`](SECURITY.md).
