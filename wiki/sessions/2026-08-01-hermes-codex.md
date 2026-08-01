---
date: 2026-08-01
project: hermes
agent: codex
status: completed
---
## What I did

- Diagnosed the offline Telegram integration against the official Hermes Agent messaging documentation.
- Confirmed the `maz-lite` Telegram token is valid and its allowlist is configured.
- Started the supported `maz-lite` messaging gateway and verified Telegram long polling connected.
- Sent a successful Telegram test message from the configured bot.
- Disabled the duplicate root-profile Windows startup launcher, which used the same bot token and could compete with `maz-lite` for Telegram polling.
- Confirmed 9Router remains available on port 20128.

## Files changed

- `wiki/sessions/2026-08-01-hermes-codex.md`
- Windows Startup: `Hermes_Gateway.cmd` renamed to `Hermes_Gateway.cmd.disabled` (recoverable backup)

## Decisions made

- Kept `Hermes_Gateway_maz-lite.cmd` as the sole active Hermes startup launcher because `maz-lite` is the selected profile.
- Did not change or expose the Telegram token.

## Next steps

- Optional: run `hermes --profile maz-lite doctor --fix` later to migrate config schema v30 to v33.
