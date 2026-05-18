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

## Disclosure

We will credit reporters in the release notes unless they prefer otherwise. We will not pursue legal action against good-faith reporters who follow this policy.
