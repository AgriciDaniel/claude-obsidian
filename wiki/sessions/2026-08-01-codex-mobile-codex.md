---
date: 2026-08-01
project: codex-mobile
agent: codex
status: in-progress
---
## What I did
- Pulled the shared vault from `fork/main` using the canonical vault path.
- Verified Codex CLI 0.146.0 is authenticated with ChatGPT.
- Checked current Codex Remote documentation and local Windows installation.
- Confirmed the CLI remote-control daemon cannot run on Windows and Remote must be hosted by the ChatGPT desktop app.
- Found the ChatGPT/Codex Windows app installed but not running, launched it, and opened `codex://settings/connections/computer`.

## Files changed
- `wiki/sessions/2026-08-01-codex-mobile-codex.md`

## Decisions made
- Treat "Codex mobile" as ChatGPT mobile Remote access to the local Windows Codex host.
- Do not modify private app state or authentication files; pairing requires the normal trusted-device flow.

## Next steps
- On the Windows app Connections screen, enable **Allow other devices to connect** / **Remote Control** if it is off.
- In the latest ChatGPT mobile app, open **Remote** and scan the displayed QR code while using the same account and workspace.
- If previously paired before June 8, 2026 but unused since then, update both apps and pair again.
