# REST API クイックリファレンス

MCP ツールが利用できないときに使う。Obsidian で Local REST API プラグインが稼働中(ポート 27124)である必要あり。

実行前にキーをセット:
```bash
API="https://127.0.0.1:27124"
KEY="your-api-key-here"
```

---

## ファイル読み取り

```bash
curl -sk \
  -H "Authorization: Bearer $KEY" \
  "$API/vault/wiki/index.md"
```

---

## ファイル作成または上書き

```bash
curl -sk -X PUT \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: text/markdown" \
  --data-binary @local-file.md \
  "$API/vault/wiki/entities/Name.md"
```

インライン内容で:
```bash
curl -sk -X PUT \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: text/markdown" \
  --data "# ページタイトル

ここに内容。" \
  "$API/vault/wiki/concepts/Name.md"
```

---

## ファイル末尾に追記

```bash
curl -sk -X POST \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: text/markdown" \
  --data "- 新ログエントリ" \
  "$API/vault/wiki/log.md"
```

---

## frontmatter フィールドの patch

```bash
curl -sk -X PATCH \
  -H "Authorization: Bearer $KEY" \
  -H "Operation: replace" \
  -H "Target-Type: frontmatter" \
  -H "Target: status" \
  -H "Content-Type: application/json" \
  --data '"mature"' \
  "$API/vault/wiki/concepts/Name.md"
```

---

## 見出し配下に内容を追記

```bash
curl -sk -X PATCH \
  -H "Authorization: Bearer $KEY" \
  -H "Operation: append" \
  -H "Target-Type: heading" \
  -H "Target: 関連" \
  -H "Content-Type: text/markdown" \
  --data "- [[New Page]]" \
  "$API/vault/wiki/entities/Name.md"
```

---

## 検索

シンプルなキーワード検索:
```bash
curl -sk -X POST \
  -H "Authorization: Bearer $KEY" \
  "$API/search/simple/?query=機械学習"
```

Dataview クエリ:
```bash
curl -sk -X POST \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/vnd.olrapi.dataview.dql+txt" \
  --data 'TABLE status FROM "wiki" WHERE status = "seed"' \
  "$API/search/"
```

---

## 全タグ一覧

```bash
curl -sk \
  -H "Authorization: Bearer $KEY" \
  "$API/tags/"
```

---

## フォルダ内のファイル一覧

```bash
curl -sk \
  -H "Authorization: Bearer $KEY" \
  "$API/vault/wiki/entities/"
```
