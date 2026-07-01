---
date: 2026-07-01
project: hermes
agent: codex
status: completed
---
## What I did
- Identified Hermes dashboard as the Vite web dashboard on port 5173.
- Confirmed the dashboard backend remains on 127.0.0.1:9119 and desktop renderer remains on 5174.
- Added a phone-accessible Vite start path and PowerShell launcher.
- Verified `netstat -ano` shows `0.0.0.0:5173` listening.

## Files changed
- `C:\Users\manaz\AppData\Local\hermes\hermes-agent\web\package.json`
- `C:\Users\manaz\AppData\Local\hermes\hermes-agent\start-hermes-phone.ps1`
- `C:\Users\manaz\AppData\Local\hermes\hermes-agent\PHONE_ACCESS.md`
- `C:\Users\manaz\claude-obsidian\wiki\sessions\2026-07-01-hermes-codex.md`

## Decisions made
- Exposed only the Vite dashboard port 5173, not Ollama, 9router, MCP, model, terminal, credential, or backend API ports.
- Kept the Hermes dashboard backend loopback-only on 127.0.0.1:9119.
- Left existing desktop renderer behavior untouched on 127.0.0.1/[::1]:5174.
- Preferred Tailscale where available; detected Tailscale IP 100.115.207.123.

## Next steps
- Run `start-hermes-phone.ps1` from an Administrator PowerShell once to create the scoped firewall rule, or add TCP 5173 manually for LocalSubnet and 100.64.0.0/10.
