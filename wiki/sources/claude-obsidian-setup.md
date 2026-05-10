---
type: source
title: "claude-obsidian セットアップ記録"
source: claude-conversation
date: 2026-05-08
topic: claude-obsidianセットアップ＋第二の脳構築＋自動保存設定
tags: [source, obsidian, claude-code, setup]
created: 2026-05-08
updated: 2026-05-08
---

# claude-obsidian セットアップ記録（2026-05-08）

TwitterでバズっていたObsidian × Claude Code連携ツール「[[claude-obsidian]]」を発見し、セットアップから[[Second Brain]]の初期構造構築、さらに[[Claude Code]]が自動でObsidianへの保存を提案する仕組みまで一気に実装した会話の記録。

## 実施内容

### インストール
- `~/claude-obsidian-vault` にGitHubからclone
- `bash bin/setup-vault.sh` でExcalidraw自動ダウンロード含め設定完了
- ObsidianでVaultとして開き、コミュニティプラグインを有効化

### Vault構造（[[Mode D Personal Second Brain]]）
```
wiki/goals / learning / people / areas / resources
wiki/North Star / Annual Goals / Weekly Review Template
.raw/   ← ソース投入フォルダ
_templates/goal / learning / person / resource
```

### 自動保存の仕組み（[[Claude Code Hooks]]）
- `~/.claude/CLAUDE.md`：全セッションで有効。タスク完了後に「📝 Obsidianに保存しますか？」と自動提示
- `~/.claude/commands/obsidian-save.md`：`/obsidian-save` コマンドで会話要約→wiki-ingest

## 参照リソース
- GitHub: [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
- 元ネタ: @defileo のX投稿（99万ビュー）、[[LLM Wiki Pattern]]（[[Andrej Karpathy]]提唱）
