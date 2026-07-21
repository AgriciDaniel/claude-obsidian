#!/usr/bin/env bash
# ============================================================
# setup-mind-os.sh — Mind-OS on claude-obsidian 一键初始化
#
# 幂等运行：已存在的目录/文件自动跳过。
# 在 vault 根目录下运行： cd /Users/ggsk/obsidian && bash bin/setup-mind-os.sh
# ============================================================
set -euo pipefail

# --- Resolve vault root ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MINDBASE="$VAULT_ROOT"

echo "🔧 Mind-OS Setup"
echo "   Vault root: $VAULT_ROOT"
echo ""

# === Helper ===
create_dir() {
  if [ -d "$1" ]; then
    echo "   ✓ exists: $1"
  else
    mkdir -p "$1"
    echo "   ✚ created: $1"
  fi
}

write_file() {
  local path="$1"
  if [ -f "$path" ]; then
    echo "   ✓ exists: $path"
    return 0
  fi
  # Read content from stdin
  cat > "$path"
  echo "   ✚ written: $path"
}

# ============================================================
# 1. Create directories
# ============================================================
echo "━━━ Directories ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

create_dir "$MINDBASE/journals"
create_dir "$MINDBASE/wiki/insights"
create_dir "$MINDBASE/wiki/books"
create_dir "$MINDBASE/_templates"
create_dir "$MINDBASE/bin"
create_dir "$MINDBASE/docs"

# ============================================================
# 2. Write wiki/insights/README.md
# ============================================================
echo "━━━ wiki/insights/README.md ━━━━━━━━━━━━━━━━━━━━━━━━"

write_file "$MINDBASE/wiki/insights/README.md" << 'README'
# wiki/insights/ — 人类知识层

**规则：此目录是人为判断的独占空间。**
LLM 可以读取和引用，但绝不可以创建、修改或删除此目录中的任何文件。

**为什么：** 有些知识不是事实，而是判断。AI 的角色是帮助捕捉和综合，
而不是取代人类的价值判断。

**使用方法：** 在这里写下任何笔记、反思、直觉或综合，
无需遵循 frontmatter 约束。这是仓库中你的自由书写空间。
README

# ============================================================
# 3. Write wiki/books/density-tracker.md
# ============================================================
echo "━━━ wiki/books/density-tracker.md ━━━━━━━━━━━━━━━━━━"

write_file "$MINDBASE/wiki/books/density-tracker.md" << 'DENSITY'
---
type: meta
domain: meta
title: "共现密度追踪"
updated: 2026-07-21
tags:
  - ember
  - nexus
  - density-tracking
---

# 共现密度追踪

## 协议
- 每次 Ember 处理 #ember/xxx 或 #book 段落时，检查是否涉及已有概念对
- 有意义共现：两个概念之间"能互相回答、互相佐证、或一个是另一个的反例"
  的语义级咬合
- count ≥ threshold（默认 5）时触发委托

## 追踪表

| 概念 A | 概念 B | 来源 | count | threshold | 状态 |
|--------|--------|------|-------|-----------|------|
| -      | -      | -    | -     | 5         | 等待 |
DENSITY

# ============================================================
# 4. Write wiki/concepts/tech-radar.md
# ============================================================
echo "━━━ wiki/concepts/tech-radar.md ━━━━━━━━━━━━━━━━━━━━"

write_file "$MINDBASE/wiki/concepts/tech-radar.md" << 'RADAR'
---
type: concept
domain: meta
complexity: basic
title: "Tech Radar"
created: 2026-07-21
updated: 2026-07-21
tags:
  - tech-radar
  - signal-grading
  - meta
status: seed
related: []
sources: []
---

# Tech Radar

## 分级规则

| 分级 | 含义 | 升降级规则 |
|------|------|------------|
| 🔴 爆发期 | 需要立即关注的热门信号 | 活跃期 > X 天无更新 → 降级至🟡 |
| 🟡 观察期 | 值得关注但非优先 | N 天无更新 → 降级至🟢 |
| 🟢 记录 | 记录在案，留作参考 | 无新信号 > 2 周 → 移至归档 |
| ⚫ 消退 | 不再活跃或已过时 | 从🟢或🟡降级后转入 |

## 当前信号 (2026-07)

### 🔴 爆发期

*（当前为空）*

### 🟡 观察期

*（当前为空）*

### 🟢 记录

*（当前为空）*

## 已编译归档

*已编译为 wiki 页面的信号在此列出。*

## 消退归档

*已消退的信号在此列出。*
RADAR

# ============================================================
# 5. Summary
# ============================================================
echo ""
echo "━━━ Complete ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Mind-OS Phase 0 基础设施已就绪。"
echo ""
echo "   接下来："
echo "   1. 修改 CLAUDE.md 追加宪法规则"
echo "   2. 新建 AGENTS.md 代理发现文件"
echo "   3. 新建 schema.md 结构约定文件"
echo "   4. 新建 _templates/book-template.md"
echo "   5. 新建 _templates/daily-journal.md"
echo "   6. 在 .claude/skills/ 下新建 skill"
echo "   7. 在 .claude/agents/ 下新建 5 个蒸馏 agent"
echo ""
