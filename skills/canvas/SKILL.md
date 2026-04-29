---
name: canvas
description: "ウィキのビジュアルレイヤ。画像、テキストカード、PDF、wiki ページを Obsidian のキャンバスファイルにゾーン内自動配置で追加する。/banana(画像生成)とも連携。応答とラベルは日本語(プロジェクト CLAUDE.md の言語ポリシー参照)。トリガー(日本語): /canvas、キャンバス新規、キャンバスに画像追加、キャンバスにテキスト追加、キャンバスに PDF 追加、キャンバスにノート追加、キャンバスゾーン、キャンバス一覧、banana からキャンバスへ、キャンバスに追加、これをキャンバスに、キャンバスを開く、キャンバスを作成。Triggers (English): /canvas, canvas new, canvas add image, canvas add text, canvas add pdf, canvas add note, canvas zone, canvas list, canvas from banana, add to canvas, put this on the canvas, open canvas, create canvas."
allowed-tools: Read Write Edit Glob Grep
---

# canvas: ビジュアルリファレンスレイヤ

3 つの知識キャプチャレイヤ:
- `/save` → テキスト合成(wiki/questions/, wiki/concepts/)
- `/autoresearch` → 構造化知識(wiki/sources/, wiki/concepts/)
- `/canvas` → ビジュアル参照(wiki/canvases/)

キャンバスは Obsidian が無限のビジュアルボードとしてレンダリングする JSON ファイルです。このスキルはキャンバス JSON を直接読み書きします。任意の編集前に `references/canvas-spec.md` で完全な形式リファレンスを読んでください。この仕様は [JSON Canvas オープン標準](https://jsoncanvas.org/) に準拠します。kepano/obsidian-skills プラグインがインストールされている場合、その json-canvas スキルが正規のキャンバス仕様リファレンスです。なければ下のガイダンスに従います。

> **言語ルール**: グループ・ラベル・テキストノードの表示テキストは日本語で書く。ファイルパス・ID・JSON キーは英語のまま。

---

## デフォルトキャンバス

`wiki/canvases/main.canvas`

存在しなければ作成:

```json
{
  "nodes": [
    {
      "id": "title",
      "type": "text",
      "text": "# ビジュアルリファレンス\n\n画像、PDF、ノートをここに置く。",
      "x": -400, "y": -300, "width": 400, "height": 120, "color": "6"
    },
    {
      "id": "zone-default",
      "type": "group",
      "label": "全般",
      "x": -400, "y": -140, "width": 800, "height": 400, "color": "4"
    }
  ],
  "edges": []
}
```

---

## 操作

### open / status(`/canvas` 引数なし)

1. `wiki/canvases/main.canvas` の存在を確認。
2. あれば: 読み、タイプ別ノード数を数え、すべてのグループノードラベル(ゾーン名)をリスト化。
   報告: 「キャンバスには N 個のノード: 画像 X、テキスト Y、wiki ページ Z。ゾーン: [list]」
3. なければ: 上のスタータ構造で作成。
   報告: 「全般ゾーン付きで main.canvas を作成しました。」
4. ユーザーに伝える: 「Obsidian で `wiki/canvases/main.canvas` を開いて確認してください。」

---

### new(`/canvas new [name]`)

1. 名前をスラッグ化: 小文字、空白 → ハイフン、特殊文字を除去(英語スラッグ)。
2. `wiki/canvases/[slug].canvas` をスタータ構造で作成、タイトルを `# [Name](日本語可)` に更新。
3. `wiki/overview.md` の「## キャンバス」サブセクション(現状セクションの後ろに追加)にエントリを追加。`wiki/index.md` は変更しない。固定セクションスキーマ(ドメイン、エンティティ、概念、ソース、質問、比較)を使用しているため。
4. 報告: 「wiki/canvases/[slug].canvas を作成しました」

---

### add image(`/canvas add image [path or url]`)

**画像を解決:**
- URL の場合(`http` で始まる): `curl -sL [url] -o _attachments/images/canvas/[filename]` でダウンロード
  ファイル名は URL パスから導出、不明なら `img-[timestamp].jpg` を使用。
- Vault 外のローカルパスの場合: `cp [path] _attachments/images/canvas/`
- すでに Vault 相対の場合: そのまま使用。

`_attachments/images/canvas/` が無ければ作成。

**アスペクト比を検出:**
`python3 -c "from PIL import Image; img=Image.open('[path]'); print(img.width, img.height)"` または `identify -format '%w %h' [path]` を使用。
完全なアスペクト比 → キャンバスサイズ表(4:3, 3:4, ウルトラワイドを含む 7 比率)は `references/canvas-spec.md` 参照。ここにインライン表は置かない。仕様がサイズ決定の単一情報源。

**自動レイアウトで配置**(下の自動配置セクション参照)。

**ノードをキャンバス JSON に追記して書き込む。**

報告: 「[filename] を [zone] ゾーンの位置 ([x], [y]) に追加しました。」

---

### add text(`/canvas add text [content]`)

テキストノードを作成:
```json
{
  "id": "text-[timestamp]",
  "type": "text",
  "text": "[内容(日本語可)]",
  "x": [auto], "y": [auto],
  "width": 300, "height": 120,
  "color": "4"
}
```

自動レイアウトで配置。書き込んで報告。

---

### add pdf(`/canvas add pdf [path]`)

add image と同じ。Obsidian は PDF をネイティブにファイルノードとしてレンダリング。
- Vault 外なら `_attachments/pdfs/canvas/` にコピー。
- 固定サイズ: width=400, height=520。
- 判別できればページ数を報告。

---

### add note(`/canvas add note [wiki-page]`)

1. `wiki/` でページ名にマッチするファイルを検索(大文字小文字無視、部分一致 OK)。
2. Vault 相対パスを `file` フィールドに使用。
   - `"type": "file"` を使う(`"type": "link"` ではなく): `.md` ファイルはファイルノードを使い、リンクノードではない。
   - `"type": "link"` は `url: "https://..."` を取る: Web URL 専用。
3. ファイルノードを作成: width=300, height=100。
4. 自動レイアウトで配置。

```json
{
  "id": "note-[timestamp]",
  "type": "file",
  "file": "wiki/concepts/LLM Wiki Pattern.md",
  "x": [auto], "y": [auto],
  "width": 300, "height": 100
}
```

---

### zone(`/canvas zone [name] [color]`)

1. キャンバス JSON を読む。
2. max_y を求める: `max(node.y + node.height for all nodes) + 60`。ノード無しなら 280(スタータタイトルノードの上にスペースを残す)。
3. グループノードを作成:

```json
{
  "id": "zone-[slug]",
  "type": "group",
  "label": "[name(日本語可)]",
  "x": -400,
  "y": [max_y],
  "width": 1000,
  "height": 400,
  "color": "[color or '3']"
}
```

有効な色: `"1"`=赤 `"2"`=オレンジ `"3"`=黄 `"4"`=緑 `"5"`=シアン `"6"`=紫

書き込んで報告。

---

### list(`/canvas list`)

1. `glob wiki/canvases/*.canvas`
2. 各キャンバス: JSON を読み、タイプ別ノード数をカウント。
3. 報告:

```
wiki/canvases/main.canvas      . 14 ノード(画像 8、テキスト 3、ファイル 2、グループ 1)
wiki/canvases/design-ideas.canvas. 42 ノード(画像 30、テキスト 4、グループ 8)
```

---

### from banana(`/canvas from banana`)(banana-claude プラグインがあれば)

1. まず `wiki/canvases/.recent-images.txt`(セッションで新規書き込みされた画像のログ)を確認。
2. 見つからない・空の場合: `find` を正しい優先順位で使用(かっこ必須。無いと `-newer` は最後の `-name` 句にしか紐づかない):
   ```bash
   python3 -c "import time,os; open('/tmp/ten-min-ago','w').close(); os.utime('/tmp/ten-min-ago',(time.time()-600,time.time()-600))"
   find _attachments/images -newer /tmp/ten-min-ago \( -name "*.png" -o -name "*.jpg" \)
   ```
   注: `/banana` はこのプラグインに同梱されない外部スキル。ユーザーがインストールしていれば `.recent-images.txt` ログが populate される。なければ上の `find` コマンドがフォールバック。
3. それでも無ければ: 直近変更された 5 件の画像を表示。
4. リスト提示: 「直近の画像が N 件見つかりました: [リスト]。キャンバスに追加しますか?どのゾーンに?(ゾーン名 / 'new [名前]' / 'スキップ')」
5. 確認後: add image ロジックで各画像を追加。

---

## 自動配置アルゴリズム

完全な座標系は `references/canvas-spec.md` を参照。

```python
def next_position(canvas_nodes, target_zone_label, new_w, new_h):
    # ゾーングループノードを探す
    zone = next((n for n in canvas_nodes
                 if n.get('type') == 'group'
                 and n.get('label') == target_zone_label), None)

    if zone is None:
        # ゾーン無し: 全コンテンツの下に配置
        max_y = max((n['y'] + n.get('height', 0) for n in canvas_nodes), default=-140)
        return -400, max_y + 60

    zx, zy = zone['x'], zone['y']
    zw, zh = zone['width'], zone['height']

    # このゾーン内のノード
    inside = [n for n in canvas_nodes
              if n.get('type') != 'group'
              and zx <= n['x'] < zx + zw
              and zy <= n['y'] < zy + zh]

    if not inside:
        return zx + 20, zy + 20

    rightmost_x = max(n['x'] + n.get('width', 0) for n in inside)
    next_x = rightmost_x + 40

    if next_x + new_w > zx + zw:
        # 新しい行
        max_row_y = max(n['y'] + n.get('height', 0) for n in inside)
        return zx + 20, max_row_y + 20

    # 同じ行: ゾーン内既存ノードのトップに揃える
    current_row_y = min(n['y'] for n in inside)
    return next_x, current_row_y
```

---

## ID 生成

キャンバスを読み、既存 ID をすべて収集。再利用しない。

安全な ID パターン: `[type]-[content-slug]-[full-unix-timestamp]`

バッチ操作での衝突を避けるためフル Unix タイムスタンプ(10 桁)を使用。

例: `img-cover-1744032823`, `text-note-1744032845`, `zone-branding-1744032901`

衝突を検出したら(キャンバスに既存)、`-2`, `-3` などを末尾に追加。

---

## セッションログ(任意の hook)

`wiki/canvases/.recent-images.txt` が存在すれば、本セッション中に `_attachments/images/` に書き込まれた新画像パスを追記(1 行 1 パス、直近 20 件保持)。

`/canvas from banana` はまずこのファイルを読むため、ファイルシステム検索なしで瞬時。

---

## Banana 連携(banana-claude プラグイン導入時)

同セッションでの `/banana` 実行後、ユーザーが「キャンバスに追加」「put on canvas」と言ったら `/canvas from banana` として扱う。

`/banana` が画像生成を完了したら提案:
> 「生成された画像をキャンバスに追加しますか?`/canvas from banana` を実行」

---

## 要約

1. キャンバス JSON 編集前に必ず canvas-spec.md を読む。
2. 書き込み前に必ずキャンバスファイルを読む。既存ノードを解析して ID 衝突を避け、自動配置を計算。
3. ダウンロード/コピーした画像用に `_attachments/images/canvas/` を作成。
4. 新規キャンバス作成時は `wiki/index.md` を更新。
5. 各 add 操作後に位置とゾーンを報告。

## 関連

スタンドアロンのビジュアル制作(12 テンプレート、6 レイアウトアルゴリズム、AI 生成、プレゼン)については [claude-canvas](https://github.com/AgriciDaniel/claude-canvas) を参照。
このスキルは wiki スコープのビジュアルボードを扱う。claude-canvas は任意プロジェクト向けのフル機能キャンバスオーケストレーションを提供する。
