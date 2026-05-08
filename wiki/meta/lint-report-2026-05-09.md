---
type: meta
title: "Lint Report 2026-05-09"
created: 2026-05-09
updated: 2026-05-09
tags: [meta, lint]
status: developing
---

# Lint Report: 2026-05-09

## Summary

- ページ数: 71
- 問題検出: 56（エラー: 22、要確認: 34）
- 自動修正済み: 0
- 要レビュー: 56

---

## 1. 孤立ページ（Orphan Pages） — 1件

何もリンクしていないページ。削除か、関連ページからリンクを追加してください。

- [[SVG Diagram Style Guide]]: 被リンクゼロ。`[[concepts/_index]]` か `[[DragonScale Memory]]` からリンク追加を推奨。

---

## 2. デッドリンク（Dead Links） — 24件

### 修正優先度: 高

| リンク | 参照元 | コメント |
|---|---|---|
| `[[How does the LLM Wiki pattern work?]]` | `Persistent Wiki Artifact`, `Query-Time Retrieval`, `Source-First Synthesis`, `log` | ファイル名は `?` なし。リンク側の `?` を除去するか、ファイル名を変更する |
| `[[Second Brain]]` | `claude-obsidian`, `claude-obsidian-setup` | ページ未作成。概念ページとして作成推奨 |
| `[[Wiki Map]]` | `concepts/_index`, `getting-started` | ページ未作成。canvas/visual mapのスタブ推奨 |
| `[[Claude Code]]` | `sources/claude-obsidian-setup` | 主要概念なのにページなし。作成推奨 |
| `[[wikilinks]]` | `MCP bridges let Obsidian remain the user interface`, `cherry-picks` | 概念ページ未作成 |

### 修正優先度: 低（旧セッションノート内）

| リンク | 参照元 | コメント |
|---|---|---|
| `[[Claude Canvas]]` | `meta/2026-04-10-backlink-empire-session` | 旧セッションノート内。放置OK |
| `[[Claude Obsidian]]` | `meta/2026-04-10-backlink-empire-session` | 旧セッションノート内 |
| `[[Karpathy LLM Wiki Pattern]]` | `meta/2026-04-10-backlink-empire-session` | 旧セッションノート内（[[Andrej Karpathy]] に合流済み） |
| `[[Rankenstein]]` | `meta/2026-04-10-backlink-empire-session` | 旧セッションノート内 |
| `[[E-commerce SEO]]` | `entities/Claude SEO`, `meta/2026-04-14-claude-seo-v190-session` | 旧セッション。スタブ作成か放置 |

### 意図的テスト例（放置推奨）

| リンク | 参照元 |
|---|---|
| `[[Foo]]`, `[[notes/Foo]]` | `concepts/DragonScale Memory`, `log` |
| `[[fold-template]]`, `[[wiki-fold]]` | `folds/fold-k3-...` |
| `[[Three laws of motion]]` | `concepts/Persistent Wiki Artifact`（比喩として使用） |
| `[[dashboard.base]]` | `meta/dashboard`（`.base` ファイルはwikilinksに非対応） |

---

## 3. フロントマターの不備（Frontmatter Gaps） — 11件

### _index.md 系（`created`, `status` 欠落）

| ページ | 不足フィールド |
|---|---|
| `areas/_index.md` | `status`, `created` |
| `goals/_index.md` | `status`, `created` |
| `learning/_index.md` | `status`, `created` |
| `people/_index.md` | `status`, `created` |
| `resources/_index.md` | `status`, `created` |
| `concepts/_index.md` | `created` |
| `entities/_index.md` | `created` |
| `sources/_index.md` | `created` |

### ソースページ

| ページ | 不足フィールド |
|---|---|
| `sources/claude-obsidian-setup.md` | `status` |
| `sources/codex-worker-knowledge-ingest.md` | `created`, `updated` |
| `sources/wiki-nav-japanese-headings.md` | `created`, `updated` |

---

## 4. DragonScale アドレス検証 — エラー20件

- カウンタ状態: `peek=3`
- 観測済み最大アドレス: `c-000001`（DragonScale Memory のみ）
- ロールアウト基準日: `2026-04-23`

### エラー: post-rollout ページのアドレス未設定（20件）

```
Annual Goals.md
North Star.md
Weekly Review Template.md
areas/career.md, areas/creative.md, areas/finance.md, areas/health.md
concepts/AI vault tools need separate thinking and writing modes.md
concepts/Claude Code Hooks.md
concepts/Claude Obsidian projects are converging on compounding wiki workflows.md
concepts/Codex Worker Pattern.md
concepts/MCP bridges let Obsidian remain the user interface.md
concepts/Mode D Personal Second Brain.md
concepts/PARA is a practical default scaffold for personal AI vaults.md
concepts/Persistent Wiki Artifact.md
concepts/Query-Time Retrieval.md
concepts/Source-First Synthesis.md
concepts/Vault adoption should be non-destructive.md
concepts/claude-obsidian.md
sources/claude-obsidian-setup.md
```

> アドレス付与は `wiki-ingest` の責任。lint は観測のみ。自動付与はしない。

### 情報: レガシーページのアドレス未設定（23件）

ロールアウト前（2026-04-23以前）に作成されたページ。バックフィル対象。エラーではない。

---

## 5. Semantic Tiling — スキップ

- ollama: 到達可能（`http://127.0.0.1:11434`）
- モデル `nomic-embed-text`: **未インストール**（exit 11）
- 有効化: `ollama pull nomic-embed-text` を実行してから再度 lint

---

## 推奨アクション（優先度順）

| 優先度 | アクション |
|---|---|
| 🔴 高 | `[[How does the LLM Wiki pattern work?]]` のリンクを修正（`?` 除去）— 4ページ影響 |
| 🔴 高 | `[[Second Brain]]`, `[[Claude Code]]` の概念ページを作成 |
| 🟡 中 | `[[Wiki Map]]` のスタブ作成（canvas連携推奨） |
| 🟡 中 | `sources/codex-worker-knowledge-ingest.md`, `sources/wiki-nav-japanese-headings.md` のフロントマター補完 |
| 🟡 中 | `_index.md` 系8ページに `created`, `status` を追加 |
| 🟢 低 | DragonScale アドレス: 次回 ingest 時に一括付与 |
| 🟢 低 | `concepts/SVG Diagram Style Guide` をどこかからリンク |
| ⬛ 任意 | `ollama pull nomic-embed-text` で Semantic Tiling を有効化 |
