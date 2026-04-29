---
type: meta
title: "ダッシュボード"
updated: 2026-04-08
aliases:
  - dashboard
  - "ダッシュボード"
tags:
  - meta
  - dashboard
status: evergreen
related:
  - "[[index]]"
  - "[[overview]]"
  - "[[log]]"
  - "[[concepts/_index]]"
  - "[[Compounding Knowledge]]"
---

# Wikiダッシュボード

ナビゲーション: [[index]] | [[overview]] | [[log]] | [[hot]]

ダッシュボードは**Obsidian Bases**を使用しています。v1.9.10(2025年8月)で同梱されたObsidianのコア機能で、プラグインのインストールは不要です。

> [!tip] 埋め込みBasesビュー
> 対話型のダッシュボードは[[dashboard.base]]にあります。そのファイルを直接開くか、以下の埋め込みを利用してください。

![[dashboard.base]]

---

## レガシーDataviewダッシュボード(任意)

Obsidian < 1.9.10を使用している、もしくはDataviewを好む場合、以下のクエリも引き続き動作します。Dataviewコミュニティプラグインをインストールするだけで使えます。

### 最近のアクティビティ

```dataview
TABLE type, status, updated FROM "wiki" SORT updated DESC LIMIT 15
```

### シードページ(発展が必要)

```dataview
LIST FROM "wiki" WHERE status = "seed" SORT updated ASC
```

### 出典が無いエンティティ

```dataview
LIST FROM "wiki/entities" WHERE !sources OR length(sources) = 0
```

### 未解決の質問

```dataview
LIST FROM "wiki/questions" WHERE status = "developing" OR status = "seed" SORT updated DESC
```

### 比較

```dataview
TABLE verdict FROM "wiki/comparisons" SORT updated DESC
```

### 出典

```dataview
TABLE author, date_published, updated FROM "wiki/sources" WHERE type = "source" SORT updated DESC LIMIT 10
```
