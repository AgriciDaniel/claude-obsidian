---
type: meta
title: "ウィキ索引"
aliases: ["Wiki Index", "ウィキ索引"]
updated: 2026-04-29
tags:
  - meta
  - index
status: evergreen
related:
  - "[[overview]]"
  - "[[log]]"
  - "[[hot]]"
  - "[[dashboard]]"
  - "[[Wiki Map]]"
  - "[[concepts/_index]]"
  - "[[entities/_index]]"
  - "[[sources/_index]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Hot Cache]]"
  - "[[Compounding Knowledge]]"
  - "[[Andrej Karpathy]]"
---

# ウィキ索引

最終更新: 2026-04-29 | 総ページ数: 34 | 取り込み済みソース: 2

ナビゲーション: [[overview]] | [[log]] | [[hot]] | [[dashboard]] | [[Wiki Map]] | [[getting-started]]

> **言語**: 日本語ローカライズ版。各ページの `aliases:` に英語ファイル名と日本語表示名を併記。`[[Hot Cache]]` でも `[[ホットキャッシュ]]` でも解決可能。

---

## 概念

- [[LLM Wiki Pattern]] — LLM を使って永続的・複利的なナレッジベースを構築するパターン(ステータス: mature)
- [[Hot Cache]] — 取り込み・セッションごとに更新される約 500 語のセッションコンテキストファイル(ステータス: mature)
- [[Compounding Knowledge]] — RAG と違いウィキの知識が時間と共に価値を増す理由(ステータス: mature)
- [[cherry-picks]] — エコシステムリサーチからの優先機能バックログ。claude-obsidian に追加すべき 13 機能(ステータス: current)
- [[SVG Diagram Style Guide]] — 全図表の正規ビジュアルスタイル: Space Grotesk、#0A0A0A ダークテーマ、#E07850 アクセント、フルデザイントークン(ステータス: evergreen)
- [[Pro Hub Challenge]] — claude-seo/claude-blog 拡張構築のためのコミュニティチャレンジパターン。最初のチャレンジで 6 提出、5 件を v1.9.0 で統合(ステータス: evergreen)
- [[Semantic Topic Clustering]] — 有料ツールを置き換える SERP ベースのキーワードグルーピング。ハブ・スポーク構造とインタラクティブ可視化(ステータス: evergreen)
- [[Search Experience Optimization]] — ページタイプミスマッチ検出とペルソナスコアリングのための「SERP を逆から読む」方法論(ステータス: evergreen)
- [[SEO Drift Monitoring]] — 17 の比較ルールと SQLite 永続化を持つ「SEO 用の git」ベースライン/差分/追跡(ステータス: evergreen)
- [[DragonScale Memory]] — Heighway ドラゴン曲線にインスパイアされた記憶層仕様。fold オペレータ、決定論的ページアドレス、セマンティックタイリング、境界優先 autoresearch(ステータス: shipped v0.4、4 メカニズムすべてオプトイン)
- [[Persistent Wiki Artifact]]: 一過性のチャットターンと区別される、LLM の記憶対象としての永続的 Markdown ページ(ステータス: developing)
- [[Source-First Synthesis]]: 由来規律。生ソースは不変のまま、ウィキ層は合成され引用される(ステータス: developing)
- [[Query-Time Retrieval]]: ウィキクエリパスは引用付きで合成。Obsidian の Vault 内検索と相補的(ステータス: developing)

---

## エンティティ

- [[Andrej Karpathy]] — AI 研究者、LLM Wiki パターンの創案者、元 Tesla AI ディレクター(ステータス: developing)
- [[Ar9av-obsidian-wiki]] — マルチエージェント互換の LLM Wiki プラグイン。デルタ追跡マニフェスト(ステータス: current)
- [[Nexus-claudesidian-mcp]] — ネイティブ Obsidian プラグイン + MCP ブリッジ。ワークスペース記憶、タスク管理(ステータス: current)
- [[ballred-obsidian-claude-pkm]] — ゴールカスケード PKM。自動コミット hook、`/adopt` コマンド(ステータス: current)
- [[rvk7895-llm-knowledge-bases]] — 3 段深さクエリシステム、Marp スライド、並列ディープリサーチ(ステータス: current)
- [[kepano-obsidian-skills]] — Obsidian 開発者による公式スキル。defuddle、obsidian-bases(ステータス: current)
- [[Claudian-YishenTu]] — Claude Code を埋め込むネイティブ Obsidian プラグイン。プランモード、@ メンション(ステータス: current)
- [[Claude SEO]] — SEO 解析用 Tier 4 Claude Code スキル。v1.9.0 で 23 スキル、17 エージェント、30 スクリプト(ステータス: evergreen)

---

## ソース

- [[claude-obsidian-ecosystem-research]] — 2026-04-08 | 16 以上のリポジトリへの Web リサーチ | 8 ウィキページ作成

---

## 質問

- [[How does the LLM Wiki pattern work]] — このパターンがどう動くか、なぜ人間規模で RAG を超えるか(ステータス: developing)

---

## 比較

- [[Wiki vs RAG]] — ウィキナレッジベースと RAG をいつ使い分けるか。判定: 1000 ページ未満ではウィキが勝る
- [[claude-obsidian-ecosystem]] — 16 以上の Claude+Obsidian プロジェクトの機能マトリクス。claude-obsidian の勝ちポイントとギャップ

---

## 決定

- [[2026-04-14-community-cta-rollout]] - Skool コミュニティ CTA フッターを 6 のスキルリポジトリに追加、ツールごとの頻度ルール付き(ステータス: active)
- [[2026-04-15-slides-and-release-session]] - Claude SEO v1.9.0 スライド(15 枚 HTML デッキ)+ PDF アセット付きの GitHub リリース v1.9.0(ステータス: complete)
- [[2026-04-15-release-report-session]] - Claude SEO v1.9.0 リリースレポート PDF: ダークテーマ、13 ページ、WeasyPrint レイアウト修正、Challenge v2 追加(ステータス: complete)
- [[2026-04-14-claude-seo-v190-session]] - Claude SEO v1.9.0 Pro Hub Challenge 統合: 5 提出、4 新規スキル、4 レビューラウンド、サイバーセキュリティ監査(ステータス: complete)

---

## ドメイン

<!-- 足場後にドメインエントリを追加 -->

---

## Fold(DragonScale Mechanism 1)

- [[fold-k3-from-2026-04-23-to-2026-04-24-n8]] — k=3、子 8 件、最初の本番 fold(2026-04-24)
