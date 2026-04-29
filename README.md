
# claude-obsidian

<p align="center">
  <img src="wiki/meta/claude-obsidian-gif-cover-16x9.gif" alt="claude-obsidian" width="100%" />
</p>

[![GitHub stars](https://img.shields.io/github/stars/AgriciDaniel/claude-obsidian?style=flat&color=e8734a)](https://github.com/AgriciDaniel/claude-obsidian/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-8B5CF6)](https://code.claude.com/docs/en/discover-plugins)
[![Blog Post](https://img.shields.io/badge/Deep_Dive-Blog_Post-22c55e)](https://agricidaniel.com/blog/claude-obsidian-ai-second-brain)

> 🇯🇵 **このフォークは日本語ローカライズ版です。** すべての出力(チャット応答、ウィキページ本文、log エントリ、要約)は日本語で行われます。ファイル名、スキル名、コードは英語のまま維持されており、上流のプラグインと完全互換です。詳しくは [`CLAUDE.md`](CLAUDE.md) の言語ポリシーを参照してください。

Claude + Obsidian のナレッジコンパニオン。永続的に成長するウィキ Vault を構築・維持する常駐ノートテイカーです。投入したソースはすべて統合され、投げた質問はそれまで読んだすべてから回答を引き出します。知識は複利のように積み上がります。

[Andrej Karpathy の LLM Wiki パターン](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) に基づく実装です。**11 のスキル、手動ファイリングゼロ、マルチエージェント対応、オプションの [DragonScale Memory](docs/dragonscale-guide.md) 拡張**(log fold、決定論的ページアドレス、セマンティックタイリング lint、境界優先 autoresearch)を提供します。

---

## 何ができるか
### [YouTube デモ](https://www.youtube.com/watch?v=a2hgayvr-H4)
<p align="center">
  <img src="wiki/meta/welcome-canvas.gif" alt="ウェルカムキャンバス。ビジュアルデモボード" width="96%" />
</p>

ソースを投入する → Claude が読み、エンティティと概念を抽出し、相互参照を更新し、構造化された Obsidian Vault に振り分けます。取り込みのたびにウィキは豊かになります。

質問する → Claude はホットキャッシュ(直近のコンテキスト)を読み、索引をスキャンし、関連ページに踏み込んで回答を合成します。回答の出典は wiki ページであり、学習データではありません。

lint する → Claude は孤立ページ、デッドリンク、古い主張、欠落した相互参照を見つけます。手作業のクリーンアップなしで Vault は健全に保たれます。

セッション終了時に Claude はホットキャッシュを更新します。次回セッションは直近コンテキスト込みで開始でき、振り返り不要です。

<p align="center">
  <img src="wiki/meta/image-example-graph-view.png" alt="グラフビュー。色分けされたウィキノード" width="48%" />
  <img src="wiki/meta/image-example-wiki-map-view.png" alt="Wiki Map キャンバス" width="48%" />
</p>

---

## なぜ claude-obsidian か?

ほとんどの Obsidian AI プラグインは「チャットインターフェース」です。既存ノートに対する質問に答えるだけ。claude-obsidian は「ナレッジエンジン」で、ノートを自律的に作成・整理・維持・進化させます。

| 機能 | claude-obsidian | Smart Connections | Copilot |
|---|---|---|---|
| **ノートの自動整理** | エンティティ・概念・相互参照を作成 | 不可 | 不可 |
| **矛盾フラグ** | `[!contradiction]` callout で出典付き表示 | 不可 | 不可 |
| **セッション記憶** | ホットキャッシュが会話を跨いで永続 | 不可 | 不可 |
| **Vault メンテナンス** | 8 カテゴリの lint(孤立、デッドリンク、ギャップ) | 不可 | 不可 |
| **自律リサーチ** | ギャップ補完付き 3 ラウンド Web リサーチ | 不可 | 不可 |
| **マルチモデル対応** | Claude, Gemini, Codex, Cursor, Windsurf | Claude のみ | 複数 |
| **ビジュアルキャンバス** | [claude-canvas](https://github.com/AgriciDaniel/claude-canvas) コンパニオン経由 | 不可 | 不可 |
| **出典付き回答** | 特定の wiki ページを引用 | 類似ノートを引用 | ノート引用 |
| **バッチ取り込み** | 複数ソースの並列エージェント | 不可 | 不可 |
| **オープンソース** | MIT | MIT | フリーミアム |

> **詳細記事:** [I Turned Obsidian Into a Self-Organizing AI Brain](https://agricidaniel.com/blog/claude-obsidian-ai-second-brain) — データ可視化、市場コンテキスト、ワークフローデモを含む完全解説(英語)。

---

## クイックスタート

### オプション 1: Vault としてクローン(推奨。約 2 分)

```bash
git clone https://github.com/AgriciDaniel/claude-obsidian
cd claude-obsidian
bash bin/setup-vault.sh
```

Obsidian でフォルダを開く: **Vault を管理 → フォルダを Vault として開く → `claude-obsidian/` を選択**

同じフォルダで Claude Code を開き、`/wiki` を入力。

> `setup-vault.sh` は `graph.json`(フィルタ + 色設定)、`app.json`(プラグインディレクトリの除外)、`appearance.json`(CSS 有効化)を構成します。最初の Obsidian 起動前に 1 回実行してください。事前構成済みのグラフビュー、カラースキーム、ウィキ構造がそのまま使えます。

---

### オプション 2: Claude Code プラグインとしてインストール

Claude Code でのプラグインインストールは 2 ステップです。まずマーケットプレイスを追加し、次にそこからプラグインをインストールします。

```bash
# ステップ 1: マーケットプレイスを追加
claude plugin marketplace add AgriciDaniel/claude-obsidian

# ステップ 2: プラグインをインストール
claude plugin install claude-obsidian@claude-obsidian-marketplace
```

任意の Claude Code セッションで `/wiki` を実行すれば、Vault のセットアップを案内します。

確認:
```bash
claude plugin list
```

---

### オプション 3: 既存の Vault に追加

`WIKI.md` を Vault のルートにコピーし、Claude に貼り付けます:

```
このプロジェクトの WIKI.md を読んで。次に:
1. Obsidian がインストールされているか確認、未インストールなら入れる。
2. Local REST API プラグインがポート 27124 で動いているか確認。
3. MCP サーバーを構成。
4. ひとつだけ質問: 「この Vault は何のため?」
そしてウィキ構造を足場として作る。
```

---

## コマンド

| ユーザー入力 | Claude の動作 |
|---------|------------|
| `/wiki` | セットアップ確認、足場作成、または続きから再開 |
| `[ファイル] を取り込んで` / `ingest [file]` | ソースを読み、8〜15 ページを生成、index と log を更新 |
| `これらをすべて取り込んで` / `ingest all of these` | 複数ソースを並列処理し、最後に相互参照を実施 |
| `X について何を知ってる?` / `what do you know about X?` | index → 関連ページ → 回答合成 |
| `/save` | 現在の会話を wiki ノートとして保存 |
| `/save [name]` | 指定タイトルで保存(命名質問をスキップ) |
| `/autoresearch [topic]` | 自律リサーチループ実行: 検索・取得・合成・保存 |
| `/canvas` | ビジュアルキャンバスを開く/作成、ゾーンとノードを一覧 |
| `/canvas add image [path]` | URL またはローカルパスから画像をキャンバスに追加(自動レイアウト) |
| `/canvas add text [content]` | Markdown テキストカードをキャンバスに追加 |
| `/canvas add pdf [path]` | PDF をプレビューノードとして追加 |
| `/canvas add note [page]` | wiki ページをリンクカードとしてキャンバスにピン留め |
| `/canvas zone [name]` | ラベル付きゾーンを追加してビジュアルを整理 |
| `/canvas from banana` | 直近に生成された画像をキャンバスに取り込む |
| `wiki を lint して` / `lint the wiki` | 健全性チェック: 孤立、デッドリンク、ギャップ、提案 |
| `ホットキャッシュを更新` / `update hot cache` | 最新コンテキスト要約で hot.md をリフレッシュ |

> **もっと欲しい?** [claude-canvas](https://github.com/AgriciDaniel/claude-canvas) は 12 テンプレート、6 レイアウトアルゴリズム、AI 画像生成、プレゼン、フルキャンバスオーケストレーションを追加します。両方を併用してください。相補的に動きます。

---

## クロスプロジェクト活用

任意の Claude Code プロジェクトをこの Vault に向けます。向こうの `CLAUDE.md` に追記:

```markdown
## ウィキナレッジベース
パス: ~/path/to/vault

このプロジェクトに無いコンテキストが必要なとき:
1. まず wiki/hot.md(直近コンテキストキャッシュ)を読む
2. 足りなければ wiki/index.md
3. ドメイン詳細が必要なら該当ドメインの sub-index
4. その上で個別 wiki ページに踏み込む

[ドメイン] と無関係な一般コーディング質問には wiki を読まない。
```

エグゼクティブアシスタント、コーディングプロジェクト、コンテンツワークフローのすべてが同じナレッジベースから引き出せます。

---

## 6 つのウィキモード

| モード | 適用シーン |
|------|---------|
| A: Website | サイトマップ、コンテンツ監査、SEO ウィキ |
| B: GitHub | コードベースマップ、アーキテクチャウィキ |
| C: Business | プロジェクトウィキ、競合インテリジェンス |
| D: Personal | セカンドブレイン、目標、ジャーナル合成 |
| E: Research | 論文、概念、論文執筆 |
| F: Book/Course | 章管理、コースノート |

モードは組み合わせ可能です。

---

## 何が作られるか

典型的な足場で作成されるもの:
- 選んだモード用のフォルダ構造
- `wiki/index.md`: マスターカタログ
- `wiki/log.md`: 追記専用の操作ログ
- `wiki/hot.md`: 直近コンテキストキャッシュ
- `wiki/overview.md`: エグゼクティブサマリー
- `wiki/meta/dashboard.base`: Bases ダッシュボード(プライマリ、ネイティブ Obsidian)
- `wiki/meta/dashboard.md`: 旧 Dataview ダッシュボード(任意のフォールバック)
- `_templates/`: 各ノートタイプ用 Obsidian Templater テンプレート
- `.obsidian/snippets/vault-colors.css`: 色分けファイルエクスプローラ
- Vault 直下 `CLAUDE.md`: 自動読み込みされるプロジェクト指示書

---

## MCP セットアップ(任意)

MCP を使うと Claude がコピペなしで Vault ノートを直接読み書きできます。

オプション A(REST API ベース):
1. Obsidian に Local REST API プラグインをインストール
2. API キーをコピー
3. 実行:
```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-obsidian"],
  "env": {
    "OBSIDIAN_API_KEY": "your-key",
    "OBSIDIAN_HOST": "127.0.0.1",
    "OBSIDIAN_PORT": "27124",
    "NODE_TLS_REJECT_UNAUTHORIZED": "0"
  }
}' --scope user
```

オプション B(ファイルシステムベース、プラグイン不要):
```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@bitbonsai/mcpvault@latest", "/path/to/your/vault"]
}' --scope user
```

---

## プラグイン

### コアプラグイン(Obsidian 内蔵、インストール不要)

| プラグイン | 用途 |
|--------|---------|
| **Bases** | `wiki/meta/dashboard.base` の動力源。ネイティブ DB ビュー。Obsidian v1.9.10(2025 年 8 月)以降利用可。**プライマリダッシュボードでは Dataview を置き換え。** |
| **Properties** | ビジュアル frontmatter エディタ |
| **Backlinks**、**Outline**、**グラフビュー** | 標準ナビゲーション |

### プリインストール済みコミュニティプラグイン

**Settings → Community Plugins → enable** で有効化:

| プラグイン | 用途 | 備考 |
|--------|---------|-------|
| **Calendar** | 単語数 + タスクドット付き右サイドバーカレンダー | 同梱 |
| **Thino** | クイックメモキャプチャパネル | 同梱 |
| **Excalidraw** | 手描きキャンバス、画像注釈 | 同梱* |
| **Banners** | `banner:` frontmatter による Notion 風ヘッダー画像 | 同梱 |

\* Excalidraw `main.js`(8MB)は `setup-vault.sh` が自動ダウンロード。git では追跡しません。

### 別途コミュニティプラグインから追加(同梱なし)

| プラグイン | 用途 |
|--------|---------|
| **Templater** | `_templates/` から frontmatter を自動補完 |
| **Obsidian Git** | Vault を 15 分ごとに自動コミット |
| **Dataview** *(任意/旧)* | 旧 `wiki/meta/dashboard.md` クエリ用のみ。プライマリは Bases。 |

ブラウザ拡張の **[Obsidian Web Clipper](https://obsidian.md/clipper)** もぜひ。Web ページをワンクリックで `.raw/` に送れます。

---

## CSS スニペット(setup-vault.sh で自動有効化)

3 つのスニペットが Vault に同梱され、自動的に有効化されます:

| スニペット | 効果 |
|---------|--------|
| `vault-colors` | ファイルエクスプローラで `wiki/` フォルダをタイプ別に色分け(青 = 概念、緑 = ソース、紫 = エンティティ) |
| `ITS-Dataview-Cards` | Dataview の `TABLE` クエリをビジュアルカードグリッド化。`.cards` クラスを付けた ` ```dataviewjs ` で利用 |
| `ITS-Image-Adjustments` | ノート内画像の細かなサイズ調整。任意の画像埋め込みに `\|100` を付加 |

---

## Banner プラグイン

任意の wiki ページ frontmatter に追加:

```yaml
banner: "_attachments/images/your-image.png"
banner_icon: "🧠"
```

ページが Obsidian で全幅ヘッダー画像付きでレンダーされます。ハブページや概要ページに最適。

---

## ファイル構成

```
claude-obsidian/
├── .claude-plugin/
│   ├── plugin.json              # マニフェスト
│   └── marketplace.json         # 配布
├── skills/
│   ├── wiki/                    # オーケストレータ + リファレンス(7 ファイル)
│   ├── wiki-ingest/             # INGEST 操作
│   ├── wiki-query/              # QUERY 操作
│   ├── wiki-lint/               # LINT 操作
│   ├── save/                    # /save: 会話を wiki に保存
│   ├── autoresearch/            # /autoresearch: 自律リサーチループ
│   │   └── references/
│   │       └── program.md       # リサーチ目的の設定
│   └── canvas/                  # /canvas: ビジュアルレイヤ(画像、PDF、ノート)
│       └── references/
│           └── canvas-spec.md   # Obsidian キャンバス JSON 形式リファレンス
├── agents/
│   ├── wiki-ingest.md           # 並列取り込みエージェント
│   └── wiki-lint.md             # 健全性チェックエージェント
├── commands/
│   ├── wiki.md                  # /wiki ブートストラップコマンド
│   ├── save.md                  # /save コマンド
│   ├── autoresearch.md          # /autoresearch コマンド
│   └── canvas.md                # /canvas ビジュアルレイヤコマンド
├── hooks/
│   └── hooks.json               # SessionStart + Stop ホットキャッシュ hook
├── _templates/                  # Obsidian Templater テンプレート
├── wiki/
│   ├── Wiki Map.canvas          # ビジュアルハブ、中央グラフノード
│   ├── canvases/                # welcome.canvas + main.canvas(ビジュアルデモ)
│   ├── getting-started.md       # オンボーディングウォークスルー
│   ├── concepts/                # シード: LLM Wiki Pattern, Hot Cache, Compounding Knowledge
│   ├── entities/                # シード: Andrej Karpathy
│   ├── sources/                 # 最初の取り込みで生成
│   └── meta/
│       ├── dashboard.base       # Bases ダッシュボード(プライマリ)
│       └── dashboard.md         # 旧 Dataview ダッシュボード(任意)
├── .raw/                        # ソース文書(Obsidian では非表示)
├── .obsidian/snippets/          # vault-colors.css(3 色スキーム)
├── WIKI.md                      # 完全スキーマリファレンス
├── CLAUDE.md                    # プロジェクト指示書
└── README.md                    # このファイル
```

---

## AutoResearch: program.md

`/autoresearch` コマンドは設定可能です。`skills/autoresearch/references/program.md` を編集して以下を制御:

- 優先するソース(学術、公式ドキュメント、ニュース)
- 信頼度スコアリングのルール
- セッションあたりの最大ラウンド数・最大ページ数
- ドメイン固有の制約

デフォルトは一般リサーチ向け。ドメインに応じて上書きしてください。医療リサーチャーは「PubMed を優先」、ビジネスアナリストは「市場データと提出資料に集中」を追加するイメージ。

---

## シード Vault

このリポジトリにはシード Vault が同梱されています。Obsidian で開くと以下が見えます:

- `wiki/concepts/`: LLM Wiki Pattern, Hot Cache, Compounding Knowledge
- `wiki/entities/`: Andrej Karpathy
- `wiki/sources/`: 最初の取り込みまで空
- `wiki/meta/dashboard.base`: Bases ダッシュボード(Obsidian v1.9.10+ で動作)
- `wiki/meta/dashboard.md`: 旧 Dataview ダッシュボード(任意)

グラフビューには 5 ページの接続クラスタが見えます。1 件取り込み後の wiki の姿です。ソースを増やすほど成長します。

<p align="center">
  <img src="wiki/meta/wiki-graph-grow.gif" alt="知識グラフの成長" width="48%" />
  <img src="wiki/meta/workflow-loop.gif" alt="ワークフローループ" width="48%" />
</p>

---

## コンパニオン: claude-canvas

ビジュアルレイヤ用に [claude-canvas](https://github.com/AgriciDaniel/claude-canvas) があります。AI が組み立てるキャンバス作成 — 知識グラフ、プレゼン、フローチャート、ムードボードを 12 テンプレート + 6 レイアウトアルゴリズムで実現。claude-obsidian Vault を自動検知します。

```bash
claude plugin install AgriciDaniel/claude-canvas
```

---

## コミュニティ

- [ブログ記事](https://agricidaniel.com/blog/claude-obsidian-ai-second-brain) — 競合分析、データチャート、ワークフローデモ込み(英語)
- [AI Marketing Hub](https://www.skool.com/ai-marketing-hub) — 2,800+ 名、無料コミュニティ
- [YouTube](https://www.youtube.com/@AgriciDaniel) — チュートリアルとデモ
- [全オープンソースツール](https://github.com/AgriciDaniel) — claude-seo, claude-ads, claude-blog ほか

---

*[Andrej Karpathy の LLM Wiki パターン](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) に基づく。作者 [Agrici Daniel](https://agricidaniel.com/about)。日本語ローカライズ追加。*
