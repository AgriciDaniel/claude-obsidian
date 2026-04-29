# Obsidian セットアップ

---

## Obsidian のインストール

### Linux(Flatpak: 推奨)

インストール状況確認:
```bash
flatpak list 2>/dev/null | grep -i obsidian && echo "FOUND via flatpak" || \
which obsidian 2>/dev/null && echo "FOUND in PATH" || echo "NOT FOUND"
```

未インストールなら:
```bash
flatpak install flathub md.obsidian.Obsidian
```

### macOS

```bash
ls /Applications/Obsidian.app 2>/dev/null && echo "FOUND" || brew install --cask obsidian
```

### Windows

```powershell
Test-Path "$env:LOCALAPPDATA\Obsidian" && echo "FOUND" || winget install Obsidian.Obsidian
```

### 全プラットフォーム共通: 直接ダウンロード

https://obsidian.md/download

---

## Vault を開く

インストール後: Obsidian → Vault を管理 → フォルダを Vault として開く → Vault ディレクトリを選択。

---

## コアプラグイン(組み込み: インストール不要)

Obsidian に同梱。設定 → コアプラグイン で有効化:

| プラグイン | 用途 |
|--------|---------|
| **Bases** | `.base` ファイルへのネイティブな DB 風ビュー。`wiki/meta/dashboard.base` の動力源。Obsidian v1.9.10(2025 年 8 月)以降。**ほとんどの wiki ユースケースで Dataview を置き換え。** |
| **Properties** | ビジュアル frontmatter エディタ。常時有効。 |
| **Backlinks** | 受信・送信リンクペイン。 |
| **Outline** | 文書見出しナビゲーション。 |

## 推奨コミュニティプラグイン

設定 → コミュニティプラグイン → 制限モードオフ → ブラウズ。

| プラグイン | 用途 |
|--------|---------|
| **Templater** | `_templates/` からノート作成時に frontmatter を自動補完。 |
| **Obsidian Git** | 15 分ごとに自動コミット。不正な書き込みから保護。 |
| **Calendar** | 単語数・タスク・リンクインジケータ付きの右サイドバーカレンダー。`.obsidian/plugins/calendar/` 経由でこの Vault に同梱。 |
| **Thino** | 右サイドバーのクイックメモキャプチャパネル。`.obsidian/plugins/thino/` 経由で同梱。 |
| **Iconize** | ナビゲーション用のフォルダアイコン。 |
| **Minimal Theme** | 高密度情報表示に最適なダークテーマ。 |
| **Dataview** *(任意/旧)* | Obsidian < 1.9.10 の場合、または旧 `dashboard.md` クエリを使いたい場合のみ必要。プライマリダッシュボードは Bases。 |

**Calendar と Thino は同梱済み**。この Vault に同梱されている。設定 → コミュニティプラグイン → トグルオンで有効化。ダウンロード不要。

別の Vault にインストールする場合: GitHub リリースから `main.js` + `manifest.json` をそれぞれ `.obsidian/plugins/calendar/` と `.obsidian/plugins/thino/` にダウンロード。

任意の追加:
- **Smart Connections**: 全ノート横断のセマンティック検索
- **QuickAdd**: 高速ノート作成のためのマクロ
- **Folder Notes**: フォルダクリックで概要ノートを開く

---

## Web Clipper

Obsidian Web Clipper ブラウザ拡張は Web 記事を Markdown に変換し `.raw/` にワンクリックで送る。

Obsidian Web サイトから Chrome、Firefox、Safari 用にインストール。

拡張設定でデフォルトフォルダを `.raw/` に設定。

---

## プラグインインストール後

1. Bases を有効化: 設定 → コアプラグイン → トグルオン(Obsidian v1.9.10+ ではデフォルトでオン)
2. Templater を有効化: 設定 → Templater → テンプレートフォルダを `_templates` に
3. Obsidian Git を有効化: 設定 → Obsidian Git → Auto backup interval: 15 分
4. CSS スニペットを有効化: 設定 → 外観 → CSS スニペット → `vault-colors` をトグルオン
5. *(任意)* 旧 `wiki/meta/dashboard.md` クエリをプライマリ `dashboard.base` と並行で使いたい場合のみ Dataview を有効化
