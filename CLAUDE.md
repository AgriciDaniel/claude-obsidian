# claude-obsidian — Claude + Obsidian Wiki Vault

This folder is both a Claude Code plugin and an Obsidian vault.

**Plugin name:** `claude-obsidian`
**Skills:** `/wiki`, `/wiki-ingest`, `/wiki-query`, `/wiki-lint`
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

## MCP (Optional)

If you configured the MCP server, Claude can read and write vault notes directly.
See `skills/wiki/references/mcp-setup.md` for setup instructions.

---

## Jakob's Instruction Style Preference

When giving instructions, walkthroughs, or technical guidance, format them like this:

- **Sektioner separerade med `---` horisontella linjer** — gör det lätt att skanna.
- **Tabeller** för strukturerad info (vad sparas var, jämförelse, daglig workflow). Två-tre kolumner, läsbara på en blick.
- **Numrerade steg-för-steg** för konkreta handlingar. Inte sammanhängande prosa.
- **Förklara både "vad det betyder" och "vad du gör"** — inte bara teori. Inte bara kommandon.
- **Var ärlig om begränsningar.** "Det här fungerar inte än", "han kommer inte ihåg mellan sessioner" osv. Inte gömma kompromisser.
- **Avsluta med konkreta nästa-steg.** "Tre saker du kan göra direkt" eller motsvarande. Användaren ska veta exakt vad de tar tag i härnäst.
- **Skriv på svenska** som primärt språk. Blanda in engelska tekniska termer naturligt (Python, API, GPU, ESP32 — översätt inte sådana).
- **Lätt visuell formatering** för skanbarhet. Fet text på nyckelord, inline-`code` för kommandon, blockcitat för viktiga varningar.
- **3–5 punkter per sektion**, inte uttömmande listor. Om en sektion blir för lång, dela upp den.
- **Leverera konkreta filer / scripts / .bat-launchers** när det är relevant — inte bara dokumentation. Om det är möjligt att göra en dubbelklicks-fil, gör det.
- **Inga em-dashes** (U+2014). Använd punkt, komma, kolon, parenteser, eller bindestreck i sammansatta ord.
- **Använd konkreta exempel och vardagliga analogier** när du förklarar nya koncept. Jakob är ny på programmering, elektronik, och delar av färgteknik. Säg inte bara "linearization kompenserar för icke-linjär ink-respons" — säg också "tänk dig att du och en kompis har en burk färg som du säger ska räcka till 50% täckning, men kompisen lägger faktiskt på 35%. Linearization är som att kalibrera om kompisens öga." Definiera tekniska termer första gången de dyker upp. Visa "före" och "efter" där det är möjligt. Använd specifika siffror och menyvägar, inte vaga "ändra värdet". Antag inte förkunskap.

Den här stilen sparades 2026-05-03 efter en walkthrough av Ollama + Jarvis-installationen och utbyggdes 2026-05-03 efter Onyx-färg-frågor där Jakob bad om mer konkreta exempel. Använd som default för all instruktions-leverans till honom.
