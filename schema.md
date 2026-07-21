# Mind-OS Schema: Structural Conventions

> This file defines extension conventions on top of claude-obsidian's WIKI.md schema.
> See `~/.claude/obsidian-toolkit/WIKI.md` for the base schema.

## Directory Conventions

### journals/
- Flat directory at vault root (no subdirectories).
- Filename format: `YYYY-MM-DD.md`.
- Each file is one day's notes.
- Frontmatter: `type: journal`, `date: YYYY-MM-DD`, `mood:` (optional).
- Agent tags: `#lumina`, `#prism`, `#vector`, `#nexus`, `#ember` at paragraph end.

### wiki/insights/
- **HUMAN ONLY**: LLM reads, never writes. This is a physical layer constraint.
- No frontmatter requirement — humans write freely.
- Structure: one insight per file, or thematic clusters.
- LLM may reference and quote insights/ in answers, but must never create or modify files here.

### wiki/books/
- One file per book. Filename: `Title Case.md`.
- Frontmatter: `domain: reading`, `status: to-read|reading|done`, `rating: star-rating`.
- Body structure: RIA (Reading / Interpretation / Appropriation).
- The A section MUST be a triple: `verb + completion-criterion + deadline`.

### wiki/concepts/tech-radar.md
- Single file, not a directory.
- Signal grading sections: RED / YELLOW / GREEN / BLACK.
- Each signal entry MUST end with `最新信号: YYYY-MM-DD`.
- Archives: "已编译归档" and "消退归档" sections.

## Distillation Protocol

1. Human writes in journals/ file, appends agent tag to paragraph.
2. Human invokes `/distill <file>`.
3. Distill skill reads file, extracts tagged paragraphs, routes to corresponding agent.
4. Agent responds with Obsidian Callout appended below the tagged paragraph.
5. Agent NEVER modifies the original paragraph text.
6. Ember additionally updates wiki/books/density-tracker.md.

## Book Note RIA Constraint

- **R** (Reading): Direct quotes or screenshots. What the book said.
- **I** (Interpretation): Your own restatement. Why it hits you. Connection to existing knowledge.
- **A** (Appropriation): Actionable commitment. MUST contain: verb + measurable criterion + deadline.
- Ember agent rejects I or A segments that are perfunctory.

## Insights/ Layer Rationale

This layer exists because some knowledge is not fact but judgment. The LLM's role
is to facilitate capture and synthesis — not to replace the human's value judgment.
The physical directory boundary enforces this separation.

---

## Sentinel Mode (Deferred Design)

设计于 2026-07-21，尚未实现。记录在此以免遗忘。

### 问题
定时采集模式（Phase 3 原设计）会引入信息波动——同一个概念随舆论周期
在 A/B 之间摇摆，导致 wiki 知识不稳定。

### 方案：哨兵模式（代替定时采集）
Collector 仍然定时抓取信号，但不自动写入 `.raw/`，而是走矛盾检测：

1. Fetch → 解析 → 与 wiki 已有概念比对（Prism 矛盾检测）
2. 无矛盾 → 安静丢弃，不留痕迹
3. 有矛盾或重大新信号 → 通知人类 + 写入 tech-radar 🔴
4. 人类决定是否 ingest

### 开关设计
```json
{
  "collectors": {
    "aihot": {
      "enabled": false,
      "mode": "guard",
      "alert_on": ["contradiction", "novelty"],
      "interval_minutes": 1440
    }
  }
}
```

### 依赖
- 需要 Phase 2 distill Prism 镜头的矛盾检测能力
- 需要 wiki 概念页积累到足够密度才有检测意义
- 预计文章 > 50 篇时值得实现
