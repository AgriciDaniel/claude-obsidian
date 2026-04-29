---
type: session
title: "claude-obsidian v1.4 リリースセッション"
created: 2026-04-08
updated: 2026-04-08
aliases:
  - claude-obsidian-v1.4-release-session
  - "claude-obsidian v1.4 リリースセッション"
tags:
  - meta
  - session
  - release
  - audit-response
status: evergreen
related:
  - "[[claude-obsidian-ecosystem]]"
  - "[[cherry-picks]]"
  - "[[full-audit-and-system-setup-session]]"
  - "[[claude-obsidian-v1.2.0-release-session]]"
  - "[[LLM Wiki Pattern]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# claude-obsidian v1.4 リリースセッション

v1.1、v1.4.0、v1.4.1を含む完全なリリースサイクル。エコシステム調査、外部監査への対応、マルチエージェント互換性の展開、em dashスタイル整理の徹底、プライバシーのためのgit履歴のスクラブ、プラグインインストールコマンド構文のhotfixを含む。

## リリース順序

| バージョン | 出荷内容 |
|---|---|
| v1.1 | URL ingestion、画像/視覚ingestion、デルタ追跡マニフェスト、新スキル3件(defuddle、obsidian-bases、obsidian-markdown)、マルチ深度のwiki-queryモード、PostToolUse自動コミットフック、無効な`allowed-tools`フロントマターフィールドの除去 |
| v1.4.0 | DataviewからBasesへの移行、Canvas JSON 1.0仕様の完全化、フックの強化とPostCompact、Obsidian CLIオプションを含むMCPセットアップの強化、カスタムcalloutの文書化、マルチエージェントbootstrapファイル6件、em dash 249個のスクラブ、プレースホルダーemailを除去するためのgit履歴のセキュリティ書き換え |
| v1.4.1 | READMEとdocs/install-guide.mdに記載のプラグインインストールコマンド構文の誤りに対するhotfix |

## v1.1: 本セッションの最初の機能リリース

エコシステム全体に対する内部品質チェックへの応答として出荷(Claude+Obsidianプロジェクト16件以上を調査、[[claude-obsidian-ecosystem]]に記録)。競合実装からもっとも価値の高い機能をcherry-pickし、v1.1として出荷した。

### 新スキル(Agent Skills仕様準拠)

- `skills/defuddle/SKILL.md`:URL ingestionの前にWebページから広告、ナビゲーション、雑要素を除去。一般的な記事でトークンを40〜60%節約。
- `skills/obsidian-markdown/SKILL.md`:Obsidian Flavored Markdown(wikilink、embed、全calloutタイプ、プロパティ、math、Mermaid)の完全リファレンス。kepano/obsidian-skillsを正典としてクロス参照。
- `skills/obsidian-bases/SKILL.md`:ネイティブのObsidian Bases `.base`ファイル構文。正しい`filters/views/formulas`構造を使用(Dataview風の`from/where`ではない)。最初の試みで誤った構文を使ったため、セッション中に書き直した。

### wiki-ingestのアップグレード

- **URL ingestion**:任意の`https://` URLを直接渡す。WebFetchを使い、必要に応じてdefuddleにパイプし、`.raw/articles/`に保存後、通常のingestパイプラインを実行。
- **画像/視覚ingestion**:`.png`、`.jpg`、`.gif`、`.webp`など。Claudeが画像をネイティブに読み、OCRでテキストを、視覚で概念を抽出し、説明を`.raw/images/`に保存後にingestする。
- **デルタ追跡**:`.raw/.manifest.json`がソースごとにMD5ハッシュ、タイムスタンプ、生成されたページを追跡。変化していないファイルへのingest再実行は自動的にスキップ。「force ingest」で上書き可能。

### wiki-queryのマルチ深度モード

3層のクエリ階層:

- **Quick**(`query quick: ...`):hot.mdとindex.mdのみ。約1,500トークン。事実の参照に最適。
- **Standard**(デフォルト):hot + index + 関連ページ3〜5件。約3,000トークン。多くの質問に最適。
- **Deep**(`query deep: ...`):wikiの完全クロス参照+ 必要に応じてweb検索を補完。約8,000+トークン。総合、比較、「Xに関する全てを教えて」に最適。

### フック:PostToolUse自動コミット

`wiki/`または`.raw/`に対する`Write`または`Edit`ツール呼び出しごとに、`git add`と`git commit`を自動的にトリガー。`[ -d .git ]`で保護され、非gitディレクトリでもエラーにならない。`git diff --cached --quiet`で空コミットを作らないようにも保護されている。マッチャー:`Write|Edit`。

### 重要修正:`allowed-tools`フロントマターを削除

Agent Skills仕様はSKILL.mdフロントマターで`name`、`description`、`argument-hint`、`compatibility`、`disable-model-invocation`、`license`、`metadata`、`user-invokable`フィールドのみをサポートする。`allowed-tools`フィールドは元々有効ではなく、黙って無視されていた。kepano/obsidian-skillsの正典規約に合わせて、すべての10件のSKILL.mdから削除した。

## v1.4.0: 外部監査への対応

外部監査者がAgent Skills仕様、Claude Codeフック、Obsidian v1.9〜v1.12、JSON Canvas 1.0に対する21ソースのレビュー(「コンパスアーティファクト」)を提出。初回監査スコア:6.5/10。多くの指摘はv1.1で既に解決済みだった(監査はそのリリース前のスナップショットに対して行われた)。残りの有効な指摘がv1.4.0となった。完全な指摘事項と優先度付けは[[cherry-picks]]に記載。

### Tier 1: 重要修正

**DataviewからBasesへの移行**(最大の正確性修正)。Obsidian Basesはv1.9.10(2025年8月)でコアプラグインとして同梱され、ほとんどのユースケースでDataviewを置き換えるネイティブのデータベース風ビューを提供する。`wiki/meta/dashboard.base`に6つのビュー(Recent Activity、Seed Pages、Entities Missing Sources、Open Questions、Comparisons、Sources)を作成。`wiki/meta/dashboard.md`を更新し、新しいベースファイルをプライマリーで埋め込み、レガシーDataviewクエリを任意のフォールバックとして残す。READMEのプラグインセクションを再構成し、Basesをプライマリ(コア、インストール不要)として推奨し、Dataviewを任意/レガシーと明記。

**Canvas JSON 1.0仕様の完全化**。`skills/canvas/references/canvas-spec.md`にこれまで欠けていたフィールドを追加:
- グループノード:`background`(文字列パス)と`backgroundStyle`(`cover`、`ratio`、`repeat`)
- エッジ:`fromEnd`(デフォルト`"none"`)と`toEnd`(デフォルト`"arrow"`)。明示的な指定なしで単一の矢印を生成する非対称デフォルト。
- 公式の16進数ID規約を、説明的IDの代替と並べて文書化。

### Tier 2: 重要な改善

**フックの強化とPostCompact**。`hooks/hooks.json`を更新:

- SessionStartが`command`型と`prompt`型の両方を使用するようになった。コマンドは`[ -f wiki/hot.md ] && cat wiki/hot.md || true`を実行し、これは非vaultセッションでもエラーを起こさない正規の安全チェックとして機能する。マッチャー:`startup|resume`。
- **新規PostCompactフック**がコンテキスト圧縮後に`wiki/hot.md`を再注入する。重要な気付き:フック注入されたコンテキストは圧縮を生き延びない。`CLAUDE.md`だけが残る。このフックがないと、ホットキャッシュは任意の圧縮イベント後にセッション中に消失する。
- PostToolUseの自動コミットが、既存のセーフガードに加えて`[ -d .git ]`でも保護されるようになった。
- 新しい`hooks/README.md`が4つのフックすべてと、既知のplugin-hooks STDOUTバグ(`anthropics/claude-code#10875`)および回避策を文書化。

**MCPセットアップの強化**。`skills/wiki/references/mcp-setup.md`に`> [!warning]`callout を`NODE_TLS_REJECT_UNAUTHORIZED: "0"`行の上に配置し、これがプロセス全体でTLS検証を無効にすること(`127.0.0.1`のみで許容される)を説明。**Option D: Obsidian CLI**(Obsidian v1.12+)を、TLS回避策を完全に避けて、ネイティブCLIをBashツール経由で使う推奨代替策として追加。

**カスタムcalloutの文書化**。vaultは`.obsidian/snippets/vault-colors.css`で4つのカスタムcalloutタイプを定義する:

| Callout | 色 | アイコン | 用途 |
|---|---|---|---|
| `contradiction` | 赤茶 | `lucide-alert-triangle` | 新ソースが既存の主張と衝突 |
| `gap` | ベージュ | `lucide-help-circle` | トピックにまだソースが無い |
| `key-insight` | 鮮やかな青 | `lucide-lightbulb` | 強調すべき重要な要点 |
| `stale` | 灰 | `lucide-clock` | 主張が古くなっている可能性 |

完全なドキュメントを`skills/wiki/references/css-snippets.md`に追加。カスタムCSSを使いたくないユーザー向けの組み込み代替も含む。`skills/wiki-ingest/SKILL.md`には`[!contradiction]`がCSSスニペットに依存するという明示的な注記を追加。

### Tier 3: マルチエージェント互換(低複雑度、高リーチ)

スキルは既にクロスプラットフォームのAgent Skills形式である。欠けていたのは、他のAIコーディングエージェントがそれらを発見できるようにするアダプタファイルだけだった。以下を追加:

| ファイル | 対象 |
|---|---|
| `AGENTS.md` | Codex CLI、OpenCode |
| `GEMINI.md` | Gemini CLI、Antigravity |
| `.cursor/rules/claude-obsidian.mdc` | Cursor(常時オンルール) |
| `.windsurf/rules/claude-obsidian.md` | Windsurf Cascade |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `bin/setup-multi-agent.sh` | `skills/`を各エージェントの想定場所に接続するidempotentなsymlinkインストーラー |

これにより、互換性コストをほぼゼロでclaude-obsidianがマルチエージェントプラグインになる。マルチエージェント対応のリファレンス実装である[[Ar9av-obsidian-wiki]]からパターンを借用。

## スタイル整理:Em Dashスクラブ

ユーザー設定をフィードバックメモリーに保存:em dash(U+2014)や`--`を句読点として使わない。代わりにピリオド、カンマ、コロン、括弧を使う。複合語のハイフン(auto-commit、multi-agent)は問題ない。

`/tmp/scrub_em_dashes.py`にコンテキスト認識のPythonスクラバーを書いた。ルール:

- 見出し行(`^#`):em dashは`:`へ
- リスト項目(`^-`、`^|`):em dashは`:`へ(ラベル-説明パターン)
- 散文:em dashは`.`へ、次の語を大文字化

**結果**: 26ファイルにわたり249個のem dashを除去。すべてのSKILL.md、すべてのドキュメント、すべてのフックファイル、すべてのbootstrapファイル、marketplace.jsonをスクラブ。手動の整理が必要だった箇所:

- `skills/obsidian-markdown/SKILL.md`:スクラバーが壊れた断片を生成したコードブロック注釈表4件。適切なmarkdown表に変換。
- `skills/wiki-query/SKILL.md`:「If X. Respond.」の断片4件を「If X, respond.」に書き直し。
- `bin/setup-multi-agent.sh`:スクラバーが見落とした行末em dash 1個(スペース-em-スペースのみ照合していた)。それに加え、ぎこちないecho文字列を1件修正。

ユーザーから受けたフィードバックは明確だった:「適切で自然にしてくれ」。スクラブされた散文は、断片化された文章を整えた結果、より読みやすい。

## セキュリティ:Email削除とgit履歴の書き換え

プレースホルダーemail `[scrubbed-email]`(ユーザーが実在のアドレスではないことを確認済み)が`marketplace.json`と2件のドキュメントに含まれていた。最初に作業ツリーから削除し、続けてすべてのコミットからスクラブするようgit履歴を書き換えた。

**ツール**: `git filter-repo`(`~/.pyenv/versions/3.12.4/bin/git-filter-repo`にあり)。

**2回のパスが必要**:

1. `git filter-repo --replace-text /tmp/email-replacements.txt --force`がすべてのコミットでblobの内容をスクラブ。
2. `git filter-repo --replace-message /tmp/email-msg-replacements.txt --force`がコミットメッセージをスクラブ。最初のパスはファイル内容の3件の出現を捕捉したが、コミット件名内の1件を見落とした。2回目のパスでそれを捕捉。

**置換文字列**: `[scrubbed-email]==>***REMOVED***`

**書き換え後の作業**:
- filter-repoが安全のため削除する`origin`リモートを再追加
- `v1.4.0`タグをセキュリティコミットを含めるように前倒し(v1.4.0はまだ誰のユーザーにも消費されていなかったため)
- mainと両タグ(`v1.1`、`v1.4.0`)をforce push
- v1.4.0のGitHubリリースノートを更新し、「Security Note」セクションを追加

**検証**: すべてのref、すべてのblob、すべてのコミットメッセージにわたるgrepでスクラブ済みemail文字列の一致は0件。GitHubリリース本文も同じく確認:v1.1、v1.4.0両方のリリースページがクリーン。

**他のクローンに対する注意**: 履歴書き換えにより、すべてのコミットハッシュが変化した。リポジトリを保持する他のマシンや、非公開の`community`リモートには古い履歴が残っている。それらは`git fetch && git reset --hard origin/main`が必要、もしくはforce pushでクリーンアップする必要がある。

## v1.4.1: プラグインインストールコマンドのhotfix

v1.4.0のREADMEとインストールガイドではこのインストールコマンドを記載していた:

```bash
claude plugin install github:AgriciDaniel/claude-obsidian
```

この形式はClaude Codeに存在しない。試したユーザーには以下が表示される:

```
Failed to install plugin "github:AgriciDaniel/claude-obsidian": Plugin "github:AgriciDaniel/claude-obsidian" not found in any configured marketplace
```

### 正しいインストールフロー(`code.claude.com/docs/en/plugin-marketplaces`より)

プラグインインストールは**2段階**のプロセス:

```bash
# ステップ1: マーケットプレースカタログを追加
claude plugin marketplace add AgriciDaniel/claude-obsidian

# ステップ2: カタログから名前でプラグインをインストール
claude plugin install claude-obsidian@claude-obsidian-marketplace
```

`claude-obsidian`はプラグイン名(`plugin.json`より)で、`claude-obsidian-marketplace`はマーケットプレース名(`marketplace.json`より)。`@`デリミタが両者を区切る。

### 混乱が起きていた理由

`claude plugin install github:owner/repo`のショートカットは存在しない。マーケットプレースの抽象化は必須:Claude Codeは常に登録済みマーケットプレース経由で取得する。claude-obsidianのような単一リポジトリプラグインは、マーケットプレースのホストとプラグインのホストの両方であり、ユーザーは任意のプラグインをインストールする前にまずマーケットプレースを登録する必要がある。

### 関連CLIコマンド(知っておくと便利)

| コマンド | 動作 |
|---|---|
| `claude plugin marketplace list` | 登録済みマーケットプレースをすべて表示 |
| `claude plugin marketplace add owner/repo` | GitHubリポジトリから新規マーケットプレースを登録 |
| `claude plugin marketplace update <name>` | マーケットプレースカタログを更新し再クローン |
| `claude plugin marketplace remove <name>` | マーケットプレースを登録解除(プラグインもアンインストール) |
| `claude plugin install <plugin>@<marketplace>` | 指定プラグインをインストール |
| `claude plugin list` | インストール済みプラグインとその状態を表示 |
| `claude plugin validate .` | marketplace.json、plugin.json、フロントマターを検証 |

### v1.4.1で変更したファイル

- `README.md`:Option 2インストールセクションを2段階フローで書き直し
- `docs/install-guide.md`:同様の修正
- `.claude-plugin/plugin.json`:1.4.0から1.4.1
- `.claude-plugin/marketplace.json`:`metadata.version`と`plugins[0].version`の両方を1.4.1にバンプ

### 動作確認済み

v1.4.1公開後、ユーザーが修正済みコマンドを実行し以下を確認:

```
claude-obsidian@claude-obsidian-marketplace
  Version: 1.4.1
  Scope: user
  Status: ✔ enabled
```

v1.4.1はuserスコープでインストールされ有効化された。

## 主要な学び(覚えておく価値あり)

1. **プラグインインストールは常に2段階**。github向けの省略形は無い。`marketplace add`してから`install plugin@marketplace`。
2. **`allowed-tools`は有効なskillフロントマターフィールドではない**。Agent Skills仕様は`name`、`description`、`argument-hint`、`compatibility`、`disable-model-invocation`、`license`、`metadata`、`user-invokable`のみを受け付ける。kepano/obsidian-skillsは`name`と`description`のみを使用しており、これがゴールド標準の規約。
3. **Obsidian Basesは`filters/views/formulas`を使い、Dataview風の`from/where`ではない**。混同しやすい。常に`help.obsidian.md/bases/syntax`で現行構文を確認する。
4. **Canvas JSON 1.0は非対称なエッジデフォルトを持つ**。`fromEnd`はデフォルト`"none"`、`toEnd`はデフォルト`"arrow"`。両方とも省略すると、ソースからターゲットへの単一矢印が生成される。
5. **フック注入されたコンテキストはコンテキスト圧縮を生き延びない**。`CLAUDE.md`だけが残る。SessionStartフック経由でコンテキストを注入するプラグインは、PostCompactフックも追加してセッション中にそれを復元すべき。
6. **`git filter-repo`は完全スクラブに2回のパスが必要**。`--replace-text`はblobの内容、`--replace-message`はコミットメッセージを処理する。片方だけでは痕跡が残る。
7. **`git filter-repo`は安全のため`origin`リモートを削除する**。force push前に手動で再追加する必要がある。
8. **マーケットプレース名とプラグイン名は異なってよい**。当方のマーケットプレースは`claude-obsidian-marketplace`、プラグインは`claude-obsidian`。`@`デリミタが両者を区別する。
9. **スタイル設定:em dashはどこにも使わない**。代わりにピリオド、カンマ、コロン、括弧。すべての散文、コミットメッセージ、リリースノート、ファイル内容に適用。複合語のハイフンは問題ない。

## このセッションで作成されたファイル

新規または新たに作成されたものすべての要約:

| パス | 種別 | 目的 |
|---|---|---|
| `skills/defuddle/SKILL.md` | skill | Webページクリーナー |
| `skills/obsidian-bases/SKILL.md` | skill | Obsidian Bases構文 |
| `skills/obsidian-markdown/SKILL.md` | skill | Obsidian構文の完全リファレンス |
| `wiki/meta/dashboard.base` | basesダッシュボード | 6ビューのBasesダッシュボード |
| `wiki/comparisons/claude-obsidian-ecosystem.md` | comparison | 16+プロジェクトの機能マトリクス |
| `wiki/concepts/cherry-picks.md` | concept | 優先度付き機能バックログ |
| `wiki/sources/claude-obsidian-ecosystem-research.md` | source | 研究まとめ |
| `wiki/entities/Ar9av-obsidian-wiki.md` | entity | マルチエージェント参照実装 |
| `wiki/entities/Nexus-claudesidian-mcp.md` | entity | ネイティブObsidianプラグイン |
| `wiki/entities/ballred-obsidian-claude-pkm.md` | entity | ゴールカスケードPKM |
| `wiki/entities/rvk7895-llm-knowledge-bases.md` | entity | マルチ深度クエリのリファレンス |
| `wiki/entities/kepano-obsidian-skills.md` | entity | 正典スキルリファレンス |
| `wiki/entities/Claudian-YishenTu.md` | entity | ネイティブObsidianプラグイン |
| `.raw/claude-obsidian-ecosystem-research.md` | raw source | エコシステム研究ダンプ |
| `hooks/README.md` | doc | フック文書 |
| `AGENTS.md` | bootstrap | Codex CLI / OpenCode |
| `GEMINI.md` | bootstrap | Gemini CLI / Antigravity |
| `.cursor/rules/claude-obsidian.mdc` | bootstrap | Cursorルール |
| `.windsurf/rules/claude-obsidian.md` | bootstrap | Windsurf Cascade |
| `.github/copilot-instructions.md` | bootstrap | GitHub Copilot |
| `bin/setup-multi-agent.sh` | script | マルチエージェントsymlinkインストーラー |

## 現在のプラグイン状態

- **インストール済みプラグイン**: `claude-obsidian@claude-obsidian-marketplace`バージョン`1.4.1`、userスコープ、有効
- **GitHubのリリース**: `v1.1`、`v1.4.0`、`v1.4.1`
- **`skills/`内の10スキル**: wiki、wiki-ingest、wiki-query、wiki-lint、save、autoresearch、canvas、defuddle、obsidian-bases、obsidian-markdown
- **`hooks/hooks.json`内の4つのライフサイクルフック**: SessionStart、PostCompact、PostToolUse、Stop
- **6つのマルチエージェントbootstrapファイル**:Codex、OpenCode、Gemini、Cursor、Windsurf、GitHub Copilotをカバー
- **`agents/`内の2エージェント**: wiki-ingest、wiki-lint

## v1.5.0へ持ち越し

監査cherry-picksリストから、これらの項目はv1.4.0には意図的に含めなかった:

- 既存vaultのインポート用`/adopt`コマンド(中複雑度、新規面の追加)
- wiki-lintへのvaultグラフ分析強化(ハブページ、クロスドメインブリッジ、デッドエンド)
- qmd MCPサーバー経由のセマンティック検索(任意の外部依存)
- wikiクエリからのMarpスライド出力(ニッチ)
- ThinkingモードとWritingモードのUX実験
