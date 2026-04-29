---
type: concept
title: "チェリーピック: エコシステム調査からの機能バックログ"
created: 2026-04-08
updated: 2026-04-08
tags:
  - backlog
  - cherry-picks
  - product-roadmap
  - claude-obsidian
status: current
aliases:
  - "cherry-picks"
  - "Cherry-Picks"
  - "チェリーピック"
related:
  - "[[claude-obsidian-ecosystem]]"
  - "[[LLM Wiki Pattern]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# チェリーピック: 機能バックログ

> エコシステム調査(2026-04-08)から抽出 | 16 以上のプロジェクトを分析
> 優先順位: インパクト × 実装容易性 × 独自性

---

## Tier 1: クイックウィン(高インパクト・低工数)

### 1. /wiki-ingest での URL 取り込み
**出典**: ekadetov/llm-wiki、Ar9av/obsidian-wiki
**内容**: ファイルパスではなく URL を直接 ingest に渡す。エージェントがページを取得・クリーンアップして `.raw/` に保存し、通常の ingest を続ける。
**現状**: ユーザーが手動で Web コンテンツをコピー&ペーストする必要がある。
**追加方法**: ingest スキルで `https://` プレフィックスを検出 → WebFetch → `.raw/articles/` に保存 → 通常の ingest を進行。
**ボーナス**: クリーンでトークン効率の高い抽出のため、**defuddle**(kepano の Web クリーナー)と組み合わせる。

### 2. PostToolUse 自動コミットフック
**出典**: ballred/obsidian-claude-pkm、ekadetov/llm-wiki
**内容**: vault 内のすべての Write/Edit ツール呼び出しが `git add -A && git commit -m "auto: [filename] [timestamp]"` をトリガする。
**現状**: 自動コミットなし。ユーザーが手動でプッシュする必要がある。
**追加方法**: Write + Edit ツールを対象とする hooks.json の PostToolUse フック、wiki/ ディレクトリにスコープ。
**注**: vault が自動的にバージョン管理された知識ベースとなる。

### 3. defuddle Web クリーニングスキル
**出典**: kepano/obsidian-skills
**内容**: `defuddle-cli` をラップするスキル。ingest 前に Web ページから広告、ナビ、雑多な要素を取り除く。典型的な Web 記事でトークン使用量を約 40〜60% 削減する。
**追加方法**: 新規 `defuddle` サブスキルか、wiki-ingest からの参照。`defuddle-cli` npm パッケージが必要。

---

## Tier 2: 中工数・高価値

### 4. デルタトラッキングマニフェスト
**出典**: Ar9av/obsidian-wiki
**内容**: `.raw/.manifest.json` で ingest 済みのすべてのソースを追跡する。パス、ハッシュ、タイムスタンプ、生成された Wiki ページを記録。再 ingest は新規/変更ファイルのみを処理する。
**現状**: 毎回の `/wiki-ingest` ですべてが再処理される。
**追加方法**:
  - ingest 時: ソースの MD5 ハッシュを計算 → マニフェストを確認 → 未変更ならスキップ
  - ingest 時: `{path, hash, ingested_at, pages_created}` をマニフェストに記録
  - 更新時: ハッシュが変わったら再処理し、変更を既存ページにマージ

### 5. マルチ深度クエリモード
**出典**: rvk7895/llm-knowledge-bases
**内容**: `/wiki-query` の 3 つのクエリ層。
  - **Quick**: hot.md + index.md のみ(約 3 ページ読み込み)
  - **Standard**: 完全な Wiki 相互参照 + 任意の Web 検索補完
  - **Deep**: 並列サブエージェント、それぞれが異なる切り口を調査
**現状**: 1 つの深度レベルのみ。
**追加方法**: SKILL.md で `/wiki-query quick <question>`、`/wiki-query deep <question>` フラグ。

### 6. /wiki-ingest のビジョン対応
**出典**: Ar9av/obsidian-wiki
**内容**: 画像、スクリーンショット、ホワイトボード写真を ingest する。画像をビジョン対応モデルに渡す。
**追加方法**: 画像拡張子を検出 → base64 として読む → 書き起こし/説明を求めるビジョンプロンプトとともに Claude へ渡す → 結果をテキストソースとして扱う → 標準 ingest パイプライン。
**有用な場面**: 会議のホワイトボード写真、Web コンテンツのスクリーンショット、図表。

---

## Tier 3: 計画に値する大型機能

### 7. /adopt: 既存 vault のインポート
**出典**: heyitsnoah/claudesidian、ballred/obsidian-claude-pkm
**内容**: `/adopt` は既存の Obsidian vault を分析し、整理方法(PARA、Zettelkasten、LYT、プレーン)を検出して、既存構造を破壊せずに LLM Wiki パターンを巻きつける。
**重要性**: 現状ユーザーはゼロから始める必要がある。これにより既存 vault を持つ人々の採用が解放される。
**実装**: フォルダ構造をスキャン → パターン分類 → 既存フォルダを Wiki 役割にマッピングする CLAUDE.md 生成 → 非破壊的。

### 8. プロダクティビティラッパー(日次/週次レビュー)
**出典**: ballred/obsidian-claude-pkm
**内容**: 目標トラッキングを知識ベースに接続するオプションの `/daily` と `/weekly` スキル。
**claude-obsidian 内に同梱せず、別プラグインとして切り出すのも可。**
**ゴール階層**: 3 年ビジョン → 年次目標 → プロジェクト → 週次 → 日次。

### 9. マルチエージェント互換(Cursor、Windsurf、Codex)
**出典**: Ar9av/obsidian-wiki、kepano/obsidian-skills
**内容**: `setup.sh` または `/wiki-convert` コマンドで `.cursor/rules/`、`AGENTS.md`、`GEMINI.md` 相当を生成し、他のコーディングエージェントでも Wiki スキルが動作するようにする。
**注**: kepano はすでに Agent Skills 形式でスキルを公開している。claude-obsidian もすでにその形式だ。アダプタファイルが必要なだけ。

### 10. Marp プレゼンテーション出力
**出典**: rvk7895/llm-knowledge-bases、ekadetov/llm-wiki
**内容**: `/wiki-query --slides <topic>` が Wiki コンテンツから Marp プレゼンテーションを生成し、`output/` に保存する。
**必須**: `marp-cli` npm パッケージ。

---

## Tier 4: リサーチ/エコシステム連携

### 11. obsidian-memory-mcp 統合
**出典**: YuNaga224/obsidian-memory-mcp
**内容**: Claude のメモリを `[[wikilinks]]` 付きの Markdown エンティティとして保存する MCP サーバーを接続する。これらは Obsidian グラフビューに自動で表示される。
**追加方法**: MEMORY_DIR を wiki/entities/ ディレクトリに向ける。エンティティメモリページが正規の Wiki ページとなる。

### 12. obsidian-bases スキル(kepano 由来)
**出典**: kepano/obsidian-skills
**内容**: 動的テーブル、ビュー、フィルタのための Obsidian Bases(.base ファイル)の作成・編集方法を Claude に教える。
**理由**: Obsidian Bases は新しいコア機能。Claude にこの機能を教えている LLM Wiki プロジェクトは他にない。

### 13. スキーマ創発型 vault モード
**出典**: Ar9av/obsidian-wiki
**内容**: 別の /wiki モードで、vault 構造を事前にスキャフォールドせず、ingest されたコンテンツから創発させる。構造化ドメインに対して、探索的な知識構築に向く。
**方法**: スキャフォールドステップを省略し、wiki-ingest がソースコンテンツに基づいて有機的にフォルダ/カテゴリを作る。

---

## 競合ポジショニング

このリサーチを終えても、claude-obsidian の独自優位は健在だ。

- **ホットキャッシュ**: 他には誰もこのセッションコンテキスト機構を持たない
- **キャンバスのビジュアル層**: LLM Wiki カテゴリで唯一
- **/save 会話**: チャット → Wiki のファイリングは独自のワークフロー
- **マーケットプレイスの磨き込み**: カテゴリ最高のインストール体験
- **コミュニティ流通**(avalonreset-pro)

エコシステムは急速に成熟している。Tier 1 項目(URL ingest、自動コミット、defuddle)を v1.3.0 で出荷して先行を保つべきだ。

---

## 実装優先順位

```
v1.3.0 (quick wins):
  - URL ingestion (#1)
  - Auto-commit hook (#2)
  - defuddle integration (#3)

v1.4.0 (quality):
  - Delta tracking (#4)
  - Multi-depth query (#5)

v1.5.0 (expansion):
  - Vision ingest (#6)
  - /adopt command (#7)
  - Multi-agent compat (#9)

Future:
  - Productivity wrapper (#8)
  - Marp output (#10)
  - Memory MCP integration (#11)
```
