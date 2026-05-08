---
type: meta
title: "Hot Cache"
updated: 2026-05-09T00:00:00
---

# Recent Context

## Last Updated
2026-05-09. Claude Code司令塔 + Codex Worker運用準備確認完了。

## Key Recent Facts
- Vault: `~/claude-obsidian-vault`（Mode D: Personal Second Brain）
- **Codex CLI v0.128.0** インストール済み（`/opt/homebrew/bin/codex`）
- Codex workerパターン確立: `codex exec --skip-git-repo-check -s workspace-write "<prompt>"`
- `bin/codex-worker-check.sh` の `rg` → `grep` 修正済み（macOS標準環境対応）
- Claude Code = オペレーター, Codex = ナロウワーカー, Obsidian = 外部メモリの役割分担が明確
- DragonScale allocator: `flock` 未インストールのためアドレス割り当て無効（スクリプトは存在）

## Recent Changes
- Created: [[2026-05-09-codex-worker-vault-readiness]]（meta/）— Codex Worker Mode運用準備確認セッション記録
- Created: [[Codex Worker Pattern]], [[Vault adoption should be non-destructive]], [[AI vault tools need separate thinking and writing modes]], [[PARA is a practical default scaffold for personal AI vaults]], [[MCP bridges let Obsidian remain the user interface]], [[Claude Obsidian projects are converging on compounding wiki workflows]]
- Created: [[codex-worker-knowledge-ingest]]（sources/）
- Updated: [[index]]（6概念 + 2ソース追加）, [[log]]（3エントリ追加）, [[sources/_index]]

## Active Threads
- North Star / Annual Goals への記入が残っている
- `.raw/` に新しいソースを入れてingestを試せる状態
- Codex Workerでタスクを並列実行する準備が整っている
- flock未インストール問題: `brew install util-linux` で解決可能
