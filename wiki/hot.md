---
type: meta
title: "ホットキャッシュ"
aliases: ["Hot Cache", "ホットキャッシュ"]
updated: 2026-04-29T00:00:00
tags:
  - meta
  - hot-cache
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
  - "[[Wiki Map]]"
  - "[[getting-started]]"
  - "[[DragonScale Memory]]"
---

# 直近のコンテキスト

ナビゲーション: [[index]] | [[log]] | [[overview]]

## 最終更新

2026-04-29: 日本語ローカライズパスを実施。CLAUDE.md に最優先の言語ポリシーを追加(本文・要約・log・チャット応答は日本語、ファイル名・skill 名・frontmatter キー・列挙値は英語維持)。トップレベル文書(README, AGENTS, GEMINI, WIKI, ATTRIBUTION, CHANGELOG)、全 SKILL.md(11 件)、references(7 件)、commands(4 件)、agents(2 件)、_templates(5 件)、hooks/README、docs/install-guide を日本語化済。トリガー語は日英バイリンガル化(英語の `ingest` も日本語の「取り込んで」も発火)。各ページに `aliases:` を追加して英語ファイル名と日本語表示名の両立を実現。残りの wiki/ コンテンツと docs/dragonscale-guide.md / v1.6.0 リリースノートは並列エージェントで翻訳中。

2026-04-24(深夜): v1.6.0 公開リリースノート出荷。`docs/releases/v1.6.0.md`(Karpathy スタイル、346 行)がリリースノート規約を確立。3 つのオリジナル SVG `wiki/meta/dragonscale-{mechanism-overview,6-test-flow,frontier-graph}.svg` がビジュアルを担当。Wikipedia のドラゴン曲線はテキストリンクのみで参照(バイナリ同梱なし)。R4 codex 検証は ACCEPT WITH FIXES、3 件の文言修正を適用。`gh release create v1.6.0 --notes-file docs/releases/v1.6.0.md` をユーザーが任意のタイミングで実行。コミット `85515bb`(docs)と SVG の wiki/meta/ 自動コミット。

2026-04-24(夜): DragonScale エンドツーエンド検証パス。チーム編成(M1 ドライラン・M1 コミット・M4 autoresearch を codex gpt-5.4、ollama pull・M2 割当・M3 フルタイリングを chair)で 6 テストメニューを実行。全 6 件グリーン。最初の本番 fold をコミット(`wiki/folds/fold-k3-from-2026-04-23-to-2026-04-24-n8.md`、115 行、子 8 件)。最初の本番タイリングレポート `wiki/meta/tiling-report-2026-04-24.md`(エラー 0、レビューバンドペア 15)。M2 カウンタは 2 から 3 へ、`c-000002` は予約済み未割当。M4 autoresearch が新規概念ページ 3 件(`Persistent Wiki Artifact`、`Source-First Synthesis`、`Query-Time Retrieval`)をファイリング、`[[How does the LLM Wiki pattern work?]]` を Karpathy gist + RAG + MemGPT + Obsidian docs を出典として拡張。v1.6.0 検証完了。

2026-04-24(夕方): v1.6.0 クローズアウトをチーム方式(chair 主導、サブエージェントは codex gpt-5.4)で実施。エクスプローラ 2 件(クローズアウトギャップ + ドキュメント表面)。境界付き書き込み 6 件(範囲非重複): `docs/dragonscale-guide.md`(新規 563 行)、`wiki/meta/2026-04-24-v1.6.0-release-session.md`(新規 346 行)、`wiki/meta/boundary-frontier-2026-04-24.md`(M4 初の本番アーティファクト、新規)、`docs/install-guide.md`(1.5.0 から 1.6.0 + M4 callout + フラット抽出修正)、`README.md`(括弧書き + ガイドリンク)、`wiki/hot.md`(ドリフト修正)。敵対検証 1 件は ACCEPT WITH FIXES、11 件の修正をその場で適用。docs コミット `eb1562f`。`make test` 緑(74+ アサーション)。v1.5.0 / v1.5.1 / v1.6.0 の git タグはまだ無し。ユーザーは gpt-5.5 を要求したが API がこの codex CLI で拒否、全工程で gpt-5.4 を使用。

2026-04-24(遅): Phase 4 出荷。Mechanism 4(境界優先 autoresearch)を `scripts/boundary-score.py` として実装、テストカバレッジ拡張。トピック無しの `/autoresearch` がフロンティア候補を提示(オプトイン、アジェンダ制御ラベル付き)。クロスファイルステータス更新。`plugin.json` + `marketplace.json` のバージョンを 1.6.0 に。git タグはローカル未作成(DragonScale 以前のタグ `v1.1` 〜 `v1.4.3` のみ存在)。

2026-04-24(午後): Phase 3.6 ハードニング、外科的修正 5 件(タイリング `--report` パス封じ込め、ロールアウトベースライン、AGENTS.md 整合性、wiki-ingest .raw 矛盾、install-guide バージョン)。v1.5.1。

2026-04-24(午前): Phase 3.5 ハードニングパス。クロスフェーズ監査で hold-ship 項目 10 件を解決。この時点で Mechanism 4 は NOT IMPLEMENTED とマーク(同日 Phase 4 で逆転)。`bin/setup-dragonscale.sh` + テスト + Makefile を追加、CHANGELOG 作成、バージョンを 1.5.0 に同期。

2026-04-23(3): Phase 3 完了。セマンティックタイリング lint をオプトインで出荷。`scripts/tiling-check.py`(flock ガード付きアトミックキャッシュ、localhost ロックの OLLAMA_URL デフォルト、シンボリックリンク拒否、モデルドリフト無効化、バンド付き閾値 error>=0.90、review>=0.80、保守的シード)。codex レビュー 4 ラウンド、10/10 accept。

2026-04-23(2): Phase 2 完了。`scripts/allocate-address.sh`(flock ガード付き、観測最大値からカウンタ復元)による決定論的ページアドレス MVP。新 frontmatter `address: c-NNNNNN`。`wiki-ingest` と `wiki-lint` をオプトインのアドレス割当・検証セクションで更新。codex 3 ラウンド、8/8 accept。

2026-04-23(1): Phase 0-1 完了。DragonScale Memory 仕様(`wiki/concepts/DragonScale Memory.md` v0.3)に Mechanism 1 用の `skills/wiki-fold/`(log ロールアップ、ドライラン検証済み)を追加。複数ラウンドの codex レビューを通過。

## プラグイン状態

- **バージョン**: 1.6.0(Phase 4 出荷済み。plugin.json + marketplace.json 同期済み。1.5.1 は Phase 3.6 ハードニングのポイントリリース)
- **インストール ID**: `claude-obsidian@claude-obsidian-marketplace`
- **言語**: 日本語ローカライズ版(2026-04-29 開始)
- **スキル**: 11(wiki, wiki-ingest, wiki-query, wiki-lint, wiki-fold, save, autoresearch, canvas, defuddle, obsidian-bases, obsidian-markdown)
- **スクリプト**: `scripts/allocate-address.sh`、`scripts/tiling-check.py`、`scripts/boundary-score.py`(すべてオプトイン、スキルが feature-detect)
- **セットアップ**: `bin/setup-vault.sh`(ベース Vault)、`bin/setup-dragonscale.sh`(オプトイン DragonScale)、`bin/setup-multi-agent.sh`(マルチエージェント bootstrap)
- **テスト**: `make test` が `tests/test_allocate_address.sh`、`tests/test_tiling_check.py`、`tests/test_boundary_score.py` を実行。コアテストに ollama 依存ゼロ。
- **Hook**: 4 件(SessionStart、PostCompact、PostToolUse [`wiki/`、`.raw/`、`.vault-meta/` をステージ]、Stop)

## DragonScale メカニズム

1. **Fold オペレータ**(Mechanism 1): `skills/wiki-fold/`、ドライラン検証 + 最初の本番 fold を `wiki/folds/fold-k3-from-2026-04-23-to-2026-04-24-n8.md` にコミット済み。
2. **決定論的アドレス**(Mechanism 2): 出荷・運用済み。Vault カウンタ 3。`c-000001` が DragonScale Memory.md に。`c-000002` は検証パスで予約済み未割当(仕様上ギャップは許容)。
3. **セマンティックタイリング lint**(Mechanism 3): 出荷・有効化済み。`nomic-embed-text` を pull 済み。最初のタイリングレポートは `wiki/meta/tiling-report-2026-04-24.md`(エラー 0、レビューバンドペア 15)。
4. **境界優先 autoresearch**(Mechanism 4): 出荷済み(Phase 4、オプトイン)。`scripts/boundary-score.py` + `tests/test_boundary_score.py`。トピック無しの `/autoresearch` が上位 5 フロンティアページを候補として表示、ユーザーは選択・上書き・辞退できる。仕様とスキルの両方で「アジェンダ制御」と明示。

## 本リリースサイクルの主な学び

1. クロスフェーズ監査は必須。個別フェーズレビューはフェーズ間ドリフトを見逃す。
2. オプトイン feature-detection(`[ -x script ] && [ -f state ]`)は採用者・非採用者の双方でデフォルトプラグイン動作を保つ。
3. PostToolUse hook の matcher は `Write|Edit` なので Bash 書き込みは発火しない。追跡対象状態を変更するスクリプトは Bash 専用にしないと副作用コミットが起きる。
4. シード Vault の自己整合性は重要。仕様で「ロールアウト後ページにアドレスが必要」と言うなら、その概念ページ自身もアドレスを持つべき。
5. Codex の敵対レビューラウンドは punch list が空になったら終わる。著者が「終わった気がする」では終わらない。

## スタイル設定

- em ダッシュ(U+2014)や `--` を句読点として使わない。。、:()を使う。複合語のハイフンは OK。
- 短く直接的な応答。末尾要約なし。
- 独立した操作は並列ツール呼び出し。
- **本文・チャット応答・log・要約は日本語**(2026-04-29 のローカライズパス以降)。

## 進行中のスレッド

- DragonScale Mechanism 4 は Phase 4 で `skills/autoresearch/` のオプトインなトピック選択モードとして出荷。4 つの DragonScale メカニズムすべて出荷済みで feature-gate 済み。
- v1.6.0 はまだ GitHub に push されていない(ローカルコミットのみ、git タグ未作成)。push とタグのタイミングはユーザー管理。
- CLAUDE.md には本セッション以前からの未コミット変更(「Release Blog Post」セクション)が 1 件存在。
- 日本語ローカライズパス進行中: 残り wiki 本文と docs/dragonscale-guide.md / v1.6.0 リリースノートを並列エージェントで翻訳中。

## リポジトリの場所

- 作業: `~/Desktop/claude-obsidian/`
- 公開: https://github.com/AgriciDaniel/claude-obsidian
