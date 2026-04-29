# Obsidian キャンバス JSON 仕様

キャンバスファイルは 2 つのトップレベルキー(`nodes` 配列と `edges` 配列)を持つ JSON。
Obsidian は `.canvas` 拡張子の UTF-8 JSON ファイルとして読み書き。

このリファレンスは [JSON Canvas 1.0 オープン仕様](https://jsoncanvas.org/spec/1.0/) に準拠。すべての構造は前方互換性のために任意の追加フィールド(`[key: string]: any`)をサポートする。Obsidian はキャンバスファイルの読み書きで未知のフィールドを保持する。

> **言語ルール**: ノードのテキスト・グループラベル・エッジラベルは日本語で書く。`id`、`type`、`file` パス、JSON キーは英語のまま。

**ID 形式**: JSON Canvas 1.0 仕様は 16 文字小文字 16 進 ID(例: `"a1b2c3d4e5f67890"`)を推奨。Obsidian 自体はこの形式で ID を生成する。本リファレンスの説明的な ID 例(`"text-title-4821"`、`"img-cover-7823"`)は人間可読性のために本プラグインが使う代替命名規約。両方とも有効な JSON Canvas。ワークフローに合うものを使う。

---

## 座標系

```
        x が増える →
   ┌─────────────────────────────────
   │  (-920, -2400)      (0, -2400)
   │
y  │  (-920, 0)          (0, 0) ← 原点
↓  │
   │  (-920, 540)        (500, 540)
```

- **原点**(0, 0)はキャンバスビューポートの中央。
- **x は右方向に増加。** 負の x = 中央の左。
- **y は下方向に増加。** 負の y = 中央の上。
- ノードの `x` と `y` は中央ではなく **左上隅**。
- Obsidian は最初に開いたとき全ノードが見えるようにパンする。

---

## ノードタイプ

### テキストノード

Markdown 内容をスタイル付きカードとしてレンダリング。

```json
{
  "id": "text-title-4821",
  "type": "text",
  "text": "# 見出し\n\n**太字** と `code` を含む段落。",
  "x": -400,
  "y": -300,
  "width": 400,
  "height": 120,
  "color": "6"
}
```

- `text`: Markdown 文字列。改行は `\n`。
- 最小可読サイズ: width >= 200, height >= 60。
- `color` は任意。デフォルト(色無し)なら省略。

---

### ファイルノード

画像、PDF、Markdown ノート、その他 Vault ファイルをインライン表示。

```json
{
  "id": "img-cover-7823",
  "type": "file",
  "file": "_attachments/images/example.png",
  "x": -900,
  "y": -100,
  "width": 420,
  "height": 236
}
```

- `file`: **Vault 相対パス**(絶対や `~/` ではない)。
- サポート: `.png` `.jpg` `.webp` `.gif` `.pdf` `.md` `.canvas`
- `.md` ファイル: プレビューカードとしてレンダリング。
- `.pdf` ファイル: 1 ページ目をプレビューレンダリング。
- ファイルノードに `color` 無し: 色は無視される。

---

### グループノード(ゾーン)

ラベル付き矩形領域。ノードをクリップしたり包含したりしない。視覚的なガイド。
グループ「内」に置かれたノードは単にバウンディングボックス内に位置するだけ。

```json
{
  "id": "zone-branding-3391",
  "type": "group",
  "label": "ブランドアイデンティティ",
  "x": -920,
  "y": -880,
  "width": 1060,
  "height": 290,
  "color": "6",
  "background": "_attachments/images/grid-bg.png",
  "backgroundStyle": "cover"
}
```

- `label`: グループボックスの上に表示。日本語可。
- `color`: グループの枠線とラベルを色付け。
- `background`(任意): グループの背景画像への Vault 相対パス。
- `backgroundStyle`(任意): 背景のレンダリング方法。
  - `"cover"`: 必要なら切り抜いてグループを満たす(デフォルト風の動作)
  - `"ratio"`: アスペクト比を保ちグループ内にフィット
  - `"repeat"`: 画像をタイル
- グループは自動レイアウトに影響しない: 純粋なビジュアルコンテナ。

---

### リンクノード

Web URL を埋め込みプレビューカードとしてレンダリング。

```json
{
  "id": "link-karpathy-2233",
  "type": "link",
  "url": "https://github.com/karpathy",
  "x": 200,
  "y": -300,
  "width": 400,
  "height": 120
}
```

- `url`: 有効な `https://` URL。
- Obsidian は Open Graph プレビュー(タイトル、説明、サムネイル)を取得。

---

## エッジ

ノード間の接続。ムードボードでは通常空。

```json
{
  "id": "e-hub-cidx",
  "fromNode": "hub",
  "fromSide": "right",
  "fromEnd": "none",
  "toNode": "c-idx",
  "toSide": "left",
  "toEnd": "arrow",
  "label": "概念",
  "color": "5"
}
```

**必須フィールド**: `id`, `fromNode`, `toNode`。それ以外は任意。

- `fromNode` / `toNode`: ソースとターゲットノードの ID。
- `fromSide` / `toSide`(任意): `"top"` `"bottom"` `"left"` `"right"`。省略時、Obsidian がノード相対位置から最適な辺を自動計算。
- `fromEnd`(任意): ソース側の端キャップ。デフォルト `"none"`。値: `"none"` | `"arrow"`。
- `toEnd`(任意): ターゲット側の端キャップ。**デフォルト `"arrow"`**: `fromEnd` と非対称。値: `"none"` | `"arrow"`。
- `label`(任意): エッジ上に表示されるテキスト。日本語可。
- `color`(任意): ノードと同じカラーパレット(`"1"`〜`"6"` または hex)。

ほとんどのエッジは有向関係を表すため、非対称デフォルト(`fromEnd: "none"`、`toEnd: "arrow"`)で何も明示せずソース → ターゲットの単方向矢印が生成される。

---

## 色リファレンス

| コード | 色 | Hex(目安) | ユースケース |
|------|-------|-------------|----------|
| `"1"` | 赤 / トマト | #e03e3e | 警告、アーカイブ |
| `"2"` | オレンジ | #d09035 | アクティブな作業 |
| `"3"` | 黄 / ゴールド | #d0a023 | 進行中、メモ |
| `"4"` | 緑 / ティール | #448361 | コンテンツ、ソース |
| `"5"` | 青 / シアン | #3ea7d3 | ナビゲーション、情報 |
| `"6"` | 紫 / バイオレット | #9063d2 | タイトル、アイデンティティ |

デフォルト(枠線色無し、透明ラベル)にしたいなら `color` 全体を省略。

---

## 画像サイズガイドライン

実際の画像寸法を PIL または `identify` から計算:

```bash
python3 -c "from PIL import Image; img=Image.open('path.png'); print(img.width, img.height)"
# または
identify -format '%w %h' path.png
```

| アスペクト比 | 条件 | キャンバス幅 | キャンバス高さ |
|-------------|-----------|-------------|--------------|
| 16:9(横長) | 比率 1.6〜2.0 | 420 | 236 |
| 2:1(超ワイド) | 比率 > 2.0 | 440 | 220 |
| 4:3 | 比率 1.2〜1.6 | 380 | 285 |
| 1:1(正方形) | 比率 0.9〜1.1 | 280 | 280 |
| 3:4 | 比率 0.6〜0.9 | 240 | 320 |
| 9:16(縦長) | 比率 < 0.6 | 200 | 356 |
| PDF | 任意 | 400 | 520 |
| 不明 | フォールバック | 320 | 240 |

---

## 自動配置の擬似コード

```
function place_node(canvas, zone_label, new_w, new_h):
  zone = label == zone_label のグループノードを検索
  padding = 20

  if zone が見つからない:
    max_y = max(n.y + n.height for n in canvas.nodes) + 60
    return (-400, max_y)

  # zone 内に視覚的にあるノード
  inside = [n for n in canvas.nodes
            if n.type != 'group'
            and zone.x <= n.x < zone.x + zone.width
            and zone.y <= n.y < zone.y + zone.height]

  if inside が空:
    return (zone.x + padding, zone.y + padding)

  # zone 内の最右点
  rightmost = max(n.x + n.width for n in inside)
  next_x = rightmost + 40

  if next_x + new_w > zone.x + zone.width - padding:
    # オーバーフロー → 新しい行
    bottom_of_row = max(n.y + n.height for n in inside)
    return (zone.x + padding, bottom_of_row + padding)

  # 同じ行
  row_y = min(n.y for n in inside)  # 既存行のトップに揃える
  return (next_x, row_y)
```

---

## 完全な例: 2 ゾーンキャンバス

```json
{
  "nodes": [
    {
      "id": "title-0001",
      "type": "text",
      "text": "# ブランドリファレンス\n\n**AI Marketing Hub** ビジュアルアセット",
      "x": -920, "y": -2440, "width": 560, "height": 180, "color": "6"
    },
    {
      "id": "zone-logos",
      "type": "group",
      "label": "ロゴとアイコン",
      "x": -920, "y": -2200, "width": 1800, "height": 320, "color": "6"
    },
    {
      "id": "img-logo-pro",
      "type": "file",
      "file": "_attachments/images/example.png",
      "x": -900, "y": -2180, "width": 420, "height": 236
    },
    {
      "id": "img-icon-free",
      "type": "file",
      "file": "_attachments/images/example-icon.png",
      "x": -440, "y": -2180, "width": 280, "height": 280
    },
    {
      "id": "zone-covers",
      "type": "group",
      "label": "スキルカバー",
      "x": -920, "y": -1820, "width": 1800, "height": 340, "color": "3"
    },
    {
      "id": "img-seo",
      "type": "file",
      "file": "_attachments/images/example-cover.png",
      "x": -900, "y": -1800, "width": 420, "height": 236
    }
  ],
  "edges": []
}
```

---

## よくある間違い

- **不正なパス形式**: `_attachments/images/file.png` を使う。`/home/user/...` や `~/...` ではない
- **ID 衝突**: 新規生成前に必ず既存 ID を読む
- **負の y の混乱**: `y: -2400` は `y: -1000` の **上**(負が大きいほど上)
- **グループはクリップしない**: ノードをグループ「内」に置くのは単にグループのバウンディングボックス内に位置するだけ。JSON 上に親子関係は無い
- **テキストノードの高さ不足**: Obsidian はテキストをレンダリングするが高さが小さすぎるとクリップする可能性あり。height >= 内容行数 × 24 を使う。
