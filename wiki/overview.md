---
type: overview
title: "Wiki Overview"
updated: 2026-05-08
mode: "D — Personal Second Brain"
---

# Second Brain Overview

Mode: D — Personal Second Brain
Owner: suzuki
Created: 2026-05-08

## Purpose

個人の知識・目標・学習・人間関係・リソースを一元管理し、複利で成長するナレッジベースを構築する。

## Structure

```
wiki/
├── goals/         # 目標 — 個人・仕事の目標と進捗
├── learning/      # 学習 — 習得中のスキル・概念
├── people/        # 人物 — 人間関係・共有コンテキスト
├── areas/         # 領域 — 健康・キャリア・財務・クリエイティブ
└── resources/     # リソース — 本・コース・ツール
```

## Key Pages

- [[North Star]] — 目指す方向性
- [[Annual Goals]] — 2026年目標
- [[Weekly Review Template]] — 週次レビュー

## How to Use

1. `.raw/` にソース（記事・メモ・書き起こし）を入れる
2. `ingest [ファイル名]` で取り込む → 自動でWikiページ生成・相互リンク
3. 質問する → `query: [質問]`
4. 週次レビュー → [[Weekly Review Template]] を使って [[hot]] を更新
5. 10〜15回のingest後に `lint the wiki` でヘルスチェック
