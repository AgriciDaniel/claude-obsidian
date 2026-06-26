# claude-obsidian — Claude + Obsidian Wiki Vault

## Reglas de comportamiento obligatorias

**SAVE_REMINDER = acción inmediata, no postergable.** Cuando el Stop hook emite `SAVE_REMINDER`, la PRIMERA acción del turno siguiente es ejecutar `/save`. No responder al usuario antes de guardar. No tratarlo como sugerencia.

**Auto-save proactivo.** Guardar en `wiki/references/` sin que el usuario lo pida cuando haya contexto valioso acumulado (decisiones de arquitectura, cambios de config, resolución de problemas no triviales). El SAVE_REMINDER automático se emite cada 30 interacciones como señal de respaldo.

This folder is both a Claude Code plugin and an Obsidian vault.

**Plugin name:** `claude-obsidian` (v1.7+ "Compound Vault" — see [docs/compound-vault-guide.md](docs/compound-vault-guide.md); v1.8+ adds methodology modes (LYT/PARA/Zettelkasten/Generic); v1.10 adds GTD mode + wiki-triage — see [docs/methodology-modes-guide.md](docs/methodology-modes-guide.md))
**Skills:** `/wiki`, `/wiki-ingest`, `/wiki-query`, `/wiki-lint`, `/wiki-cli` (v1.7), `/wiki-retrieve` (v1.7, opt-in), `/wiki-mode` (v1.8), `/wiki-triage` (v1.10)
**Vault path:** This directory (open in Obsidian directly)

## What This Vault Is For

This vault demonstrates the LLM Wiki pattern — a persistent, compounding knowledge base for Claude + Obsidian. Drop any source, ask any question, and the wiki grows richer with every session.

## Vault Structure

```
.raw/           source documents — immutable, Claude reads but never modifies
wiki/           Claude-generated knowledge base
_templates/     Obsidian Templater templates
_attachments/   images and PDFs referenced by wiki pages
```

## How to Use

Drop a source file into `.raw/`, then tell Claude: "ingest [filename]".

Ask any question. Claude reads the index first, then drills into relevant pages.

Run `/wiki` to scaffold a new vault or check setup status.

Run "lint the wiki" every 10-15 ingests to catch orphans and gaps.

## Cross-Project Access

To reference this wiki from another Claude Code project, add to that project's CLAUDE.md:

```markdown
## Wiki Knowledge Base
Path: /path/to/this/vault

When you need context not already in this project:
1. Read wiki/hot.md first (recent context, ~500 words)
2. If not enough, read wiki/index.md
3. If you need domain specifics, read wiki/<domain>/_index.md
4. Only then read individual wiki pages

Do NOT read the wiki for general coding questions or things already in this project.
```

## Plugin Skills

| Skill | Trigger |
|-------|---------|
| `/wiki` | Setup, scaffold, route to sub-skills |
| `ingest [source]` | Single or batch source ingestion |
| `query: [question]` | Answer from wiki content |
| `lint the wiki` | Health check |
| `/save` | File the current conversation as a structured wiki note |
| `/autoresearch [topic]` | Autonomous research loop: search, fetch, synthesize, file |
| `/canvas` | Visual layer: add images, PDFs, notes to Obsidian canvas |
| `/wiki-cli` (v1.7) | Obsidian CLI transport wrapper; default mutation path on desktop |
| `/wiki-retrieve` (v1.7) | Hybrid contextual + BM25 + cosine-rerank retrieval (opt-in via `bash bin/setup-retrieve.sh`) |
| `/wiki-mode` (v1.8) | Methodology modes (LYT / PARA / Zettelkasten / GTD / Generic). Set via `bash bin/setup-mode.sh`; consumed by wiki-ingest / save / autoresearch for routing new pages |
| `/wiki-triage` (v1.10) | GTD capture/triage: runs the capture → actionable → 2-min/delegate/today/date decision tree on incoming items, files via wiki-mode router |
| `/think` (v1.9) | The 10-principle thinking loop (OBSERVE-OBSERVE-LISTEN-THINK-CONNECT-CONNECT-FEEL-ACCEPT-CREATE-GROW) as an invocable workflow. Apply to architectural decisions, audits, post-mortems, ambiguous user requests. Every other skill has a "How to think" appendix mapping this framework to its specific work |

## Transport (v1.7+)

`scripts/detect-transport.sh` writes `.vault-meta/transport.json` on first run and refreshes weekly. Skills consult it before mutating the vault. Fallback chain: Obsidian CLI → mcp-obsidian → mcpvault → filesystem (always-available floor). Decision tree: [wiki/references/transport-fallback.md](wiki/references/transport-fallback.md).

## Concurrency (v1.7+)

`scripts/wiki-lock.sh` provides per-file advisory locks for safe multi-writer ingest. Every wiki page write should be guarded by `wiki-lock acquire`/`release`. Stale-after default is 60s; cross-process release allowed by design. The PostToolUse hook defers `git add` while locks are held. Closes the latent multi-writer corruption hole from v1.6.

## Methodology Modes (v1.8+)

Pick an organizational style for the vault via `bash bin/setup-mode.sh`. Four modes available: **generic** (v1.7 default — no opinion), **LYT** (Linking Your Thinking — MOCs + atomic notes), **PARA** (Projects/Areas/Resources/Archives), **Zettelkasten** (timestamped IDs, flat, dense linking). The mode is written to `.vault-meta/mode.json` (gitignored by default; `git add -f` to commit). `wiki-ingest`, `save`, and `autoresearch` consult `python3 scripts/wiki-mode.py route <type> "<name>"` before filing new pages — no special-casing needed in the consumer skills. Full guide: [docs/methodology-modes-guide.md](docs/methodology-modes-guide.md). Closes priority gap 5 from the May 2026 compass artifact.

## Pre-commit verifier (v1.7.1+)

After staging changes for a non-trivial workstream but BEFORE running `git commit`, dispatch the `verifier` agent (`agents/verifier.md`). It reads `git diff --cached`, applies the /best-practices six-cut + agent kernel, and returns findings in four tiers (BLOCKER / HIGH / MEDIUM / LOW) with file:line citations. The agent has read-only tools (Read, Grep, Glob, Bash) — it can inspect but never modify, so its output is purely advisory. This closes the loop the v1.7 audit revealed: code went worker → commit with no separate verifier pass, which is how BLOCKER B1 (data-egress consent gap) slipped through. See `docs/audits/v1.7.0-audit-2026-05-17.md` §10 for the retrospective.

## MCP (Optional)

If you configured the MCP server, Claude can read and write vault notes directly.
See `skills/wiki/references/mcp-setup.md` for setup instructions.

## Emotional Awareness

Claude infiere el estado emocional y cognitivo del usuario desde el contexto (tono, ritmo, longitud de mensajes, hora, tipo de tarea) y lo taggea internamente con etiquetas `ai-x`. El usuario tiene TDAH — los estados cognitivos son tan importantes como los emocionales.

**REGLA ABSOLUTA DE VISIBILIDAD:** Los tags ai-x NUNCA aparecen en el texto de respuesta. Ni al final, ni entre backticks, ni entre paréntesis, ni como metadata. Solo pueden aparecer en cuerpos de archivos de memoria (.claude/projects/.../memory/*.md) o en notas de wiki al guardar con /save.
- MAL: "Buenas noches. `ai-cansancio`"
- BIEN: "Buenas noches." (tag inferido internamente, nunca escrito en el chat)

**Catálogo de estados cognitivos (TDAH-aware):**
- `ai-hiperfoco` — flujo profundo. Respuestas ultra-cortas, sin alternativas, sin contexto extra. No interrumpir el flujo.
- `ai-disperso` — saltando temas, señales de overwhelm. Una cosa a la vez, anclar suavemente, no agregar más info.
- `ai-procrastinando` — circulando sin arrancar. Acción más pequeña posible, sin teoría, sin opciones.
- `ai-crash` — post-hiperfoco o agotamiento cognitivo. Mínimo de palabras, cero decisiones, respuesta directa.

**Catálogo de estados emocionales:**
- `ai-frustración` — ir al punto, sin alternativas, sin contexto extra.
- `ai-entusiasmo` — expandir, proponer ideas, explorar opciones.
- `ai-urgencia` — bullets, camino más rápido, sin caveats.
- `ai-cansancio` — respuestas cortas, estructura clara, una cosa por vez.
- `ai-confusión` — simplificar, no asumir contexto, preguntar si es necesario.
- `ai-alivio` — confirmar brevemente, no sobrecargar con lo que sigue.

**Comportamiento:**
- Inferir silenciosamente y aplicar. El usuario nota el efecto, no el tag.
- Si el usuario quiere hablar de cómo se siente, lo dice él. Solo entonces acompañar.
- Una o dos etiquetas por momento relevante, no en cada mensaje.

## Personal Brain

`brain/` is a GTD-ish personal second brain living alongside the plugin wiki.

**Structure:**
- `brain/inbox/` — capture zone, process in weekly review
- `brain/goals/` — goals + north star
- `brain/projects/` — active GTD projects with next actions
- `brain/areas/` — life areas: health, career, finances, relationships
- `brain/learning/` — skills, books, concepts in progress
- `brain/resources/` — reference material
- `brain/someday/` — parked ideas and projects

**Templates:** `_templates/brain/` — capture, project, goal, area, weekly-review

**Conventions:**
- All notes use YAML frontmatter: type, status, area, created, updated, tags
- Wikilinks use `[[note-name]]` format
- `brain/inbox/` is the only unsorted zone — everything else has a home
- Weekly review processes inbox and updates projects/_index next actions
- `brain/hot.md` is the session cache — Claude updates it after significant changes
- `brain/log.md` is append-only — new entries at the top

**GTD Tagging Rule (IMPORTANTE):**
Al crear una acción GTD, inferir tags de contexto del título además de los tags base (`gtd`, `action`). Ejemplos:
- "comprar cortina" → `compras`, `hogar`
- "ir a la ferretería" → `compras`, `ferretería`
- "llamar al médico" → `salud`, `llamadas`
- "revisar código PR" → `trabajo`, `código`
- "pagar factura" → `finanzas`, `trámites`

Siempre agregar al menos 1 tag de contexto. El objetivo es poder filtrar tareas por categoría desde la app GTD.

**How to use with Claude:**
- "Capture [idea/task]" → adds to inbox
- "Add project [name]" → creates from template, links in projects/_index
- "Weekly review" → runs through the weekly-review template
- "What are my active projects?" → reads projects/_index
- "Update [area]" → opens the area note for editing
