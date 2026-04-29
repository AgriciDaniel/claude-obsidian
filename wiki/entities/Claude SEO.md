---
type: entity
title: "Claude SEO"
aliases: ["Claude SEO"]
created: 2026-04-14
updated: 2026-04-15
tags:
  - entity
  - project
  - claude-code
  - seo
status: evergreen
related:
  - "[[Pro Hub Challenge]]"
  - "[[2026-04-14-claude-seo-v190-session]]"
  - "[[Semantic Topic Clustering]]"
  - "[[Search Experience Optimization]]"
  - "[[SEO Drift Monitoring]]"
  - "[[E-commerce SEO]]"
  - "[[2026-04-15-slides-and-release-session]]"
  - "[[2026-04-15-release-report-session]]"
---

# Claude SEO

全業種に対応する包括的なSEO分析のためのTier 4 Claude Codeスキル。リポジトリ: [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo)

## 現在の状況(v1.9.0、2026年4月15日リリース)

- **23スキル**(コア20 + 拡張3: DataForSEO、Firecrawl、Banana)
- **17サブエージェント**(コア15 + 拡張エージェント2)
- **30 Pythonスクリプト**(追跡対象28 + 開発専用2)
- **アーキテクチャ**: 3層構成(指示層、オーケストレーション層、実行層)
- **エントリポイント**: `/seo [command] [url]`
- **GitHubリリース**: [v1.9.0](https://github.com/AgriciDaniel/claude-seo/releases/tag/v1.9.0) — PDFレポート添付
- **スライド**: `claude-seo-slides/v190.html` — 15枚のコミュニティ向け発表スライド
- **コントリビューター**: 6件提出、5件統合(Lutfiya Miller、Florian Schmitz、Dan Colta、Matej Marjanovic、Chris Muller)

## 主要コマンド

| カテゴリ | コマンド |
|----------|----------|
| 分析 | audit, page, technical, content, schema, images, geo |
| 計画 | plan, cluster, sxo, programmatic, competitor-pages |
| モニタリング | drift baseline, drift compare, drift history |
| ローカル | local, maps |
| 国際化 | hreflang(文化プロファイル付き) |
| Eコマース | ecommerce |
| データ | google, backlinks, dataforseo |
| 生成 | sitemap, image-gen |

## バージョン履歴

| バージョン | 日付 | 主な追加内容 |
|---------|------|-------------|
| v1.9.0 | 2026-04-15 | Pro Hub Challenge: cluster、SXO、drift、ecommerce、コストガードレール、文化プロファイル。GitHubリリース + PDFレポート + 15枚スライド。 |
| v1.8.2 | 2026-04-10 | ウクライナ語ローカライゼーション、CI修正、バージョン同期 |
| v1.8.1 | 2026-04-06 | Google Images SERP、画像最適化 |
| v1.8.0 | 2026-03-31 | 無料の被リンクデータ(Moz、Bing、Common Crawl) |
| v1.7.0 | 2026-03-28 | Google SEO API群(GSC、PageSpeed、CrUX、GA4) |

## エコシステム

- [[Claude SEO]] — SEO分析(本プロジェクト)
- Claude Blog — 連携するブログエンジン。SEOの知見を取り込む
- Claude Banana — AI画像生成。拡張としてバンドル
- AI Marketing Claude — Zubair Trabzadaによるコミュニティ向けマーケティングスイート

## セキュリティ評価(v1.9.0監査)

- **スコア**: 85/100(B+ランク)
- **SSRF対策**: validate_url() + fetch_page.pyのDNS解決
- **SQL**: 全クエリをパラメータ化済み
- **コストガードレール**: 閾値承認、日次上限、ファイルロック、監査証跡
- **既存の負債**: validate_urlのDNSリバインディング欠陥、インストールスクリプトのインジェクション、OAuthファイルパーミッション
