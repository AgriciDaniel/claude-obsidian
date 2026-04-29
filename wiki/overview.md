---
type: overview
title: "ウィキ概観"
aliases: ["Wiki Overview", "ウィキ概観"]
created: 2026-04-07
updated: 2026-04-29
tags:
  - meta
  - overview
status: developing
related:
  - "[[index]]"
  - "[[hot]]"
  - "[[log]]"
  - "[[dashboard]]"
  - "[[LLM Wiki Pattern]]"
sources:
---

# ウィキ概観

ナビゲーション: [[index]] | [[hot]] | [[log]] | [[dashboard]]

---

## 目的

これは claude-obsidian デモ Vault です。[[LLM Wiki Pattern]] を実演します。Claude と Obsidian で永続的・複利的に成長するナレッジベースを構築するパターンです。

`/wiki` を実行してこの Vault を自分のドメイン用に足場として作り、この概観を置き換えてください。

> **言語ローカライズ**: 本 Vault は日本語ローカライズ版です。本文・要約・チャット応答は日本語、ファイル名・wikilink ターゲット・コードは英語のまま。詳細は `CLAUDE.md` の言語ポリシー参照。

---

## 現在のシードコンテンツ

**シード概念:**
- [[LLM Wiki Pattern]] — 中心アーキテクチャ
- [[Hot Cache]] — セッションコンテキスト機構
- [[Compounding Knowledge]] — このパターンが機能する理由

**シードエンティティ:**
- [[Andrej Karpathy]] — このパターンの創案者

**シードソース:**
- [[claude-obsidian-ecosystem-research]] — 16 以上のプロジェクト、13 のチェリーピック特定(2026-04-08)

---

## 現状

- 取り込み済みソース: 2
- ウィキページ数: 26
- 最終アクティビティ: 2026-04-29(日本語ローカライズパス実施)

---

## キャンバス

- [[claude-obsidian-presentation]] — フルプレゼン: ヒーロー、概観、スキル、アーキテクチャ、Wiki vs RAG、ビジュアルデモ(2026-04-07)
- [[AI Marketing Hub Cover Images Canvas]] — AI Marketing Hub ブランドアセット用カバー画像ライブラリ

---

## 主要テーマ

**知識は複利で積み上がる。** RAG と異なり、ウィキは合成を事前コンパイルする。相互参照はすでに張られている。矛盾はフラグされている。各取り込みは孤立したチャンクを追加するのではなく既存ページを豊かにする。

**ホットキャッシュが力の源。** 約 500 語のファイルが直近コンテキストを捕捉。新セッションは最小トークンコストでフルコンテキストから始まる。

**Obsidian は IDE、Claude はプログラマ。** グラフビューは何が繋がっているかを示す。人間はソースをキュレーションし質問する。それ以外のすべての書き込みと維持は Claude が担当。
