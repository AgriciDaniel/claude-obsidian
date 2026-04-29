---
type: entity
title: "Ar9av/obsidian-wiki"
aliases: ["Ar9av-obsidian-wiki", "Ar9av/obsidian-wiki"]
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - llm-wiki-pattern
  - multi-agent
status: current
related:
  - "[[LLM Wiki Pattern]]"
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# Ar9av/obsidian-wiki

**種別**: Claude Codeプラグイン(スキルベース)
**URL**: https://github.com/Ar9av/obsidian-wiki
**パターン**: Karpathy LLM Wiki
**独自の特徴**: `setup.sh` により任意のAIコーディングエージェントで動作

## 概要

Karpathy LLM Wikiパターンを用いて、AIエージェントがObsidianウィキを構築・維持するためのフレームワーク。最大の差別化要素は、単一の `setup.sh` で7種類のエージェントに同時にスキルを配備できる点である。

## エージェント互換性マトリクス

| エージェント | ブートストラップ | スキルディレクトリ |
|-------|-----------|-----------|
| Claude Code | CLAUDE.md | `.claude/skills/` |
| Cursor | `.cursor/rules/obsidian-wiki.mdc` | `.cursor/skills/` |
| Windsurf | `.windsurf/rules/` | `.windsurf/skills/` |
| Codex (OpenAI) | AGENTS.md | `~/.codex/skills/` |
| Gemini/Antigravity | GEMINI.md | `~/.gemini/antigravity/skills/` |
| OpenClaw | AGENTS.md | `.agents/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` | — |

## 主な革新点

### デルタ追跡マニフェスト
`.manifest.json` が取り込まれた全ソースを追跡する。パス、ハッシュ、タイムスタンプ、生成されたウィキページが記録される。新規または変更があったファイルのみ処理する。これにより「全件再取り込み」問題を解決している。

### 4ステージのパイプライン
1. **取り込み(Ingest)** — ソースを読み込む(PDF、JSONL、テキスト、会話エクスポート、画像)
2. **抽出(Extract)** — 概念、エンティティ、主張、関係、未解決の問いを抽出する
3. **解決(Resolve)** — 既存ウィキと突き合わせて新知識をマージする(重複させない)
4. **スキーマ(Schema)** — 構造はソースから創発し、事前定義しない

### ビジョン対応
画像、スクリーンショット、ホワイトボード写真をビジョン対応モデルで取り込み可能。各ページのフロントマターに1〜2文の `summary:` が付与され、開かずにプレビューできる。

## claude-obsidianへのチェリーピック

- [[cherry-picks#4. Delta Tracking Manifest]]
- [[cherry-picks#6. /wiki-ingest Vision Support]]
- [[cherry-picks#9. Multi-Agent Compatibility (Cursor, Windsurf, Codex)]]
- [[cherry-picks#13. Schema-Emergent Vault Mode]]
