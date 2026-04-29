---
type: entity
title: "rvk7895/llm-knowledge-bases"
aliases: ["rvk7895-llm-knowledge-bases", "rvk7895/llm-knowledge-bases"]
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - llm-wiki-pattern
  - deep-research
status: current
related:
  - "[[LLM Wiki Pattern]]"
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
  - "[[Andrej Karpathy]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# rvk7895/llm-knowledge-bases

**種別**: Claude Codeプラグイン(マーケットプレイス公開)
**URL**: https://github.com/rvk7895/llm-knowledge-bases
**インストール**: `/plugin marketplace add rvk7895/llm-knowledge-bases`

## 概要

生の研究資料を、LLMが維持するObsidianウィキへと変換し、多段階の深さでクエリと豊富な出力フォーマットに対応させる。Karpathyのパターンの上に、並列エージェントによる深掘り研究パイプラインを追加している。

## 主な革新点

### 3段階の深さを持つクエリシステム
- **Quick** — ウィキインデックスとサマリーのみから回答(読み取り最小限)
- **Standard** — ウィキ全体を相互参照し、Web検索で補完
- **Deep** — マルチエージェントの並列Web検索パイプライン

### 出力フォーマット
Markdownにとどまらず、Marpスライドやmatplotlibチャートに対応。出力はすべて `output/` に保存され、必要に応じてウィキにファイリングし直される。

### スキル一覧
| スキル | 用途 |
|-------|---------|
| `/kb-init` | 初回セットアップ |
| `/kb compile` | 生データ → ウィキ化 |
| `/kb query` | 深さを指定したクエリ |
| `/kb lint` | 健全性チェック |
| `/kb evolve` | メンテナンスパス |
| `/research <topic>` | 構造化されたリサーチアウトライン |
| `/research-deep` | アウトラインの各項目に対する並列エージェント |
| `/research-report` | 深掘り結果のMarkdownへのコンパイル |

### X/Twitter連携
Smaugツール(`npm install -g @steipete/bird`)経由で、URLを貼り付けるだけでX/Twitterのツイート、スレッド、ブックマークを取り込む。セッションクッキーを使用する(読み取り専用、個人利用)。

## アトリビューション
Karpathyのパターン + Weizhenaのディープリサーチスキルをリサーチパイプライン向けに適応した上に構築されている。

## claude-obsidianへのチェリーピック

- [[cherry-picks#5. Multi-Depth Query Modes]]
- [[cherry-picks#10. Marp Presentation Output]]
