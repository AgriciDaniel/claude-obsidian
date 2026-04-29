---
description: ビジュアルキャンバスを開く・作成・更新 — 画像、テキスト、PDF、wiki ページ、banana 生成アセットを Obsidian キャンバスファイルに追加。応答は日本語(プロジェクト CLAUDE.md の言語ポリシー参照)。
---

`canvas` スキルを読む。次にユーザーのコマンドにマッチする操作を実行。

| コマンド | 動作 |
|---------|-------------|
| `/canvas` | ステータス確認 — ノード数を報告、ゾーン一覧、操作説明 |
| `/canvas new [name]` | wiki/canvases/ に新しい名前付きキャンバスを作成 |
| `/canvas add image [path]` | キャンバスに画像追加(URL ならダウンロード、Vault 外ならコピー) |
| `/canvas add text [content]` | キャンバスにテキストカードを追加 |
| `/canvas add pdf [path]` | PDF 文書ノードを追加 |
| `/canvas add note [page]` | wiki ページをリンクカードとして追加 |
| `/canvas zone [name] [color]` | 新しいラベル付きゾーングループを追加 |
| `/canvas list` | 全キャンバスをノード数とともに一覧 |
| `/canvas from banana` | 直近の生成画像を見つけて追加 |

デフォルトキャンバス: `wiki/canvases/main.canvas`

キャンバスファイルが存在しない場合、何かを追加する前に作成。
