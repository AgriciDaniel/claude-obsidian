# claude-obsidian — Claude + Obsidian ウィキ Vault(日本語ローカライズ版)

このフォルダは Claude Code プラグインであり、同時に Obsidian の Vault でもあります。

**プラグイン名:** `claude-obsidian`
**スキル:** `/wiki`, `/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/save`, `/autoresearch`, `/canvas`, `/wiki-fold`
**Vault パス:** このディレクトリ(Obsidian で直接開けます)

---

## 🇯🇵 言語ポリシー(最優先・全スキル共通)

**この Vault に関わるすべての出力は日本語で行います。** 以下のルールを厳守してください。

### 日本語化する対象

- ユーザーへのチャット応答、要約、確認質問、説明文
- ウィキページの本文、見出し、箇条書き、表、callout の中身
- `log.md` のエントリ本文(セクション見出しも日本語)
- `hot.md` の要約セクション
- `index.md` の説明テキスト
- frontmatter の **値**(`title`, `description`, `summary`, `tags` のうち日本語化が自然なもの)
- callout のタイトル文字列(例: `> [!contradiction] [[既存ページ]] と矛盾`)
- コミットメッセージ本文(prefix `wiki:` `docs:` などは英語のまま)

### 英語のまま維持する対象(動作互換のため)

- ファイル名・スラッグ・パス(例: `wiki/concepts/Hot Cache.md`)
- wikilink のターゲット文字列(例: `[[Hot Cache]]`)
- frontmatter の **キー名**(`type`, `title`, `created`, `updated`, `tags`, `address`, `aliases`, `related`, `sources`, `status`)
- frontmatter の `type:` 値(`concept`, `entity`, `source`, `question`, `meta` 等の列挙値)。Obsidian Bases / DataView クエリの互換のため
- frontmatter の `status:` 値(`developing`, `evergreen`, `stale` 等)
- frontmatter の `tags:` の英数字タグ(例: `dragonscale`, `meta`)。日本語タグも併記して構いません
- DragonScale のアドレス(`c-000042` の `c-` プレフィックス)、`fold_id`、`address` 値
- スキル名・コマンド名・プラグイン名・スクリプト名・関数名
- コードブロック内のコード、bash コマンド、JSON、YAML キー
- 外部システム名(GitHub, Obsidian, Anthropic 等の固有名詞)

### 日英併記すべき対象

- ウィキページ作成時の `aliases:` に **英語のファイル名と日本語の表示名を両方** 入れる:

  ```yaml
  ---
  type: concept
  title: "ホットキャッシュ"
  aliases: ["Hot Cache", "ホットキャッシュ", "hot cache"]
  ---
  ```

  これによりファイル名は英語のまま、Obsidian の表示・グラフ・リンク補完では日本語名が使え、`[[ホットキャッシュ]]` でも `[[Hot Cache]]` でも解決できます。

- スキルやコマンドのトリガー語は **日英バイリンガル**(skill description に両方記述)

### 例: log エントリの日本語化フォーマット

```markdown
## [YYYY-MM-DD] ingest | ソースタイトル
- ソース: `.raw/articles/filename.md`
- 要約ページ: [[Source Title]]
- 作成: [[Page 1]], [[Page 2]]
- 更新: [[Page 3]], [[Page 4]]
- 主な発見: 新たに分かったことを 1 文で。
```

### 例: hot.md の日本語化フォーマット

```markdown
---
type: meta
title: "ホットキャッシュ"
aliases: ["Hot Cache"]
updated: YYYY-MM-DDTHH:MM:SS
---

# 直近のコンテキスト

## 最終更新
YYYY-MM-DD。何が起きたか。

## 重要な最近の事実
- 一番大事な点
- 二番目

## 最近の変更
- 作成: [[New Page 1]], [[New Page 2]]
- 更新: [[Existing Page]](X についてのセクションを追記)
- フラグ: [[Page A]] と [[Page B]] の Y についての矛盾を検出

## 進行中のスレッド
- 現在のリサーチトピック
- 未解決の問い
```

### 既存ページの扱い

旧バージョンで英語のまま作成された wiki ページは、編集や再 ingest のタイミングで日本語化していきます。当初の翻訳パスでは可能な範囲で本文を日本語に書き換え、`aliases` を補います。新規作成は最初から日本語で書きます。

### 違反したら

英語で応答してしまった場合は、ユーザーに謝らず、**そのまま日本語に切り替えて続行** してください。トリガーは内容で判断し、ユーザーの入力言語に依存させない(英語でリクエストされても日本語で返す)。例外: ユーザーが明示的に `respond in english` と指示した場合のみ英語で応答。

---

## この Vault の用途

LLM Wiki パターンを実演するための、永続的に成長するナレッジベースです。任意のソースを投入し、任意の質問を投げると、セッションを重ねるほど Vault が豊かになります。

## Vault 構造

```
.raw/           ソース文書(不変。Claude は読むだけで書き換えない)
wiki/           Claude が生成・維持するナレッジベース
_templates/     Obsidian Templater 用テンプレート
_attachments/   wiki ページが参照する画像・PDF
```

## 使い方

`.raw/` にソースファイルを置いてから「[ファイル名] を ingest して」と指示してください(英語の `ingest [filename]` も同じく動作します)。

質問は自由形式で OK。Claude はまず索引を読み、関連ページに辿ってから答えます。

`/wiki` で新規 Vault のスキャフォールドや状態確認を行います。

ingest を 10〜15 件こなしたら「ウィキを lint して」(または `lint the wiki`)で健全性チェックを走らせてください。

## クロスプロジェクト参照

別の Claude Code プロジェクトからこの Vault を参照するには、向こうの CLAUDE.md に以下を追記:

```markdown
## ウィキナレッジベース
パス: /path/to/this/vault

このプロジェクトに無いコンテキストが必要なとき:
1. まず wiki/hot.md(直近のコンテキスト約 500 語)を読む
2. 足りなければ wiki/index.md(全カタログ)を読む
3. ドメイン詳細が必要なら wiki/<domain>/_index.md を読む
4. その上で個別の wiki ページを読む

一般的なコーディング質問やこのプロジェクト内で完結する話題には wiki を読まない。
```

## プラグインのスキル

| スキル | トリガー(日英) |
|-------|---------|
| `/wiki` | セットアップ、足場、サブスキルへのルーティング |
| `ingest [source]` / `[ファイル名] を取り込んで` | 単発・バッチのソース取り込み |
| `query: [question]` / `wiki に聞く: [質問]` | wiki から回答を合成 |
| `lint the wiki` / `ウィキを lint して` | 健全性チェック |
| `/save` / 保存して | 現在の会話を構造化ノートとして保存 |
| `/autoresearch [topic]` / `[トピック] を自動リサーチ` | 自律リサーチループ |
| `/canvas` / `キャンバスに追加` | ビジュアルキャンバス操作 |
| `/wiki-fold` / `log を fold` | log の階層的圧縮(DragonScale) |

## MCP(任意)

MCP サーバーを設定すれば Claude が Vault ノートを直接読み書きできます。詳細は `skills/wiki/references/mcp-setup.md` を参照。
