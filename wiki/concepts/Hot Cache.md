---
type: concept
title: "ホットキャッシュ"
complexity: basic
domain: knowledge-management
aliases:
  - "Hot Cache"
  - "ホットキャッシュ"
  - "hot.md"
  - "Session Cache"
  - "Context Cache"
created: 2026-04-07
updated: 2026-04-07
tags:
  - concept
  - knowledge-management
  - context
status: mature
related:
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[index]]"
  - "[[hot]]"
  - "[[concepts/_index]]"
sources:
---

# ホットキャッシュ

Wiki vault における最新コンテキストを約 500 語にまとめた要約。`wiki/hot.md` に保存される。各セッションの終わり、および重要な ingest やクエリの後に毎回更新される。

ホットキャッシュは「前回どこで終わったか」という一つの問いに答えるために存在する。新しいセッションはまず `hot.md` を読む。そこに答えがあれば、Wiki の他の部分を巡回する必要はない。

---

## 何を保存するか

- 直近で ingest または議論した内容
- 重要な最近の事実と要点
- 最近作成または更新されたページ
- 進行中のスレッドと未解決の問い
- 現在ユーザーが集中していること

---

## フォーマット

```markdown
---
type: meta
title: "Hot Cache"
updated: YYYY-MM-DDTHH:MM:SS
---

# Recent Context

## Last Updated
YYYY-MM-DD — [what happened]

## Key Recent Facts
- [Most important recent takeaway]
- [Second]

## Recent Changes
- Created: new wiki pages from this ingest
- Updated: existing pages with new connections
- Flagged: contradictions between sources where found

## Active Threads
- User is researching [topic]
- Open question: [thing being investigated]
```

---

## ルール

- 500 語以内に保つこと。これはキャッシュであってジャーナルではない。
- 毎回完全に上書きする。追記式ではない。
- 一つのファイル。日付ごとに分割しない。
- ingest のたび、重要なクエリのたび、各セッションの終わりに更新する。

---

## なぜ重要か

ホットキャッシュがないと、各セッションはコールドスタートになる。index を読み(1000 トークン)、いくつかのドメインのサブインデックスを読み、複数の個別ページを読む必要がある。ホットキャッシュがあれば、最初の 500 トークンに必要なものがほぼ全て揃っていることが多い。

実際の運用では、エグゼクティブアシスタント vault に `hot.md` を加えたことで、複数の Wiki ページを巡回する場合と比較してセッション開始時のトークンコストが大幅に削減された。

ホットキャッシュは特にクロスプロジェクト構成で価値が高い。別の Claude Code プロジェクトがこの vault を指し示し、まず `hot.md` を読むだけで最小トークンコストで最近のコンテキストを得られる。

---

## 関連

ホットキャッシュは [[LLM Wiki Pattern]] のトークン規律戦略の一部だ。広範なナビゲーションについては [[index]] を参照。
