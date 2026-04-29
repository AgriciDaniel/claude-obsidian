# claude-obsidian: エージェント向け指示書

このリポジトリは Claude Code プラグインであり、同時に Obsidian Vault でもあります。Andrej Karpathy の LLM Wiki パターンに基づき、永続的に成長するナレッジベースを構築します。Agent Skills 標準に対応した **任意の AI コーディングエージェント**(Codex CLI, OpenCode 等)で動作します。

オリジナルは Claude Code 向けですが、スキルはクロスプラットフォームの Agent Skills 仕様に従います。新しめのスキル(`wiki-fold`, `wiki-ingest`, `wiki-lint`)は frontmatter に `name` と `description` のみを使用(kepano 規約)。古めのスキルは Claude Code 互換のため `allowed-tools` フィールドを残しています。これを認識しないクロスプラットフォームエージェントは無視して構いません。

> **注意:** すべての応答およびウィキへの書き込みは日本語で行うこと(プロジェクト `CLAUDE.md` の言語ポリシーを参照)。ファイル名・スキル名・frontmatter キー名・コードは英語のまま。

## スキルの探索

すべてのスキルは `skills/<name>/SKILL.md` に配置されています。Codex / OpenCode / その他の Agent Skills 互換エージェントは、ディレクトリをシンボリックリンクすれば自動探索します:

```bash
# Codex CLI
ln -s "$(pwd)/skills" ~/.codex/skills/claude-obsidian

# OpenCode
ln -s "$(pwd)/skills" ~/.opencode/skills/claude-obsidian
```

または同梱インストーラを実行:

```bash
bash bin/setup-multi-agent.sh
```

## 利用可能なスキル

| スキル | トリガー(日英) |
|---|---|
| `wiki` | `/wiki`、ウィキを設定、足場を作る、set up wiki, scaffold vault |
| `wiki-ingest` | 取り込んで、ingest、URL を取り込む、画像を取り込む、バッチ取り込み |
| `wiki-query` | 質問、wiki に聞く、query、query quick:、query deep: |
| `wiki-lint` | wiki を lint、健全性チェック、孤立ページを探す、find orphans |
| `wiki-fold` | log を fold、log を畳む(DragonScale Mechanism 1、オプトイン) |
| `save` | `/save`、保存、この会話を保存 |
| `autoresearch` | 自動リサーチ、autoresearch |
| `canvas` | `/canvas`、キャンバスに追加、キャンバス作成 |
| `defuddle` | URL をクリーン化、defuddle |
| `obsidian-markdown` | obsidian 構文、wikilink、callout |
| `obsidian-bases` | obsidian bases、`.base` ファイル、動的テーブル |

## 重要な規約

- **Vault ルート**: `wiki/` と `.raw/` を含むディレクトリ
- **ホットキャッシュ**: `wiki/hot.md`(セッション開始時に読み、終了時に更新)
- **ソース文書**: `.raw/`(不変。エージェントは絶対に書き換えない)
- **生成知識**: `wiki/`(エージェント所有。wikilink でソースを参照)
- **マニフェスト**: `.raw/.manifest.json`(取り込み済みソースのデルタ追跡)

## ブートストラップ

ユーザーが初めてこのプロジェクトを開いた時:

1. このファイル(`AGENTS.md`)とプロジェクトの `CLAUDE.md` を読んで全体コンテキストを把握
2. `skills/wiki/SKILL.md` を読んでオーケストレーションパターンを把握
3. `wiki/hot.md` があれば静かに読んで直近コンテキストを復元
4. ユーザーが `/wiki`(あるいは「ウィキを設定」)と入力したら wiki スキルの足場ワークフローへ

## 参照リンク

- プラグインホームページ: https://github.com/AgriciDaniel/claude-obsidian
- パターンの出典: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- 関連: https://github.com/kepano/obsidian-skills(Obsidian 特化スキルの権威ある実装)
