---
type: entity
title: "Claudian (YishenTu/claudian)"
aliases: ["Claudian-YishenTu", "YishenTu/claudian"]
created: 2026-04-08
updated: 2026-04-08
tags:
  - github-repo
  - native-obsidian-plugin
  - embedded-ai
status: current
related:
  - "[[cherry-picks]]"
  - "[[claude-obsidian-ecosystem]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# Claudian (YishenTu/claudian)

**種別**: Obsidianネイティブプラグイン(TypeScript製、Claude Code/Codexを内蔵)
**URL**: https://github.com/YishenTu/claudian
**インストール**: BRATまたは手動(コミュニティストアには未掲載)

## 概要

Claude Code(またはCodex CLI)をObsidian内のサイドバーチャットとして直接埋め込む。ボールトがそのままエージェントの作業ディレクトリとなり、Claude CodeのすべてのツールがそのままネイティブにObsidian内で動作する。

## 主な機能

### 単語単位の差分付きインライン編集
ノート内のテキストを選択してホットキーを押すと、Claudeが単語単位の差分プレビュー付きで編集案を提示し、ワンクリックで適用できる。Obsidian AIエコシステムにおいて最も完成度の高いインライン編集である。

### プランモード(Shift+Tab)
実装に着手する前にエージェントが探索と設計を行う。ファイルを変更する前に承認用のプランを提示する。Claude Code本体のプランモードを反映している。

### @メンションシステム
`@` を入力すると以下を参照できる:
- ボールト内のファイル
- サブエージェント
- MCPサーバー
- 外部ディレクトリのファイル(ボールト外)

### 指示モード(#)
チャット入力から直接、洗練されたカスタム指示を追加できる。セッション中は永続化される。

### MCPサーバー連携
stdio、SSE、HTTPで外部ツールを接続する。Claudeはアプリ内でボールトのMCPを管理し、CodexはCLIで管理される設定を使う。

### マルチタブ会話
複数のチャットタブ、会話履歴、フォーク、再開、コンパクトモードに対応。

## プライバシー
- テレメトリなし
- 設定は `vault/.claudian/` に保存
- Claudeのファイルは `vault/.claude/` に配置
- トランスクリプトは `~/.claude/projects/` に保存

## claude-obsidianへの関連性
Claudianはネイティブプラグインであり別カテゴリだが、そのプランモード、@メンション、インライン編集の各パターンはclaude-obsidianスキルの新機能、特にcanvasやwiki-queryワークフローのインスピレーションとなり得る。
