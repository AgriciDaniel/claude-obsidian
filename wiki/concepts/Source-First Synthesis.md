---
type: concept
title: "ソース優先の合成"
created: 2026-04-24
updated: 2026-04-24
tags:
  - llm-wiki
  - synthesis
  - provenance
status: developing
aliases:
  - "Source-First Synthesis"
  - "ソース優先の合成"
related:
  - "[[How does the LLM Wiki pattern work?]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[Persistent Wiki Artifact]]"
  - "[[Query-Time Retrieval]]"
---

# ソース優先の合成

ソース優先の合成とは、生のソースを生成された Wiki から分離して保ちつつ、Wiki にそれらのソースの引用と統合を要求する LLM Wiki の実践である。Karpathy のパターンは、生のソースを真実の源、生成された Wiki を維持された合成層として記述している: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## 埋められる境界

選択された質問は Wiki パターンがソースを統合すると述べているが、来歴の規律を明示していない。本ページはそのルールを記録する。合成は書き換え可能だが、ソース資料は引用される錨であり続ける。

## 抽出された主張

- Karpathy の LLM Wiki パターンは、生のソースが記事、論文、画像、データファイルを含み得ること、また LLM はそれらを変更せずに読むことを述べている: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- 同ソースは、Wiki を、要約、エンティティページ、概念ページ、比較、概要、合成として記述しており、これらは LLM によって維持される: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- ingest 操作は、ソース要約を作成し、インデックスを更新し、関連するエンティティと概念のページを更新し、ログエントリを追記できる: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- query 操作は、関連 Wiki ページを読み、引用付きで回答を合成する。有用な回答は Wiki に戻してファイルできる: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- RAG 論文は、知識集約型生成システムの未解決問題として、来歴と世界知識の更新を挙げている: https://arxiv.org/abs/2005.11401

## 運用ルール

ソース優先の合成は、出典なしの要約より厳格である。新しい概念ページは使用したソースを明示し、何を抽出したかを述べ、生成されたページをソース文書の代替として扱わないようにすべきだ。

## 一次ソース

- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- https://arxiv.org/abs/2005.11401
