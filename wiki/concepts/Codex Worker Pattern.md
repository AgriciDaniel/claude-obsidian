---
type: concept
title: "Codex Worker Pattern"
created: 2026-05-09
updated: 2026-05-09
tags:
  - concept
  - codex
  - automation
  - agent-workflow
status: developing
related:
  - "[[LLM Wiki Pattern]]"
  - "[[claude-obsidian]]"
  - "[[Claude Code Hooks]]"
sources:
  - "[[codex-worker-knowledge-ingest]]"
---

# Codex Worker Pattern

Claude Codeがオーケストレーターとして機能し、Codex CLIをナロウ・ワーカーとして起動する分業パターン。Briefファイルで作業スコープを事前に制約することで、Codexに余計な判断をさせずに特定のwiki操作に集中させる。

## 構成要素

- **Brief** (`ops/codex/briefs/*.md`): ミッション・コンテキスト・入力・書き込みスコープ・完了レポート形式を宣言
- **Worker**: `codex exec --skip-git-repo-check -s workspace-write "<brief読み込み指示>"` で起動
- **ログ**: `ops/codex/runs/<name>.log` / `<name>.pid` / `<name>.final.md`
- **チェックスクリプト**: `bin/codex-worker-check.sh` でRUNNING/DONE/BLOCKED/CHECKを分類

## 責任分担

| 主体 | 責任 |
|---|---|
| Claude Code | Brief作成・Worker起動・ログ確認・diff採否判定 |
| Codex Worker | Brief内スコープのみ読み書き・DONE/BLOCKEDレポートで終了 |

## 動作確認済み起動コマンド

```bash
codex exec \
  --skip-git-repo-check \
  -s workspace-write \
  "Read ops/codex/briefs/<brief-name>.md and follow it exactly. Work within ~/claude-obsidian-vault. End with a DONE: or BLOCKED: report."
```

## 既知の注意点

- `--quiet` フラグは無効（codex v0.128.0）
- `bin/codex-worker-check.sh` は macOS では `rg` を `grep` に要置換
- `scripts/allocate-address.sh` は `flock` 依存のためmacOS標準環境では動作しない
