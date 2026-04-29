# claude-obsidian — インストールガイド(日本語ローカライズ版)

**Claude + Obsidian ナレッジコンパニオン**
バージョン 1.6.0 · [github.com/AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)

> 🇯🇵 **このフォークは日本語ローカライズ版です。** チャット応答・ウィキ書き込み・ログ・要約はすべて日本語で行われます。ファイル名・スキル名・コードは英語のままで上流プラグインと完全互換です。詳細は `CLAUDE.md` の言語ポリシー参照。

> **任意: DragonScale Memory 拡張。** フラットな抽出的 log fold、決定論的ページアドレス、セマンティックタイリング lint、境界優先 autoresearch トピック選択が欲しい場合、ベースインストール後に `bash bin/setup-dragonscale.sh` を実行。ベースに加えて追加前提: `flock`(Linux 標準、macOS では `util-linux` 経由)と `python3`(タイリング・境界ヘルパー用)。任意: `ollama` と `nomic-embed-text` の pull(セマンティックタイリング lint(Mechanism 3 のみ)が必要なら。ollama またはモデルが利用不可なら正常に no-op)。境界優先スコアラ(Mechanism 4)は `python3` のみ必要、ollama 不要。詳細は [`docs/dragonscale-guide.md`](./dragonscale-guide.md)、フル仕様は `wiki/concepts/DragonScale Memory.md`、1.6.0 の変更内容は `CHANGELOG.md` 参照。

---

## claude-obsidian とは?

claude-obsidian は Claude Code プラグイン + Obsidian Vault で、永続的に成長するナレッジベースを構築・維持します。投入したソースは相互参照付きの wiki ページに処理されます。投げた質問はそれまで読んだすべてから回答を引き出します。知識は複利のように積み上がります。

Andrej Karpathy の LLM Wiki パターンに基づきます。

---

## 前提

| ツール | 取得方法 | 備考 |
|------|--------------|-------|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | 無料プランあり |
| **Obsidian** | [obsidian.md](https://obsidian.md) | 無料 |
| **Git** | ほとんどのシステムにプリインストール | オプション 1 用 |

---

## インストール

### オプション 1 — Vault としてクローン(推奨)

完全セットアップが 2 分以内。

```bash
git clone https://github.com/AgriciDaniel/claude-obsidian
cd claude-obsidian
bash bin/setup-vault.sh
```

その後 Obsidian で: **Vault を管理 → フォルダを Vault として開く → `claude-obsidian/` を選択**

同じフォルダで Claude Code を開き `/wiki` を入力。

### オプション 2: Claude Code プラグインとしてインストール

Claude Code でのプラグインインストールは 2 ステップ。まずマーケットプレイスを追加し、次にそこからプラグインをインストール。

```bash
# ステップ 1: マーケットプレイスを追加
claude plugin marketplace add AgriciDaniel/claude-obsidian

# ステップ 2: プラグインをインストール
claude plugin install claude-obsidian@claude-obsidian-marketplace
```

インストール確認:
```bash
claude plugin list
```

任意の Claude Code セッションで `/wiki` を入力すれば Claude が Vault セットアップを案内。

### オプション 3 — 既存の Vault に追加

このリポジトリの `WIKI.md` を Vault のルートにコピー。次に Claude に貼り付け:

```
このプロジェクトの WIKI.md を読んで。次に:
1. Obsidian がインストール済みか確認、未インストールなら入れる。
2. Local REST API プラグインがポート 27124 で動いているか確認。
3. MCP サーバを構成。
4. ひとつだけ質問: 「この Vault は何のため?」
そしてウィキ構造を足場として作る。
```

---

## 最初のステップ

### 1. Vault の足場

Claude Code で `/wiki` を入力。Claude は:
- Vault モードを検出(website、GitHub、business、personal、research、または book/course)
- フォルダ構造とコア wiki ページを作成
- `wiki/index.md`、`wiki/hot.md`、`wiki/log.md`、`wiki/overview.md` をセットアップ

### 2. 最初のソースを投入

任意の文書を `.raw/` に配置:
- PDF、Markdown ファイル、トランスクリプト、記事、URL

Claude に伝える: `[ファイル名] を取り込んで`(英語の `ingest [filename]` も同等)

Claude はソースを読み 8〜15 の相互参照付き wiki ページを日本語で作成。

### 3. 質問する

```
[トピック] について何を知ってる?
```

Claude はホットキャッシュを読み、index をスキャンし、関連ページに踏み込み、合成回答を返す — 学習データではなく特定の wiki ページを引用して。

---

## コマンドリファレンス

| コマンド | Claude の動作 |
|---------|-----------------|
| `/wiki` | セットアップ確認、足場、または続きから再開 |
| `[ファイル] を取り込んで` / `ingest [file]` | ソースを読み、8〜15 ページ作成、index と log 更新 |
| `これら全部を取り込んで` | 複数ソースをバッチ処理し、相互参照 |
| `X について何を知ってる?` | index → 関連ページ → 回答合成 |
| `/save` | 現在の会話を wiki ノートとして保存 |
| `/save [name]` | 特定タイトルで保存 |
| `/autoresearch [topic]` | 自律リサーチループ: 検索・取得・合成・保存 |
| `/canvas` | ビジュアルキャンバスを開く・作成 |
| `/canvas add image [path]` | キャンバスに画像追加 |
| `/canvas add text [content]` | Markdown テキストカード追加 |
| `/canvas add pdf [path]` | PDF 文書追加 |
| `/canvas add note [page]` | wiki ページをリンクカードとしてピン |
| `wiki を lint して` | 健全性チェック: 孤立、デッドリンク、ギャップ |
| `ホットキャッシュを更新` | 最新コンテキスト要約で `hot.md` をリフレッシュ |

---

## プラグイン(プリインストール)

**設定 → コミュニティプラグイン** で有効化:

| プラグイン | 用途 |
|--------|---------|
| **Calendar** | 単語数・タスクドット付きの右サイドバーカレンダー |
| **Thino** | クイックメモキャプチャパネル |
| **Excalidraw** | 手描き、画像注釈 |
| **Banners** | `banner:` frontmatter によるヘッダー画像 |

別途コミュニティプラグインから:

| プラグイン | 用途 |
|--------|---------|
| **Dataview** | ダッシュボードクエリの動力源 |
| **Templater** | テンプレートから frontmatter を自動補完 |
| **Obsidian Git** | 15 分ごとに自動コミット |

---

## CSS スニペット

3 つのスニペットが `setup-vault.sh` で自動有効化:

| スニペット | 効果 |
|---------|--------|
| `vault-colors` | wiki フォルダをファイルエクスプローラで色分け |
| `ITS-Dataview-Cards` | Dataview クエリをビジュアルカードグリッド化 |
| `ITS-Image-Adjustments` | 細かな画像サイズ調整 — 埋め込みに `\|100` を付加 |

---

## 6 つのウィキモード

| モード | 適用 |
|------|---------|
| **A: Website** | サイトマップ、コンテンツ監査、SEO ウィキ |
| **B: GitHub** | コードベースマップ、アーキテクチャウィキ |
| **C: Business** | プロジェクトウィキ、競合インテリジェンス |
| **D: Personal** | セカンドブレイン、目標、ジャーナル合成 |
| **E: Research** | 論文、概念、論文執筆 |
| **F: Book/Course** | 章管理、コースノート |

モードは組み合わせ可能。

---

## MCP セットアップ(任意)

MCP は Claude がコピペなしで Vault ノートを直接読み書きできるようにする。

**オプション A — REST API:**

1. Obsidian に **Local REST API** プラグインをインストール
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

**オプション B — ファイルシステム(プラグイン不要):**

```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@bitbonsai/mcpvault@latest", "/path/to/your/vault"]
}' --scope user
```

---

## トラブルシューティング

| 問題 | 解決 |
|---------|-----|
| `/wiki` が「見つからない」と言う | `claude-obsidian` プラグインが有効化されているか確認: `claude plugin list` |
| Obsidian を閉じたらグラフ色がリセット | グラフビュー → 歯車 → カラーグループ → 一度だけ追加し直す。以後は永続化。 |
| Excalidraw がロードしない | `bash bin/setup-vault.sh` を実行して `main.js`(8MB、git 外)をダウンロード |
| ダッシュボードに何も表示されない | コミュニティプラグインから **Dataview** をインストール |
| セッション開始時にホットキャッシュがロードされない | hook を確認: `claude hooks list` — SessionStart hook が存在するべき |

---

## クロスプロジェクト活用

任意の Claude Code プロジェクトをこの Vault に向ける。向こうのプロジェクトの `CLAUDE.md` に追記:

```markdown
## ウィキナレッジベース
パス: ~/path/to/claude-obsidian

このプロジェクトに無いコンテキストが必要なとき:
1. まず wiki/hot.md(直近コンテキストキャッシュ)を読む
2. 足りなければ wiki/index.md を読む
3. ドメイン詳細が必要なら関連 wiki ページを読む

一般的なコーディング質問には wiki を読まない。
```

エグゼクティブアシスタント、コーディングプロジェクト、コンテンツワークフローのすべてが同じナレッジベースから引き出せる。

---

## サポート

- **GitHub**: [github.com/AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
- **Issues**: [github.com/AgriciDaniel/claude-obsidian/issues](https://github.com/AgriciDaniel/claude-obsidian/issues)
- **コミュニティ**: [AI Marketing Hub on Skool](https://skool.com)

---

*作: [AgriciDaniel](https://github.com/AgriciDaniel) / AI Marketing Hub*
*Andrej Karpathy の LLM Wiki パターンに基づく。日本語ローカライズ追加。*
