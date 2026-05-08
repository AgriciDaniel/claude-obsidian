---
type: meta
title: "Hot Cache"
updated: 2026-05-09T00:00:00
---

# Recent Context

## Last Updated
2026-05-09. wiki-lint初回実行 + デッドリンク修正。

## Key Recent Facts
- Vault: `~/claude-obsidian-vault`（Mode D: Personal Second Brain）
- **Codex CLI v0.128.0** インストール済み（`/opt/homebrew/bin/codex`）
- Codex workerパターン確立: `codex exec --skip-git-repo-check -s workspace-write "<prompt>"`
- `bin/codex-worker-check.sh` の `rg` → `grep` 修正済み（macOS標準環境対応）
- Claude Code = オペレーター, Codex = ナロウワーカー, Obsidian = 外部メモリの役割分担が明確
- **lint実施済み**: 71ページ、問題56件。レポート → [[lint-report-2026-05-09]]
- DragonScaleアドレス未設定: post-rolloutページ20件（次回ingest時に付与）

## Recent Changes
- Created: [[lint-report-2026-05-09]]（meta/）— wiki-lint初回実行レポート
- Fixed: `[[How does the LLM Wiki pattern work]]` デッドリンク4箇所（`?` 除去）
- Created: [[2026-05-09-codex-worker-vault-readiness]]（meta/）— Codex Worker Mode運用準備確認セッション記録
- Created: [[Codex Worker Pattern]], [[Vault adoption should be non-destructive]], [[AI vault tools need separate thinking and writing modes]], [[PARA is a practical default scaffold for personal AI vaults]], [[MCP bridges let Obsidian remain the user interface]], [[Claude Obsidian projects are converging on compounding wiki workflows]]
- Created: [[codex-worker-knowledge-ingest]], [[wiki-nav-japanese-headings]]（sources/）

## Active Threads
- lint残課題: `[[Second Brain]]` / `[[Claude Code]]` 概念ページ作成、フロントマター補完11件
- `ollama pull nomic-embed-text` でSemantic Tilingを有効化できる
- North Star / Annual Goals への記入が未着手
- flock未インストール問題: `brew install util-linux` で解決可能
