---
type: concept
title: "セマンティックトピッククラスタリング"
created: 2026-04-14
updated: 2026-04-14
tags:
  - concept
  - seo
  - content-strategy
  - clustering
status: evergreen
aliases:
  - "Semantic Topic Clustering"
  - "セマンティックトピッククラスタリング"
related:
  - "[[Claude SEO]]"
  - "[[Pro Hub Challenge]]"
  - "[[Search Experience Optimization]]"
---

# セマンティックトピッククラスタリング

SERP に基づくキーワードグループ化により、有料ツール(月額 $50〜200)を Claude の推論で置き換える。Lutfiya Miller により [[Claude SEO]] v1.9.0 へ貢献された(Pro Hub Challenge 優勝者)。

## 仕組み

1. **シードキーワード**: ユーザーが指定する
2. **SERP 取得**: シードと関連語の Google 結果を取得する(WebSearch または DataForSEO 経由)
3. **オーバーラップ採点**: キーワードペア間でトップ 10 結果を比較する。
   - 7〜10 個の URL が重複 = 同一記事(キーワードカニバリゼーション)
   - 4〜6 個の重複 = 同一クラスタ(支援コンテンツ)
   - 2〜3 個の重複 = 内部リンクの機会
   - 0〜1 個の重複 = 別クラスタ
4. **ハブ・スポーク構造**: ピラーページ 1 本(2500〜4000 語)+ クラスタ 2〜5 本 + 各クラスタに記事 2〜4 本
5. **内部リンクマトリクス**: 双方向リンク計画と後方リンク注入
6. **可視化**: インタラクティブな cluster-map.html(SVG、ダークモード、キーボードアクセシブル)

## 主な設計判断

- **Python スクリプト不使用**: クラスタリングはプロンプト駆動(Claude の推論 + WebSearch)
- **オプション実行**: claude-blog 未インストール時はコンテンツブリーフを出力、インストール済みならフルパイプライン
- **再開機能**: 長時間のマルチ記事実行に対応
- **DataForSEO 統合**: 利用可能な場合は `serp_organic_live_advanced` でライブ SERP データを使用(コストチェック付き)

## コマンド

```
/seo cluster <seed-keyword>
```
