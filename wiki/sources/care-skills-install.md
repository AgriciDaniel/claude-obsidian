---
source: claude-conversation
date: 2026-05-11
topic: テンダーヒルズ向け特養スキル3種のClaude Codeインストール
type: source
tags: [care-facility, claude-code, skills, tender-hills]
raw: .raw/2026-05-11-care-skills-install.md
---

# 特養スキル3種 Claude Codeインストール

## 概要

テンダーヒルズ（秋田県大仙市）向けに作成された3つのSKILL.mdをGoogleドライブから発見し、`~/.claude/skills/` へインストールした会話記録。

**ソースフォルダ**: `GoogleDrive/マイドライブ/022_利用者フェースシート/進藤榮子/`

---

## インストールしたスキル

| スキル名 | 用途 |
|---|---|
| [[care-user-info-excel]] | 複数資料から利用者基本情報Excelを入力・確認リスト付きで整備 |
| [[admission-script]] | 入所調整委員会の司会者読み上げ台本(.docx)を生成 |
| [[admission-assessment]] | 入所判定資料（7セクション・カラーテーブル）を生成 |

---

## 関連概念

- [[テンダーヒルズ特養スキル群]] — 施設固有のClaude Codeスキルセット
- [[Claude Code Skills]] — スキルシステム全般

---

## インストール手順

```bash
mkdir -p ~/.claude/skills/{care-user-info-excel,admission-script,admission-assessment}
cp "$GDRIVE/care-user-info-excel/SKILL.md" ~/.claude/skills/care-user-info-excel/SKILL.md
cp "$GDRIVE/admission-script/SKILL.md"     ~/.claude/skills/admission-script/SKILL.md
cp "$GDRIVE/SKILL.md"                      ~/.claude/skills/admission-assessment/SKILL.md
```
