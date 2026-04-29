# claude-obsidian: Gemini CLI 用指示書

このリポジトリは Andrej Karpathy の LLM Wiki パターンに基づき、永続的に成長する Obsidian ウィキ Vault を構築するナレッジベースコンパニオンです。スキルはクロスプラットフォームの Agent Skills 形式で書かれ、Gemini CLI / Antigravity と Claude Code の両方で動作します。

> **注意:** 応答およびウィキへの書き込みは日本語で(プロジェクト `CLAUDE.md` の言語ポリシーを参照)。ファイル名・スキル名・コード・frontmatter キーは英語のまま。

## スキルの探索

スキルは `skills/<name>/SKILL.md` に配置されています。Gemini CLI から利用するには:

```bash
ln -s "$(pwd)/skills" ~/.gemini/skills/claude-obsidian
```

または同梱インストーラを実行:

```bash
bash bin/setup-multi-agent.sh
```

## スキル一覧

| スキル | 機能 |
|---|---|
| `wiki` | 新規 Vault の足場、ホットキャッシュ管理、サブスキルへのルーティング |
| `wiki-ingest` | ソース(ファイル・URL・画像)を読み、1 件あたり 8〜15 ページを生成 |
| `wiki-query` | 3 段階の深さモードで wiki から回答を生成 |
| `wiki-lint` | 健全性チェック: 孤立ページ、デッドリンク、古い主張、欠落 |
| `save` | 現在の会話を wiki ノートとして保存 |
| `autoresearch` | 自律リサーチループ: 検索 → 取得 → 合成 → 保存 |
| `canvas` | Obsidian キャンバス(`.canvas`)ファイルの作成・編集 |
| `defuddle` | 取り込み前に Web ページをクリーン化(40〜60% トークン節約) |
| `obsidian-markdown` | Obsidian Flavored Markdown 構文リファレンス |
| `obsidian-bases` | Obsidian Bases(`.base` ファイル): ネイティブのデータベースビュー |

## トリガーフレーズ(例)

- 「ウィキを設定」「set up wiki」 → `wiki`
- 「この記事を取り込んで」「ingest this article」 → `wiki-ingest`
- 「https://example.com/article を取り込んで」 → `wiki-ingest`(URL モード)
- 「X について何を知ってる?」「what do you know about X」 → `wiki-query`
- 「wiki を lint して」「lint the wiki」 → `wiki-lint`
- 「この会話を保存して」「save this conversation」 → `save`
- 「[トピック] をリサーチして」「research [topic]」 → `autoresearch`

## Vault の規約

- `.raw/`: ソース文書、不変(絶対に書き換えない)
- `wiki/`: エージェント生成ナレッジ(あなたが所有)
- `wiki/hot.md`: 直近コンテキストキャッシュ(約 500 トークン)、セッション開始時に最初に読む
- `wiki/index.md`: マスターカタログ
- `.raw/.manifest.json`: 取り込みデルタ追跡

## ブートストラップ

最初のセッションで:
1. このファイル + プロジェクトの `CLAUDE.md` を読む
2. `wiki/hot.md` があれば静かに読んで直近コンテキストを復元
3. ユーザーが `/wiki`、`ingest`、`query` を入力するのを待つ

## プロジェクトリンク

- プラグイン: https://github.com/AgriciDaniel/claude-obsidian
- パターン: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
