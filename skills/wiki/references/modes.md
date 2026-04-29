# ウィキモード

6 つのモードでよくあるユースケースをカバー。フィットするものを選ぶか、組み合わせる。応答テキストとフォルダ説明は日本語で書く。

---

## モード A: Website / Sitemap

使用場面: 「自分のサイトのサイトマップウィキを作って」「コンテンツのギャップを把握」「SEO 監査ウィキ」

```
vault/
├── .raw/              # クロールエクスポート、解析、スクレイプページ、GSC データ
├── wiki/
│   ├── pages/         # URL 1 件ずつ: ステータス、メタ、コンテンツ要約
│   ├── structure/     # サイトアーキテクチャ、ナビ階層、内部リンクマップ
│   ├── audits/        # コンテンツのギャップ、リダイレクト要件、薄いコンテンツ
│   ├── keywords/      # キーワードクラスタ、ターゲットページ割当
│   └── entities/      # ブランド、執筆者、トピックハブ
├── _meta/
│   ├── index.md
│   └── log.md
└── CLAUDE.md
```

`wiki/pages/` ノートの frontmatter:
```yaml
---
type: page
url: "https://example.com/page-slug"
status: live          # live | redirect | 404 | stub | no-index
title: ""
h1: ""
meta_description: ""
word_count: 0
has_schema: false
indexed: true
canonical: ""
internal_links_in: 0
internal_links_out: 0
last_crawled: YYYY-MM-DD
tags: [page]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

作成すべき主要 wiki ページ: `[[Site Overview]]`, `[[Navigation Structure]]`, `[[Content Gaps]]`, `[[Redirect Map]]`, `[[Keyword Clusters]]`(`aliases:` に日本語名を併記)

---

## モード B: GitHub / Repository

使用場面: 「コードベースをマップ」「リポジトリのアーキテクチャウィキ」「このプロジェクトを理解」

```
vault/
├── .raw/              # README、git log エクスポート、コードダンプ、issue エクスポート
├── wiki/
│   ├── modules/       # 主要モジュール / パッケージ / サービスごとに 1 ノート
│   ├── components/    # 再利用可能な UI または機能コンポーネント
│   ├── decisions/     # アーキテクチャ決定記録(ADR)
│   ├── dependencies/  # 外部依存、バージョン、リスク評価
│   └── flows/         # データフロー、リクエストパス、認証フロー
├── _meta/
│   ├── index.md
│   └── log.md
└── CLAUDE.md
```

`wiki/modules/` ノートの frontmatter:
```yaml
---
type: module           # module | component | decision | dependency | flow
path: "src/auth/"
status: active         # active | deprecated | experimental | planned
language: typescript
purpose: ""
maintainer: ""
last_updated: YYYY-MM-DD
linked_issues: []
depends_on: []
used_by: []
tags: [module]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

作成すべき主要 wiki ページ: `[[Architecture Overview]]`, `[[Data Flow]]`, `[[Tech Stack]]`, `[[Dependency Graph]]`, `[[Key Decisions]]`

---

## モード C: Business / Project

使用場面: 「プロジェクトウィキ」「競合インテリジェンス」「チームナレッジベース」「会議メモ」

```
vault/
├── .raw/              # 会議トランスクリプト、Slack エクスポート、ドキュメント、メール
├── wiki/
│   ├── stakeholders/  # 人物、企業、意思決定者
│   ├── decisions/     # 重要な決定、根拠と日付
│   ├── deliverables/  # マイルストーン、成果物、ステータス追跡
│   ├── intel/         # 競合分析、市場調査
│   └── comms/         # 合成された会議メモ、主要スレッド
├── _meta/
│   ├── index.md
│   └── log.md
└── CLAUDE.md
```

`wiki/decisions/` ノートの frontmatter:
```yaml
---
type: decision         # stakeholder | decision | deliverable | intel | meeting | competitor
status: active         # active | pending | done | blocked | superseded
priority: 3            # 1(最高)〜 5(最低)
date: YYYY-MM-DD
owner: ""
due_date: ""
context: ""
tags: [decision]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

作成すべき主要 wiki ページ: `[[Project Overview]]`, `[[Stakeholder Map]]`, `[[Decision Log]]`, `[[Competitor Landscape]]`

---

## モード D: Personal / Second Brain

使用場面: 「個人セカンドブレイン」「目標を追跡」「ジャーナル合成」「人生ウィキ」

```
vault/
├── .raw/              # ジャーナル、記事、ポッドキャストメモ、音声トランスクリプト
├── wiki/
│   ├── goals/         # 個人および専門の目標、進捗追跡付き
│   ├── learning/      # 習得中の概念、スキル開発
│   ├── people/        # 関係性、共通文脈、フォローアップ
│   ├── areas/         # 人生領域: 健康、財政、キャリア、創造
│   └── resources/     # 書籍、コース、参照価値のあるツール
├── _meta/
│   ├── index.md
│   ├── log.md
│   └── hot-cache.md   # 最もアクティブな文脈の約 500 語要約
└── CLAUDE.md
```

`wiki/goals/` ノートの frontmatter:
```yaml
---
type: goal             # goal | concept | person | area | resource | reflection
status: active         # active | paused | completed | abandoned
area: career           # health | career | finance | creative | relationships | growth
priority: 1
target_date: YYYY-MM-DD
progress: 0            # 0〜100 パーセント
tags: [goal]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

ホットキャッシュノート: `_meta/hot-cache.md` は約 500 語のファイルで Claude が各セッション終了時に更新。現在のフォーカス領域、最近の成果、未解決スレッドを捕捉。「どこまで進んだ?」に答えるために wiki 全体をクロールする必要が無くなる。

作成すべき主要 wiki ページ: `[[North Star]]`, `[[Weekly Review Template]]`, `[[Annual Goals]]`

---

## モード E: Research

使用場面: 「[トピック] のリサーチウィキ」「読んでる論文を追跡」「論文執筆」

```
vault/
├── .raw/              # PDF、Web クリップ、データファイル、生メモ
├── wiki/
│   ├── papers/        # 主要主張と方法論つきの論文要約
│   ├── concepts/      # 抽出された概念、モデル、フレームワーク
│   ├── entities/      # 人物、組織、手法、データセット
│   ├── thesis/        # 進化中の合成: 「分野の現状」ページ
│   └── gaps/          # 未解決の問い、矛盾、必要なリサーチ
├── _meta/
│   ├── index.md
│   └── log.md
└── CLAUDE.md
```

`wiki/papers/` ノートの frontmatter:
```yaml
---
type: paper            # paper | concept | entity | thesis | gap
status: summarized     # raw | summarized | synthesized | superseded
year: 2024
authors: []
venue: ""
key_claim: ""
methodology: ""
contradicts: []
supports: []
tags: [paper]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

作成すべき主要 wiki ページ: `[[Research Overview]]`, `[[Key Claims Map]]`, `[[Open Questions]]`, `[[Methodology Comparison]]`

---

## モード F: Book / Course

使用場面: 「書籍のコンパニオンウィキ」「コースノートウィキ」「[タイトル] を読みながら」

```
vault/
├── .raw/              # 章メモ、ハイライト、演習
├── wiki/
│   ├── characters/    # 登場人物、ペルソナ、エージェント、専門家(内容に適応)
│   ├── themes/        # 根拠つきの主要テーマ
│   ├── concepts/      # ドメイン固有の用語とフレームワーク
│   ├── timeline/      # プロット構造、カリキュラム順序、章マップ
│   └── synthesis/     # 自分なりの気づき、問い、応用
├── _meta/
│   ├── index.md
│   └── log.md
└── CLAUDE.md
```

`wiki/concepts/` ノートの frontmatter:
```yaml
---
type: concept          # concept | character | theme | chapter | synthesis
status: developing     # stub | developing | mature
source_chapters: []
first_appearance: ""
tags: [concept]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

作成すべき主要 wiki ページ: `[[Book Overview]]`, `[[Theme Map]]`, `[[Character / Expert Index]]`, `[[My Takeaways]]`

---

## モードの組み合わせ

モードは組み合わせ可能。例:

- 「GitHub リポジトリ + 使用 AI アプローチのリサーチ」 → モード B フォルダ + モード E papers/ フォルダ
- 「自分の SaaS ビジネス + セカンドブレイン」 → モード C intel/ + モード D goals/
- 「YouTube チャンネル」 → モード F(コンテンツを「本」として) + モード E(扱うトピックのリサーチ)

組み合わせるときはフォルダ名を区別すること。モード B とモード C の `decisions/` を 1 つのフォルダにマージしない。
