# MCP セットアップ

MCP は Claude がコピペなしで Vault ノートを直接読み書きできるようにする。最も簡単なものから多機能なものへ 4 つのオプション。

> [!tip] 推奨
> **Obsidian v1.12 以降** なら **オプション D: Obsidian CLI** から始める。MCP サーバ不要、プラグイン不要、TLS 回避不要。永続的な MCP 統合が必要なときや古い Obsidian バージョンのときのみ A や B を使う。

---

## ステップ 1: Local REST API プラグインのインストール

これは Obsidian で行う必要あり(Claude はプログラム的にできない):

1. Obsidian → 設定 → コミュニティプラグイン → 制限モードをオフ
2. ブラウズ → 「Local REST API」を検索 → インストール → 有効化
3. 設定 → Local REST API → API キーをコピー

プラグインは自己署名証明書付きで `https://127.0.0.1:27124` で動作。

テスト:
```bash
curl -sk -H "Authorization: Bearer <YOUR_KEY>" https://127.0.0.1:27124/
```

Vault 情報の JSON 応答が返るはず。

---

## オプション A: mcp-obsidian(REST API ベース)

MarkusPfundstein の mcp-obsidian を使用。Local REST API プラグインの稼働が必要。

```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "uvx",
  "args": ["mcp-obsidian"],
  "env": {
    "OBSIDIAN_API_KEY": "<YOUR_KEY>",
    "OBSIDIAN_HOST": "127.0.0.1",
    "OBSIDIAN_PORT": "27124",
    "NODE_TLS_REJECT_UNAUTHORIZED": "0"
  }
}' --scope user
```

> [!warning] セキュリティ
> `NODE_TLS_REJECT_UNAUTHORIZED: "0"` は MCP サーバのプロセス全体で **TLS 証明書検証を無効化** する。Local REST API プラグインが自己署名証明書を使うためここでは必要。`127.0.0.1`(localhost)接続にのみ許容できる。ループバック以外の接続には絶対に使わない。グローバル TLS バイパスが不安なら、それを完全に避ける **オプション D(Obsidian CLI)** または **オプション B(ファイルシステムベース)** を選ぶ。

機能: ノート読み取り、ノート書き込み、検索、frontmatter フィールドの patch、見出し配下への追記。

---

## オプション B: MCPVault(ファイルシステムベース)

Obsidian プラグイン不要。Vault ディレクトリを直接読む。

```bash
claude mcp add-json obsidian-vault '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@bitbonsai/mcpvault@latest", "/absolute/path/to/your/vault"]
}' --scope user
```

`/absolute/path/to/your/vault` を実際の Vault パスに置き換える。

利用可能なツール: `search_notes`(BM25), `read_note`, `create_note`, `update_note`, `get_frontmatter`, `update_frontmatter`, `list_all_tags`, `read_multiple_notes`。

---

## オプション C: curl で直接 REST API

MCP 不要。セッション中ずっと bash で curl を使う。すべてのコマンドは `rest-api.md` 参照。

---

## オプション D: Obsidian CLI(v1.12+ では推奨)

Obsidian は v1.12(2026)でネイティブ CLI を出荷。Vault 操作をターミナルに直接公開。REST API プラグイン不要、MCP サーバ不要、自己署名証明書不要、TLS 回避不要。Claude が Bash ツール経由で呼ぶ。

**利用可能性確認:**
```bash
which obsidian-cli 2>/dev/null && obsidian-cli --version
# または flatpak の場合:
flatpak run md.obsidian.Obsidian --cli --version
```

**よくある操作:**
```bash
# フォルダ内の全ノート一覧
obsidian-cli list /path/to/vault wiki/

# ノート読み取り
obsidian-cli read /path/to/vault wiki/index.md

# ノート作成・更新
obsidian-cli write /path/to/vault wiki/new-note.md < content.md

# 内容でノート検索
obsidian-cli search /path/to/vault "クエリ語"
```

**なぜ推奨か**:
- プラグインインストール不要(CLI は Obsidian 組み込み)
- 管理する MCP サーバプロセス無し
- TLS 証明書バイパス不要
- Obsidian 再起動を生き延びる(永続接続なし)
- デスクトップとヘッドレス環境で同一動作

**A/B/C を使うべきとき**: 永続的なセマンティック検索、frontmatter patching が必要、または Obsidian < v1.12 の場合。

`kepano/obsidian-skills` リポジトリには再利用可能なパターンとしてこれらのコマンドをラップする `obsidian-cli` スキルが含まれる。一級 CLI サポートのため本プラグインと一緒にインストール。

---

## `--scope user` を使う

両方の MCP オプションで `--scope user` を使い、コマンドを実行したプロジェクトだけでなく全 Claude Code プロジェクトで Vault が利用可能にする。

---

## 検証

セットアップ後:

```bash
claude mcp list               # サーバが表示されるか確認
claude mcp get obsidian-vault # パスや URL が正しいか確認
```

Claude Code セッションで `/mcp` を入力して接続状態確認。

その後テスト: 「wiki フォルダ内の全ノートを一覧して。」
