---
type: entity
title: "kepano/obsidian-skills"
aliases: ["kepano-obsidian-skills", "kepano/obsidian-skills"]
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - official
  - agent-skills
  - obsidian-creator
status: current
related:
  - "[[LLM Wiki Pattern]]"
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# kepano/obsidian-skills

**種別**: Agent Skills(Agent Skills標準)
**URL**: https://github.com/kepano/obsidian-skills
**作者**: **Linus Kepano** — ObsidianとMinimalテーマの作者
**インストール**: `/plugin marketplace add kepano/obsidian-skills`

## なぜ重要か

このリポジトリはObsidianの作者によるものである。意義は以下のとおり:
1. Agent Skills標準がObsidian系AIツールの正しい形式であることを裏付ける
2. Obsidian固有の構文をClaudeに教えるための正規リファレンスを提供する
3. 他のどのAIプロジェクトもまだ対応していない、Obsidianの新コア機能であるObsidian Basesをカバーする

## スキル

| スキル | Claudeに教える内容 |
|-------|----------------------|
| `obsidian-markdown` | Obsidian Flavored Markdownの全範囲: ウィキリンク、埋め込み、コールアウト、プロパティ、タグ |
| `obsidian-bases` | Obsidian Bases(.baseファイル): ビュー、フィルタ、フォーミュラ、サマリー |
| `json-canvas` | JSON Canvas仕様: ノード、エッジ、グループ、コネクション |
| `obsidian-cli` | Obsidian CLIによるボールト管理、プラグイン/テーマ開発 |
| `defuddle` | Webページからクリーンなマークダウンを抽出。広告、ナビゲーション、雑多な要素を除去 |

## defuddle

`defuddle` スキルは `defuddle-cli` をラップする。Webコンテンツの取り込み時にdefuddleを先に実行すると以下の効果がある:
- 広告、ナビゲーション、フッターを削除
- 一般的なWebページでトークン使用量を約40〜60%削減
- コンテキストウィンドウに収まりやすい、よりクリーンなMarkdownを生成

これはclaude-obsidianの取り込みパイプラインに対する直接的なチェリーピックである。

## マルチプラットフォーム

Claude Code、Codex CLI、OpenCodeで標準動作する。

## claude-obsidianへのチェリーピック

- [[cherry-picks#1. URL Ingestion in /wiki-ingest]](defuddleと組み合わせる)
- [[cherry-picks#3. defuddle Web Cleaning Skill]]
- [[cherry-picks#12. obsidian-bases Skill (from kepano)]]
- [[cherry-picks#9. Multi-Agent Compatibility]](フォーマットはすでに互換)
