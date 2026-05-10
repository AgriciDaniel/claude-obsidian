---
type: concept
title: "claude-obsidian"
status: mature
tags: [concept, tool, obsidian, claude-code]
created: 2026-05-08
updated: 2026-05-08
---

# claude-obsidian

Claude Code × Obsidian を連携して「自動成長するWiki Vault（[[Second Brain]]）」を構築するオープンソースツール。[[LLM Wiki Pattern]]（[[Andrej Karpathy]]提唱）を実装したもの。

- GitHub: [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)
- ライセンス: MIT
- 対応モデル: Claude / Gemini / Codex / Cursor / Windsurf

## 仕組み

```
.raw/      ← 投入したソースを変更しない（不変）
wiki/      ← LLMが生成するナレッジベース
CLAUDE.md  ← スキーマと指示（このプラグイン）
```

セッション間のコンテキストは `wiki/hot.md`（ホットキャッシュ）で保持。`wiki/index.md` がマスターカタログ。

## コアコマンド

| コマンド | 機能 |
|---|---|
| `/wiki` | Vault初期化・スキャフォールド |
| `ingest [file]` | ソースをWiki化 |
| `/save` | 会話をWikiノートに保存 |
| `/autoresearch [topic]` | 自律リサーチループ |
| `/canvas` | ビジュアルナレッジマップ生成 |
| `lint the wiki` | ヘルスチェック |

## セットアップ方法

```bash
git clone https://github.com/AgriciDaniel/claude-obsidian ~/claude-obsidian-vault
cd ~/claude-obsidian-vault
bash bin/setup-vault.sh
# → ObsidianでVaultとして開く
```

## 関連
- [[LLM Wiki Pattern]]
- [[Second Brain]]
- [[Hot Cache]]
- [[Mode D Personal Second Brain]]
