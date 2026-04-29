---
type: concept
title: "Pro Hub チャレンジ"
created: 2026-04-14
updated: 2026-04-14
tags:
  - concept
  - community
  - ai-marketing-hub
  - claude-seo
  - open-source
status: evergreen
aliases:
  - "Pro Hub Challenge"
  - "Pro Hub チャレンジ"
related:
  - "[[Claude SEO]]"
  - "[[2026-04-14-claude-seo-v190-session]]"
  - "[[Semantic Topic Clustering]]"
  - "[[Search Experience Optimization]]"
---

# Pro Hub チャレンジ

[AI Marketing Hub Pro](https://www.skool.com/ai-marketing-hub-pro) Skool コミュニティで開催されるコミュニティチャレンジ。メンバーが Claude SEO や Claude Blog の拡張機能を開発し、$600 分の Claude Credits を競う。

## 第 1 回チャレンジ(v1.9.0、2026 年 4 月)

**6 件の応募、5 件が Proficient 以上の評価**

| 貢献者 | 応募内容 | スコア | 統合状況 |
|------------|------------|-------|-------------|
| Lutfiya Miller | Semantic Cluster Engine | 優勝 | あり: `seo-cluster` |
| Florian Schmitz | SXO Skill | Proficient | あり: `seo-sxo` |
| Dan Colta | SEO Drift Monitor | Proficient | あり: `seo-drift` |
| Chris Muller | Multi-lingual Blog | Proficient | 一部: SEO 部分を `seo-hreflang` へ |
| Matej Marjanovic | E-commerce + Cost Config | Proficient | あり: `seo-ecommerce` + コストガードレール |
| Benjamin Samar | SEO Dungeon | Reviewed | なし: v1.9.0 では未統合 |

## 統合パターン

コミュニティ応募は以下を経る。

1. **完全コードレビュー**: アーキテクチャ、品質、セキュリティ
2. **セキュリティ監査**: SSRF、インジェクション、認証情報の取り扱い
3. **チェリーピック**: claude-seo には SEO 関連部分のみ。ブログ部分は claude-blog へ残す
4. **デブランド**: 貢献者固有のブランディングを除去(例: ScienceExperts.ai)
5. **クレジット表記**: SKILL.md フロントマターの `original_author`、エージェント内の HTML コメント、CONTRIBUTORS.md

## 応募ガイドライン(CONTRIBUTING.md より)

1. SKILL.md は 500 行以内、references は 200 行以内
2. すべてのスクリプトは SSRF 保護のため `validate_url()` をインポートすること
3. SKILL.md フロントマターのメタデータに `original_author` を含めること
4. PR で提出するか、AI Marketing Hub コミュニティに投稿すること

## 第 2 回チャレンジ(2026 年 4 月)

**キーワード**: LEADS
**賞金プール**: $600($400 が 1 位、$200 が 2 位)分の Claude Credits
**締切**: 2026 年 4 月 28 日
**スコープ**: リード生成に関わるあらゆるもの。Claude Code スキル、n8n ワークフロー、MCP サーバー、スクレイパー、ダッシュボード、パイプライン。誰かのリードの獲得、選別、育成、転換を助けるなら対象となる。
**ルール**: GitHub リポジトリまたは .zip ファイル + 1〜2 分のデモ動画。コンセプトではなく動作するものであること。個人でもチームでも参加可。
**前回の優勝者**: Lutfiya Miller(seo-cluster、v1.9.0 に統合)
