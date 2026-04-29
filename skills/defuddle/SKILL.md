---
name: defuddle
description: "ウィキ取り込み前に Web ページから装飾を取り除く。広告、ナビゲーション、ヘッダ、フッタ、定型文を除去し、読みやすいクリーンな markdown を残す。トークンを 40〜60% 節約。応答は日本語(プロジェクト CLAUDE.md の言語ポリシー参照)。トリガー(日本語): defuddle、このページをクリーン化、この URL を整形、取得してクリーン、取り込み前に Web 内容を整形、広告除去、装飾除去、URL 内容をクリーン化、URL から読みやすい markdown を取得。Triggers (English): defuddle, clean this page, strip this url, fetch and clean, clean web content before ingesting, strip ads, remove clutter, clean URL content, readable markdown from URL."
allowed-tools: Read Bash
---

# defuddle: Web ページクリーナー

defuddle は Web ページから意味のあるコンテンツを抽出し、それ以外(広告、Cookie バナー、ナビバー、関連記事、フッタ、ソーシャルシェアボタン)を捨てます。残るのは記事本文をクリーンな markdown 化したもの。

URL 取り込み前に必ず使用。任意ですが強く推奨。典型的な Web 記事でトークン使用量を 40〜60% 削減し、よりクリーンな wiki ページを生成します。

---

## インストール

```bash
npm install -g defuddle-cli
```

確認: `defuddle --version`

---

## 使い方

### URL を直接クリーン化
```bash
defuddle https://example.com/article
```
クリーンな markdown を stdout に出力。

### `.raw/` に保存
```bash
defuddle https://example.com/article > .raw/articles/article-slug-$(date +%Y-%m-%d).md
```

### 保存後に frontmatter ヘッダを追加
defuddle 実行後、ソース URL と取得日を先頭に付ける:
```bash
SLUG="article-slug-$(date +%Y-%m-%d)"
{ echo "---"; echo "source_url: https://example.com/article"; echo "fetched: $(date +%Y-%m-%d)"; echo "---"; echo ""; defuddle https://example.com/article; } > .raw/articles/$SLUG.md
```

### ローカル HTML ファイルをクリーン化
```bash
defuddle page.html
```

---

## 使用するべき場面

**defuddle を使う:**
- URL からニュース記事、ブログ投稿、ドキュメントページを取り込む
- ページに周辺コンテンツが多い(ほとんどの Web ページがそう)
- 長い記事でトークン予算内に収めたい

**defuddle をスキップ:**
- ソースが既にクリーンな markdown または PDF
- ページがダッシュボード、アプリ、構造化データ(defuddle は記事スタイルを想定)
- defuddle が未インストールで、生で処理できる短い記事

---

## フォールバック

defuddle が未インストールなら確認:

```bash
which defuddle 2>/dev/null || echo "not installed"
```

未インストールなら WebFetch を直接使用。コンテンツはクリーンさが落ちるが利用可能。

---

## /wiki-ingest との連携

`/wiki-ingest` スキルは URL が渡されたとき自動で defuddle をチェックします。URL 取り込み前に手動で defuddle を実行する必要はありません。取り込みスキルが利用可能なら呼び出します。

ページを手動でクリーン化して取り込み前に保存するには:
1. 上の保存コマンドを実行
2. その後: `ingest .raw/articles/[slug].md`
