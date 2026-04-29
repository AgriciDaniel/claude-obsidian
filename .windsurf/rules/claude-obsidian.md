# claude-obsidian: Windsurf ルール

このリポジトリは Andrej Karpathy の LLM Wiki パターンを使い、永続的に成長する Obsidian ウィキ Vault を構築するナレッジコンパニオンです。スキルはクロスプラットフォームの Agent Skills 形式で書かれ、Cascade と Claude Code の両方で動作します。

> **言語ポリシー:** すべての応答とウィキ書き込みは日本語で行う(プロジェクト `CLAUDE.md` 参照)。ファイル名・コード・スキル名・frontmatter キーは英語のまま。

## プロジェクト種別

- **ハイブリッド**: Claude Code プラグイン + Obsidian Vault
- **パターン**: LLM Wiki(Karpathy)
- **スタック**: Markdown のみ。ビルドステップなし、ランタイム依存なし

## リポジトリの中身

```
claude-obsidian/
├── skills/              ← 10+ の SKILL.md(Agent Skills 形式)
├── hooks/               ← SessionStart, PostCompact, PostToolUse, Stop
├── .claude-plugin/      ← Claude Code プラグインマニフェスト
├── _templates/          ← Obsidian Templater テンプレート
├── wiki/                ← 生成されたナレッジベース
│   ├── hot.md           ← 直近コンテキストキャッシュ(約 500 トークン)
│   ├── index.md         ← マスターカタログ
│   ├── log.md           ← 追記専用の操作ログ
│   ├── concepts/, entities/, sources/, comparisons/, questions/
│   └── meta/dashboard.base ← Obsidian Bases ダッシュボード
└── .raw/                ← 不変のソース文書
```

## Cascade で利用できるスキル

`bash bin/setup-multi-agent.sh` を 1 回実行して `skills/` を `.windsurf/skills/` にシンボリックリンク。以後 Cascade が全スキルを自動探索します:

- `wiki`: オーケストレーション、Vault 足場、ホットキャッシュ
- `wiki-ingest`: ファイル、URL、画像 → 8〜15 ウィキページ
- `wiki-query`: Quick / Standard / Deep のクエリモード
- `wiki-lint`: 健全性チェック(孤立、デッドリンク、ギャップ)
- `save`: 会話を wiki ノートとして保存
- `autoresearch`: 自律リサーチループ
- `canvas`: Obsidian キャンバス(`.canvas`)ファイル
- `defuddle`: 取り込み前に Web ページをクリーン化
- `obsidian-markdown`: Obsidian 構文の完全リファレンス
- `obsidian-bases`: Obsidian Bases(`.base`)データベースビュー

## 重要なルール

- **`.raw/` を絶対に書き換えない**: ソース文書である
- **セッション開始時に `wiki/hot.md` を静かに読む**(コンテキスト復元)
- **すべての内部参照は wikilink** `[[Note Name]]` を使う
- **frontmatter はフラットな YAML**、複数形キー(`tags`, `aliases`)
- **自動コミット hook** が `wiki/` と `.raw/` への Write/Edit ごとに発火
- **`wiki/log.md` には先頭に追記**、過去エントリは編集しない
- **本文・要約・チャット応答は日本語**、frontmatter キー・コード・列挙値は英語

## ブートストラップ

ユーザーが Windsurf でこのプロジェクトを開いたら:

1. このルールファイルを読む
2. `wiki/hot.md` があれば静かに読む
3. 「ウィキを設定」「set up wiki」「取り込んで」「ingest」「質問」「query」などのトリガーを待つ

## リンク

- https://github.com/AgriciDaniel/claude-obsidian
- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- https://github.com/kepano/obsidian-skills
