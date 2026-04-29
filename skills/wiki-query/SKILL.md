---
name: wiki-query
description: "Obsidian ウィキ Vault を使って質問に回答する。まずホットキャッシュ、次に index、それから関連ページを読む。引用付きで回答を合成し、良い回答は wiki ページとして保存する。Quick / Standard / Deep の 3 モード対応。回答は日本語で行い、wikilink で出典を引用する(プロジェクト CLAUDE.md の言語ポリシー参照)。トリガー(日本語): 何を知ってる、wiki に聞く、X とは、説明して、要約して、wiki から探して、wiki を検索、wiki に基づいて、quick query、deep query。Triggers (English): what do you know about, query:, what is, explain, summarize, find in wiki, search the wiki, based on the wiki, wiki query quick, wiki query deep."
allowed-tools: Read Glob Grep
---

# wiki-query: ウィキへの問い合わせ

ウィキは合成作業を済ませてある。戦略的に読み、的確に答え、良い回答を戻して保存することで知識を複利で積み上げる。**回答は日本語で書く**。出典は wikilink で引用する。

---

## クエリモード

3 段階の深さ。質問の複雑さに応じて選択。

| モード | トリガー | 読む対象 | トークン目安 | 適用 |
|------|---------|-------|------------|---------|
| **Quick** | `query quick: ...` または単純な事実質問 | hot.md + index.md のみ | 約 1,500 | 「X とは?」、日付確認、簡単な事実 |
| **Standard** | デフォルト(フラグ無し) | hot.md + index + 3〜5 ページ | 約 3,000 | ほとんどの質問 |
| **Deep** | `query deep: ...` または「徹底的」「網羅的」 | フル wiki + 任意で web | 約 8,000+ | 「A vs B を全方位比較」、合成、ギャップ分析 |

---

## Quick モード

ホットキャッシュや index 要約に答えがありそうなときに使う。

1. `wiki/hot.md` を読む。質問に答えられたら即応答。
2. 答えられなければ `wiki/index.md` を読む。説明文をスキャンして答えを探す。
3. index 要約に答えがあれば、そのまま応答。ページは開かない。
4. 見つからなければ「クイックキャッシュにありません。Standard で検索しますか?」と返す。

Quick モードでは個別の wiki ページは開かない。

---

## Standard クエリワークフロー

1. **まず `wiki/hot.md`** を読む。すでに答えや直接関連する文脈があるかも。
2. **`wiki/index.md`** を読み、最も関連するページを特定(タイトルと説明をスキャン)。
3. それらのページを **読む**。主要エンティティは深さ 2 まで wikilink を辿る。それ以上深く行かない。
4. チャットで回答を **合成**。出典は wikilink で引用: `(出典: [[Page Name]])`。
5. **保存を提案**: 「この分析は保存しておく価値がありそうです。`wiki/questions/answer-name.md` として保存しますか?」
6. 質問で **ギャップ** が見えた場合: 「X についての情報が不足しています。ソースを探しますか?」

---

## Deep モード

合成質問、比較、「X について全部教えて」などに使う。

1. `wiki/hot.md` と `wiki/index.md` を読む。
2. 関連セクションを全部特定(concepts、entities、sources、comparisons)。
3. 関連ページをすべて読む。スキップなし。
4. wiki のカバレッジが薄ければ web 検索で補完を提案。
5. 完全な引用付きで網羅的な回答を合成。
6. 結果は必ず wiki ページとして保存。深い回答を失うのは惜しい。

---

## トークン規律

最小限を読む:

| 開始位置 | トークン目安 | 停止条件 |
|------------|---------------|--------------|
| hot.md | 約 500 トークン | 答えがあれば |
| index.md | 約 1000 トークン | 関連 3〜5 ページを特定できれば |
| wiki ページ 3〜5 件 | 各約 300 トークン | 通常はこれで十分 |
| wiki ページ 10 件以上 | 高コスト | wiki 全体に跨る合成のみ |

hot.md に答えがあればそれ以上読まずに応答。

---

## index 形式リファレンス

マスター index(`wiki/index.md`)はこのような形:

```markdown
## ドメイン
- [[Domain Name]] — 説明(N 件のソース)

## エンティティ
- [[Entity Name]] — 役割(初出: [[Source]])

## 概念
- [[Concept Name]] — 定義(ステータス: developing)

## ソース
- [[Source Title]] — 著者、日付、種別

## 質問
- [[Question Title]] — 回答要約
```

セクションの見出しを先にスキャンしてどれを読むか判断する。

---

## ドメインサブインデックス形式

各ドメインフォルダには焦点を絞った検索用に `_index.md` がある:

```markdown
---
type: meta
title: "エンティティ索引"
aliases: ["Entities Index"]
updated: YYYY-MM-DD
---
# エンティティ

## 人物
- [[Person Name]] — 役割、所属

## 組織
- [[Org Name]] — 何をしているか

## 製品
- [[Product Name]] — カテゴリ
```

質問が 1 ドメインに絞られているときはサブインデックスを使う。狭いクエリでマスター index 全体を読むのは避ける。

---

## 回答の保存

良い回答は wiki に複利で積み上がる。気づきをチャット履歴に消えさせない。

回答を保存するとき:

```yaml
---
type: question
title: "短い説明的タイトル"
aliases: ["Short Descriptive Title"]
question: "聞かれた正確なクエリ"
answer_quality: solid
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [question, <domain>]
related:
  - "[[回答で参照したページ]]"
sources:
  - "[[wiki/sources/relevant-source.md]]"
status: developing
---
```

そして本文に回答を書く。引用を含める。言及した概念やエンティティすべてに wikilink を張る。

保存後、`wiki/index.md` の Questions セクションにエントリを追加し、`wiki/log.md` に追記する。

---

## ギャップ処理

wiki から回答できない質問の場合:

1. はっきり言う: 「wiki にはこの質問にうまく答える材料が足りません。」
2. 具体的なギャップを特定: 「[サブトピック] については何もありません。」
3. 提案: 「これに関するソースを探しますか?検索やソース処理を手伝えます。」
4. 捏造しない。この wiki の特定ドメインの質問にはトレーニングデータから答えない。
