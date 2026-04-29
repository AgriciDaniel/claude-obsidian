# claude-obsidian Hooks

claude-obsidian ウィキ Vault 用のプラグイン hook。すべての hook は `hooks.json` で定義。

## イベント

| イベント | 型 | 目的 |
|---|---|---|
| `SessionStart` | command + prompt | `wiki/hot.md` をコンテキストにロード。command 型は `[ -f wiki/hot.md ] && cat wiki/hot.md` を正規の安全チェックとして実行(Vault 無しセッションでもエラーせず)。prompt 型はセマンティックコンテキスト復元で補完。Matcher: `startup\|resume`。 |
| `PostCompact` | prompt | コンテキスト圧縮後に `wiki/hot.md` を再ロード。hook 注入コンテキストは圧縮を生き延びない(`CLAUDE.md` のみ生き延びる)ため、本 hook がセッション中盤でホットキャッシュを復元。 |
| `PostToolUse` | command | Write または Edit ツール呼び出し後の wiki/ または .raw/ 変更を自動コミット。`[ -d .git ]` でガードされ非 git ディレクトリでエラーせず、`git diff --cached --quiet` で空コミットを作らない。 |
| `Stop` | prompt | 各 Claude 応答終了時に何が変わったかの簡単な要約で `wiki/hot.md` を更新。 |

## 既知の問題: プラグイン Hook の STDOUT バグ

`anthropics/claude-code#10875` は **プラグイン hook の STDOUT が Claude Code に捕捉されない可能性** を文書化しているが、`settings.json` の同等インライン hook は正しく動作する。

**影響**: お使いの Claude Code バージョンで本バグが有効な場合、prompt 型の SessionStart と PostCompact hook が期待通りにコンテキストを注入しない可能性。

**回避策**: command 型の SessionStart hook(`cat wiki/hot.md`)が正規の安全チェック。STDOUT 捕捉に依存するため、ホットキャッシュ復元が失敗したら本問題を疑う。フォールバックとして `hooks.json` の hook 設定をプラグイン hook ではなくユーザレベルの `~/.claude/settings.json` にコピーする。

**バグテスト**: プラグインインストール後、populate された `wiki/hot.md` があるディレクトリで新しい Claude Code セッションを開き、「ホットキャッシュには何があるか?」と尋ねる。Claude が分からないと答えたら STDOUT バグが有効。

## Vault 無しセッション

SessionStart command hook は `[ -f wiki/hot.md ] && cat wiki/hot.md || true` を使い常に exit 0 を返す。Vault が無くても 0。これでプラグインをグローバルインストールしても Vault 無しの Claude Code セッションを壊さない。
