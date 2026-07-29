---
date: 2026-06-21
project: supabase-mcp
agent: codex
status: blocked
---
## What I did
- Synced the shared vault from `fork/main`.
- Verified the Supabase MCP endpoint is reachable and returns the expected unauthenticated HTTP 401.
- Confirmed Codex has the Supabase MCP server configured for project `nfjwuwsuaapufmkppoeo`.
- Started a persistent Codex MCP OAuth listener and opened the Supabase authorization page.
- Re-ran the auth flow and verified Chrome is running.
- Confirmed the selected Chrome profile does not have the Codex Chrome Extension installed.
- Verified the native messaging host manifest is present and correct.

## Files changed
- `wiki/sessions/2026-06-21-supabase-mcp-codex.md`

## Decisions made
- Kept the existing project-scoped Supabase MCP configuration.
- Left the OAuth listener running so browser consent can complete.
- Marked the session blocked on Chrome extension installation in the selected profile.

## Next steps
- Install or enable the Codex Chrome Extension in the selected Chrome profile.
- Re-run `codex mcp login supabase`, approve OAuth consent, then reload Codex and verify Supabase MCP tools are available.
