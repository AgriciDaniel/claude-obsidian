---
type: question
title: "LLM Wikiパターンはどう機能するのか?"
aliases: ["How does the LLM Wiki pattern work", "LLM Wikiパターンはどう機能するのか"]
question: "LLM Wikiパターンはどう機能するのか? なぜRAGより優れているのか?"
answer_quality: definitive
created: 2026-04-07
updated: 2026-04-07
tags:
  - question
  - llm-wiki
  - knowledge-management
status: developing
related:
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[Hot Cache]]"
  - "[[index]]"
  - "[[Wiki vs RAG]]"
sources: []
---

# LLM Wikiパターンはどう機能するのか?

**質問:** LLM Wikiパターンはどう機能するのか? なぜRAGより優れているのか?

## 回答

[[LLM Wiki Pattern]] はLLMを検索エンジンではなく知識アーキテクトとして機能させる。

**標準的なRAG**(Retrieval-Augmented Generation): 各クエリで生のドキュメントを検索し、チャンクを取得し、ゼロから回答を組み立てる。何も積み上がらない。同じ質問を二度すれば、二度同じ作業を行う。

**ウィキパターン** はこれと異なる。ソースが届くと、LLMはそれを読んで統合する。エンティティページを更新し、矛盾を記録し、クロスリファレンスを追加する。シンセシスは一度行えば永続する。すべてのクエリは過去の取り込みの恩恵を受ける。

### 3つのレイヤー

1. **`.raw/`** — ソースドキュメント。不変。Claudeは読み取るだけで変更しない。
2. **`wiki/`** — Claudeが生成する知識。サマリー、エンティティ、概念、シンセシス。
3. **`CLAUDE.md`** — スキーマ。ウィキの構造とClaudeの振る舞いを定義する。

### なぜ累積するのか

完全な議論は [[Compounding Knowledge]] を参照。要点としては、新しいソースが1ページを追加するだけでなく、既存の8〜15ページを充実させるという点にある。価値が宿るのは生のコンテンツそのものではなく、ページ間の接続である。

### ホットキャッシュという近道

[[Hot Cache]](wiki/hot.md)は最近の文脈の約500語のサマリー。新規セッションはこれを最初に読む。クロスプロジェクト参照もこれを最初に読む。「どこまで進んでいたか?」という問いに答えるためにウィキ全体を読み直すのを防ぐ。

(ソース: [[LLM Wiki Pattern]])

## 確信度

definitive — これはこのボールト全体が体現している中心概念である。
