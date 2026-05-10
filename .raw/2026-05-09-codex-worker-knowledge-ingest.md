---
source: claude-conversation
date: 2026-05-09
topic: Codex workerによるvaultナレッジ・インジェスト自動化セットアップと実行
---

# Codex Worker Knowledge Ingest セットアップ

## Summary

`ops/codex/templates/knowledge-ingest-brief.md` テンプレートを使い、`.raw/claude-obsidian-ecosystem-research.md`（マニフェスト未登録の唯一の未処理素材）向けにCodex workerブリーフを作成・起動した。起動後に `bin/codex-worker-check.sh` のバグ（`rg` 未インストール）を発見・修正し、`grep` へ置換した。またCodexの `--quiet` フラグが無効であることも確認し、`-s workspace-write` を使った正しい起動コマンドを確立した。

## Key Points

- 未処理素材は `.raw/.manifest.json` で管理されており、未登録ファイルが1つ（`claude-obsidian-ecosystem-research.md`）あった
- `ops/codex/briefs/ecosystem-research-ingest.md` を新規作成：対象ソース・許可書き込みスコープ・重複チェックパス・抽出すべき概念候補を明示
- `codex exec --quiet` は無効フラグ → `-s workspace-write` を使用
- `bin/codex-worker-check.sh` の `rg` を `grep` に修正（macOS環境ではripgrepが未インストール）
- Codex worker起動コマンド確定: `codex exec --skip-git-repo-check -s workspace-write "<brief読み込み指示>"`
- DragonScaleアドレス割り当て: `flock` 未インストールのため実質無効（スクリプトは存在するが動作しない）

## Details

### 未処理素材の特定方法

`.raw/.manifest.json` の `sources` キーと `.raw/` ディレクトリの実ファイルを照合。
- 処理済み: `.raw/2026-05-08-claude-obsidian-setup.md`（hash一致）
- 未処理: `.raw/claude-obsidian-ecosystem-research.md`（マニフェスト未登録）

### Briefファイルの構成

`ops/codex/templates/knowledge-ingest-brief.md` の構造に従い以下を埋めた：
- **Mission**: 対象ソースとゴールの1文説明
- **Required Context**: 読むべきコンテキストファイル一覧
- **Inputs**: source path / allowed write scope / duplicate check paths
- **Extraction Rules**: テンプレートの標準ルール + ソース固有の補足
- **Suggested Concepts**: Vault import pattern / Thinking vs Writing Mode / PARA / MCP bridge / 競合プロジェクト比較
- **Completion Report Format**: `DONE:` または `BLOCKED:` の完了レポート形式

### codex-worker-check.sh 修正

`rg`（ripgrep）を macOS 標準の `grep` に置換：
```bash
# 変更前
rg -q '^DONE:' "$final"
# 変更後
grep -q '^DONE:' "$final"
```
3箇所を修正（DONE判定・BLOCKED判定・ログのエラー検索）。

### Codex worker 起動コマンド

```bash
cd ~/claude-obsidian-vault && codex exec \
  --skip-git-repo-check \
  -s workspace-write \
  "Read ops/codex/briefs/ecosystem-research-ingest.md and follow it exactly. Work within ~/claude-obsidian-vault. End with a DONE: or BLOCKED: report."
```

ログ: `ops/codex/runs/ecosystem-research-ingest.log`
PID管理: `ops/codex/runs/ecosystem-research-ingest.pid`
