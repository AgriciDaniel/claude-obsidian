---
type: concept
title: "Mode D: Personal Second Brain"
status: active
tags: [concept, pkm, second-brain, wiki-mode]
created: 2026-05-08
updated: 2026-05-08
---

# Mode D: Personal Second Brain

[[claude-obsidian]] の6つのVaultモードのひとつ。個人の知識・目標・学習・人間関係・リソースを一元管理する構成。

## フォルダ構造

```
wiki/
├── goals/     — 目標（個人・仕事）と進捗トラッキング
├── learning/  — 習得中のスキル・概念
├── people/    — 人間関係・共有コンテキスト・フォローアップ
├── areas/     — 人生領域（health / career / finance / creative）
└── resources/ — 本・コース・ツール
```

## キーページ

- [[North Star]] — 目指す方向性・価値観・Anti-Goals
- [[Annual Goals]] — 年間目標（領域別）
- [[Weekly Review Template]] — 週次レビューテンプレート

## 日常ループ

1. `.raw/` にソース（記事・メモ・書き起こし）を投入
2. `ingest [ファイル名]` でWikiページ自動生成
3. 週次: [[Weekly Review Template]] でレビュー → `wiki/hot.md` 更新
4. 10〜15回ingest後: `lint the wiki` でヘルスチェック

## 関連
- [[claude-obsidian]]
- [[LLM Wiki Pattern]]
- [[Hot Cache]]
