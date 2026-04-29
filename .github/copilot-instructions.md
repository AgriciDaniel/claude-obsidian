# claude-obsidian: GitHub Copilot 用指示書

このリポジトリは **Claude Code プラグインかつ Obsidian Vault** で、Andrej Karpathy の LLM Wiki パターンを使い永続的に成長するナレッジベースを構築します。Markdown のみで構成され、ビルドステップ、コンパイル済みコード、ランタイム依存はありません。

> **言語ポリシー:** すべての応答とウィキ書き込みは日本語で行う(プロジェクト `CLAUDE.md` 参照)。ファイル名・コード・スキル名・frontmatter キーは英語のまま。

## プロジェクト種別

- Agent Skills パッケージ(クロスプラットフォーム Agent Skills 標準)
- Obsidian Vault(Obsidian で直接解釈可能)
- Claude Code プラグイン(マーケットプレイスでインストール可能)

## リポジトリ構成

- `skills/`: 10+ のスキル。各スキルは `SKILL.md` でトリガー語と指示を定義
- `hooks/hooks.json`: Claude Code ライフサイクル hook(SessionStart, PostCompact, PostToolUse, Stop)
- `.claude-plugin/plugin.json`: プラグインマニフェスト
- `wiki/`: 生成されたナレッジベース(YAML frontmatter 付き Markdown)
- `.raw/`: 不変のソース文書(絶対に書き換えない)
- `_templates/`: Obsidian Templater テンプレート
- `_attachments/`: wiki ページが参照する画像・PDF

## Copilot が従うべき規約

編集を提案するときは:

1. **frontmatter はフラットな YAML**、複数形キーを使う(`tags`, `aliases`, `cssclasses`)
2. **内部リンクは wikilink**: `[[Note Name]]`、`.md` パスへの Markdown リンクは使わない
3. **日付は `YYYY-MM-DD`**、ISO 日時形式は使わない
4. **`.raw/` は不変**。配下の編集を提案しない
5. **`wiki/log.md` は追記専用**、新エントリは TOP に
6. **`wiki/hot.md` はセッション終了時に上書き**、追記ではない
7. **スキルの frontmatter は `name` と `description` のみ**。`allowed-tools`、`triggers`、`globs` は使わない(Agent Skills 仕様外)
8. **カスタム callout**: この Vault は `[!contradiction]`, `[!gap]`, `[!key-insight]`, `[!stale]` を `.obsidian/snippets/vault-colors.css` で定義。スニペット有効時のみレンダリング
9. **本文・要約・チャット応答は日本語**、frontmatter のキー名・列挙値・コードは英語

## スキル(`skills/<name>/SKILL.md`)を編集するとき

- frontmatter: `name`(ディレクトリ名と一致)と `description`(クォート付き 1 行、最大約 250 文字、有用情報)
- 本文: 短い命令形の指示。ファイル参照はバッククォートで。本質的でない大コードブロックは貼らない
- トリガー語は `description` に書く(本文や非標準フィールドではなく)。日英バイリンガルにする(例: `triggers on: ingest, 取り込んで, ingest this url, この URL を取り込む`)

## hook(`hooks/hooks.json`)を編集するとき

- 有効なイベント名のみ: `SessionStart`, `Stop`, `PreToolUse`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`
- hook タイプ: `command`(shell)、`prompt`(LLM)、`http`(POST)、`agent`(サブエージェント)
- `matcher` フィールドは `PreToolUse`/`PostToolUse` でツール名に対する正規表現
- `SessionStart` の場合: matcher は `startup`, `resume`, `clear`, `compact` を使う

## 関連リンク

- プラグイン: https://github.com/AgriciDaniel/claude-obsidian
- パターン出典: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- 権威ある Obsidian 特化スキル: https://github.com/kepano/obsidian-skills
