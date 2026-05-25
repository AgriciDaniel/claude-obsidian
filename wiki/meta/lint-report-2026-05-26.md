---
type: meta
title: "Lint Report 2026-05-26"
created: 2026-05-26
updated: 2026-05-26
tags:
  - meta
  - lint
status: developing
related:
  - "[[index]]"
  - "[[hot]]"
  - "[[DragonScale Memory]]"
---

# Lint Report: 2026-05-26

## Summary

- ページスキャン数: 46 (うち folds/ 1, meta/ 12)
- 検出された問題: 12 件 (本件)
- 自動修正: 0 (確認待ち)
- 要レビュー: 12

## 環境上の制約 (実行前提)

- `flock(1)` が macOS に存在しない → `./scripts/allocate-address.sh --peek` および `./scripts/tiling-check.py --peek` がロック取得失敗で停止します。アドレス検証はカウンタファイル直読で代替実行しました。タイリングは別途 Ollama 停止のため未実行。
- Ollama (`http://127.0.0.1:11434`) 応答なし → セマンティックタイリング (Mechanism 3) はスキップ。前回レポートは [[tiling-report-2026-04-24]]。

## Orphan Pages

なし。すべてのページに被リンクが存在します (meta/folds/index 系を除外して計測)。

## Dead Links

実害のあるリンク切れ:

- `[[How does the LLM Wiki pattern work?]]` が `wiki/hot.md` (L25) と `wiki/log.md` (L47, L53) に存在。実ファイル名は `wiki/questions/How does the LLM Wiki pattern work.md` (末尾 `?` なし)。Obsidian は末尾 `?` 付きを別ページ扱いします。修正: `?` を削るか、ファイル名側に `?` を付けてリネーム。`wiki/index.md` の L71 では `?` なしで正しくリンクされているので、後者は不要。
- `[[AI Marketing Hub Cover Images Canvas]]` が `wiki/overview.md` (L60) に存在。対応する canvas/.md ファイルが見当たりません。修正: 該当キャンバスを作成するか、リンクを削除。

意図的なプレースホルダ (修正不要):

- `[[Foo]]` × 2 (`DragonScale Memory.md`, `log.md`): 例示。
- `[[Three laws of motion]]` (`Persistent Wiki Artifact.md`): 例示。
- `[[wikilinks]]` (`cherry-picks.md`): 例示文中。
- `[[fold-template]]`, `[[wiki-fold]]` (`folds/fold-k3-...`): スキル/テンプレ参照、外部リソース。

Obsidian では解決済み (`.md` 以外を指す):

- `[[Wiki Map]]` (`getting-started.md`, `index.md`) → `wiki/Wiki Map.canvas` 存在。
- `[[claude-obsidian-presentation]]` (`overview.md` L59) → `wiki/canvases/claude-obsidian-presentation.canvas` 存在。
- `[[dashboard.base]]` (`meta/dashboard.md`) → `wiki/meta/dashboard.base` 存在。

## Frontmatter Gaps

- [[tiling-report-2026-04-24]]: フロントマター全欠落 (`type`, `status`, `created`, `updated`, `tags`)。Mechanism 3 ヘルパが書き出す出力にフロントマターが付与されていません。次回出力テンプレに `type: meta` ほかを足すのが構造的修正。今回のファイルは手動補填可能。
- 多くのページで `tags` のみ欠落と検出されましたが、これは YAML リスト形式 (`tags:` 改行→`  - foo`) を当方の簡易パーサが読めないことによる **誤検知** です。実ファイルではタグは付与されています ([[Hot Cache]] L12-15 等で確認)。要対応なし。
- `_index.md` 系、`hot.md`、`index.md`、`log.md`、`getting-started.md`、`dashboard.md` の `created` 欠落も Evergreen 系メタページの慣習で意図的、要対応なし。

## Address Validation (DragonScale Mechanism 2)

- DragonScale 有効: `scripts/allocate-address.sh` 実行可、`.vault-meta/address-counter.txt` 存在。
- カウンタ: `3` (`.vault-meta/address-counter.txt` 直読)。`--peek` は flock 不在で実行不可。
- 観測された最大 `c-` アドレス: `c-000001` (DragonScale Memory.md のみ)。
- 観測されたアドレス総数: 1。重複・不正フォーマットなし。
- レガシー (rollout 2026-04-23 より前) で未付与: 26 件、情報。

### Errors

- [[Persistent Wiki Artifact]]: `created: 2026-04-24` (rollout 後) で `address:` 欠落。Mechanism 4 自動研究で生成された 3 ページの一つ。
- [[Query-Time Retrieval]]: 同上。
- [[Source-First Synthesis]]: 同上。

修正: 3 ページに `./scripts/allocate-address.sh` でアドレスを払い出してフロントマターに追記、ただし `flock` 不在のためまずスクリプトを修正する必要があります (下記「ツール不具合」参照)。

### Pending backfill (informational)

- 26 ページがレガシー (rollout 2026-04-23 以前作成) で未バックフィル。仕様上必須ではありません。

## Semantic Tiling (DragonScale Mechanism 3)

- 今回未実行。理由: `OLLAMA` 応答なし (exit 10 相当)。
- 直近のレポート [[tiling-report-2026-04-24]] では Error バンド 0 件、Review バンド 15 件 (calibrated: false)。
- 当該レポート自体にフロントマターが無いため上記「Frontmatter Gaps」で別途指摘。

## Empty Sections

実質的に空 (見出し直下も子見出しも本文も無い):

- [[cherry-picks]]: `Tier 1 — Quick Wins`, `Tier 2`, `Tier 3`, `Tier 4` すべて見出しのみ。コンテンツ未記入。
- [[Hot Cache#Recent Context]]: 概念ページ側の例示セクションが空。実コンテンツは `wiki/hot.md` 側にあります。意図的かもしれませんが、空のままなら削除推奨。
- `_index.md` 系の "Add new concepts here as they are extracted" / "Add new sources here" / "Add new entities here" 見出し: テンプレ由来の案内文を見出し化したのが残存。見出し化を解除してプレーン段落に直すのが妥当。

子見出しが直後にあるため検出された (実質的には誤検知レベル、要対応なし):

- [[SVG Diagram Style Guide]] の `Color Palette`, `Layout Primitives`
- 各 `meta/...-session.md` の `What Was Done` / `What Was Built` / `Phase Timeline` 等

## ツール不具合 (環境依存、要修正)

- `scripts/allocate-address.sh` (L36) と `scripts/tiling-check.py` が `flock(1)` を使用。macOS には `flock` が無いため `--peek` 含めすべての呼び出しが失敗。代替案: `python3 fcntl.flock` ベースのラッパ、もしくは `mkdir` を使った疑似ロック。プラグインを macOS で運用するなら根本対応が必要。
- 当該 [[hot]] には `2026-04-24 (night)` に "M1 commit, M2 allocate, M3 full tiling" が green と記録されています。当時別環境 (Linux/coreutils) で実行されたか、Homebrew の `flock` がインストールされていた可能性。

## Naming Conventions

逸脱は検出されませんでした。ファイル名はタイトルケース、フォルダは小文字ダッシュ、タグは小文字階層、Wikilinks はファイル名一致 (`?` の差異を除く)。

## 推奨次アクション (優先順)

1. **Dead links** (実害): `wiki/hot.md` / `wiki/log.md` の `[[How does the LLM Wiki pattern work?]]` の末尾 `?` を削除。`wiki/overview.md` の `[[AI Marketing Hub Cover Images Canvas]]` を削除または作成。
2. **flock 依存解決**: `scripts/allocate-address.sh` を macOS 互換に書き換え。これが解けないと Mechanism 2/3 が現環境で動かないので、レポートに記録された "green" 状態を維持できません。
3. **Mechanism 4 由来 3 ページのアドレス付与**: 上記が解決後に `./scripts/allocate-address.sh` を 3 回実行してフロントマター追記。
4. **`tiling-report-2026-04-24.md` のフロントマター付与**: 次回ヘルパ出力テンプレを修正、当該既存ファイルも手動補填。
5. **`cherry-picks.md` の Tier 1-4 セクション**: 内容を埋めるか、骨組みなら "TBD" 等を明示。

## 自動修正可否

上記すべて、まず内容の判断が必要なため自動修正はしません。1, 4 は機械的修正可能なので明示的に指示があれば実行します。
