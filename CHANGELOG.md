# 変更履歴 (Changelog)

claude-obsidian の重要な変更点。書式は [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)、バージョニングは [SemVer](https://semver.org/) に準拠。

## [1.6.0-ja] — 2026-04-29

### 追加(日本語ローカライズ)

- **完全日本語ローカライズ**: チャット応答、ウィキページ本文、ログエントリ、要約をすべて日本語で出力するように切替。ファイル名・スキル名・frontmatter キーは英語のまま維持し、上流プラグインと完全互換。
- `CLAUDE.md` に「言語ポリシー」セクションを追加(最優先・全スキル共通の指示)。
- 全 SKILL.md・コマンド・エージェント定義を日本語化、トリガー語は日英バイリンガル化(英語と日本語の両方で発火可能)。
- 全 wiki ページに `aliases:` を追加して英語ファイル名と日本語表示名を併存。
- README、AGENTS、GEMINI、WIKI、ATTRIBUTION、各種 docs を日本語化。

## [1.6.0] - 2026-04-24

### 追加(DragonScale Mechanism 4、オプトイン)

- **境界優先 autoresearch**: `scripts/boundary-score.py` が wikilink グラフ全体で `(出次数 - 入次数) * 鮮度重み` を計算し、上位 K のフロンティアページを出力。トピックなしで `/autoresearch` を起動すると、Vault が DragonScale を採用済みの場合に上位 5 件のフロンティアページをリサーチ候補として提示。
- `tests/test_boundary_score.py` — frontmatter パース、鮮度重み、wikilink 抽出(コードブロック保護付き)、グラフ構築、スコアリング、CLI インターフェースをカバーする 35 件のユニットテスト。
- `make test-boundary` ターゲット + `make test` への統合。

### 変更

- `skills/autoresearch/SKILL.md` — 新「トピック選択」セクション。3 つの経路: 明示(A)、境界優先(B、オプトイン)、ユーザー質問(C、DragonScale 未採用時のデフォルト)。
- `commands/autoresearch.md` — トピックなし利用法を両モードで文書化。
- `wiki/concepts/DragonScale Memory.md` — Mechanism 4 を「未実装」から「実装済み」に切替、正確なスコアリング式と「含まれないもの」 callout を追加。バージョン v0.4 に更新。
- バージョンを plugin.json と marketplace.json で 1.6.0 に同期。

## [1.5.1] - 2026-04-24(Phase 3.6 ハードニング)

### 修正

- `scripts/tiling-check.py`: `--report PATH` を VAULT_ROOT 基準で解決し、外側に逃げる場合は拒否(セキュリティ: 悪意ある書き込みや偶発的書き込みを防止)。
- `.vault-meta/legacy-pages.txt`: ロールアウトベースラインを 2026-04-24 から 2026-04-23 に修正(シード Vault の最初期アドレス付きページに合わせる)。
- `AGENTS.md`: スキル表に wiki-fold を追加。古い主張「全スキルが name/description のみを使用」を新しめのスキル限定に narrow(古いスキルは Claude Code 互換のため allowed-tools を維持)。
- `skills/wiki-ingest/SKILL.md`: 「不変な .raw/」と「.raw/.manifest.json を維持」の内部矛盾を解消 — ユーザー投入のソース文書は不変、マニフェストのみが wiki-ingest 管理対象。
- `docs/install-guide.md`: バージョン 1.2.0 → 1.5.0、DragonScale オプションインストール callout を追加。

## [1.5.0] - 2026-04-24

### 追加(DragonScale Memory 拡張、オプトイン)

- **Mechanism 1 — Fold オペレータ**(`skills/wiki-fold/`): `wiki/log.md` のエントリを抽出的・構造的に冪等な形でバッチごとのメタページ(`wiki/folds/` 配下)にロールアップ。デフォルトは標準出力へのドライラン(PostToolUse 自動コミット hook を発火させない)、コミットモードは明示的。
- **Mechanism 2 — 決定論的ページアドレス**(オプトイン): `scripts/allocate-address.sh` の flock ガード付きアトミック割当器、新しい `address: c-NNNNNN` frontmatter 規約、`.raw/.manifest.json address_map` による再取り込み冪等性。`wiki-ingest` と `wiki-lint` のスキルは DragonScale セットアップを feature-detect。
- **Mechanism 3 — セマンティックタイリング lint**(オプトイン): `scripts/tiling-check.py` がローカル `nomic-embed-text`(ollama 経由)を使ってコサイン類似度で重複候補ページをフラグ。バンド付き閾値(error/review/pass)を保守的シードとして文書化、手動キャリブレーション手順あり。
- `wiki/concepts/DragonScale Memory.md` — 完全設計仕様(v0.3): 4 メカニズム、スコープ境界、一次出典引用。
- `bin/setup-dragonscale.sh` — `.vault-meta/` カウンタ・閾値・レガシーページマニフェストを冪等にプロビジョン。
- `tests/` — 割当器とタイリングチェック用の shell + python テストスイート。`make test` で実行。
- `Makefile` — 開発者ターゲット(`test`, `setup-dragonscale`, `clean-test-state`)。

### 変更

- `hooks/hooks.json` の PostToolUse は `wiki/` と `.raw/` に加えて `.vault-meta/` もステージし、DragonScale ランタイム状態を自動コミット hook で捕捉。
- `skills/wiki-ingest/SKILL.md` と `skills/wiki-lint/SKILL.md` は feature-detection ガードに守られたオプトインの DragonScale セクションを取得。`setup-dragonscale.sh` を実行していない Vault では従来動作のまま。
- `agents/wiki-ingest.md` で並列サブエージェントが割当器を呼ぶことを明示的に禁止(アドレス割当の単一書き込みルール)。
- `agents/wiki-lint.md` を Address Validation と Semantic Tiling チェックを含むよう拡張。
- 古い `allowed-tools` frontmatter を `wiki-ingest` と `wiki-lint` SKILL.md から除去(kepano 規約: `name` と `description` のみ)。
- バージョン文字列を `.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json`、ドキュメント間で同期。

### セキュリティ

- `scripts/tiling-check.py` はデフォルトで `OLLAMA_URL` を localhost にロック。リモートエンドポイントは `--allow-remote-ollama` 必須。シンボリックリンクと Vault ルート脱出は読み込み前に拒否。

### このリリースに含まれないもの

- **Mechanism 4 — 境界優先 autoresearch**: 仕様には将来案として記載、コード未出荷。`skills/autoresearch/SKILL.md` 変更なし。

## [1.4.3] - 以前

過去の状態。詳細は git log を参照。
