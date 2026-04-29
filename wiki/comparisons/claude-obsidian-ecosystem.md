---
type: comparison
title: "Claude + Obsidian エコシステム: 機能マトリクス"
aliases: ["claude-obsidian-ecosystem", "Claude + Obsidian エコシステム"]
created: 2026-04-08
updated: 2026-04-08
tags:
  - ecosystem
  - competitive-analysis
  - claude-obsidian
  - cherry-picks
status: current
related:
  - "[[cherry-picks]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Andrej Karpathy]]"
sources:
  - "[[claude-obsidian-ecosystem-research]]"
---

# Claude + Obsidian エコシステム: 機能マトリクス

> 調査日: 2026-04-08 | 16以上のプロジェクトを分析 | アクションアイテムは [[cherry-picks]] を参照

---

## 凡例
- ✅ 実装済み
- ❌ 未実装
- 🟡 部分対応
- ⭐ ベストインクラスの実装

---

## LLM Wikiパターン系プロジェクト(Claude Codeスキル)

| 機能 | claude-obsidian | claudesidian | llm-knowledge-bases | llm-wiki | obsidian-wiki | obsidian-claude-pkm |
|---------|:-:|:-:|:-:|:-:|:-:|:-:|
| /wiki セットアップとスキャフォールド | ✅ | 🟡 `/init-bootstrap` | 🟡 `/kb-init` | ✅ | ✅ setup.sh | 🟡 `/onboard` |
| ソース取り込み | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| ウィキクエリ | ✅ | ❌ | ✅ 3段階 | 🟡 | ✅ | ❌ |
| ウィキlint | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| /save 会話保存 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| autoresearch ループ | ✅ | ❌ | 🟡 | ❌ | ❌ | ❌ |
| Canvas / ビジュアルレイヤー | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| ホットキャッシュ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **デルタ追跡** | ❌ | ❌ | ❌ | ❌ | ✅⭐ | ❌ |
| **多段階クエリ** | ❌ | ❌ | ✅⭐ | ❌ | ❌ | ❌ |
| **URL取り込み** | ❌ | 🟡 firecrawl | ❌ | ✅ | ✅ | ❌ |
| **ビジョン / 画像取り込み** | ❌ | 🟡 gemini | ❌ | ❌ | ✅⭐ | ❌ |
| **自動コミットフック** | ❌ | ❌ | ❌ | ✅ git | ❌ | ✅⭐ |
| **Marp / スライド出力** | ❌ | ❌ | ✅⭐ | ✅ | ❌ | ❌ |
| **チャート出力** | ❌ | ❌ | ✅ matplotlib | ❌ | ❌ | ❌ |
| **ハイブリッド検索 (BM25+vec)** | ❌ | ❌ | ❌ | ✅⭐ qmd | ❌ | ❌ |
| **ゴールカスケード(PKM)** | ❌ | 🟡 PARA | ❌ | ❌ | ❌ | ✅⭐ |
| **デイリー/ウィークリーレビュー** | ❌ | 🟡 | ❌ | ❌ | ❌ | ✅⭐ |
| **既存ボールトの取り込み** | ❌ | ✅⭐ | ❌ | ❌ | ❌ | ✅⭐ |
| **マルチエージェント互換** | ❌ | ❌ | ❌ | ❌ | ✅⭐ | ❌ |
| **X/Twitter 取り込み** | ❌ | ❌ | ✅⭐ smaug | ❌ | ❌ | ❌ |
| マーケットプレイス導入 | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| 公開リポジトリ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Obsidianネイティブプラグイン(UI埋め込み型)

| 機能 | Claudian | Nexus (claudesidian-mcp) | infio-copilot |
|---------|:-:|:-:|:-:|
| Obsidian内サイドバーチャット | ✅ | ✅ | ✅ |
| 差分付きインライン編集 | ✅⭐ 単語単位 | ✅ | ✅ |
| プランモード | ✅⭐ Shift+Tab | ❌ | ❌ |
| ファイル/エージェント @メンション | ✅⭐ | ❌ | 🟡 |
| MCPサーバー対応 | ✅ | ✅⭐ 外部 | ❌ |
| マルチタブ会話 | ✅ | ❌ | ❌ |
| ワークスペースメモリ | ❌ | ✅⭐ JSONL | ✅ workspaces |
| タスク管理 | ❌ | ✅⭐ | ❌ |
| セマンティック検索 | ❌ | ✅ | ✅⭐ ローカル埋め込み |
| PDF → Markdown | ❌ | ✅ | ❌ |
| Webページキャプチャ | ❌ | ✅ | ❌ |
| モバイル対応 | ❌ | ✅⭐ | ❌ |
| Obsidian Sync互換 | N/A | ✅⭐ | N/A |
| スター数/人気度 | 約200(推定) | 約800(推定) | 約300(推定) |

---

## MCPサーバー

| サーバー | 主な差別化要素 | 必要環境 |
|--------|-------------------|----------|
| obsidian-mcp-tools | Templater実行 + SLSAアテステーション | Local REST API + Smart Connections |
| obsidian-memory-mcp | グラフビュー上のMarkdownとしてのAI記憶 | Node 18+ |
| obsidian-claude-code-mcp | WebSocket、ボールト自動検出 | Claude Code |
| administrativetrick/obsidian-mcp | 最小限、シンプル | Claude Desktop |
| MarkusPfundstein/mcp-obsidian | REST API経由 | Local REST API |

---

## kepano/obsidian-skills(特別枠 — Obsidian作者によるリポジトリ)

Linus Kepano(Obsidian作者 + Minimalテーマ作者)が公式のAgent Skillsを公開:

| スキル | 教える内容 |
|-------|----------------|
| obsidian-markdown | Obsidian Flavored Markdown(コールアウト、埋め込み、ウィキリンク、プロパティ) |
| obsidian-bases | Obsidian Bases(.baseファイル、ビュー、フィルタ、フォーミュラ) |
| json-canvas | JSON Canvas仕様(.canvas のノード/エッジ/グループ) |
| obsidian-cli | Obsidian CLIによるボールト管理 |
| defuddle | Webページからクリーンなマークダウンを抽出(トークン節約) |

> **重要なシグナル**: このプロジェクトはAgent Skillsフォーマットが正しい標準であることを裏付ける。
> これらのスキルはプラットフォーム非依存である(Claude Code、Codex、OpenCode)。

---

## 人気スナップショット(従来型プラグイン)

| プラグイン | スター数 | アプローチ |
|--------|-------|---------|
| obsidian-copilot | 5,776 | マルチプロバイダ対応のボールトチャット |
| obsidian-smart-connections | 4,357 | セマンティック検索 + 埋め込み |
| obsidian-textgenerator-plugin | 1,837 | テキスト生成 |
| chatgpt-md | 1,229 | Markdown内でのチャット |
| obsidian-local-gpt | 569 | ローカルLLM |
| obsidian-ai-tools | 272 | Supabase + OpenAIによるセマンティック検索 |

---

## claude-obsidianが優れている点

1. **ホットキャッシュ** — セッションコンテキストの仕組みはエコシステム内で唯一無二
2. **Canvasスキル** — ビジュアルレイヤーを持つLLM Wikiプロジェクトは他にない
3. **マーケットプレイス導入** — 最も洗練されたインストール体験
4. **/save 会話保存** — チャットセッションをウィキページとしてファイリングする機能は唯一無二
5. **ドキュメント品質** — README、インストールガイド、デモGIF
6. **デュアルリポジトリ**(public + community) — 配布モデルが独自

## claude-obsidianのギャップ

実装ノート付きの優先順位リストは [[cherry-picks]] を参照。

影響度の高いギャップ上位5つ:
1. デルタ追跡なし → コンパイルのたびに全件再取り込み
2. URL取り込みなし → 手動コピー&ペーストを強制
3. 自動コミットなし → ボールトの変更が自動的にバージョン管理されない
4. 多段階クエリなし → どんな質問にも単一モードで対応
5. ビジョン入力なし → スクリーンショットや画像を取り込めない
