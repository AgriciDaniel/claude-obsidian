---
name: wiki-fold
description: "wiki log エントリのメタページへのロールアップ。`wiki/log.md` から最後の 2^k 件を読み、子にリンクバックする構造的に冪等な fold ページを `wiki/folds/` に書く。抽出的要約(発明なし)。デフォルトでドライラン・stdout のみ、commit モードは Write を使い PostToolUse hook の自動コミットを受け入れる。出力本文は日本語(プロジェクト CLAUDE.md の言語ポリシー参照)。トリガー(日本語): log を fold、log を畳む、wiki-fold 実行、log ロールアップ、log エントリをまとめる。Triggers (English): fold the log, run a fold, run wiki-fold, log rollup, roll up log entries."
---

# wiki-fold: 抽出的 log ロールアップ

[[DragonScale Memory]] の Mechanism 1 の境界付きサブセットを実装: 生の `wiki/log.md` エントリに対するフラット fold。fold-of-folds(階層的レベルスタッキング)は **このスキルのスコープ外**(下の「スコープ境界」参照)。

fold は **加算的**: 子 log エントリと参照ページは決して変更・移動・削除されない。fold は **抽出的**: 出力のすべての outcome とテーマが特定の子 log エントリに辿れる必要がある。子エントリがサポートしない事実の発明や合成はしない。

> **言語ルール**: fold ページの本文・要約・テーブル列見出しは日本語。frontmatter キー、ファイル名、`fold_id` 値、wikilink ターゲット、コードは英語のまま。

---

## スコープ境界(明示)

このスキルが実装 **しない** こと:
- fold-of-folds / 階層的レベルスタッキング(DragonScale 仕様にあるが、将来のスキルに延期)。
- 自動トリガー(Phase 1 では fold は常に人間が起動)。
- セマンティックタイリング dedup(Mechanism 3、別スキル)。

このスキルが実装 **する** こと:
- 選んだバッチ指数 `k` での生 log.md エントリへのフラット fold。
- 決定論的 fold ID による構造的冪等性。
- カウントチェック付き抽出的要約。

frontmatter で level に言及するときは `batch_exponent: k`(`level: k` ではなく)を使う。本スキルは階層レベルを生成しないため。

---

## モード

| モード | 書き込みあり? | 起動 |
|---|---|---|
| **ドライラン(デフォルト)** | **Write ツール呼び出しなし。** Bash の `cat`/heredoc で fold 内容を stdout のみに出力。 | `log を fold、ドライラン k=3` |
| **commit** | Write/Edit ツールを使用。各 Write は repo の PostToolUse hook を発火させ wiki 変更を自動コミットする。これを受け入れる。先に完全な内容を組み立てて、その後書き込みを順次行う。 | `log を fold、commit k=3`(クリーンなドライラン後のみ) |

**なぜドライランは stdout のみか**: repo の `hooks/hooks.json` PostToolUse hook は `Write|Edit` で発火し `git add wiki/ .raw/` を実行する。`/tmp` への書き込みは /tmp をステージしないが、それでも hook を発火させ、**保留中の任意の wiki 変更** を generic メッセージでコミットしてしまう。ドライランは 0 残留が必須。Bash stdout は hook を発火させない。

---

## 決定論的 fold ID

すべての fold は入力から導出された ID を持つ:

```
fold-k{K}-from-{EARLIEST-DATE}-to-{LATEST-DATE}-n{COUNT}
```

例: `fold-k3-from-2026-04-10-to-2026-04-23-n8`。

commit モードでのファイル名は `wiki/folds/{FOLD-ID}.md`。ファイル名に作成日無し。タイトルにタイムスタンプ無し。

**重複検出(必須)**: 任意の出力を出す前に `wiki/folds/{FOLD-ID}.md` が既存か確認。既存なら「fold は既に wiki/folds/{FOLD-ID}.md にあります。上書きするには --force、または別の範囲を選んでください。」と報告して停止。これが no-op 冪等保証。バイト同一の内容は **保証されない**(LLM 出力は揺らぐ)が、ファイル名とスコープは固定。

---

## パラメータ

- `k`(デフォルト 4): バッチ指数。バッチサイズ = `2^k`。典型値: k=3(8)、k=4(16)、k=5(32)。
- `range`(任意): 明示的なエントリ範囲 `entries 1-16`。k より優先。
- `--force`: 同 ID の既存 fold を上書き。デフォルト無し。
- `--commit`: wiki/ に書き込む。なしならドライラン stdout のみ。

`2^k` 件未満の log エントリしか無ければ不足を報告して停止。部分バッチを黙って fold しない。

---

## 手順

### 1. log エントリを解析

```
grep -n "^## \[" wiki/log.md | head -{2^k}
```

各エントリについて記録: 行番号、日付、操作、タイトル、次の `## [` または section 末までの後続箇条書き行。

### 2. 子ページ識別子を抽出

各エントリの箇条書きから抽出:
- `Location: wiki/path/to/page.md`(主要ページ)/「場所:」も同義
- インラインの `[[Wikilinks]]`
- `Pages created:` と `Pages updated:` のリスト(日本語版では「作成:」「更新:」)

構造化された children リストを構築:
```yaml
children:
  - date: "2026-04-23"
    op: "save"
    title: "DragonScale Memory v0.2 — 敵対レビュー後"
    page: "[[DragonScale Memory]]"
  - ...
```

log エントリ 1 件につき 1 レコード。ページで dedupe しない: 2 つのエントリが両方 `[[DragonScale Memory]]` を指していたら両レコードを残し、日付とタイトルで区別。

### 3. 参照ページを読む(境界付き)

log エントリの箇条書きで完全に捕捉されていないページのみ読む。予算: 0〜10 ページ読み取り。ハード上限: 15。エントリの参照ページが欠落していたら `page_missing: true` を記録して進む。

### 4. カウントチェック付き抽出的要約

`references/fold-template.md` に従って fold 本文を書く。**ルール**:

- **抽出のみ。** 出力の各 outcome 箇条と theme 箇条は特定の子エントリを引用するか(例: `(2026-04-14 セッションより)`)、そのエントリの引用行を持たねばならない。子エントリにないイベント、カウント、解釈を導入しない。
- **log エントリが一次出典。** log エントリの箇条書きと参照メタページが事実(例: カウント)で食い違うとき、log エントリの箇条書きを優先し、不一致を「ソース不一致: log は X、メタは Y」とフラグ。
- **カウントチェック。** 「N 件の概念ページ」「M 件のリポジトリ更新」と書いたら、ソースエントリを grep して数値を検証。数値不一致はドライランブロッカー。
- **エントリを名指しせずまたがってマージしない。** 複数エントリにまたがるテーマは、寄与する各エントリをインラインで名指しすること。
- **不確実性は機能。** エントリが曖昧なら、解釈を 1 つに決めず「ソースで曖昧: [[Entry]]」と書く。

### 5. 出力前のセルフチェック

出力する前に検証:
- `children:` frontmatter の各子が Child Entries テーブルにちょうど 1 回現れる。
- テーブルの各エントリが `children:` frontmatter にある。
- Key Outcomes の各数値主張が子エントリに対し grep 検証可能。
- fold ID が決定論的で、ファイルが既存でない(または `--force` 設定)。

いずれかの検証に失敗したら中止して具体的失敗を報告。

### 6. 出力

**ドライラン**: Bash `cat <<'EOF' ... EOF` で stdout に出力。Write を使わない。fold ID と commit ステップで何をするかの 1 行サマリを表示。

**Commit**(ユーザーが「fold をコミット」と言った後のみ):
1. fold ページを `wiki/folds/{FOLD-ID}.md` に `Write`。(PostToolUse hook が自動コミット。)
2. `wiki/index.md` に `Edit` で `## Folds` セクション配下に fold リンクを追加(セクションが無ければ作成)。(hook 自動コミット。)
3. `wiki/log.md` に `Edit` で 1 エントリを先頭に追加:
   ```
   ## [YYYY-MM-DD] fold | バッチ指数 k{K} で N エントリをロールアップ
   - 場所: wiki/folds/{FOLD-ID}.md
   - 範囲: {EARLIEST-DATE} 〜 {LATEST-DATE}
   - 子エントリ数: N
   ```
   (hook 自動コミット。)

3 件の自動コミットが発生する。ユーザーは git log で 3 件の `wiki: auto-commit` エントリを見る。これは想定通り。hook の抑止を試みない。

---

## 出力スキーマ

正規の frontmatter と本文レイアウトは `references/fold-template.md` 参照。

---

## 不変条件

1. **構造的冪等性**: 同じ範囲 + 同じ k → 同じ fold ID → 重複検出が二重書きを防止。LLM 出力は実行ごとに揺らぐが *場所とスコープ* は固定。
2. **加算的**: 子は変更されない。
3. **境界付き読み取り**: fold あたり 0〜15 ページ読み取り。
4. **抽出的**: 発明された事実 0。カウントチェック強制。
5. **連鎖なし**: wiki-fold は wiki-lint, wiki-ingest, autoresearch, save を呼ばない。

---

## 禁止事項

- ドライラン中に Write/Edit を使わない。Bash stdout のみ。
- fold ファイル名やタイトルに現在の日付を含めない。子エントリの範囲を使う。
- ページタイトルで子を黙って dedupe しない。log エントリ 1 件につき 1 レコード。
- どのエントリが寄与するか名指しせずに「emergent themes」を書かない。
- バイト同一の冪等性を主張しない。実際の保証は構造的冪等性。
- PostToolUse 自動コミット hook を抑止・バイパスしない。
- `wiki/hot.md` を更新しない。所有権は save/ingest スキルにある。

---

## 取り消し

コミット済み fold の取り消し(3 コミット、この順で着地):
1. log.md の fold エントリを削除。
2. index.md のエントリを削除。
3. fold ページファイルを削除。

または 3 つの自動コミットを `git revert`。子ページはどちらの経路でも触られない。

---

## ドライランシーケンス例

ユーザー: 「log を fold、ドライラン k=3」

1. `wiki/log.md` の上位 8 エントリを解析。
2. 構造化された children リストを構築(8 レコード)。
3. 必要に応じて参照ページを 0〜10 件読む。
4. fold ID を生成: `fold-k3-from-2026-04-10-to-2026-04-23-n8`。
5. `wiki/folds/fold-k3-from-2026-04-10-to-2026-04-23-n8.md` が存在しないことを確認。
6. テンプレートに従って fold 本文を書く。
7. セルフチェックを実行(frontmatter/テーブル整合性、カウント検証)。
8. `cat <<'EOF' ... EOF` で stdout に出力。
9. 報告: 「ドライラン完了。fold ID: {FOLD-ID}。コミットには『fold をコミット』。」
