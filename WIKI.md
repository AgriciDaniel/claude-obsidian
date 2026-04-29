# WIKI.md — LLM ウィキスキーマ

> claude-obsidian プラグインを使っている場合、ここで説明するすべてはスキルが自動的に処理します。
> このファイルはリファレンス文書です。仕組みを理解するために読んでください。
> Andrej Karpathy の LLM Wiki パターンに基づきます。

---

## これは何か

あなたは Obsidian Vault 内の永続的に成長するウィキを維持しています。質問に答えるだけではありません。ソースが追加され質問が投げられるたびに豊かになっていく構造化ナレッジベースを構築・維持します。人間はソースのキュレーションと質問を担当します。書く・相互参照する・ファイリングする・メンテナンスする、すべてあなたの役目です。

ウィキこそが成果物です。チャットは単なるインターフェース。

RAG との決定的な違い: ウィキは永続的なアーティファクトです。相互参照はすでに張られている。矛盾はすでにフラグされている。合成はすでに読んだすべてを反映している。知識は複利のように積み上がります。

> **言語ポリシー:** すべての本文・要約・ログ・チャット応答は日本語で書く。ファイル名・wikilink ターゲット・frontmatter のキーは英語のまま(プロジェクト `CLAUDE.md` 参照)。

---

## 0 — ブートストラップ: 初回セットアップ

新規プロジェクトでの初回実行時、以下を順に実施してください。完了済みのステップはスキップ。

### 0.1 Obsidian インストール確認

```bash
# Linux: flatpak を先に、次に PATH を確認
flatpak list 2>/dev/null | grep -i obsidian && echo "FOUND via flatpak" || \
which obsidian 2>/dev/null && echo "FOUND in PATH" || echo "NOT FOUND"

# macOS
ls /Applications/Obsidian.app 2>/dev/null && echo "FOUND" || echo "NOT FOUND"

# Windows (PowerShell)
Test-Path "$env:LOCALAPPDATA\Obsidian" && echo "FOUND" || echo "NOT FOUND"
```

未インストールの場合:

```bash
# Linux (Flatpak)
flatpak install flathub md.obsidian.Obsidian

# macOS (Homebrew)
brew install --cask obsidian

# Windows (winget)
winget install Obsidian.Obsidian

# 全プラットフォーム共通: https://obsidian.md/download
```

インストール後: Obsidian → Vault を管理 → フォルダを Vault として開く → Vault ディレクトリを選択。

パッケージマネージャが使えない場合、ユーザーに伝える: 「https://obsidian.md からダウンロードしてインストールし、Vault を作成してパスを教えてください。」

### 0.2 Vault の場所

Vault のパスを尋ねるか、デフォルトを使用:

```
VAULT_PATH=~/Documents/Obsidian Vault
```

確認: `ls "$VAULT_PATH/.obsidian" 2>/dev/null`

### 0.3 Local REST API プラグインのインストール

ユーザーを案内(プログラム的にはできない):

1. Obsidian → 設定 → コミュニティプラグイン → 制限モードをオフ
2. ブラウズ → 「Local REST API」を検索 → インストール → 有効化
3. 設定 → Local REST API → API キーをコピー
4. プラグインは `https://127.0.0.1:27124` で稼働(自己署名証明書)

テスト: `curl -sk -H "Authorization: Bearer <KEY>" https://127.0.0.1:27124/`

### 0.4 MCP サーバの構成

**オプション A: mcp-obsidian(REST API ベース、最も一般的)**

```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-obsidian"],
  "env": {
    "OBSIDIAN_API_KEY": "<KEY>",
    "OBSIDIAN_HOST": "127.0.0.1",
    "OBSIDIAN_PORT": "27124",
    "NODE_TLS_REJECT_UNAUTHORIZED": "0"
  }
}' --scope user
```

**オプション B: MCPVault(ファイルシステムベース、プラグイン不要)**

```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@bitbonsai/mcpvault@latest", "<VAULT_PATH>"]
}' --scope user
```

**オプション C: curl で直接 REST API を叩く** — どんな環境でも動く、MCP 不要。第 11 節参照。

`--scope user` を使うと全プロジェクトで Vault が利用可能になります。

**確認:**

```bash
claude mcp list               # サーバが表示されるか
claude mcp get obsidian-vault # パスが正しいか
```

Claude Code セッションで `/mcp` を入力して接続状態を確認。

### 0.5 推奨プラグイン

設定 → コミュニティプラグイン → ブラウズ:

| プラグイン | 理由 |
|--------|-----|
| **Dataview** | Vault を DB として検索。ダッシュボードの動力源。 |
| **Templater** | ノート作成時に frontmatter を自動補完。 |
| **Obsidian Git** | 15 分ごとに自動コミット。データロスから保護。 |
| **Iconize** | フォルダのビジュアルアイコン。 |
| **Minimal Theme** | 高密度情報表示に最適なダークテーマ。 |

任意: Smart Connections(セマンティック検索)、QuickAdd(マクロ)、Folder Notes(クリック可能なフォルダ)。

ブラウザ拡張の **Obsidian Web Clipper** もインストール推奨。Web 記事を Markdown に変換し `.raw/` にワンクリックで送れます。Chrome / Firefox / Safari 対応。

---

## 1 — アーキテクチャ

```
vault/
├── .raw/                   # 第 1 層: 不変のソース文書
│   ├── articles/
│   ├── transcripts/
│   ├── screenshots/
│   ├── data/
│   └── assets/
│
├── wiki/                   # 第 2 層: LLM 生成のナレッジベース
│   ├── index.md            # 全 wiki ページのマスターカタログ
│   ├── log.md              # 全操作の時系列記録
│   ├── hot.md              # ホットキャッシュ: 直近コンテキスト要約(約 500 語)
│   ├── overview.md         # ウィキ全体のエグゼクティブサマリー
│   ├── sources/            # 生ソース 1 件につき 1 ページの要約
│   ├── entities/           # 人物・組織・製品・リポジトリ
│   │   └── _index.md
│   ├── concepts/           # アイデア・パターン・フレームワーク
│   │   └── _index.md
│   ├── domains/            # トップレベルのトピック領域
│   │   └── _index.md
│   ├── comparisons/        # 並列分析
│   ├── questions/          # ユーザー質問への回答ファイル
│   └── meta/               # ダッシュボード、lint レポート、規約
│
├── _templates/             # Templater テンプレート
├── _attachments/           # wiki ページが参照する画像・PDF
│
├── WIKI.md                 # 第 3 層: このファイル
└── .obsidian/              # Obsidian 設定(自動管理)
```

### ルール

- `.raw/` は読み取り専用。ソースファイルを書き換えてはいけない。
- `wiki/` はあなたのもの。自由に作成・更新・改名・削除できる。
- すべての wiki ページに frontmatter がある。例外なし。
- パスより wikilink。`[[Page Name]]` を使い、`[text](path/to/file.md)` は使わない。
- アトミックノート。1 ページ 1 概念。2 つ扱うなら分割。
- 重複を作らない。既存ページがあれば更新する。

---

## 2 — ホットキャッシュ

`wiki/hot.md` は直近コンテキストの約 500 語の要約です。この Vault を参照する他プロジェクトが、フル wiki をクロールせずに直近文脈を取得できるように存在します。

更新タイミング: 毎回の取り込み後、重要な質問のやり取り後、毎セッション終了時。

書式:

```markdown
---
type: meta
title: "ホットキャッシュ"
aliases: ["Hot Cache"]
updated: 2026-04-07T14:30:00
---

# 直近のコンテキスト

## 最終更新
2026-04-07 — YouTube トランスクリプト 3 本を取り込み

## 重要な最近の事実
- 一番大事な点
- 二番目

## 最近の変更
- 作成: [[New Page 1]], [[New Page 2]]
- 更新: [[Existing Page]](X についてのセクションを追記)
- フラグ: トピック Y について [[Page A]] と [[Page B]] の矛盾を検出

## 進行中のスレッド
- ユーザーが現在リサーチ中: [トピック]
- 未解決の問い: [調査継続中の事項]
```

500 語以下に収めること。これはキャッシュであってジャーナルではない。毎回完全に上書きする。

---

## 3 — Frontmatter スキーマ

すべての wiki ページはフラットな YAML frontmatter で始まる。ネストオブジェクトは禁止(Obsidian の Properties UI が対応していない)。

### 共通フィールド(全ページ):

```yaml
---
type: <source|entity|concept|domain|comparison|question|overview|meta>
title: "人間が読むタイトル"
aliases: ["English Filename", "日本語表示名"]
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

> `type:`、`status:` の値は英語の列挙値のまま(Obsidian Bases / DataView クエリ互換のため)。`title:` 値や本文は日本語で書く。`aliases:` には英語ファイル名と日本語表示名の両方を入れる。

### タイプ別追加フィールド:

**source**: `source_type`, `author`, `date_published`, `url`, `confidence`(high|medium|low), `key_claims`(リスト)

**entity**: `entity_type`(person|organization|product|repository|place), `role`, `first_mentioned`

**concept**: `complexity`(basic|intermediate|advanced), `domain`, `aliases`(リスト)

**comparison**: `subjects`(wikilink のリスト), `dimensions`(リスト), `verdict`(1 行)

**question**: `question`(元のクエリ), `answer_quality`(draft|solid|definitive)

---

## 4 — 操作

### 4.1 SCAFFOLD — 初回構造構築

トリガー: ユーザーが Vault の用途を説明する。

1. ウィキモードを判別(下のモード表と 4.1a の詳細参照)。
2. 質問を 1 つだけ: 「この Vault は何のため?」
3. `wiki/` 配下にフォルダ構造を作成。
4. 各ドメインに対しドメインページ + `_index.md` のサブインデックスを作成。
5. `wiki/overview.md`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` を作成。
6. `_templates/` に各ノートタイプのテンプレートを配置。
7. ビジュアルカスタマイズを適用(第 7 節)。`.obsidian/snippets/vault-colors.css` を作成。
8. Vault の CLAUDE.md を作成(4.1b のテンプレート)。
9. git を初期化(第 8 節)。
10. 構造を提示し、「始める前に調整したい点はありますか?」と尋ねる。

**モード選択:**

| ユーザー入力 | 最適モード |
|-----------|----------|
| 「自分のサイト」「サイトマップ」「コンテンツ監査」 | A: Website |
| 「自分のリポジトリ」「コードベースマップ」「アーキテクチャウィキ」 | B: GitHub |
| 「自分のビジネス」「プロジェクトウィキ」「競合分析」 | C: Business |
| 「セカンドブレイン」「目標」「ジャーナル」「自分の人生」 | D: Personal |
| 「リサーチトピック」「論文」「深掘り」 | E: Research |
| 「読んでる本」「コースノート」「章管理」 | F: Book/Course |

モードは組み合わせ可能。「GitHub リポジトリ + AI アプローチに関するリサーチ」ならモード B のフォルダ + モード E の papers/ を併用。

### 4.1a — 6 つのウィキモード

**モード A: Website / Sitemap**

```
vault/
├── .raw/              # クロールエクスポート、解析、GSC データ
├── wiki/
│   ├── pages/         # URL 1 件につき 1 ノート
│   ├── structure/     # サイトアーキテクチャ、ナビ階層
│   ├── audits/        # コンテンツのギャップ、リダイレクト要件
│   ├── keywords/      # キーワードクラスタ、ターゲットページ割当
│   └── entities/      # ブランド、執筆者、トピックハブ
```

pages/ の frontmatter: `url`, `status`(live|redirect|404|stub|no-index), `h1`, `meta_description`, `word_count`, `has_schema`, `indexed`, `canonical`, `internal_links_in`, `internal_links_out`, `last_crawled`

主要ページ: `[[Site Overview]]`, `[[Navigation Structure]]`, `[[Content Gaps]]`, `[[Redirect Map]]`, `[[Keyword Clusters]]`

---

**モード B: GitHub / Repository**

```
vault/
├── .raw/              # README、git log エクスポート、コードダンプ
├── wiki/
│   ├── modules/       # モジュール / パッケージ / サービス 1 件につき 1 ノート
│   ├── components/    # 再利用可能コンポーネント
│   ├── decisions/     # アーキテクチャ決定記録(ADR)
│   ├── dependencies/  # 外部依存、バージョン、リスク
│   └── flows/         # データフロー、リクエストパス、認証フロー
```

modules/ の frontmatter: `path`, `status`(active|deprecated|experimental|planned), `language`, `purpose`, `maintainer`, `depends_on`, `used_by`, `linked_issues`

主要ページ: `[[Architecture Overview]]`, `[[Data Flow]]`, `[[Tech Stack]]`, `[[Dependency Graph]]`, `[[Key Decisions]]`

---

**モード C: Business / Project**

```
vault/
├── .raw/              # 会議トランスクリプト、Slack エクスポート、ドキュメント
├── wiki/
│   ├── stakeholders/  # 人物、企業、意思決定者
│   ├── decisions/     # 重要な決定とその根拠・日付
│   ├── deliverables/  # マイルストーン、成果物、ステータス
│   ├── intel/         # 競合分析、市場調査
│   └── comms/         # 合成された会議メモ
```

decisions/ の frontmatter: `status`(active|pending|done|blocked|superseded), `priority`(1-5), `date`, `owner`, `due_date`, `context`

主要ページ: `[[Project Overview]]`, `[[Stakeholder Map]]`, `[[Decision Log]]`, `[[Competitor Landscape]]`

---

**モード D: Personal / Second Brain**

```
vault/
├── .raw/              # ジャーナル、記事、音声トランスクリプト
├── wiki/
│   ├── goals/         # 個人および専門分野の目標
│   ├── learning/      # 習得中の概念
│   ├── people/        # 関係性、共通文脈
│   ├── areas/         # 人生の領域: 健康、財政、キャリア
│   └── resources/     # 書籍、コース、ツール
├── _meta/
│   └── hot-cache.md   # アクティブコンテキスト約 500 語
```

goals/ の frontmatter: `area`(health|career|finance|creative|relationships|growth), `priority`, `target_date`, `progress`(0-100)

主要ページ: `[[North Star]]`, `[[Weekly Review Template]]`, `[[Annual Goals]]`

---

**モード E: Research**

```
vault/
├── .raw/              # PDF、Web クリップ、生メモ
├── wiki/
│   ├── papers/        # 主要主張つきの論文要約
│   ├── concepts/      # 抽出された概念、モデル、フレームワーク
│   ├── entities/      # 人物、組織、データセット
│   ├── thesis/        # 進化中の合成
│   └── gaps/          # 未解決の問い、矛盾
```

papers/ の frontmatter: `year`, `authors`, `venue`, `key_claim`, `methodology`, `contradicts`, `supports`

主要ページ: `[[Research Overview]]`, `[[Key Claims Map]]`, `[[Open Questions]]`, `[[Methodology Comparison]]`

---

**モード F: Book / Course**

```
vault/
├── .raw/              # 章メモ、ハイライト、演習
├── wiki/
│   ├── characters/    # 登場人物、ペルソナ、専門家
│   ├── themes/        # 根拠つきの主要テーマ
│   ├── concepts/      # ドメイン固有用語
│   ├── timeline/      # 構造、順序、章マップ
│   └── synthesis/     # 自分なりの気づきと応用
```

concepts/ の frontmatter: `source_chapters`, `first_appearance`

主要ページ: `[[Book Overview]]`, `[[Theme Map]]`, `[[Character / Expert Index]]`, `[[My Takeaways]]`

### 4.1b — Vault CLAUDE.md テンプレート

新規プロジェクト Vault 足場時、Vault ルートに作成:

```markdown
# [WIKI NAME] — LLM ウィキ

モード: [MODE A/B/C/D/E/F]
目的: [一文]
所有者: [名前]
作成日: YYYY-MM-DD

## 構造

[選んだモードのフォルダマップを貼る]

## 規約

- 全ノートは YAML frontmatter を持つ: type, status, created, updated, tags(最低限)
- wikilink は [[Note Name]] 形式 — ファイル名は一意なのでパス不要
- .raw/ はソース文書 — 絶対に書き換えない
- wiki/index.md はマスターカタログ — 取り込みごとに更新
- wiki/log.md は追記専用 — 新エントリは TOP に、過去エントリは編集しない

## 操作

- 取り込み: .raw/ にソースを置き、「[ファイル名] を取り込んで」
- 質問: 自由に質問 — Claude は index を読み、関連ページに踏み込む
- lint: 「wiki を lint して」で健全性チェック
```

### 4.2 INGEST — 単一ソース

トリガー: ユーザーが `.raw/` にファイルを置く、もしくは内容を貼り付ける。

1. ソースを完全に読む。
2. 主要な気づきをユーザーと議論。「とにかく取り込んで」と言われたらスキップ。
3. `wiki/sources/` に要約ページを作成。
4. 言及されたすべての人物・組織・製品・リポジトリのエンティティページを作成または更新。
5. 重要なアイデアの概念ページを作成または更新。
6. 関連ドメインページとそれらの `_index.md` サブインデックスを更新。
7. 全体像が変わったら `wiki/overview.md` を更新。
8. `wiki/index.md` を更新。新ページのエントリを追加。
9. `wiki/hot.md` をこの取り込みのコンテキストで更新。
10. `wiki/log.md` の **先頭** に追記:
    ```markdown
    ## [2026-04-07] ingest | ソースタイトル
    - ソース: `.raw/articles/filename.md`
    - 要約ページ: [[Source Title]]
    - 作成: [[Page 1]], [[Page 2]]
    - 更新: [[Page 3]], [[Page 4]]
    - 主な発見: 新たに分かったことを 1 文で。
    ```
11. 矛盾チェック。両ページに `> [!contradiction]` callout でフラグ。

1 件のソースは通常 8〜15 ページに影響を与える。

### 4.3 INGEST — バッチモード

トリガー: ユーザーが複数ファイルを投入、または「これら全部を取り込んで」と指示。

1. 処理対象ファイルをリスト化。ユーザーに確認。
2. 単一取り込みフローで各ソースを処理。相互参照は後回し。
3. 全ソース処理後: 相互参照パス。新ソース間の関連を探す。
4. index、ホットキャッシュ、log を最後に 1 回だけ更新(各ソースごとではなく)。
5. 報告: 「N 件処理しました。X ページ作成、Y ページ更新。主な接続: ...」

バッチ取り込みは対話性が低い。30 件以上なら 10 件ごとに進捗確認。

### 4.4 QUERY — 質問への回答

1. まず `wiki/hot.md` を読む。回答が含まれているかも。
2. `wiki/index.md` を読み、関連ページを特定。
3. それらを読む(通常 3〜5 件、10 件以上は読みすぎ)。
4. チャットで回答を合成。wikilink で引用。
5. `wiki/questions/` に保存するか提案。
6. 質問でギャップが見えた: 「X についての情報が足りません。ソースを探しますか?」

### 4.5 LINT — 健全性チェック

トリガー: ユーザーが「lint」と言うか、10〜20 件取り込みごと。

チェック項目: 孤立ページ、デッドリンク、古い主張、言及された概念のページ欠落、欠けた相互参照、frontmatter のギャップ、空セクション。

出力: `wiki/meta/lint-report-YYYY-MM-DD.md`。自動修正前に確認を取る。

---

## 5 — Index とサブインデックス

### wiki/index.md(マスター)

```markdown
---
type: meta
title: "ウィキ索引"
aliases: ["Wiki Index"]
updated: 2026-04-07
---
# ウィキ索引

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

### ドメインサブインデックス

各ドメインフォルダに、そのドメインのページのみカタログ化した `_index.md` を置く。

```markdown
---
type: meta
title: "エンティティ索引"
aliases: ["Entities Index"]
updated: 2026-04-07
---
# エンティティ

## 人物
- [[Person Name]] — 役割、所属

## 組織
- [[Org Name]] — 何をしているか
```

### wiki/log.md

追記専用。新エントリは TOP に。各エントリ: `## [YYYY-MM-DD] operation | title`

直近エントリの解析:
```bash
grep "^## \[" wiki/log.md | head -10
```

---

## 6 — クロスプロジェクト参照

任意の Claude Code プロジェクトはコンテキスト重複なしであなたの wiki を読める。

向こうのプロジェクトの CLAUDE.md に追記:

```markdown
## ウィキナレッジベース
パス: ~/Documents/Obsidian Vault

このプロジェクトに無いコンテキストが必要なとき:
1. まず wiki/hot.md(直近コンテキスト約 500 語)を読む
2. 足りなければ wiki/index.md(全カタログ)を読む
3. ドメイン詳細が必要なら wiki/<domain>/_index.md
4. その上で個別 wiki ページを読む

一般的なコーディング質問やこのプロジェクトに既にあるコンテキスト、
[ドメイン] と無関係な作業には wiki を読まない。
```

これでトークン使用量が低く保たれる。ホットキャッシュ約 500 トークン、index 約 1000 トークン、個別ページ各 100〜300 トークン。

---

## 7 — ビジュアルカスタマイズ

足場時に適用。`.obsidian/snippets/vault-colors.css` を作成:

```css
:root {
  --wiki-1: #4fc1ff;  --wiki-2: #c586c0;  --wiki-3: #dcdcaa;
  --wiki-4: #ce9178;  --wiki-5: #6a9955;  --wiki-6: #d16969;
  --wiki-7: #569cd6;
}

.nav-folder-title[data-path^="wiki/domains"]     { color: var(--wiki-1); }
.nav-folder-title[data-path^="wiki/entities"]    { color: var(--wiki-2); }
.nav-folder-title[data-path^="wiki/concepts"]    { color: var(--wiki-3); }
.nav-folder-title[data-path^="wiki/sources"]     { color: var(--wiki-4); }
.nav-folder-title[data-path^="wiki/questions"]   { color: var(--wiki-5); }
.nav-folder-title[data-path^="wiki/comparisons"] { color: var(--wiki-6); }
.nav-folder-title[data-path^="wiki/meta"]        { color: var(--wiki-7); }
.nav-folder-title[data-path=".raw"]              { color: #808080; opacity: 0.6; }

.callout[data-callout='contradiction'] { --callout-color: 209, 105, 105; --callout-icon: lucide-alert-triangle; }
.callout[data-callout='gap']           { --callout-color: 220, 220, 170; --callout-icon: lucide-help-circle; }
.callout[data-callout='key-insight']   { --callout-color: 79, 193, 255;  --callout-icon: lucide-lightbulb; }
.callout[data-callout='stale']         { --callout-color: 128, 128, 128; --callout-icon: lucide-clock; }
```

有効化: 設定 → 外観 → CSS スニペット → リフレッシュ → 有効化。

### グラフビューのグループ

グラフビュー設定で:

| クエリ | 色 |
|-------|-------|
| `path:wiki/domains` | 青 |
| `path:wiki/entities` | 紫 |
| `path:wiki/concepts` | 黄 |
| `path:wiki/sources` | オレンジ |
| `path:wiki/questions` | 緑 |
| `path:.raw` | グレー(薄く) |

---

## 8 — Git セットアップ

```bash
cd "$VAULT_PATH"
git init
cat > .gitignore << 'EOF'
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.smart-connections/
.obsidian-git-data
.trash/
.DS_Store
node_modules/
EOF
git add -A && git commit -m "Initial vault scaffold"
```

Obsidian Git を有効化: 設定 → Obsidian Git → Auto backup interval → 15 分。

---

## 9 — Dataview ダッシュボード

足場後 `wiki/meta/dashboard.md` に作成:

````markdown
---
type: meta
title: "ダッシュボード"
aliases: ["Dashboard"]
---
# ウィキダッシュボード

## 最近の活動
```dataview
TABLE type, status, updated FROM "wiki" SORT updated DESC LIMIT 15
```

## シードページ(育成が必要)
```dataview
LIST FROM "wiki" WHERE status = "seed" SORT updated ASC
```

## ソース未紐付けのエンティティ
```dataview
LIST FROM "wiki/entities" WHERE !sources OR length(sources) = 0
```
````

---

## 10 — コンテキストウィンドウ管理

必要最小限を読む:

- まず `hot.md`。すでに必要な情報があるかも。
- 次に `index.md`。関連ページを特定。全部スキャンしない。
- 焦点を絞った検索にはドメインサブインデックスを使う。
- 1 質問あたり 3〜5 ページのみ。10 件以上は読みすぎ。
- キーワード検索には search を使う。1 単語のためにフルページをスキャンしない。
- 外科的編集には PATCH を使う。1 フィールドの変更でファイル全体を読み直して書き直さない。
- wiki ページは短く保つ。最大 100〜300 行。長くなったら分割。
- ユーザーに頼まれない限り wiki 内容をチャットに貼らない。wikilink で参照する。

---

## 11 — REST API クイックリファレンス

実行前にセット:

```bash
API="https://127.0.0.1:27124"
KEY="your-api-key-here"
```

**ファイル読み取り:**
```bash
curl -sk -H "Authorization: Bearer $KEY" "$API/vault/wiki/index.md"
```

**ファイル作成または上書き:**
```bash
curl -sk -X PUT \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: text/markdown" \
  --data-binary @file.md \
  "$API/vault/wiki/entities/Name.md"
```

**ファイル末尾追記:**
```bash
curl -sk -X POST \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: text/markdown" \
  --data "- 新項目" \
  "$API/vault/wiki/log.md"
```

**Frontmatter の特定フィールドを更新:**
```bash
curl -sk -X PATCH \
  -H "Authorization: Bearer $KEY" \
  -H "Operation: replace" -H "Target-Type: frontmatter" \
  -H "Target: status" -H "Content-Type: application/json" \
  --data '"mature"' \
  "$API/vault/wiki/concepts/Name.md"
```

**見出し配下に追記:**
```bash
curl -sk -X PATCH \
  -H "Authorization: Bearer $KEY" \
  -H "Operation: append" -H "Target-Type: heading" \
  -H "Target: 関連" -H "Content-Type: text/markdown" \
  --data "- [[New Page]]" \
  "$API/vault/wiki/entities/Name.md"
```

**検索:**
```bash
curl -sk -X POST \
  -H "Authorization: Bearer $KEY" \
  "$API/search/simple/?query=機械学習"
```

**Dataview クエリ:**
```bash
curl -sk -X POST \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/vnd.olrapi.dataview.dql+txt" \
  --data 'TABLE status FROM "wiki" WHERE status = "seed"' \
  "$API/search/"
```

---

## 12 — Vault CLAUDE.md テンプレート

新規プロジェクト用にウィキを作るとき(このプラグインではなく)、Vault ルートに CLAUDE.md を作成:

```markdown
# [WIKI NAME] — LLM ウィキ

モード: [MODE A/B/C/D/E/F]
目的: [一文]
所有者: [名前]
作成日: YYYY-MM-DD

## 構造

[選んだモードのフォルダマップを貼る]

## 規約

- 全ノートは YAML frontmatter: type, status, created, updated, tags(最低限)
- wikilink は [[Note Name]] 形式
- .raw/ はソース文書 — 絶対に書き換えない
- wiki/index.md はマスターカタログ — 取り込みごとに更新
- wiki/log.md は追記専用 — 新エントリは TOP に

## 操作

- 取り込み: .raw/ にソースを置き、「[ファイル名] を取り込んで」
- 質問: 自由に質問
- lint: 「wiki を lint して」
```

---

## 13 — 規約

### 命名

- **ファイル名**: スペース付きのタイトルケース(`Machine Learning.md`)。日本語ページでも英語ファイル名を維持し、`aliases:` に日本語名を入れる
- **フォルダ**: 小文字 + ハイフン(`wiki/data-models/`)
- **タグ**: 小文字、階層化(`#domain/architecture`)
- **ファイル名は一意** に — wikilink がパス不要で動作

### 文体

- 平叙、現在形。「X は Y を使う」と書き、「X は基本的に Y する」と書かない。
- 積極的にリンク。wiki ページへの言及はすべて wikilink を貼る。
- 出典を引用: `(出典: [[Page]])`。
- 不確実性をフラグ: `> [!gap] さらに証拠が必要。`
- 矛盾をフラグ: `> [!contradiction] [[Page A]] は X を主張するが、[[Page B]] は Y と言う。`

### 相互参照

ページ A を更新してページ B に言及するとき、ページ B から戻リンクを張るべきか確認する。双方向リンクがグラフビューを有用にする。

---

## 14 — キャンバスマップ

ビジュアル概観用に `.canvas` ファイルを作成:

```json
{
  "nodes": [
    {"id": "1", "type": "file", "file": "wiki/domains/Architecture.md",
     "x": 0, "y": 0, "width": 250, "height": 120, "color": "4"},
    {"id": "2", "type": "file", "file": "wiki/domains/APIs.md",
     "x": 300, "y": 0, "width": 250, "height": 120, "color": "5"}
  ],
  "edges": [
    {"id": "e1", "fromNode": "1", "fromSide": "right",
     "toNode": "2", "toSide": "left", "toEnd": "arrow"}
  ]
}
```

キャンバスノード色(Obsidian キャンバス色コード): 1=赤、2=オレンジ、3=黄、4=緑、5=シアン、6=紫。
注: これらは wiki グラフ CSS のカラースキームと異なる。完全な色テーブルは `skills/canvas/references/canvas-spec.md` 参照。

足場時にドメイン関係キャンバスを作成。wiki の成長に合わせて更新。

---

## 要約

LLM(あなた)の仕事:
1. Vault のセットアップ(1 回)
2. ユーザーのドメイン記述からウィキ構造を足場にする
3. ソースの取り込み: 読み・要約・相互参照・ファイリング
4. 操作のたびにホットキャッシュを維持
5. index → 関連ページ → 合成 で質問に答える
6. 良い回答を wiki に戻して保存
7. 定期的に lint: 健全性問題を見つけて修正
8. `.raw/` ソースを書き換えない
9. 常に index・サブインデックス・log・ホットキャッシュを更新
10. 常に frontmatter と wikilink を使う

人間の仕事: ソースのキュレーション、良い質問、意味についての考察。それ以外はすべてあなたの担当。

---

*Andrej Karpathy の LLM Wiki パターンに基づく。プラグイン: claude-obsidian by AgriciDaniel / AI Marketing Hub。日本語ローカライズ追加。*
