---
type: concept
title: "Claude Code Hooks"
status: developing
tags: [concept, claude-code, automation, hooks]
created: 2026-05-08
updated: 2026-05-08
---

# Claude Code Hooks

Claude Code の `~/.claude/settings.json` に設定するイベントドリブンな自動化機能。特定のイベントに応じてシェルコマンドを実行できる。

## 主なイベント

| イベント | タイミング |
|---|---|
| `PreToolUse` | ツール実行前 |
| `PostToolUse` | ツール実行後 |
| `Stop` | Claudeが応答を止めたとき |
| `SessionStart` | セッション開始時 |

## グローバル設定ファイル

- `~/.claude/settings.json` — ユーザー全体に適用
- `~/.claude/CLAUDE.md` — 全セッションに適用されるグローバル指示
- `~/.claude/commands/` — グローバルスラッシュコマンド定義

## 自分の設定（2026-05-08）

`~/.claude/CLAUDE.md` に以下を設定済み：
- 重要なタスク完了後に「📝 Obsidianに保存しますか？」と自動提示
- 「はい」で `/obsidian-save` コマンドが起動し [[claude-obsidian]] vaultに保存

## 関連
- [[claude-obsidian]]
- [[Mode D Personal Second Brain]]
