# Fold ページテンプレート

`wiki-fold` の正規出力形式。すべての fold ページはこのレイアウトを正確に使う。

> **言語ルール**: テーブル列ラベル・要約・主題の文言は日本語で書く。frontmatter のキー名と列挙値、`fold_id` 値、wikilink ターゲット、`op:` の値(`save`/`ingest`/`fold`/`session`/`setup`/`decision`)は英語のまま。

---

## frontmatter

```yaml
---
type: fold
title: "Fold k{K} — {EARLIEST-DATE} 〜 {LATEST-DATE} — n{COUNT}"
fold_id: "fold-k{K}-from-{EARLIEST-DATE}-to-{LATEST-DATE}-n{COUNT}"
batch_exponent: {K}
entry_count: {COUNT}
entry_range:
  from: "{EARLIEST-CHILD-DATE}"
  to: "{LATEST-CHILD-DATE}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
tags:
  - meta
  - fold
  - "fold/k{K}"
status: mature
children:
  - date: "{YYYY-MM-DD}"
    op: "{save|ingest|fold|session|setup|decision}"
    title: "{log エントリのタイトルそのまま}"
    page: "[[{正規ページ wikilink}]]"
    page_missing: false
  # ... log エントリ 1 件につき 1 レコード。ページで dedupe しない。
related:
  - "[[DragonScale Memory]]"
  - "[[log]]"
  - "[[index]]"
---
```

すべてのフィールド必須。欠落はドライラン失敗。`title` に現在の日付を含めない。`fold_id` は決定論的でファイル名と一致。

---

## 本文セクション(順序、すべて必須)

### 1. スコープ(1 段落)

```markdown
レベル {K} の fold、{COUNT} 件の log エントリを {FROM} 〜 {TO} の範囲でカバー。主要テーマ: {THEME-1}, {THEME-2}, {THEME-3}。
```

### 2. 子エントリ

log エントリ 1 件につき 1 行。行数は frontmatter の `entry_count` と `children:` の長さに一致しなければならない。

```markdown
## 子エントリ

| 日付 | Op | タイトル | ページ | 要約(抽出的) |
|---|---|---|---|---|
| 2026-04-23 | save | DragonScale Memory v0.2 — 敵対レビュー後 | [[DragonScale Memory]] | 敵対レビュー後の書き直し。7/7 の批評を 1 件の外科的修正後に受け入れ。 |
| 2026-04-15 | save | Claude SEO v1.9.0 スライドと GitHub リリース | [[2026-04-15-slides-and-release-session]] | 15 スライド HTML デッキ、v1.9.0 タグ付け、PDF アセット付き GitHub リリース。 |
<!-- log エントリ 1 件につき 1 行。ページで dedupe しない -->
```

要約列は抽出的: log エントリの箇条書きを 1 文で言い換え。出典が曖昧なら推測せず「ソースで曖昧」と書く。

### 3. 主要 Outcome(3〜7 箇条、抽出的)

各箇条は引用元の特定の子エントリ(日付)を引用。各数値は当該子エントリで grep 検証可能。出力前にカウントチェック。

```markdown
## 主要 Outcome

- {具体的な変更 1、子エントリを引用または言い換え}(2026-04-14 セッションエントリより)
- {具体的な変更 2、ソースで grep 検証された数値付き}(2026-04-10 セッションエントリより)
<!-- 最大 7 箇条。各箇条は具体的な成果物または決定を名指し、出典エントリを引用 -->
```

### 4. エントリ横断テーマ(0〜4 箇条、貢献エントリを必ず名指し)

テーマは任意。少なくとも 2 つの貢献子エントリを名指しできないテーマは書かない。

```markdown
## エントリ横断テーマ

- {テーマ: 複数エントリでサポートされるパターンを記述}(サポート: 2026-04-14、2026-04-15、2026-04-23 のエントリ)
```

fold を正当化するためにテーマを発明しない。エントリ横断パターンが無ければ「エントリ横断テーマは検出されず。本範囲内のエントリは互いに独立。」と書く。

### 5. 矛盾または訂正

```markdown
## 矛盾または訂正

- 検出なし。
```

または存在する場合:

```markdown
## 矛盾または訂正

- [[Earlier Entry]] は X を主張、[[Later Entry]] が Y に訂正。解決: {ステータス}。
```

### 6. リンク

`子ページ` セクションは **ページで dedupe**: 複数の log エントリが同一ページを指していてもユニークなターゲットページごとに 1 wikilink。これがグラフ接続セクションで、frontmatter の `children:`(log エントリごと、dedupe なし)とは別。

```markdown
## 子ページ

- [[{UNIQUE-PAGE-1}]]
- [[{UNIQUE-PAGE-2}]]
<!-- ページで dedupe。エントリごとのレコードは frontmatter の `children:` 参照 -->

## 関連

- [[DragonScale Memory]] — fold オペレータ仕様
- [[log]] — ソースエントリ
- [[index]] — Vault カタログ
```

---

## 注

- ホットキャッシュ更新なし: それは save/ingest スキルの責務。
- 子ページの編集なし。fold は子に対して厳密に読み取り専用。
- 子エントリの参照ページが欠落していたら、要約列に「ソース欠落」と書き、内容を捏造しない。
- 本文は簡潔。fold はロールアップであって再話ではない。k=4 fold で合計 200〜400 行を目標。
