---
type: session
title: "Codex Worker Mode: Vault準備確認"
created: 2026-05-09
updated: 2026-05-09
tags:
  - session
  - codex
  - operator-worker
  - vault-setup
status: evergreen
related:
  - "[[Codex Worker Pattern]]"
  - "[[claude-obsidian]]"
  - "[[Mode D Personal Second Brain]]"
  - "[[Claude Code Hooks]]"
---

# Codex Worker Mode: Vault準備確認

2026-05-09セッションで `CLAUDE.md`, `AGENTS.md`, `wiki/hot.md`, `ops/codex/README.md` を読み、Claude Code司令塔 + Codex Worker運用体制の準備が完全に整っていることを確認した。

## 役割分担

| レイヤー | 担当 | 責任 |
|---|---|---|
| **オペレーター** | Claude Code | コンテキスト読み込み → Brief作成 → Worker起動 → ログ検査 → 採用/棄却 |
| **ワーカー** | Codex CLI | Briefを読む → スコープ内のみ編集 → `DONE:`/`BLOCKED:` で報告 |
| **外部メモリ** | Obsidian vault | `.raw/`（イミュータブルソース）+ `wiki/`（生成知識）|

## インフラ確認済み項目

- **Codex CLI**: `v0.128.0` インストール済み（`/opt/homebrew/bin/codex`）
- **起動スクリプト**: `bin/codex-worker-run.sh` — `codex exec --sandbox workspace-write` でバックグラウンド実行、PID/log/final.mdを自動生成
- **状態確認**: `bin/codex-worker-check.sh`
- **Briefテンプレート**: `ops/codex/templates/worker-brief.md` + `knowledge-ingest-brief.md`
- **実行ディレクトリ**: `ops/codex/briefs/`（Brief）→ `ops/codex/runs/`（ログ+final）

## Workerの制約（AGENTS.mdで定義）

- `.raw/` は絶対に書き換えない（ソースのイミュータビリティ保証）
- `CLAUDE.md`, `AGENTS.md`, `bin/`, `ops/codex/templates/` は書き換えない
- 並列Worker起動時はwrite scopeが互いに重複しないこと
- 最終出力は必ず `DONE:` または `BLOCKED:` ブロックで終わること

## Worker起動の基本コマンド

```bash
# Brief作成後、起動
bash bin/codex-worker-run.sh ops/codex/briefs/<task>.md

# ログ確認
bash bin/codex-worker-check.sh
```

## ホットキャッシュ状態（確認時点）

- 最終更新: 2026-05-08（前回セッション）
- セットアップ完了済み
- North Star / Annual Goals への記入が未着手
- `.raw/` に新しいソースを入れてingestする準備が整っている

## 次のアクション

- `.raw/` に素材を入れてingestを試す
- 特定タスクのBriefを書いてWorkerを試験運用する
