---
name: wiki-ingest
description: "Obsidian ウィキ Vault にソースを取り込む。ソースを読み、エンティティと概念を抽出し、wiki ページを作成または更新し、相互参照を張り、操作をログに残す。ファイル、URL、バッチモードに対応。すべてのページ本文・要約・log エントリは日本語で書く(プロジェクト CLAUDE.md の言語ポリシー参照)。トリガー(日本語): 取り込んで、このソースを処理、ウィキに追加、これを読んでファイル化、バッチ取り込み、これら全部を取り込んで、この URL を取り込んで。Triggers (English): ingest, process this source, add this to the wiki, read and file this, batch ingest, ingest all of these, ingest this url."
---

# wiki-ingest: ソース取り込み

ソースを読む。ウィキを書く。すべてに相互参照を張る。1 件のソースは通常 8〜15 ウィキページに影響を与える。

**言語ルール**: ページ本文、見出し、log エントリ、ユーザーへの応答はすべて日本語。frontmatter のキー名(`type`, `title`, `tags`, `address` 等)と `type:` の列挙値、ファイル名、wikilink ターゲット、コードは英語のまま維持。

**構文標準**: すべての Obsidian Markdown は適切な Obsidian Flavored Markdown で書く。wikilink は `[[Note Name]]`、callout は `> [!type] タイトル`、埋め込みは `![[file]]`、プロパティは YAML frontmatter。kepano/obsidian-skills プラグインがインストールされている場合は、その正規 obsidian-markdown スキルの構文を優先。なければこのスキル内のガイダンスに従う。

---

## デルタ追跡

ファイルを取り込む前に `.raw/.manifest.json` をチェックして、変更のないソースの再処理を避ける。

```bash
# マニフェストの存在確認
[ -f .raw/.manifest.json ] && echo "exists" || echo "no manifest yet"
```

**マニフェスト形式**(無ければ作成):
```json
{
  "sources": {
    ".raw/articles/article-slug-2026-04-08.md": {
      "hash": "abc123",
      "ingested_at": "2026-04-08",
      "pages_created": ["wiki/sources/article-slug.md", "wiki/entities/Person.md"],
      "pages_updated": ["wiki/index.md"]
    }
  }
}
```

**ファイル取り込み前:**
1. ハッシュ計算: `md5sum [file] | cut -d' ' -f1`(Linux なら `sha256sum`)。
2. `.manifest.json` 内のパスとハッシュが一致するか確認。
3. ハッシュが一致したらスキップ。報告: 「すでに取り込み済み(変更なし)。再取り込みするには `force` を指定してください。」
4. 不在またはハッシュが異なれば取り込みを進める。

**ファイル取り込み後:**
1. `{hash, ingested_at, pages_created, pages_updated}` を `.manifest.json` に記録。
2. 更新されたマニフェストを書き戻す。

ユーザーが「強制取り込み」「再取り込み」「force ingest」と言った場合はデルタチェックをスキップ。

---

## URL 取り込み

トリガー: ユーザーが `https://` で始まる URL を渡す。

手順:

1. WebFetch でページを **取得**。
2. **クリーン化**(任意): `defuddle` が利用可能なら(`which defuddle 2>/dev/null`)、`defuddle [url]` を実行して広告・ナビ・装飾を除去。通常 40〜60% のトークン節約。未インストールなら生の WebFetch 出力にフォールバック。
3. URL パスから **スラッグを導出**(末尾セグメントを小文字化、空白はハイフン化、クエリ文字列を除去)。
4. `.raw/articles/[slug]-[YYYY-MM-DD].md` に **保存**。frontmatter ヘッダ:
   ```markdown
   ---
   source_url: [url]
   fetched: [YYYY-MM-DD]
   ---
   ```
5. **単一ソース取り込み** の手順 2 から進める(ファイルは `.raw/` に既に置かれた状態)。

---

## 画像 / ビジョン取り込み

トリガー: ユーザーが画像ファイルパス(`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`, `.avif`)を渡す。

手順:

1. Read ツールで画像ファイルを **読む**。Claude は画像をネイティブに処理できる。
2. 画像内容を **記述**: テキストの抽出(OCR)、主要概念・エンティティ・図表・データの特定。
3. 記述を `.raw/images/[slug]-[YYYY-MM-DD].md` に **保存**:
   ```markdown
   ---
   source_type: image
   original_file: [元のパス]
   fetched: YYYY-MM-DD
   ---
   # 画像: [slug]

   [画像内容の完全記述、文字起こし、見えるエンティティなど]
   ```
4. 画像が Vault 内にまだ無ければ `_attachments/images/[slug].[ext]` にコピー。
5. 保存した記述ファイルに対して **単一ソース取り込み** を進める。

ユースケース: ホワイトボード写真、スクリーンショット、図表、インフォグラフィック、文書スキャン。

---

## 単一ソース取り込み

トリガー: ユーザーが `.raw/` にファイルを置く、もしくは内容を貼り付ける。

手順:

1. ソースを **完全に読む**。流し読みしない。
2. 主要な気づきをユーザーと **議論**。質問: 「何を強調しますか?どの粒度で?」 「とにかく取り込んで」と言われたらスキップ。
3. `wiki/sources/` に **要約ページを作成**。`references/frontmatter.md` のソース frontmatter スキーマを使用。下記の **アドレス割当** セクションに従ってアドレスを割り当てる。
4. 言及されたすべての人物・組織・製品・リポジトリのエンティティページを **作成または更新**。1 エンティティ 1 ページ。新規エンティティページにアドレスを割り当てる。
5. 重要なアイデア・フレームワークの概念ページを **作成または更新**。新規概念ページにアドレスを割り当てる。
6. 関連ドメインページとそれらの `_index.md` サブインデックスを **更新**。
7. 全体像が変わったら `wiki/overview.md` を **更新**。
8. `wiki/index.md` を **更新**。新ページのエントリを追加。
9. `wiki/hot.md` をこの取り込みのコンテキストで **更新**(日本語で)。
10. `wiki/log.md` の **TOP に追記**(新エントリを上に):
    ```markdown
    ## [YYYY-MM-DD] ingest | ソースタイトル
    - ソース: `.raw/articles/filename.md`
    - 要約ページ: [[Source Title]]
    - 作成: [[Page 1]], [[Page 2]]
    - 更新: [[Page 3]], [[Page 4]]
    - 主な発見: 新たに分かったことを 1 文で。
    ```
11. **矛盾チェック**。新情報が既存ページと衝突する場合、両ページに `> [!contradiction]` callout を追加。

---

## バッチ取り込み

トリガー: ユーザーが複数ファイルを置くか「これら全部を取り込んで」と言う。

手順:

1. 処理対象ファイルをリスト化。開始前にユーザーに確認。
2. 各ソースを単一取り込みフローで処理。手順 3 まで相互参照は後回し。
3. 全ソース処理後: 相互参照パスを実行。新ソース間の関連を探す。
4. index、ホットキャッシュ、log を最後に 1 回だけ更新(各ソースごとではなく)。
5. 報告: 「N 件処理しました。X ページ作成、Y ページ更新。主な接続: ...」

バッチ取り込みは対話性が低い。30 件以上は処理時間がかなり長い。10 件ごとにユーザーに進捗確認。

---

## コンテキストウィンドウ規律

トークン予算は重要。取り込み中は以下のルールに従う:

- まず `wiki/hot.md` を読む。関連コンテキストがあればフルページを再読しない。
- 既存ページを探す前に `wiki/index.md` を読む。
- 取り込み 1 件あたり既存ページは 3〜5 件のみ読む。10 件以上読むようなら範囲が広すぎる。
- 外科的編集は PATCH を使う。1 フィールド更新のためにファイル全体を再読しない。
- ウィキページは短く保つ。最大 100〜300 行。300 行を超えたら分割。
- 検索(`/search/simple/`)で特定の内容を見つけ、フルページの読み込みを避ける。

---

## 矛盾

> [!note] カスタム callout の依存
> 以下で使用する `[!contradiction]` callout は **カスタム callout** で、`/wiki` の足場が自動インストールする `.obsidian/snippets/vault-colors.css` で定義されています。スニペット有効時に赤茶色のスタイリングと alert-triangle アイコンでレンダリングされます。スニペットが無い場合 Obsidian はデフォルトの callout スタイリングにフォールバックするため、視覚的装飾が無くてもページは動作します。4 つのカスタム callout(`contradiction`, `gap`, `key-insight`, `stale`)については `[[skills/wiki/references/css-snippets.md]]` を参照。

新情報が既存 wiki ページと矛盾するとき:

既存ページに追加:
```markdown
> [!contradiction] [[New Source]] と矛盾
> [[Existing Page]] は X を主張。[[New Source]] は Y と言う。
> 解決が必要。日付・文脈・一次出典を確認。
```

新ソース要約に参照を追加:
```markdown
> [!contradiction] [[Existing Page]] と矛盾
> このソースは Y と言うが既存 wiki は X と言う。詳細は [[Existing Page]] 参照。
```

古い主張を黙って上書きしない。フラグを立ててユーザーに判断を委ねる。

---

## 禁止事項

- **`.raw/` 配下のソースファイルは不変。** ユーザーが置いた記事・トランスクリプト・画像を書き換えない。`.raw/.manifest.json` のデルタ追跡器とその `address_map`(DragonScale Mechanism 2)のみが `wiki-ingest` 自身が `.raw/` 配下で管理するファイルです。それ以外の `.raw/` 配下のファイルはすべて読み取り専用ソースコンテンツとして扱う。
- 重複ページを作らない。作成前に必ず index と検索を確認。
- log エントリをスキップしない。すべての取り込みを記録する。
- ホットキャッシュ更新をスキップしない。次回セッションを高速化するキー機構。
- 英語で書かない。すべての本文・要約・log エントリは日本語で書く。

---

## アドレス割当(DragonScale Mechanism 2 MVP)

**オプトイン機能**。DragonScale アドレス割当は `scripts/allocate-address.sh` が存在し、かつ `.vault-meta/` がある場合のみ実行。それ以外はこのセクション全体をスキップして通常通り取り込む。

**機能検出**(各取り込みの開始時に実行):

```bash
if [ -x ./scripts/allocate-address.sh ] && [ -d ./.vault-meta ]; then
  DRAGONSCALE_ADDRESSES=1
else
  DRAGONSCALE_ADDRESSES=0
fi
```

`DRAGONSCALE_ADDRESSES=0` の場合、ページは frontmatter の `address:` フィールド無しで作成され、`wiki-lint` の Address Validation セクションは完全にスキップされる(欠落アドレスはどの重大度でもフラグされない)。これで DragonScale を採用していない Vault のデフォルト動作が保たれる。

`DRAGONSCALE_ADDRESSES=1` の場合、本セクションの残りに進む。

---

**新規作成される非メタ wiki ページ** はすべて、frontmatter に安定したアドレスを取得する:

```yaml
address: c-000042
```

形式: `c-<6 桁カウンタ>`。`c-` プレフィックスは「creation-order counter(作成順カウンタ)」を意味。ゼロパディング。

ロールアウトベースライン: **2026-04-23**(Phase 2 出荷日)。`created:` が この日以降のページはロールアウト後で **必ず** アドレスを持つ(下記の除外を除く)。それ以前のページはレガシー免除で、意図的なバックフィルパスで `l-NNNNNN` アドレスが割り当てられるまでアドレス無し。

### 必須ツール: `scripts/allocate-address.sh`

アドレス割当はアトミック Bash ヘルパーに委譲。ヘルパーは `.vault-meta/.address.lock` の `flock` で読み取り・利用・インクリメントの競合を防ぎ、カウンタファイルが無ければ既存 frontmatter をスキャンして復元する。

```bash
ADDR=$(./scripts/allocate-address.sh)
# ADDR は "c-000042" などになる。カウンタはすでにインクリメント済み
```

**重要**: `.vault-meta/address-counter.txt` に対して Write や Edit ツールを **絶対に** 使わない。それは PostToolUse hook を発火させ、`git add wiki/ .raw/` を実行して関係ない wiki 変更を generic コミットメッセージで誤って commit する可能性がある。カウンタの変更は **必ずヘルパースクリプト経由(Bash ツール)** のみ。

### ヘルパーモード

- `./scripts/allocate-address.sh` — 次のアドレスをアトミックに予約して返す。
- `./scripts/allocate-address.sh --peek` — 予約せず次の値だけ表示(安全、読み取り専用)。
- `./scripts/allocate-address.sh --rebuild` — 既存 frontmatter で観測された最大の `c-NNNNNN` からカウンタを再計算。既存ページにアドレスがあれば 1 へのリセットは絶対にしない。カウンタファイルの破損が疑われる場合に実行。

### 割当手順(新ページごと)

1. 新規非メタページ作成前に `./scripts/allocate-address.sh` を呼んで出力をキャプチャ。
2. ページの frontmatter に `address: c-XXXXXX` を含める。
3. パス → アドレスのマッピングを `.raw/.manifest.json` のトップレベルキー `address_map` に記録(下記スキーマ参照)。

### `.raw/.manifest.json` の `address_map`

```json
{
  "sources": { ... },
  "address_map": {
    "wiki/concepts/Example.md": "c-000042",
    "wiki/entities/Another.md": "c-000043"
  }
}
```

同じソースの再取り込み(`--force` でもハッシュ変化でも)では、まず `address_map` を参照する。対象ページパスに既存アドレスがあれば **再利用**。新規割当はしない。

ページ改名時、スキルは `address_map` のキー(旧パス → 新パス)を更新しつつアドレス値を保持する。

### 除外(アドレスを割り当てない)

- メタファイル: `_index.md`, `index.md`, `log.md`, `hot.md`, `overview.md`, `dashboard.md`, `dashboard.base`, `Wiki Map.md`, `getting-started.md`。
- `wiki/folds/` 配下の fold ページ(独自の決定論的 `fold_id` を使用)。
- ロールアウト前のレガシーページ(`created:` < 2026-04-23)。レガシーページは意図的なバックフィル操作経由でのみ `l-NNNNNN` アドレスを取得。

### 冪等性ルール

- 書き直し中のページが現在の内容に既に `address:` フィールドを持つなら **再利用**。新規割当しない。
- ソースが再取り込みされ、`address_map` に対象パスのマッピングがあれば、そのマッピングを再利用。
- ソースが過去に取り込まれていて、対象ページにアドレスが無く、ページの `created:` がロールアウト後ならアドレスを割り当てて記録。Phase 2 ロールアウト前に古い取り込みで作られたページのケースをカバー。ロールアウトカットオフは引き続き適用(2026-04-23 より前のページはレガシーのまま)。

### 並行性ポリシー

- Phase 2 では **シングルライタのみ**。アドレスを割り当てる複数 Claude セッションやサブエージェントから並列取り込みを実行しない。ヘルパーの `flock` はカウンタ破損を防ぐが、ページ書き込み自体を直列化はしない。
- リサーチやレビューでディスパッチされるサブエージェント(codex、general-purpose)は割当器を **呼ばない**。この点で読み取り専用。
- マルチライタ対応は将来機能。

### バッチ取り込み

各ソースの単一取り込み中にアドレスを順次割り当てる。カウンタ値のブロックを事前予約しない。ヘルパーは安価(1 ロック、1 整数の読み書き)。
