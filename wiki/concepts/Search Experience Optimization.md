---
type: concept
title: "検索体験最適化(SXO)"
created: 2026-04-14
updated: 2026-04-14
tags:
  - concept
  - seo
  - ux
  - serp-analysis
status: evergreen
aliases:
  - "Search Experience Optimization"
  - "検索体験最適化"
  - "SXO"
related:
  - "[[Claude SEO]]"
  - "[[Pro Hub Challenge]]"
  - "[[Semantic Topic Clustering]]"
---

# 検索体験最適化(SXO)

SERP を逆方向に読むことでページタイプの不一致を検出し、検索機能からユーザーストーリーを導出し、ペルソナの視点でページを採点する方法論。Florian Schmitz により [[Claude SEO]] v1.9.0 へ貢献された。

## 中核の洞察

> 「SERP を逆方向に読む」。SERP に向けてコンテンツを最適化するのではなく、ユーザーの期待について SERP が何を示しているかを分析し、ページがそれを満たしているかを確認する。

## プロセス

1. **ページタイプ検出**: URL を 8 タイプ(Landing、Blog、Product、Hybrid、Service、Comparison、Local、Tool)のいずれかに分類する
2. **SERP パターンマッチ**: Google が表示するもの(フィーチャードスニペット、PAA、広告、関連検索)とページが提供するものを比較する
3. **不一致検出**: SERP が「ユーザーは比較を求めている」と示しているのにページが「製品ページ」なら、それは不一致である
4. **ユーザーストーリー導出**: SERP の機能から、感情状態、障壁、目標を持つ 4〜7 のペルソナを導出する
5. **ペルソナ採点**: 各ペルソナの視点でページを採点する(4 次元で 0〜100 点)
6. **ワイヤーフレーム生成**: 極めて具体的なプレースホルダー付きの IST(現在)対 SOLL(理想)ワイヤーフレーム

## 鍵となる革新

ほとんどの SEO ツールはページを単独で分析する。SXO は SERP をユーザーインテントの代理指標として使う。SERP こそ、Google がユーザーの欲求についてすでに行ったリサーチである。これにより、ユーザーテストなしにデータ駆動の分析が可能になる。

## コマンド

```
/seo sxo <url>
/seo sxo wireframe <url>
```
