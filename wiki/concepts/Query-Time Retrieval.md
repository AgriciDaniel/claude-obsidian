---
type: concept
title: "クエリ時取得"
created: 2026-04-24
updated: 2026-04-24
tags:
  - rag
  - retrieval
  - llm-wiki
status: developing
aliases:
  - "Query-Time Retrieval"
  - "クエリ時取得"
related:
  - "[[How does the LLM Wiki pattern work?]]"
  - "[[Wiki vs RAG]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Persistent Wiki Artifact]]"
  - "[[Source-First Synthesis]]"
---

# クエリ時取得

クエリ時取得とは、LLM Wiki と対比される基準的なメモリパターンである。ユーザーが質問した時点で関連資料を取得し、取得したコンテキストから回答を生成する。

## 埋められる境界

選択された質問は Wiki の蓄積を RAG と対比しているが、取得側を厳密には定義していない。本ページは元の RAG 論文と LLM Wiki gist でその対比を裏付ける。

## 抽出された主張

- RAG 論文は、検索拡張生成をパラメトリックメモリとノンパラメトリックメモリを言語生成に組み合わせるものとして定義している: https://arxiv.org/abs/2005.11401
- RAG 論文は、ノンパラメトリックメモリを、ニューラル検索器でアクセスする Wikipedia の密ベクトルインデックスとして記述している: https://arxiv.org/abs/2005.11401
- 同論文は、評価された生成タスクにおいて、RAG モデルがパラメトリックのみの seq2seq ベースラインよりも具体的、多様、事実的な言語を生成したと報告している: https://arxiv.org/abs/2005.11401
- Karpathy の LLM Wiki gist は、一般的な文書ワークフローを、ファイルのアップロード、クエリ時の関連チャンク取得、回答生成として記述している: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Karpathy の LLM Wiki gist は、このクエリ時パターンが合成を蓄積する代わりに、毎回モデルに知識を再発見・再構成させると述べている: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- MemGPT 論文は、LLM の限られたコンテキストウィンドウを長時間の会話と文書解析に対する制約として位置付け、メモリ階層をまたぐ仮想コンテキスト管理を提案している: https://arxiv.org/abs/2310.08560

## Wiki メモリとの対比

クエリ時取得は回答時に外部のエビデンスを提供できる。LLM Wiki パターンは、後続のクエリが届く前にソース資料を維持されたページにコンパイルすることで、作業の一部を前倒しにする: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## 一次ソース

- https://arxiv.org/abs/2005.11401
- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- https://arxiv.org/abs/2310.08560
