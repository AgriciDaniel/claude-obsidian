---
type: meta
title: "操作ログ"
aliases: ["Operation Log", "操作ログ"]
updated: 2026-04-29
tags:
  - meta
  - log
status: evergreen
related:
  - "[[index]]"
  - "[[hot]]"
  - "[[overview]]"
  - "[[sources/_index]]"
---

# 操作ログ

ナビゲーション: [[index]] | [[hot]] | [[overview]]

追記専用。新エントリは TOP に。過去エントリは編集しない。

エントリ形式: `## [YYYY-MM-DD] operation | タイトル`

直近エントリの解析: `grep "^## \[" wiki/log.md | head -10`

> **言語**: 2026-04-29 以降の新エントリは日本語、それ以前のエントリは日本語ローカライズパスで日本語化済み。`operation` キー(`save`/`ingest`/`fold`/`session`/`setup`)は英語のまま維持。

---

## [2026-04-29] localize | 日本語ローカライズパス v1.6.0-ja
- 種別: ローカライズ + ドキュメント
- 場所(更新): `CLAUDE.md`(言語ポリシーセクションを最優先で追加)、トップレベル文書全件(`README.md`、`AGENTS.md`、`GEMINI.md`、`WIKI.md`、`CHANGELOG.md`、`ATTRIBUTION.md`)、外部エディタ規則(`.github/copilot-instructions.md`、`.windsurf/rules/claude-obsidian.md`)、プラグイン定義(`.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json`)、全 SKILL.md 11 件、全 references 7 件、全 commands 4 件、全 agents 2 件、全 _templates 5 件、`hooks/README.md`、`docs/install-guide.md`、wiki ルートメタ全件(`index.md`、`log.md`、`hot.md`、`overview.md`、`getting-started.md`)。残り(`docs/dragonscale-guide.md`、`docs/releases/v1.6.0.md`、wiki 本文ページ)は並列エージェントで日本語化。
- 範囲: チャット応答、ウィキ書き込み、log エントリ、要約はすべて日本語化。ファイル名、wikilink ターゲット、frontmatter キー、列挙値(`type:`/`status:`/`confidence:` の値)、コードブロック、スキル名、コマンド名、アドレス(`c-NNNNNN`)、`fold_id` は英語維持。各ページの frontmatter に `aliases:` を追加し、英語ファイル名と日本語表示名の両立を実現(`[[Hot Cache]]` でも `[[ホットキャッシュ]]` でも解決可能)。
- スキル description のトリガーは日英バイリンガル化: 「取り込んで」も `ingest` も発火。「wiki を lint して」も `lint the wiki` も発火。これによりユーザーが日本語でも英語でもスキルを起動できる。
- 主要な学び: (1) frontmatter のキー名と列挙値は英語のまま維持しないと Obsidian Bases / DataView クエリが壊れる。(2) `aliases:` を使えばファイル名は英語でも Obsidian 上の表示と検索は日本語名でできる。(3) hot.md は SessionStart hook で読まれるため、ローカライズの最重要ファイルの 1 つ。(4) スキル description にトリガー語を埋め込む方式なので、日本語トリガーを追加すれば即座に発火する。
- バージョン: `1.6.0-ja` を CHANGELOG に記録(plugin.json/marketplace.json は 1.6.0 のまま、description のみ日本語化)。
- 次の推奨: `make test` 実行で機能の非破壊を確認、その後コミット。

## [2026-04-24] save | v1.6.0 公開リリースノート(Teams、Karpathy スタイル)
- 種別: リリースドキュメント + ビジュアルアセット
- 場所(新規): `docs/releases/v1.6.0.md`(346 行、6 セクション、Karpathy スタイル散文)、`wiki/meta/dragonscale-mechanism-overview.svg`(共有 .vault-meta/ ゲート付き 4 メカニズム図)、`wiki/meta/dragonscale-6-test-flow.svg`(検証タイムライン)、`wiki/meta/dragonscale-frontier-graph.svg`(M4 候補 + 3 ファイリング済みページ)
- 場所(更新): `wiki/meta/2026-04-24-v1.6.0-release-session.md`(公開リリースノートへの相互参照を追加)
- 範囲: Teams アプローチ。R1(chair)が SVG Diagram Style Guide に従って 3 つのオリジナル SVG を作成。R2(codex worker)が Karpathy スタイルのリリース散文を起草。R3(chair)が SVG を縫合、Wikipedia 画像はテキストリンクのみに転換(許可によりバイナリ同梱なし)。R4(codex 検証者)が ACCEPT WITH FIXES、バージョン物語の文言修正 3 件。R5(chair)が修正適用とコミット。
- スタイル: 直接的・短く・シグナル密、散文より箇条書き、em ダッシュなし、マーケティング用語なし。検証者が em ダッシュゼロと禁止マーケティング用語(「revolutionary」「seamless」「world-class」「game-changing」「unlock」「transform」)ゼロを確認。
- 配信(3 経路すべてカバー): (1) `docs/releases/v1.6.0.md` 公開ファイル(コミット `85515bb`)、(2) `wiki/meta/2026-04-24-v1.6.0-release-session.md` 内部エンジニアリング記録(相互リンク)、(3) GitHub リリース本文(`gh release create v1.6.0` の準備が整ったらユーザーが docs/releases/v1.6.0.md から貼り付ける)。
- Wikipedia 画像: ホットリンクや同梱ではなく `https://en.wikipedia.org/wiki/Dragon_curve` へのテキストリンクとして参照。ライセンス上クリーン(CC-BY-SA 表記不要)で外部依存なし。3 つのオリジナル SVG が代わりにビジュアルを担当。
- 書き込み後の PII スキャン: `docs/releases/v1.6.0.md` と 3 SVG すべてクリーン。`/home/` パスなし、実メールなし、トークンなし。
- 次の推奨: 公開リリースカットの準備が整ったらユーザーが `gh release create v1.6.0 --notes-file docs/releases/v1.6.0.md` を実行。これで注釈付きタグも作成される。

## [2026-04-24] save | DragonScale エンドツーエンド検証パス(Teams、6 テスト)
- 種別: 検証 + 最初の本番 fold + 最初の本番 autoresearch
- 実行テスト(全件グリーン):
  - T0 ollama pull `nomic-embed-text`: 完了(274MB、ウォール 15 秒)
  - T1 codex 経由 M1 ドライラン k=3: DRY-RUN OK、子 8 件、em ダッシュなし
  - T2 M2 本番割当: カウンタ 2 から 3 へ、`c-000002` を取得(未割当予約。仕様上ギャップは許容)
  - T3 モデル存在下の M3 フルタイリング: 41 ページスキャン、21 件埋め込み、20 件正しくスキップ(meta/除外/埋め込みエラー)、>=0.9 でエラー 0、0.8〜0.9 レビューバンドで 15 ペア(トップ 0.8822 は Compounding Knowledge vs LLM Wiki Pattern、正当なセマンティック近隣)、レポートは `wiki/meta/tiling-report-2026-04-24.md`
  - T4 codex 経由 M1 コミット: 最初の本番 fold をコミット、`wiki/folds/fold-k3-from-2026-04-23-to-2026-04-24-n8.md`(115 行、子 8 件、フラット抽出)。長期間の「fold 未コミット」ステータスを反転
  - T6 codex 経由 M4 autoresearch トピック無し: 「How does the LLM Wiki pattern work?」を候補として選択(スコア 1.7022、トップ 1 のソース + トップ 2 の自己参照をスキップして #3)。Web 取得 6 件(Karpathy gist、RAG 論文 arXiv 2005.11401、MemGPT arXiv 2310.08560、Obsidian docs)。3 つの新規概念ページをファイリング、各々一次出典付き
- 場所(新規): `wiki/folds/fold-k3-from-2026-04-23-to-2026-04-24-n8.md`、`wiki/meta/tiling-report-2026-04-24.md`、`wiki/concepts/Persistent Wiki Artifact.md`、`wiki/concepts/Source-First Synthesis.md`、`wiki/concepts/Query-Time Retrieval.md`
- 場所(更新): `.vault-meta/address-counter.txt`(2 から 3)、`wiki/index.md`(概念リンク 3)、`wiki/concepts/_index.md`(概念リンク 3)
- 範囲: ユーザーが承認した 6 テストメニュー。codex gpt-5.4 が T1/T4/T6(サブエージェント委譲)、chair が T0/T2/T3(ワンショット shell)とすべての統合(index、log、hot、コミット)。
- スタイル: 新規コンテンツはすべて em ダッシュではなくコロンや括弧を使用。index エントリと wiki/concepts/_index.md の既存 em ダッシュはそのまま(クリーンルーム境界、F スライスのスタイルパスに延期)。
- テストは引き続きグリーン: `make test` パス(74+ アサーション)。
- 統合: chair が新規 3 概念を `wiki/index.md` と `wiki/concepts/_index.md` にコロンスタイル説明で追加し、新ページが発見可能に。クラスタは `[[How does the LLM Wiki pattern work?]]` を拡張し `[[LLM Wiki Pattern]]` と相互参照。
- 次の推奨スライス: (G) このテストバッチをコミットして v1.6.0 検証完了を宣言、または(H)この上に新エントリ 8 件が積まれた状態でもう 1 件 k=3 fold を実行し、階層 fold 未対応のループを将来フェーズで閉じる。

## [2026-04-24] save | v1.6.0 クローズアウト(Teams、chair 主導)
- 種別: ドキュメント + リリース衛生
- 場所(新規): wiki/meta/2026-04-24-v1.6.0-release-session.md(リリースセッション要約、346 行)、wiki/meta/boundary-frontier-2026-04-24.md(本 Vault に対する最初の M4 実行アーティファクト)、docs/dragonscale-guide.md(ユーザー向け DragonScale ガイド、563 行)
- 場所(更新): wiki/hot.md(タグ主張修正、Scripts 行に boundary-score 追加、tests 行に test_boundary_score 追加、push 行ドリフト、tiling 行カウント、em ダッシュ 1 件)、docs/install-guide.md(バージョン 1.5.0 から 1.6.0、DragonScale callout を 4 メカニズム全てに拡大、「hierarchical log folds」を「flat extractive log folds」に修正、docs/dragonscale-guide.md を指す)、README.md(DragonScale 括弧書きを 4 メカニズム全てに拡大、ガイドリンク追加)
- 範囲: Teams アプローチ、chair 主導。スライス A(codex 読み取り専用エクスプローラ 2 件: クローズアウト punch list + ドキュメント表面マップ)。スライス B(境界付き書き込み 6 件: chair 4 + codex worker 2、書き込み範囲非重複)。スライス C(codex 敵対検証者、ACCEPT WITH FIXES)。スライス D(修正パス + log エントリ + ドキュメント手動コミット + README)。
- 検証者: C1 が 6 ファイルにわたる 11 項目を発見。11 件すべて適用。`--allow-remote-ollama` と `--report PATH` のフラグタイポをリリースセッションで修正、boundary-frontier 由来をデフォルト vs 明示トップに合わせて `--top 7` に修正、hot.md タイリング行カウントの主張をドリフト回避のため削除、hot.md の「local tag only」を「local commits only, no git tag」に修正、install-guide の log fold 文言を「hierarchical」から「flat extractive」に修正、dragonscale-guide ロールバック文言を修正(`.vault-meta/` は M2+M3+M4 で共有のゲートであり、メカニズムごとではない)。
- モデル: 全工程で codex gpt-5.4 を使用。ユーザーは gpt-5.5 を要求したが当時の codex CLI 0.123.0 / このアカウントから到達不能。models_cache の上限は gpt-5.4、API は gpt-5.5 を「does not exist or you do not have access」で拒否。既存設定は既に `service_tier = "fast"` と `sandbox_mode = "workspace-write"` で「権限フルアクセスの chatgpt 用 fast」意図に一致。
- テスト: `make test` パス。test_allocate_address.sh(shell、12 アサーション)、test_tiling_check.py(python、18 アサーション)、test_boundary_score.py(python、44 アサーション)。ollama 依存ゼロ。
- タグ: ローカルにまだ v1.5.0 / v1.5.1 / v1.6.0 のタグなし。タグ作成と push はユーザー管理。既存タグ変更なし(v1.1、v1.4.0 〜 v1.4.3)。
- 意図的に未実施: M1 本番 fold のコミットなし、M3 エンドツーエンド実行なし(`ollama pull nomic-embed-text` が必要)、install-guide.md と README.md の既存 em ダッシュは未変更(クリーンルーム境界、本スライスの書き込み範囲外)、CLAUDE.md の既存未コミット変更も未変更。
- 次の推奨スライス: (E) origin/main に push、注釈タグ v1.5.0、v1.5.1、v1.6.0 を着地順に作成、または(F)install-guide.md、README.md、grep スキャンでフラグされた他 wiki ファイルの既存 em ダッシュを scrub する専用スタイルパス。

## [2026-04-24] save | DragonScale Phase 4 — 境界優先 autoresearch 出荷(v1.6.0)
- 種別: 機能リリース
- 場所(新規): scripts/boundary-score.py(`--top`、`--page`、`--json`、stdout 専用 CLI)、tests/test_boundary_score.py(40+ アサーション)
- 場所(更新): skills/autoresearch/SKILL.md(ヘルパー失敗フォールバック付きの新トピック選択セクション A/B/C)、commands/autoresearch.md(アジェンダ制御ラベル付きのトピック無し候補フロー)、wiki/concepts/DragonScale Memory.md(v0.4: M4 を NOT IMPLEMENTED から shipped に反転、鮮度フロアなしの正確な式、ファイル名ステム開示、フェンス処理修飾子)、CHANGELOG.md、.claude-plugin/{plugin,marketplace}.json(1.5.0 → 1.6.0)、Makefile(test-boundary ターゲット)、wiki/hot.md、wiki/index.md、wiki/concepts/_index.md(ステータスドリフト解決)。
- 範囲: 境界優先 autoresearch をオプトインのトピック選択モードとして。トピック無しの `/autoresearch` が上位 5 フロンティアページを表示、ユーザーは選択・上書き・辞退できる。明示的なヘルパー失敗フォールバックでユーザー質問へ。仕様のスコープ開示に合わせて全文「アジェンダ制御」とラベル付け。
- 正確性: フォルダ修飾 `[[notes/Foo]]` → Foo.md を含むファイル名ステム解決。自己ループ、未解決ターゲット、メタターゲット、シンボリックリンク、Vault エスケープすべて除外。コードフェンスパーサはバッククォートとチルダの両方を CommonMark 長さ追跡で処理(より長い開始フェンスはより短い内側フェンスで閉じない)。インデントブロックは意図的にフィルタしない(Obsidian の bullet 規約)。
- 鮮度: exp(-days/30)、フロアなし。古いページはゼロ重みに近づきフロンティアランキングを支配しない。
- レビューラウンド: codex 敵対 Phase 4 ラウンド 1(10 項目: 7 reject + 3 refine)。ラウンド 2(7 accept + still-reject 3: フォルダ修飾ステム、docstring フロア言及、hot.md 履歴ドリフト)。ラウンド 3(3 accept、PASS)。
- Phase 3.6(Phase 4 前のハードニング)は v1.5.1 として既に着地: tiling `--report` の VAULT_ROOT 封じ込め、ロールアウトベースライン、AGENTS.md 整合性、wiki-ingest .raw/ 矛盾、install-guide バージョン。
- 4 つの DragonScale メカニズムすべて出荷・オプトイン。origin/main から 44 コミット先、push なし。

## [2026-04-24] save | DragonScale Phase 3.5 — クロスフェーズハードニングを v1.5.0 に
- 種別: リリースハードニング
- 場所(新規): bin/setup-dragonscale.sh(オプトインインストーラ)、tests/test_allocate_address.sh、tests/test_tiling_check.py、Makefile、CHANGELOG.md
- 場所(更新): hooks/hooks.json(+.vault-meta/ ステージング)、agents/wiki-ingest.md(アドレスのシングルライタルール)、agents/wiki-lint.md(Mechanism 2+3 チェック)、skills/wiki-ingest/SKILL.md(非 DragonScale 文言の整合)、wiki/concepts/DragonScale Memory.md(M2 重大度を lint と一致、M4 を NOT IMPLEMENTED とマーク、シードページにアドレス c-000001)、.claude-plugin/{plugin.json,marketplace.json}(1.4.2/1.4.3 → 1.5.0)、README.md(11 スキル + DragonScale callout)、wiki/hot.md(v1.5.0 用にリフレッシュ)、.raw/.manifest.json(address_map に DragonScale Memory.md → c-000001)、.gitignore(`.vault-meta/.tiling.lock` + cache)、.vault-meta/address-counter.txt(2 に進める)。
- 範囲: クロスフェーズ監査からの hold-ship 項目 10 件を解決。再現可能なテストハーネスを追加(`make test` パス)。plugin.json と marketplace.json のバージョンを 1.5.0 に bump。CHANGELOG.md 作成。ホットキャッシュリフレッシュ。
- レビューラウンド: codex 3.5a(ドキュメント/エージェント修正で 5/5 accept)、codex 最終ホリスティック(監査項目 + 外科的回帰修正 2 件で 10/10 accept: wiki-ingest/wiki-lint 非 DragonScale 文言整合、README スキル数)。
- テスト: `make test` が shell アサーション 12(allocator)+ python アサーション 18(tiling-check)を実行。すべてパス、ollama 依存なし。
- Phase 3.5 完了。リポジトリ状態: 本パスで開発者コミット 6 件追加(f2e73c1、2b49a0c、8b28e48、19ad7e4、365f557、2e7dd16)。origin/main から計 39 コミット先。push なし。

## [2026-04-24] save | DragonScale Phase 3 — セマンティックタイリング MVP
- 種別: スキル更新 + 新スクリプト + 閾値状態
- 場所: scripts/tiling-check.py(485 行)、.vault-meta/tiling-thresholds.json(シードデフォルト)、skills/wiki-lint/SKILL.md(109 行のセマンティックタイリングセクション + チェックの項目 #10)、wiki/concepts/DragonScale Memory.md(Mechanism 3 のコストフレーミング明確化)
- 範囲: ollama nomic-embed-text を使ったオプトインの埋め込みベース重複検出。デフォルトバンド error>=0.90、review>=0.80、保守的シードと明示文書化(文献裏付け補間ではない)。キャリブレーション手順は文書化、自動化なし。
- セキュリティ: デフォルト OLLAMA_URL を 127.0.0.1 にロック。非 localhost は `--allow-remote-ollama` フラグ必須。シンボリックリンクと Vault ルートエスケープはファイル読み込み前に拒否(データ流出防止)。
- 正確性: cache キーは sha256(model+body)。保存時に孤立 GC。ロード時にモデルドリフト自動無効化。
- 並行性: `.vault-meta/.tiling.lock` への flock(LOCK_EX)。書き込みアトミシティのため PID ごとの一時ファイル。
- スケール: 500 ページ超で warn、5000 ページ超でハードフェイル exit 4。
- exit code: 0/2/3/4/10/11 を wiki-lint 連携で個別に表面化(「unknown」にまとめない)。
- レビューラウンド: codex exec 敵対パス 4 ラウンド。セキュリティ、cache 正確性、機能ゲート、包含論理、スケール、閾値正直さ、並行性、exit code、モデルドリフト、用語結合をカバー。
  ラウンド 1: 10 項目 → 7 reject + 3 refine。
  ラウンド 2: 6 accept + still-reject 4(symlink 順序、散文同期、exit-code 連携、checklist の用語 + 「API コストなし」主張)。
  ラウンド 3: 3 accept + still-reject 1(コストフレーミング文言)。
  ラウンド 4: accept。
- 最終評価: 10/10 accept。
- Phase 3 完了。初期仕様で範囲内だった DragonScale メカニズム 3 件すべてオプトイン機能として出荷。Mechanism 4(境界優先 autoresearch)は v0.2 のスコープ境界に従いアジェンダ制御のスコープ外としてフラグ。将来フェーズで出荷するかは未定。

## [2026-04-23] save | DragonScale Phase 2 — 決定論的ページアドレス MVP
- 種別: スキル更新 + 新スクリプト
- 場所: scripts/allocate-address.sh、skills/wiki-ingest/SKILL.md(アドレス割当セクション)、skills/wiki-lint/SKILL.md(アドレス検証セクション)、wiki/concepts/DragonScale Memory.md(Mechanism 2 を v0.2→v0.3 に書き直し)、.vault-meta/address-counter.txt、.raw/.manifest.json(新規)
- 範囲: MVP アドレス形式 `c-NNNNNN`(作成順カウンタ、6 桁ゼロパディング)。ロールアウトベースライン 2026-04-23。レガシーページは意図的バックフィルまで除外(将来の `l-` プレフィックス)。MVP にコンテンツハッシュ無し、fold 系譜エンコーディング無し(両方とも延期)。
- 並行性: flock ガード付き Bash ヘルパーによるアトミック割当。観測された最大 `c-` アドレスからのカウンタ復元、1 への黙ったリセットは絶対に無し。
- lint: ロールアウト後ページのアドレス無しはエラー、レガシーページのアドレス無しは情報。任意の `.vault-meta/legacy-pages.txt` マニフェストが `created:` メタが欠落・誤りのページを祖父権で扱う。
- 再取り込み冪等性: `.raw/.manifest.json` の `address_map` が再取り込みと改名にまたがってパス → アドレスマッピングを保持。
- 命名: メカニズムを「content-addressable paths」から「決定論的ページアドレス」に改名(MVP はコンテンツハッシュではなくカウンタ。旧名は overclaim だった)。
- レビューラウンド: codex exec 敵対パス 2 ラウンド。ラウンド 1: 8 reject(カウンタ変更、レース、一意性アトミシティ、ファイル欠落復旧、用語ドリフト、静かな後退経路、レガシー分類、再取り込み冪等性)。ラウンド 2: 7 accept + 1 reject(manifest.json 欠落)。ラウンド 3(項目 8 のみ): `.raw/.manifest.json` 作成後 accept。
- 最終評価: 8/8 accept。
- Phase 2 完了。Phase 3(セマンティックタイリング lint)は人間承認待ち。

## [2026-04-23] save | DragonScale Phase 1 — wiki-fold スキル出荷
- 種別: スキル
- 場所: skills/wiki-fold/SKILL.md、skills/wiki-fold/references/fold-template.md
- 範囲: 生 wiki/log.md エントリへのフラット抽出 fold。Bash stdout でのドライランがデフォルト(Write ツールなし、PostToolUse hook 残留を回避)。決定論的 fold_id による構造的冪等性。重複範囲検出。fold-of-folds は明示的にスコープ外。
- レビューラウンド: codex exec 敵対パス 3 ラウンド。ラウンド 1: 7 項目に refine 1 + reject 6(allowed-tools、hook 変更リスク、冪等性主張、ドライラン忠実性、children 構造、Mechanism 1 カバレッジ、自動コミット衝突)。ラウンド 2: 6 accept + 1 reject(25/26 カウント反転)。ラウンド 3(項目 4 のみ): accept。
- 最終評価: 7/7 accept。
- ドライランアーティファクト: /tmp/wiki-fold-dry-run-v2.md(コミット無し)。fold_id: fold-k3-from-2026-04-10-to-2026-04-23-n8。
- Phase 1 完了。Phase 2(content-addressable paths)は人間承認待ち。

## [2026-04-23] save | DragonScale Memory v0.2 — 敵対レビュー後
- 種別: 概念改訂
- 場所: wiki/concepts/DragonScale Memory.md
- レビュー: codex exec 敵対レビューが v0.1 の 7 件すべての load-bearing 主張を reject
- 変更: LSM 類比を弱化、強いプロンプトキャッシュ主張を削除、0.85 閾値をキャリブレーション手順で置換、2^k を MVP 利便性として正当化、境界優先 autoresearch のスコープ境界リークを認める、運用ポリシーセクション追加(retention/tombstones/versioning/conflict/concurrency/provenance/ACL)、主張に [sourced]/[derived]/[conjecture] タグ付け、再レビュー後にタグ付けスコープを narrow
- 再レビュー結果: 7/7 accept(タグ付けスコープ言語の外科的修正 1 件後)
- Phase 0 完了。Phase 1(wiki-fold スキル)は人間承認待ち。

## [2026-04-23] save | DragonScale Memory — Phase 0 設計ドキュメント(提案)
- 種別: 概念
- 場所: wiki/concepts/DragonScale Memory.md
- 出典: Heighway ドラゴン曲線の性質を LLM ウィキ記憶アーキテクチャに適用するブレインストーミングセッション
- 範囲: 記憶層のみ、エージェント推論ではない。4 メカニズム: (1) fold オペレータ(2^k log エントリで LSM スタイル指数圧縮)、(2) プロンプトキャッシュ安定性のためのコンテンツアドレス可能ページパス、(3) セマンティックタイリング lint(埋め込みベース dedup、0.85 コサイン閾値)、(4) 境界優先 autoresearch スコアリング
- ステータス: 提案。Phase 0 は codex 敵対レビュー待ち。Phase 1+(fold スキル、アドレスアンカー、タイリング lint、境界スコア)はレビュー通過待ち。
- 検証された一次出典: ドラゴン曲線(Wikipedia、境界次元 1.523627086)、正規ペーパーフォールディング系列(OEIS A014577)、LSM ツリー(arXiv 2504.17178、LevelDB 10x レベル比)、MemGPT(arXiv 2310.08560)、Anthropic プロンプトキャッシュ docs(5min/1hr TTL、20-block lookback)
- 更新リンク: wiki/concepts/_index.md、wiki/index.md

## [2026-04-15] save | Claude SEO v1.9.0 スライドと GitHub リリース
- 種別: セッション
- 場所: wiki/meta/2026-04-15-slides-and-release-session.md
- 出典: 15 枚 HTML プレゼンテーションデッキ(v190.html)構築、release_report.py のハードコードパス修正、GitHub に 68 ファイル push、v1.9.0 タグ付け、PDF アセット付き GitHub リリース作成
- 主な学び: ハードコードパスではなく Path.home()、大プッシュ前に git pull --rebase、Chrome は file:// クロスオリジン画像をブロック、`.claude/` は常に .gitignore へ
- リリース: https://github.com/AgriciDaniel/claude-seo/releases/tag/v1.9.0

## [2026-04-15] save | Claude SEO v1.9.0 リリースレポート — PDF 完成
- 種別: セッション
- 場所: wiki/meta/2026-04-15-release-report-session.md
- 出典: v1.9.0 PDF リリースレポート完成のフルセッション。ダークテーマ、13 ページ、1.53 MB。ロゴ修正(ダブルスペースファイル名)、空白、ページブレークオーファン、file:// URL エンコーディング修正。
- 主な修正: file:// URI の `urllib.parse.quote()`。WeasyPrint で `display:table-cell` はアトミック(ページブレークなし)。`height:297mm` が空白を生む問題を修正、オーファンテーブルを段落で置換
- Challenge v2 追加: キーワード LEADS、賞金プール $600、締切 4 月 28 日
- 出力: `~/Desktop/Claude-SEO-v1.9.0-Release-Report.pdf`

## [2026-04-14] save | Claude SEO v1.9.0 — Pro Hub Challenge 統合セッション
- 種別: セッション + 概念ページ 4 件 + エンティティページ 1 件
- 場所: wiki/meta/2026-04-14-claude-seo-v190-session.md
- 出典: v1.9.0 実装フルセッション。コミュニティ提出 5 件をレビュー、新規 4 スキル統合(seo-cluster、seo-sxo、seo-drift、seo-ecommerce)、seo-hreflang 強化、DataForSEO コストガードレール追加
- 作成ページ: [[2026-04-14-claude-seo-v190-session]]、[[Claude SEO]]、[[Pro Hub Challenge]]、[[Semantic Topic Clustering]]、[[Search Experience Optimization]]、[[SEO Drift Monitoring]]
- レビューラウンド: 4(コードレビュー x3 + サイバーセキュリティ監査)。スコア: 87 → 93 → 97 → 85 セキュリティ
- 主な学び: サブエージェント出力は必ず検証(40 行カウントエラー検出)、最大努力プランレビューで挿入ポイントバグ検出、既存セキュリティ負債特定(15 件中 10 件)

## [2026-04-14] save | SVG 図表スタイルガイド
- 種別: 概念
- 場所: wiki/concepts/SVG Diagram Style Guide.md
- 出典: claude-ads/assets/diagrams/ の本番 SVG 17 件からデザイントークン抽出
- カバー: 色、タイポグラフィ、レイアウトプリミティブ、カードパターン、矢印コネクタ、番号付き円、ファイル命名

## [2026-04-14] save | コミュニティ CTA フッターロールアウト
- 種別: 決定
- 場所: wiki/meta/2026-04-14-community-cta-rollout.md
- 出典: 6 スキルリポジトリ(claude-ads、claude-seo、claude-obsidian、claude-blog、banana-claude、claude-cybersecurity)に Skool コミュニティフッターを追加するセッション
- 主な気づき: ツールタイプごとの頻度キャリブレーション、単一ポイントオーケストレータ指示パターン

## [2026-04-10] save | バックリンク帝国 — ブログ投稿、Karpathy gist、GitHub クロスリンク
- 種別: セッション
- 場所: wiki/meta/2026-04-10-backlink-empire-session.md
- 出典: ブログ作成(claude-obsidian + claude-canvas)、Karpathy gist コメント、26 GitHub README 更新(Author/community/backlink セクション)、10 リポジトリのホームページ URL、25 リポジトリのトピック、5 SEO リポジトリへの rankenstein.pro バックリンクをカバーするフルセッション
- ブログ投稿: agricidaniel.com/blog/claude-obsidian-ai-second-brain、agricidaniel.com/blog/claude-canvas-ai-visual-production
- インパクト: DA 96 github.com からの新規バックリンク約 87 本、rankenstein.pro バックリンク 6 本、Skool コミュニティリンク 25 本

## [2026-04-08] save | claude-obsidian v1.4 リリースセッション
- 種別: セッション
- 場所: wiki/meta/claude-obsidian-v1.4-release-session.md
- 出典: v1.1(URL/ビジョン/デルタ追跡、新規 3 スキル)、v1.4.0(監査対応、マルチエージェント互換性、Bases ダッシュボード、em ダッシュ scrub、セキュリティ履歴書き換え)、v1.4.1(プラグイン install コマンドホットフィックス)をカバーするフルリリースサイクル
- 主な学び: プラグインインストールは 2 ステップ(marketplace add → install)、allowed-tools は有効な frontmatter ではない、Bases は filters/views/formulas を使い Dataview 構文ではない、hook コンテキストは圧縮を生き延びない、git filter-repo はフル scrub に 2 パス必要

## [2026-04-08] ingest | Claude + Obsidian エコシステムリサーチ
- 種別: リサーチ取り込み
- ソース: `.raw/claude-obsidian-ecosystem-research.md`
- クエリ: 並列 Web 検索 6 + リポジトリ深掘り 12
- 作成ページ: [[claude-obsidian-ecosystem]]、[[cherry-picks]]、[[claude-obsidian-ecosystem-research]]、[[Ar9av-obsidian-wiki]]、[[Nexus-claudesidian-mcp]]、[[ballred-obsidian-claude-pkm]]、[[rvk7895-llm-knowledge-bases]]、[[kepano-obsidian-skills]]、[[Claudian-YishenTu]]
- 主な発見: 16 以上のアクティブな Claude+Obsidian プロジェクト、v1.3.0+ 用に 13 のチェリーピック機能を特定
- トップギャップ確認: デルタ追跡なし、URL 取り込みなし、自動コミットなし

## [2026-04-07] session | フル監査、システムセットアップ、プラグインインストール
- 種別: セッション
- 場所: wiki/meta/full-audit-and-system-setup-session.md
- 出典: 12 領域のリポジトリ監査、3 修正、プラグインをローカルシステムにインストール、フォルダ改名

## [2026-04-07] session | claude-obsidian v1.2.0 リリースセッション
- 種別: セッション
- 場所: wiki/meta/claude-obsidian-v1.2.0-release-session.md
- 出典: v1.2.0 計画実行、cosmic-brain → claude-obsidian 改名、法務/セキュリティ監査、ブランド GIF、PDF インストールガイド、デュアル GitHub リポジトリのフルビルドセッション


- ソース: `.raw/`(初回取り込み)
- 更新ページ: [[index]]、[[log]]、[[hot]]、[[overview]]
- 主な気づき: ウィキパターンは一過性の AI チャットを複利知識に変える。あるユーザーはトークン使用量を 95% 削減した。

## [2026-04-07] setup | Vault 初期化

- プラグイン: claude-obsidian v1.1.0
- 構造: シードファイル + 初回取り込み完了
- スキル: wiki、wiki-ingest、wiki-query、wiki-lint、save、autoresearch
