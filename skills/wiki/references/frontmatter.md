# Frontmatter スキーマ

すべての wiki ページはフラットな YAML frontmatter で始まる。オブジェクトをネストしない。Obsidian の Properties UI はフラットな構造を要求する。

> **言語ルール**: frontmatter のキー名と列挙値は英語のまま。`title:` の値、`description:` の値、`question:` の値などは日本語可。`aliases:` には英語ファイル名と日本語表示名を併記する。

---

## 共通フィールド

すべてのページに(例外なし):

```yaml
---
type: <source|entity|concept|domain|comparison|question|overview|meta>
title: "人間が読むタイトル(日本語可)"
aliases: ["English Filename Slug", "日本語表示名"]
created: 2026-04-07
updated: 2026-04-07
tags:
  - <domain-tag>
  - <type-tag>
status: <seed|developing|mature|evergreen>
related:
  - "[[Other Page]]"
sources:
  - "[[.raw/articles/source-file.md]]"
---
```

**status の値:**
- `seed`: 存在するが populate されていない
- `developing`: 実コンテンツあり、未完成
- `mature`: 包括的、リンクが豊富
- `evergreen`: 更新がほぼ不要

---

## タイプ別追加フィールド

### source

共通フィールドの後に追加:

```yaml
source_type: article    # article | video | podcast | paper | book | transcript | data
author: ""
date_published: YYYY-MM-DD
url: ""
confidence: high        # high | medium | low
key_claims:
  - "このソースの最初の主要主張"
  - "2 つ目の主要主張"
```

### entity

```yaml
entity_type: person     # person | organization | product | repository | place
role: ""
first_mentioned: "[[Source Title]]"
```

### concept

```yaml
complexity: intermediate  # basic | intermediate | advanced
domain: ""
aliases:
  - "別名(日本語可)"
  - "略称"
```

### comparison

```yaml
subjects:
  - "[[Thing A]]"
  - "[[Thing B]]"
dimensions:
  - "性能"
  - "コスト"
  - "使いやすさ"
verdict: "1 行の結論。"
```

### question

```yaml
question: "聞かれた元のクエリ。"
answer_quality: solid   # draft | solid | definitive
```

### domain

```yaml
subdomain_of: ""        # トップレベルドメインなら空
page_count: 0
```

---

## ルール

1. フラットな YAML のみ使用。オブジェクトをネストしない。
2. 日付は `YYYY-MM-DD` の文字列。ISO 日時ではない。
3. リストは常に `- item` 形式。インラインの `[a, b, c]` ではない。
4. YAML フィールド内の wikilink は引用符必須: `"[[Page Name]]"`。
5. `related` と `sources` は wikilink にする。プレーン URL ではない。
6. ページ内容を編集するたびに `updated` を更新。
7. **日本語ローカライズ版**: `aliases:` を必ず付け、英語ファイル名と日本語表示名の両方を含める。
