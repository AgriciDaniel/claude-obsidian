---
type: entity
title: "ballred/obsidian-claude-pkm"
aliases: ["ballred-obsidian-claude-pkm", "ballred/obsidian-claude-pkm"]
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - llm-wiki-pattern
  - pkm
  - productivity
status: current
related:
  - "[[LLM Wiki Pattern]]"
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# ballred/obsidian-claude-pkm

**種別**: Claude Codeプラグイン(スキルベースのPKMシステム)
**URL**: https://github.com/ballred/obsidian-claude-pkm
**バージョン**: 3.1
**タグライン**: 「もう一つのPKMスターターキットではない。実行システムだ。」

## 概要

3年ビジョンのカスケードを日々のタスク実行に接続し、Claudeをアカウンタビリティパートナーとして用いる。すべてのレイヤーがリンクされており、デイリーノートは週の「ONE Big Thing」を表示し、それがアクティブなプロジェクトに、そして年間ゴールへとつながる。

## ゴールカスケード

```
3-Year Vision → Yearly Goals → Projects → Monthly Goals → Weekly Review → Daily Tasks
```

各レイヤーには専用スキルが用意されている: `/goal-tracking`、`/project`、`/monthly`、`/weekly`、`/daily`、`/review`。

## 主な革新点

### PostToolUseフックによる自動コミット
すべてのWrite/Editツール呼び出しで `git add -A && git commit` が自動実行される。ボールトは常にバージョン管理される。

### /adopt コマンド
既存のObsidianボールトをスキャンし、そのオーガナイズ手法(PARA、Zettelkasten、LYT、シンプルなフォルダ構成)を検出する。フォルダをPKMの各レイヤーに対話的にマッピングし、設定ファイルを生成する。非破壊的に動作する。

### メモリ付き専門エージェント4種
- `goal-aligner` — 設定したゴールに対する活動を監査し、ズレを指摘する
- `weekly-reviewer` — 3フェーズの週次レビューを進行し、振り返りスタイルを学習する
- `note-organizer` — 壊れたリンクを修復し、重複を統合する
- `inbox-processor` — GTDスタイルの受信箱処理を行う

`memory: project` を使用することで、エージェントはセッション間でパターンを記憶できる。

### 生産性コーチ・アウトプットスタイル
`/output-style coach` でClaudeをアカウンタビリティパートナーに変身させる。前提を疑い、本質的な問いを投げかけ、ゴールと行動の不整合を指摘する。

## アーキテクチャ

依存関係なし(bash + Markdownのみ)。パスごとのルールが文脈に応じて読み込まれる。セッション初期化時にONE Big Thing、アクティブプロジェクト数、最終レビューからの経過日数が表示される。

## claude-obsidianへのチェリーピック

- [[cherry-picks#2. Auto-Commit PostToolUse Hook]]
- [[cherry-picks#7. /adopt — Import Existing Vault]]
- [[cherry-picks#8. Productivity Wrapper (Daily/Weekly Reviews)]]
