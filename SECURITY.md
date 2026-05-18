# Security policy

## Reporting a security concern

If you find a security issue in claude-obsidian, please report it privately rather than opening a public issue.

**Preferred:** GitHub's private reporting at the repository's [Security Advisories](../../security/advisories/new) page.

**Alternative:** Email **agricidaniel@gmail.com** with subject line `claude-obsidian security`.

Please include:
- A short description of the issue
- Steps to reproduce
- Affected file(s) and version
- Suggested fix if you have one

## Response

You will receive an acknowledgement within 5 business days. Fix timeline depends on severity:

- Critical (data exposure, command execution, supply-chain risk): patched within 7 days
- High (exposure with conditions): patched within 30 days
- Medium / Low: rolled into the next scheduled release

## Scope

This policy covers:
- The plugin code under `skills/`, `agents/`, `scripts/`, `hooks/`, `bin/`
- The plugin manifests under `.claude-plugin/`
- The pre-commit verifier agent

Out of scope:
- Content of user-authored wiki pages (your data, your control)
- Third-party tools the plugin shells out to (Obsidian, defuddle-cli, ollama, etc.) — report upstream
- Issues that require pre-existing local access to the user's machine

## Threat model: single-tenant vault

claude-obsidian assumes a **single-tenant** deployment: one user, one vault, one machine. Several design decisions follow from this assumption and would need explicit hardening for multi-tenant or shared-CI scenarios:

- **`scripts/wiki-lock.sh release`** unconditionally removes a lock file regardless of which process acquired it. This is intentional — acquire and release typically come from separate bash invocations of the same skill on the same host, so a PID-bound release would fail in normal use. In a shared-host or multi-user setup, any user able to write to `.vault-meta/locks/` could release another user's in-flight lock. Mitigation in that scenario: restrict filesystem permissions on `.vault-meta/locks/` to the vault owner.
- **The PostToolUse auto-commit hook** (`hooks/hooks.json`) runs as the user invoking Claude Code. It auto-commits `wiki/`, `.raw/`, and `.vault-meta/` paths to the local repo on every Write/Edit. Set `.vault-meta/auto-commit.disabled` (any contents) to opt out per-vault. For shared repos, prefer disabling the hook entirely or using a more restrictive commit policy.
- **Cross-process resource access** (lockfiles, transport snapshots, embed cache) is governed by filesystem permissions, not by application-layer identity checks. Standard Linux/macOS file permissions are the trust boundary.

If you are deploying in a setting where any of these assumptions fail, reach out via the security contact above before adoption.

## Disclosure

We will credit reporters in the release notes unless they prefer otherwise. We will not pursue legal action against good-faith reporters who follow this policy.
