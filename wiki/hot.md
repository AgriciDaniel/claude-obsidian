---
type: meta
title: "Hot Cache"
updated: 2026-05-08T22:30:00
---

# Recent Context

## Last Updated
2026-05-09. Codex workerブリーフ駆動ワークフロー確立 + ecosystem-researchインジェスト完了。

## Key Recent Facts
- Vault: `~/claude-obsidian-vault`（Mode D: Personal Second Brain）
- Codex workerパターン確立: `codex exec --skip-git-repo-check -s workspace-write "<prompt>"`
- `bin/codex-worker-check.sh` の `rg` → `grep` 修正済み（macOS標準環境対応）
- DragonScale allocator: `flock` 未インストールのためアドレス割り当て無効（スクリプトは存在）
- `.raw/.manifest.json`: 処理済みファイル1件 + 新規追加1件（2026-05-09）

## Recent Changes
- Created: [[Codex Worker Pattern]], [[Vault adoption should be non-destructive]], [[AI vault tools need separate thinking and writing modes]], [[PARA is a practical default scaffold for personal AI vaults]], [[MCP bridges let Obsidian remain the user interface]], [[Claude Obsidian projects are converging on compounding wiki workflows]]
- Created: [[codex-worker-knowledge-ingest]]（sources/）
- Updated: [[index]]（6概念 + 2ソース追加）, [[log]]（2エントリ追加）, [[sources/_index]]

## Active Threads
- ecosystem-researchのingestが完了。`[[claude-obsidian-ecosystem]]` へのリンクが未解決（既存ファイルに存在するが、brief対象外で放置）
- North Star / Annual Goals への記入が残っている
- flock未インストール問題: `brew install util-linux` で解決可能
