---
type: session
title: "claude-obsidian v1.2.0 リリースセッション"
created: 2026-04-07
updated: 2026-04-07
aliases:
  - claude-obsidian-v1.2.0-release-session
  - "claude-obsidian v1.2.0 リリースセッション"
tags:
  - session
  - release
  - plugin
  - github
status: evergreen
related:
  - "[[getting-started]]"
  - "[[index]]"
  - "[[overview]]"
  - "[[LLM Wiki Pattern]]"
---

# claude-obsidian v1.2.0 リリースセッション

claude-obsidianプラグイン+vaultキットの完全なビルド、監査、磨き上げ、コミュニティリリース。以前は`cosmic-brain`という名称だった。

---

## 構築内容

### フェーズ1:重要修正
- `marketplace.json`:バージョンを`1.0.0→1.2.0`に修正、オーナーメタデータを更新
- `main.canvas`:壊れたファイルノード参照5件を削除(コミュニティユーザーには存在しないgitignore対象ファイル)
- `community-plugins.json`:6→4の正規エントリへ重複排除:`[excalidraw, banners, calendar, thino]`

### フェーズ2:Vaultオンボーディング
- `wiki/getting-started.md`:vault内に新たなオンボーディングページを作成(3ステップのクイックスタート、ホットキャッシュの説明、コマンドリファレンス、ナビゲーションリンク)
- `wiki/index.md`:Entities、Questions、Comparisonsの各セクションに既存のシードページを記載
- `wiki/meta/dashboard.md`:Dataviewクエリを修正:シードページに存在しない`answer_quality`と`confidence`フィールドをクエリしていた。`status`と`updated`に置換
- `CLAUDE.md`:プレースホルダーを実際のvault説明に置換
- `wiki/canvases/welcome.canvas`:getting-startedと`/wiki`を指すCTAノードを追加

### フェーズ3:README + ドキュメント
- README:プリインストールプラグイン表を完全化、CSSスニペットセクション、Bannerの利用方法セクション、ファイル構成を更新
- `bin/setup-vault.sh`:成功メッセージで4つのプリインストールプラグインと3つのCSSスニペットすべてを列挙

### フェーズ4:PDFインストールガイド
- `docs/install-guide.md`:印刷可能な完全インストールガイド(前提条件、3つのインストールオプション、初回セットアップ、コマンドリファレンス、プラグインガイド、MCPセットアップ、トラブルシューティング)
- `docs/install-guide.pdf`:159KB、`npx md-to-pdf`で生成

### フェーズ5:バージョンバンプ
- `plugin.json`と`marketplace.json`を`1.2.0`にバンプ

---

## リネーム: cosmic-brain → claude-obsidian

プロジェクト全体のリネームを実行:
- GitHubリポジトリのリネーム:`AgriciDaniel/cosmic-brain` → `AgriciDaniel/claude-obsidian`(公開)、`avalonreset-pro/cosmic-brain` → `avalonreset-pro/claude-obsidian`(非公開)
- ローカルディレクトリ:`~/cosmic-brain/` → `~/claude-obsidian/`
- 14ファイルにわたるテキスト参照をすべてsedで更新
- `wiki/meta/cosmic-brain-cover.gif`を`wiki/meta/claude-obsidian-cover.gif`にリネーム

---

## 法務とセキュリティ

### セキュリティ監査
- 追跡ファイルにAPIキー、トークン、シークレットは見つからず
- 秘密鍵や証明書も無し
- ドキュメント内の資格情報参照はすべてプレースホルダー値
- Excalidrawの`main.js`は監査エージェントの主張に反し、正しく追跡対象外となっていた

### 法務修正
- `LICENSE`:MITライセンスファイルを作成(plugin.jsonでは宣言されていたがファイルが欠落していた)
- `ITS-Dataview-Cards.css` + `ITS-Image-Adjustments.css`:GPL-2.0表記ヘッダーを追加

### .gitignoreの厳格化
動画ファイル(`*.mkv`、`*.mp4`)、トランスクリプト、スクラッチキャンバス(`Untitled *.canvas`、`*Images.canvas`)、vaultルート内の個人画像が誤って今後コミットされるのを防ぐルールを追加。

---

## ビジュアル/README

### GIFと画像
- 新しいClaude Obsidianブランド資産を追加(16x9カバーGIF、1x1 GIF、静的PNG)
- 圧縮:`gif-cover-16x9.gif` 2.6MB→1.3MB(50%)、`gif-1x1.gif` 2.6MB→848KB(68%):FFmpegパレット最適化、960px/640pxにスケール、15fps、128色パレットによる
- サンプルスクリーンショットを追加:`image-example-graph-view.png`、`image-example-wiki-map-view.png`

### README構成(上から下)
1. `claude-obsidian-gif-cover-16x9.gif`:ヘッダー
2. 説明文
3. `welcome-canvas.gif`:What It Doesのデモ(全幅)
4. 説明的な段落
5. `image-example-graph-view.png` + `image-example-wiki-map-view.png`:横並びのスクリーンショット
6. Quick Start → Commands → Cross-Project → Six Modes → What Gets Created → MCP → Plugins → CSS Snippets → Banner → File Structure → AutoResearch → Seed Vault
7. `wiki-graph-grow.gif` + `workflow-loop.gif`:Seed Vaultセクション末尾

---

## リポジトリ状態

| リポジトリ | 公開範囲 | URL |
|------|-----------|-----|
| AgriciDaniel/claude-obsidian | 公開 | https://github.com/AgriciDaniel/claude-obsidian |
| avalonreset-pro/claude-obsidian | 非公開 | https://github.com/avalonreset-pro/claude-obsidian |

コミュニティ向けインストールコマンド: `claude plugin install github:AgriciDaniel/claude-obsidian`

今後の更新: `git push origin main && git push community main`

---

## 主要な意思決定

- **claude-obsidianへのリネーム**:より明確なブランディング、Claude+Obsidianのペアリングを直ちに伝える
- **avalonreset-proリポジトリは非公開**:コミュニティメンバー専用、公開しない
- **Excalidrawのmain.jsはgit管理外**:`setup-vault.sh`がセットアップ時に8MBをダウンロード
- **同梱プラグインの再配布**:許容できる:4つのプラグインすべてがObsidianコミュニティプラグインシステム経由で公開配布されている
- **GIF圧縮戦略**:パレット縮小(256→128色)+解像度スケーリングで、GitHubのレンダリング幅では視覚的劣化なしに50〜68%節約
