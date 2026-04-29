---
type: concept
title: "永続的な Wiki アーティファクト"
created: 2026-04-24
updated: 2026-04-24
tags:
  - llm-wiki
  - knowledge-management
  - agent-memory
status: developing
aliases:
  - "Persistent Wiki Artifact"
  - "永続的な Wiki アーティファクト"
related:
  - "[[How does the LLM Wiki pattern work?]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[Source-First Synthesis]]"
  - "[[Query-Time Retrieval]]"
---

# 永続的な Wiki アーティファクト

永続的な Wiki アーティファクトとは、生のソースと将来の質問の間に置かれる、維持された Markdown 層のことである。Karpathy の LLM Wiki 記述では、エージェントはソース資料を読み、重要情報を抽出し、回答時にチャンクを取得するだけでなく、相互リンクされた Wiki に統合する: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## 埋められる境界

選択された質問は LLM Wiki が知識を複利で増やすことを説明しているが、メモリの単位としてアーティファクト自体を切り出してはいない。本ページはその境界を明確にする。メモリは、閲覧、リンク、レビュー、改訂が可能なファイルに保存される。

## 抽出された主張

- LLM Wiki パターンは、生のソース、生成された Wiki、スキーマ文書を別々の層として定義している: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- そのパターンでは、生のソース集合は不変として扱われ、Wiki 層は LLM が所有・維持する: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- パターンは Wiki を複利で増えるアーティファクトとして位置付け、相互参照、矛盾フラグ、合成は後続の質問にまたがって永続する: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Obsidian は `[[Three laws of motion]]` のような Wikilink をサポートしており、Markdown ファイルが内部のノートネットワークを形成できる: https://obsidian.md/help/links
- Obsidian は vault の設定によって、ファイル名変更時に内部リンクを自動更新できる: https://obsidian.md/help/links

## 本 vault への含意

- 永続的なメモリオブジェクトはチャットターンではなくページである。
- ページにはフロントマター、安定したタイトル、Wikilink、ソース URL が必要であり、後続のエージェントが来歴を確認できるようにする。
- ページは直接改訂できる程度に小さく保つべきだ。LLM Wiki パターンは、新しいソースが届いたときに既存の合成を更新することに依存しているからだ: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## 一次ソース

- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- https://obsidian.md/help/links
