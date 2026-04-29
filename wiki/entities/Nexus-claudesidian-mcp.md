---
type: entity
title: "Nexus (ProfSynapse/claudesidian-mcp)"
aliases: ["Nexus-claudesidian-mcp", "ProfSynapse/claudesidian-mcp"]
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - obsidian-plugin
  - mcp-server
  - native-plugin
status: current
related:
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# Nexus(旧 Claudesidian MCP)

**種別**: Obsidianネイティブプラグイン + MCPブリッジ
**URL**: https://github.com/ProfSynapse/claudesidian-mcp
**現在の名称**: Nexus MCP for Obsidian
**インストール**: `.obsidian/plugins/nexus/`

## 概要

2つのモードを備えるObsidianのフルプラグイン:
1. **Obsidian内ネイティブチャット** — 任意のAIプロバイダに接続
2. **MCPブリッジ** — Claude Desktop、Claude Code、Codex CLI、Gemini CLI、Cursor、Clineにボールトを公開

## 主な機能

- **ワークスペースメモリ** — セッションをまたいで永続化されるコンテキストをJSONLとして保存し、Obsidian Syncに自動的に含まれる
- **タスク管理** — プロジェクト、タスク、ブロッカー、依存関係をボールト内で追跡
- **セマンティック検索** — 意味ベースでノートと過去の会話を検索
- **インライン編集** — ノート内で選択したテキストを編集
- **PDF + 音声 → Markdown** — 右クリックまたは追加時の自動変換
- **Webページキャプチャ** — ObsidianでURLを開き、Markdown/PNG/PDFとして保存
- **モバイル対応** — ネイティブチャットがiOS/Androidで動作
- **2ツールアーキテクチャ** — 読み取りと書き込みアクションに専用ツールを用意

## ストレージ構成

データは `.obsidian/plugins/nexus/data/` 内のJSONLファイルとして保存される。これはv1の `.nexus/` フォルダと異なり、Obsidian Syncに自動的に含まれる。SQLiteキャッシュはローカル専用で、各デバイスでJSONLから再構築される。

## claude-obsidianへの関連性

Nexusは別カテゴリ、すなわちClaude Codeスキルプラグインではなく、TypeScript製のObsidianネイティブプラグインに属する。両者は直接競合しないが、ワークスペースメモリやタスク管理のパターンはチェリーピックの対象となる。

## claude-obsidianへのチェリーピック

- [[cherry-picks#11. obsidian-memory-mcp Integration]](実装は異なるが概念は同じ)
