---
name: wiki-lint
description: >
  Obsidian ウィキ Vault の健全性チェック。孤立ページ、デッドリンク、古い主張、欠けた相互参照、
  frontmatter のギャップ、空セクションを発見。Dataview ダッシュボードを作成または更新し、
  キャンバスマップを生成。レポートと応答は日本語(プロジェクト CLAUDE.md の言語ポリシー参照)。
  トリガー(日本語): lint、健全性チェック、ウィキ掃除、ウィキ確認、ウィキメンテ、孤立を探す、
  ウィキ監査。Triggers (English): "lint", "health check", "clean up wiki", "check the wiki",
  "wiki maintenance", "find orphans", "wiki audit".
---

# wiki-lint: ウィキ健全性チェック

10〜15 件取り込みごと、もしくは週次で lint を実行。自動修正前に必ず確認を取る。lint レポートは `wiki/meta/lint-report-YYYY-MM-DD.md` に日本語で出力。

---

## チェック項目

順番に実行:

1. **孤立ページ**。被リンクが無い wiki ページ。存在するが何からも指されていない。
2. **デッドリンク**。存在しないページを参照する wikilink。
3. **古い主張**。新しいソースで矛盾または更新された古いページの主張。
4. **欠落ページ**。複数ページで言及されているが独自ページが無い概念やエンティティ。
5. **欠けた相互参照**。ページで言及されているがリンクが張られていないエンティティ。
6. **frontmatter のギャップ**。必須フィールド(type, status, created, updated, tags)が欠けているページ。
7. **空セクション**。中身が無い見出し。
8. **古い index エントリ**。改名・削除されたページを指す `wiki/index.md` の項目。
9. **アドレス検証**(DragonScale Mechanism 2)。`address:` frontmatter フィールドを持つすべてのページについて形式を検証。下の **アドレス検証** セクション参照。
10. **セマンティックタイリング**(DragonScale Mechanism 3、オプトイン)。スキャン対象タイプ全体(概念だけでなく)を埋め込みコサイン類似度で重複候補ページとしてフラグ。下の **セマンティックタイリング** セクション参照。

---

## lint レポート形式

`wiki/meta/lint-report-YYYY-MM-DD.md` に作成:

```markdown
---
type: meta
title: "Lint レポート YYYY-MM-DD"
aliases: ["Lint Report YYYY-MM-DD"]
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [meta, lint]
status: developing
---

# Lint レポート: YYYY-MM-DD

## サマリ
- スキャン対象ページ: N
- 検出された問題: N
- 自動修正済み: N
- 要レビュー: N

## 孤立ページ
- [[Page Name]]: 被リンク無し。提案: [[Related Page]] からリンクするか削除する。

## デッドリンク
- [[Missing Page]]: [[Source Page]] から参照されているが存在しない。提案: スタブを作成するかリンクを削除。

## 欠落ページ
- 「concept name」: [[Page A]], [[Page B]], [[Page C]] で言及。提案: 概念ページを作成。

## frontmatter のギャップ
- [[Page Name]]: 欠落フィールド: status, tags

## 古い主張
- [[Page Name]]: 主張「X」は新しいソース [[Newer Source]] と矛盾する可能性。

## 相互参照のギャップ
- [[Entity Name]] が [[Page A]] で言及されているが wikilink 無し。
```

---

## 命名規約

lint 中に強制:

| 要素 | 規約 | 例 |
|---------|-----------|---------|
| ファイル名 | スペース付きタイトルケース(英語) | `Machine Learning.md` |
| フォルダ | 小文字 + ハイフン | `wiki/data-models/` |
| タグ | 小文字、階層化 | `#domain/architecture` |
| Wikilink | ファイル名と完全一致 | `[[Machine Learning]]` |

ファイル名は Vault 全体で一意。wikilink がパス無しで動作するのはファイル名が一意のときのみ。

> 日本語ローカライズ版: ファイル名は **英語のまま** だが、各ページの frontmatter `aliases:` に日本語表示名を入れる。これにより `[[日本語名]]` でもリンクが解決する。lint で `aliases` の有無もチェック対象に。

---

## 文体チェック

lint 中、スタイルガイド違反のページにフラグ:

- 平叙の現在形でない(「X は Y を使う」の代わりに「X は基本的に Y する」)
- 主張に出典引用が無い
- 不確実性が `> [!gap]` でフラグされていない
- 矛盾が `> [!contradiction]` でフラグされていない
- 本文が英語のまま(日本語ローカライズ版では本文は日本語であるべき。`aliases:` 等のメタは英語可)

---

## Dataview ダッシュボード

`wiki/meta/dashboard.md` を以下のクエリで作成または更新:

````markdown
---
type: meta
title: "ダッシュボード"
aliases: ["Dashboard"]
updated: YYYY-MM-DD
---
# ウィキダッシュボード

## 最近の活動
```dataview
TABLE type, status, updated FROM "wiki" SORT updated DESC LIMIT 15
```

## シードページ(育成が必要)
```dataview
LIST FROM "wiki" WHERE status = "seed" SORT updated ASC
```

## ソース未紐付けのエンティティ
```dataview
LIST FROM "wiki/entities" WHERE !sources OR length(sources) = 0
```

## 未解決の質問
```dataview
LIST FROM "wiki/questions" WHERE answer_quality = "draft" SORT created DESC
```
````

---

## キャンバスマップ

`wiki/meta/overview.canvas` を作成または更新してビジュアルなドメインマップを提供:

```json
{
  "nodes": [
    {
      "id": "1",
      "type": "file",
      "file": "wiki/overview.md",
      "x": 0, "y": 0,
      "width": 300, "height": 140,
      "color": "1"
    }
  ],
  "edges": []
}
```

ドメインページごとに 1 ノード追加。重要な相互参照を持つドメイン同士を接続。色は CSS スキームに対応: 1=青、2=紫、3=黄、4=オレンジ、5=緑、6=赤。

---

## アドレス検証(DragonScale Mechanism 2 MVP)

**オプトイン機能。** Vault が DragonScale を使っているときのみ実行。検出方法:

```bash
if [ -x ./scripts/allocate-address.sh ] && [ -f ./.vault-meta/address-counter.txt ]; then
  DRAGONSCALE_ADDRESSES=1
else
  DRAGONSCALE_ADDRESSES=0
fi
```

`DRAGONSCALE_ADDRESSES=0` の場合、本セクション全体をスキップ。`address:` フィールド欠落は情報レベルでもフラグしない。たまたま `address:` を持っているページは検証なしで通過(ユーザー管理メタとして扱う)。

`DRAGONSCALE_ADDRESSES=1` の場合、下のロールアウトベースラインとチェックを進める。

ロールアウトベースライン: **2026-04-23**(その日に DragonScale を採用した Vault における Phase 2 出荷日)。後から DragonScale を採用した Vault は、アドレス付きページの最初の `created:` 日付を自分のロールアウト日として上書きすべき。`.vault-meta/legacy-pages.txt` の先頭にコメント行で記録: `# rollout: YYYY-MM-DD`。

### 分類ルール(ページごと)

検証前にページを分類:

| 分類 | 基準 |
|---|---|
| **メタ / fold / 除外** | ファイルが `wiki/folds/` 配下、またはファイル名が `{_index.md, index.md, log.md, hot.md, overview.md, dashboard.md, dashboard.base, Wiki Map.md, getting-started.md}` のいずれか。アドレス不要。 |
| **ロールアウト後(アドレス必須)** | `type` がメタ/fold でない、AND frontmatter `created:` 日付が 2026-04-23 以降、AND ファイルパスがレガシーベースラインマニフェストに無い。 |
| **レガシー(バックフィル対象)** | `type` がメタ/fold でない、AND frontmatter `created:` 日付が 2026-04-23 より前、OR ファイルパスがレガシーベースラインマニフェストにある。バックフィルまでアドレス不要。 |

**レガシーベースラインマニフェスト**: 任意のファイル `.vault-meta/legacy-pages.txt`、1 行に 1 つの相対パス。`created:` 日付に関係なくここに列挙されたページはレガシー扱い。`created:` メタが間違っていたり欠けているページに祖父権を与えるのに使う。

### 検証チェック(順番に実行)

1. **形式チェック**: `address:` 設定済みのページは以下のいずれかに一致しなければならない:
   - `^c-[0-9]{6}$` — ロールアウト後の作成アドレス。
   - `^l-[0-9]{6}$` — レガシーバックフィルアドレス。
   - `wiki/folds/` 配下のページは `address` ではなく `fold_id` を使用。`c-`/`l-` の正規表現は適用しない。

2. **一意性チェック**: 同じアドレス値を持つページが 2 つ以上あってはならない。両パスを報告。

3. **カウンタ整合性**: `./scripts/allocate-address.sh --peek` が次のカウンタ値を返す。観測された各 `c-NNNNNN` は `NNNNNN < peek_value` を満たさねばならない。違反 = カウンタドリフト。

4. **ロールアウト後の強制**: 「ロールアウト後(アドレス必須)」に分類されたページで `address:` フィールドを **欠いた** ものは情報レベルではなく lint **エラー**。新ページがアドレス割当をスキップする静かな後退を防ぐ。

5. **レガシー識別**: 「レガシー」分類でアドレス無しのページは情報レベル。lint レポートでは「バックフィル待ち」セクションに件数とともに列挙。

6. **address-map 整合性**(`.raw/.manifest.json`): `address_map` の各ページパスは存在し、その frontmatter `address` がマッピングと一致しなければならない。不一致はエラー(改名がマップ更新を漏らした、または手動編集が分岐した可能性)。

### lint 姿勢サマリ

- アドレス形式が不正なページ: **エラー**。
- アドレスが衝突しているページ: **エラー**。
- **ロールアウト後** 分類でアドレス無しのページ: **エラー**。
- **レガシー** 分類でアドレス無しのページ: **情報**(想定通り)。
- メタ・fold ページにアドレス無し: **無視**(該当しない)。
- カウンタドリフト(観測カウンタ >= peek): **エラー**。
- address-map 不一致: **エラー**。

lint は観察のみ。lint 中に欠落アドレスを **自動割当しない**。割当は `wiki-ingest` の責務のみ。

### lint レポート出力セクション

```markdown
## アドレス検証

- カウンタ状態: `$(./scripts/allocate-address.sh --peek)`
- 観測された最大の c- アドレス: c-XXXXXX
- ロールアウト後ページ確認済み: N(X 件合格、Y 件エラー)
- バックフィル待ちレガシーページ: M

### エラー
- [[Page Name]]: 不正なアドレス形式 `{value}`。期待値 `c-NNNNNN` または `l-NNNNNN`。
- [[Page A]] と [[Page B]] がアドレス `c-000042` で衝突。
- [[Post-Rollout Page]]: アドレス欠落。ページ作成 2026-04-25(ロールアウト後)、アドレス必須。wiki-ingest を再実行するか、手動で `./scripts/allocate-address.sh` を実行して frontmatter に追加。
- [[Page Name]] のアドレス `c-000100` だがカウンタ peek は `50`。カウンタドリフト。`./scripts/allocate-address.sh --rebuild` を実行。
- `.raw/.manifest.json` は `wiki/foo.md` -> `c-000010` をマップしているが、ページ frontmatter は `c-000012`。不一致を解決。

### バックフィル待ち(情報)
- M 件のレガシーページにアドレス無し。`.vault-meta/legacy-pages.txt` の正規レガシーセット、または `created:` < 2026-04-23 でフィルタ。
```

---

## セマンティックタイリング(DragonScale Mechanism 3 MVP、オプトイン)

**オプトイン機能。** セマンティックタイリングは埋め込みコサイン類似度を使って重複候補 *ページ*(概念ページだけではない、下記スコープ参照)をフラグする。デフォルトはローカル ollama のみ。リモートエンドポイントは明示的なオーバーライドフラグが必要。

### 検出と委譲

```bash
if [ -x ./scripts/tiling-check.py ] && command -v python3 >/dev/null 2>&1; then
  ./scripts/tiling-check.py --peek > /tmp/tiling-peek.json 2>/dev/null
  PEEK_EXIT=$?
  case $PEEK_EXIT in
    0)  TILING_READY=1 ;;                                  # 準備完了
    2)  TILING_READY=0 ; echo "tiling ERROR: usage error (exit 2); /tmp/tiling-peek.json を確認" ;;
    3)  TILING_READY=0 ; echo "tiling ERROR: cache corrupt (exit 3); .vault-meta/tiling-cache.json を確認" ;;
    4)  TILING_READY=0 ; echo "tiling ERROR: vault がスケールハードフェイル (exit 4); バッチ処理が必要" ;;
    10) TILING_READY=0 ; echo "tiling skipped: ollama 到達不能 (exit 10)" ;;
    11) TILING_READY=0 ; echo "tiling skipped: 'ollama pull nomic-embed-text' を実行 (exit 11)" ;;
    *)  TILING_READY=0 ; echo "tiling ERROR: tiling-check.py --peek から想定外の exit code $PEEK_EXIT" ;;
  esac
else
  TILING_READY=0
  echo "tiling skipped: scripts/tiling-check.py または python3 が利用不可"
fi
```

ステータスが曖昧なときは `/tmp/tiling-peek.json`(構造化診断: スクリプトパス、python interpreter、ollama URL、cache 状態、閾値状態)を確認する。未知の exit を黙って「unknown status」にまとめない。

`TILING_READY=1` のとき:

```bash
./scripts/tiling-check.py --report wiki/meta/tiling-report-YYYY-MM-DD.md
REPORT_EXIT=$?
case $REPORT_EXIT in
  0)  echo "tiling レポート出力済み" ;;
  2)  echo "tiling ERROR: --report 中の usage error" ;;
  3)  echo "tiling ERROR: --report 中の cache corrupt" ;;
  4)  echo "tiling ERROR: --report 中の scale hard-fail" ;;
  10) echo "tiling ERROR: --peek と --report の間で ollama が到達不能になった" ;;
  11) echo "tiling ERROR: --peek と --report の間でモデルが利用不可になった" ;;
  *)  echo "tiling ERROR: tiling-check.py --report から想定外の exit code $REPORT_EXIT" ;;
esac
```

### スコープ(ヘルパーがスキャンする対象)

- 含む: `wiki/` 配下のすべての `.md`、ただし以下の除外セットを除く。スコープは「タイル化候補ページ」、`type: concept` だけではない。
- 除外(パス): `wiki/folds/` または `wiki/meta/` 配下のすべて。
- 除外(ファイル名): `_index.md`, `index.md`, `log.md`, `hot.md`, `overview.md`, `dashboard.md`, `Wiki Map.md`, `getting-started.md`。
- 除外(frontmatter): `type: meta` または `type: fold`。
- 除外(セキュリティ): シンボリックリンク。シンボリックリンクであるか、解決後パスが Vault ルート外に逃げるページファイルはスキップ。

`wiki/meta/` 配下に実際の概念を置くと、内容に関わらずパスで除外される。概念は正規フォルダに置く。

### ヘルパーの動作

- 含まれた各ページに対し ollama の `nomic-embed-text` モデルでデフォルトで 1 つの埋め込みを計算。
- 埋め込みを `.vault-meta/tiling-cache.json` にキャッシュ。キーは `sha256(model + body)` でモデルドリフトを自動無効化。frontmatter はハッシュにも埋め込み入力にも含まれない — 純粋な frontmatter 編集(タグ変更、status 変更)は再計算をトリガーしない。
- 孤立は GC: キャッシュされたページパスがディスクに無くなると保存時にエントリを削除。
- 並行安全: cache I/O 周辺で `.vault-meta/.tiling.lock` を排他 flock。書き込みアトミシティのため PID ごとの一時ファイル。

### セキュリティ姿勢

- デフォルトは `http://127.0.0.1:11434`。ページ本文は埋め込み入力として POST されるため、`OLLAMA_URL` 環境変数オーバーライドは `--allow-remote-ollama` 付きでのみ受け付ける。
- シンボリックリンクと Vault ルート脱出は拒否。

### デフォルトバンド(保守的シード、未キャリブレーション)

| バンド | 類似度 | レポートセクション |
|---|---|---|
| エラー | `>= 0.90` | **エラー** — 強い近似重複、ほぼ同じ概念 |
| レビュー | `0.80 - 0.90` | **レビュー** — タイル重複の可能性。人間判断必要 |
| 合格 | `< 0.80` | 出力しない |

**これらは保守的シード値で、文献に基づく補間ではない。** 公開された参照点: Sentence Transformers の `community_detection` はデフォルト 0.75。Quora 重複キャリブレーションは目的により 0.7715-0.8352 の範囲。0.80 のレビュー下限は引用された Quora 最適解の少なくとも 1 つより既に厳しいため、それらのベースラインに対して **偽陰性** を予期する。感度を上げたければキャリブレーション中にレビュー下限を下げる。

### キャリブレーション手順(手動、Vault ごとに 1 回)

1. デフォルトでヘルパーを実行。**レビュー** バンドのペアをキャプチャ。
2. `.vault-meta/tiling-thresholds.json` の `bands.review` を一時的に `0.70` に下げて広いサンプルを表示。0.70-0.95 にまたがる 50 ペア以上を目指す。
3. 各ペアにラベル付け: `duplicate`, `similar`, `distinct`。
4. バンドを選ぶ: (a) `error` バンドが真の重複 95% 以上を含む、(b) `review` バンドが `similar` ペアを捕捉しつつ `distinct` でレポートを溢れさせない。
5. `.vault-meta/tiling-thresholds.json` を編集: 新 `bands.error` と `bands.review` を設定、`calibrated: true` に、`calibration_pairs_labeled` をラベル数に。
6. lint 再実行。レポートフッターは `calibrated: true` を表示。

### スケール

- コールドキャッシュコストは ollama への O(N) POST。ウォームキャッシュコストは純粋 Python での O(N^2) コサイン。
- ヘルパーは 500 ページ超で警告、5000 ページ超でハードフェイル(exit 4)。いずれかの限界を超える前に実装を見直す(バッチ化、ベクトル化コサイン、外部ツール)。

### lint レポート埋め込み

```markdown
## セマンティックタイリング
完全なペア一覧は [[tiling-report-YYYY-MM-DD]] 参照。
- エラー(>=0.90): N ペア
- レビュー(0.80-0.90): M ペア
- キャリブレーション済み: true|false
```

### 不変条件

- 読み取り専用。`tiling-check.py` は wiki ページを書き換えない。
- 自動マージなし。重複は列挙されるだけで解決はされない。
- キャッシュはインクリメンタルかつモデル単位。変更されていないページは再埋め込みされない。
- exit code: `0` 正常、`2` usage error、`3` cache corrupt、`4` scale hard-fail、`10` ollama 到達不能、`11` モデル不在。すべてを表面化する。単一の "unknown" バケットにまとめない。

---

## 自動修正前

必ず先に lint レポートを表示。質問: 「自動修正しますか?それとも 1 つずつレビューしますか?」

自動修正可能:
- プレースホルダ値で frontmatter フィールドを補完
- 欠落エンティティのスタブページを作成
- リンクされていない言及に wikilink を追加

レビュー必要:
- 孤立ページの削除(意図的に分離されている可能性)
- 矛盾の解決(人間判断必要)
- 重複ページのマージ
