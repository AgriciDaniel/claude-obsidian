# ビジュアルカスタマイズ

足場時に適用。ファイルエクスプローラがフォルダタイプ別に色分けされ、カスタム callout スタイルが追加される。

---

## CSS スニペット

Vault 内の `.obsidian/snippets/vault-colors.css` に作成:

```css
:root {
  --wiki-1: #4fc1ff;
  --wiki-2: #c586c0;
  --wiki-3: #dcdcaa;
  --wiki-4: #ce9178;
  --wiki-5: #6a9955;
  --wiki-6: #d16969;
  --wiki-7: #569cd6;
}

/* ファイルエクスプローラのフォルダ色 */
.nav-folder-title[data-path^="wiki/domains"]     { color: var(--wiki-1); }
.nav-folder-title[data-path^="wiki/entities"]    { color: var(--wiki-2); }
.nav-folder-title[data-path^="wiki/concepts"]    { color: var(--wiki-3); }
.nav-folder-title[data-path^="wiki/sources"]     { color: var(--wiki-4); }
.nav-folder-title[data-path^="wiki/questions"]   { color: var(--wiki-5); }
.nav-folder-title[data-path^="wiki/comparisons"] { color: var(--wiki-6); }
.nav-folder-title[data-path^="wiki/meta"]        { color: var(--wiki-7); }
.nav-folder-title[data-path=".raw"]              { color: #808080; opacity: 0.6; }

/* カスタム callout */
.callout[data-callout='contradiction'] {
  --callout-color: 209, 105, 105;
  --callout-icon: lucide-alert-triangle;
}
.callout[data-callout='gap'] {
  --callout-color: 220, 220, 170;
  --callout-icon: lucide-help-circle;
}
.callout[data-callout='key-insight'] {
  --callout-color: 79, 193, 255;
  --callout-icon: lucide-lightbulb;
}
.callout[data-callout='stale'] {
  --callout-color: 128, 128, 128;
  --callout-icon: lucide-clock;
}
```

---

## スニペットの有効化

ユーザーに伝える: 設定 → 外観 → CSS スニペット → フォルダを開く → ファイルを貼る → 更新アイコンをクリック → 有効化トグル。

---

## グラフビューのグループ

ユーザーをグラフビュー設定に誘導(グラフビュー内の設定アイコンをクリック):

| クエリ | 色 |
|-------|-------|
| `path:wiki/domains` | 青(`#4fc1ff`) |
| `path:wiki/entities` | 紫(`#c586c0`) |
| `path:wiki/concepts` | 黄(`#dcdcaa`) |
| `path:wiki/sources` | オレンジ(`#ce9178`) |
| `path:wiki/questions` | 緑(`#6a9955`) |
| `path:.raw` | グレー(薄く) |

---

## カスタム callout

この Vault は Obsidian の組み込みセット(`note`, `tip`, `warning`, `info`, `todo`, `success`, `question`, `failure`, `danger`, `bug`, `example`, `quote`)に加えて **4 つのカスタム callout タイプ** を定義する。`vault-colors.css` を有効化したときのみ正しくレンダリングされる。スニペットが無いとデフォルト callout スタイルにフォールバック(読めるが装飾なし)。

| カスタム callout | 色 | アイコン | 用途 |
|---|---|---|---|
| `contradiction` | 赤茶(rgb 209,105,105) | `lucide-alert-triangle` | 新ソースが既存主張と矛盾 |
| `gap` | ベージュ(rgb 220,220,170) | `lucide-help-circle` | トピックにソースが無い |
| `key-insight` | 明るい青(rgb 79,193,255) | `lucide-lightbulb` | 強調すべき重要な気づき |
| `stale` | グレー(rgb 128,128,128) | `lucide-clock` | 主張が古い、ソースが閾値より古い |

### 使用例

wiki ページで重要な状態をフラグ:

```markdown
> [!contradiction] タイトル
> [[Page A]] は X を主張。[[Page B]] は Y と言う。解決が必要。

> [!gap] タイトル
> このトピックにはまだソースが無い。1 つ見つけることを検討。

> [!key-insight] タイトル
> このセクションで最も重要な気づき。

> [!stale] タイトル
> この主張は古い可能性。ソースは 2022 年。
```

### なぜカスタム callout か(組み込みではなく)

4 つのカスタムタイプは Obsidian のデフォルトセットにきれいに収まらない wiki 固有の概念にマッピングする:

- `contradiction` は `warning` より具体的: 一般的警告ではなく、2 つの wiki ページ間の **解決可能な衝突** を示す。
- `gap` は `question` より具体的: アクション可能な改善である **ソースの欠落** を示す。
- `key-insight` は `tip` より具体的: セクションで **最重要** な気づきを少なくマーク。
- `stale` には組み込み相当が無い: 主張の時間ベース減衰を示す。

カスタム callout を使いたくなければ組み込みに置き換える:
- `[!contradiction]` → `[!warning] 矛盾`
- `[!gap]` → `[!question] ギャップ`
- `[!key-insight]` → `[!tip] 重要な気づき`
- `[!stale]` → `[!warning] 古い`

---

## Minimal テーマ(推奨)

カラースキームは Minimal テーマで最も映える。設定 → 外観 → 管理 → 「Minimal」を検索でインストール。
