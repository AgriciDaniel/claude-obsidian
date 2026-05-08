---
source: claude-conversation
date: 2026-05-08
topic: claude-obsidianセットアップ＋第二の脳構築＋自動保存フック設定
---

# claude-obsidian セットアップ記録

## Summary
TwitterでバズっていたObsidian × Claude Code連携ツール「claude-obsidian」を発見し、セットアップから第二の脳の初期構造構築、さらにClaude Codeが自動でObsidianへの保存を提案する仕組みまで一気に実装した。

## Key Points
- `~/claude-obsidian-vault` にclone・セットアップ完了（setup-vault.shでExcalidrawも自動DL）
- Mode D（Personal Second Brain）として構造化：goals / learning / people / areas / resources
- キーページ作成：North Star / Annual Goals / Weekly Review Template
- `~/.claude/CLAUDE.md` にグローバル指示を追加：タスク完了後に「Obsidianに保存しますか？」と自動で聞く
- `~/.claude/commands/obsidian-save.md` を作成：保存時に .raw/ へ要約→wiki-ingestで自動WikiページDを生成

## Details

### インストール手順（実行済み）
```bash
git clone https://github.com/AgriciDaniel/claude-obsidian ~/claude-obsidian-vault
cd ~/claude-obsidian-vault
bash bin/setup-vault.sh
```

### Vault構造（Mode D: Personal Second Brain）
```
wiki/
├── goals/         — 目標管理
├── learning/      — 学習・概念
├── people/        — 人間関係
├── areas/         — health / career / finance / creative
├── resources/     — 本・ツール・記事
├── North Star.md
├── Annual Goals.md
└── Weekly Review Template.md
.raw/              — ソース投入フォルダ（ここに記事やメモを入れてingest）
_templates/        — goal / learning / person / resource
```

### 自動保存の仕組み
- **グローバルCLAUDE.md** (`~/.claude/CLAUDE.md`)：すべてのClaude Codeセッションで有効。重要なタスク完了後に「📝 Obsidianに保存しますか？」と聞く
- **`/obsidian-save` コマンド** (`~/.claude/commands/obsidian-save.md`)：「はい」と答えると会話要約を.raw/に保存し、wiki-ingestで自動WikiPage生成

### 日常的な使い方
1. 記事・メモ・書き起こしを `.raw/` に入れる
2. `cd ~/claude-obsidian-vault && claude` で起動
3. `ingest [ファイル名]` で自動Wiki化
4. 週次レビュー：`Weekly Review Template` を使って `hot.md` を更新
5. 10〜15回のingest後に `lint the wiki` でヘルスチェック

### 参照
- GitHub: https://github.com/AgriciDaniel/claude-obsidian
- 元ツイート: @defileo による「Claude + Obsidian | How to use your second brain」（99万ビュー）
- Vault path: ~/claude-obsidian-vault
- Obsidianで開くVault: claude-obsidian-vault（knowledge-baseではなく）

## Related Concepts
- LLM Wiki Pattern（Andrej Karpathy提唱）
- Second Brain / PKM（Personal Knowledge Management）
- Hot Cache（セッション間コンテキスト保持）
- Claude Code hooks（PostToolUse / Stop）
