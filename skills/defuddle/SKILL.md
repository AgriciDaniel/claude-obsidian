---
name: defuddle
description: Plan and, with explicit network consent, use an optional external Defuddle cleaner to extract article-like HTTPS pages as Markdown. Use for defuddle, clean this URL, strip page clutter, readable Markdown from a web page, or preparing a web source for later wiki ingestion.
---

# Defuddle

Treat Defuddle as an optional external extractor, not an internal capability.
Cleaning, raw capture, and wiki ingestion are separate operations.

Resolve the installed product root from this skill's own location, never from
the selected vault or process working directory:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

Every `../wiki/references/` link in this file resolves the same way, relative
to this skill's own directory under `$PRODUCT_ROOT`, never relative to the
selected vault's `wiki/` directory.

If a separately installed `kepano/obsidian-skills` `defuddle` skill is
available, prefer it for current CLI flags. Retain the privacy, consent, and
transaction rules in this skill.

## Safety contract

- Accept remote inputs only as HTTPS URLs.
- Reject credentials in URLs, fragments, private or local hosts, non-public IP
  addresses, control characters, and sensitive query parameters.
- Never interpolate a URL into a shell string. Pass it as one argv element.
- Treat redirects to a different host as denied until that host is explicitly
  approved.
- State that the URL and request metadata will leave the machine. Network
  access requires explicit consent in the current request or a separate
  confirmation.
- Do not install a cleaner, execute a placeholder runner, or silently switch to
  another network fetcher.
- Do not claim a fixed token reduction or extraction quality. Inspect the
  actual output.

## Plan first

Create an inert URL plan. This validates the URL and executes no network call:

```bash
python3 "$CORE" capture external-plan url "HTTPS_URL"
```

Report the normalized host, network egress, redirect policy, optional external
dependency, and `execute: false`. Then inspect whether this package can find a
configured Defuddle executable:

```bash
python3 "$CORE" contracts --verify --capability defuddle --vault VAULT
```

An `available` state means no executable was found; stop with the inert plan.
A `configured` state means the executable was discovered, but this package has
no bundled behavioral verifier for it. Show that state and reason, identify the
resolved executable path, and require manual review of its provenance, version,
and exact argv before execution. Never relabel `configured` as `verified`.

When unavailable or when manual review is declined, offer these honest
fallbacks: let the user install/configure an external runner, accept a local
HTML or Markdown file in `inbox/`, or leave the URL queued for later. Do not
claim that content was cleaned, captured, or ingested.

## Execute after consent

After network consent, configured-state detection, and manual executable
review, invoke the approved executable with an argv equivalent to:

```text
defuddle parse HTTPS_URL --md
```

Capture bounded stdout in a temporary draft outside shared vault state. Fail
closed on a non-zero exit, empty output, unexpected binary output, an
unapproved redirect, or a response that is clearly an authentication/error
page. Preserve headings, links, code fences, tables, quotations, and source
wording; do not invent missing content.

Preview the cleaned Markdown and report extraction limitations. If the user
asked only to read or analyze it, keep the result transient.

## Optional raw capture

When the user asks to retain the cleaned source:

1. Resolve the user vault.
2. Hash the exact cleaned bytes with SHA-256.
3. Draft a new immutable payload such as
   `.raw/captured/<sha256>.md` and, when provenance metadata is needed, a new
   create-only sidecar with the normalized URL, retrieval date, extractor name
   and version, and content hash.
4. Use `expected_hashes: null` and `mode: create`. If that content-addressed
   payload already exists with the same bytes, report a no-op; never overwrite
   it.
5. Build, inspect, and apply one `claude-obsidian.transaction.v1` capture
   bundle as described in
   [operation-transactions.md](../wiki/references/operation-transactions.md).

Do not create wiki pages, update indexes, assess claims, or mark the source as
ingested. Invoke `wiki-ingest` as a distinct requested operation if the user
wants the captured payload incorporated into the knowledge base.
