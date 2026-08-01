# Install claude-obsidian

claude-obsidian has two independent parts:

1. the product package—skills, portable core, Claude adapter, and templates;
2. a user-owned Obsidian vault containing mutable knowledge.

Do not use an installed plugin cache as the vault. A source clone is suitable
for development, but a normal user vault should be a separate directory.

## Requirements

- Python 3.11 or newer
- an Agent Skills compatible host, or Claude Code for the plugin adapter
- Obsidian when you want its visual editor
- Bash for installer and optional legacy-extension scripts
- Git only for source development, release builds, or explicit checkpoints

## Claude Code marketplace

Add the artifact-clean public catalog and install the namespaced plugin:

```bash
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian@agricidaniel-claude-obsidian
claude plugin list
```

The private development tree deliberately has no
`.claude-plugin/marketplace.json`; it can contain contributor-vault state and
must not be added as a marketplace. The deterministic release builder injects
that manifest only into its audited output. The public default branch must be
promoted from the extracted audited artifact before these marketplace commands
are advertised for a new version.

Invoke skills as `/claude-obsidian:wiki`,
`/claude-obsidian:wiki-ingest`, and `/claude-obsidian:save`.

The plugin cache contains read-only product assets. Run Claude from the user
vault, set `CLAUDE_OBSIDIAN_VAULT`, or pass `--vault` to portable commands.

## Local Claude plugin development

From a product clone:

```bash
claude --plugin-dir <product-repository>
```

This mode is for testing uninstalled changes. Skills remain namespaced. It does
not convert the product repository into a user vault.

## Portable Agent Skills hosts

The installer defaults to a no-write preview for Codex, OpenCode, and Gemini:

```bash
bash bin/setup-multi-agent.sh
bash bin/setup-multi-agent.sh --apply
```

It links each canonical `skills/<name>/` directory into the host's direct
`<skill-root>/<name>/SKILL.md` discovery layout. Destinations are created only
when absent; an existing skill or link is never replaced. Check readiness
without writing:

```bash
bash bin/setup-multi-agent.sh --check
```

Cursor and Windsurf use workspace-local discovery and require an explicit
workspace:

```bash
bash bin/setup-multi-agent.sh --host cursor --host windsurf \
  --workspace <workspace> --apply
```

ZCode is opt-in and user-level (no `--workspace` needed):

```bash
bash bin/setup-multi-agent.sh --host zcode
bash bin/setup-multi-agent.sh --host zcode --apply
```

You can also create equivalent per-skill links manually. For each `<name>` under
the product's `skills/` directory, link that directory at:

```text
Codex:     ~/.agents/skills/<name>          -> <product-repository>/skills/<name>
OpenCode:  ~/.config/opencode/skills/<name> -> <product-repository>/skills/<name>
Gemini:    ~/.gemini/skills/<name>          -> <product-repository>/skills/<name>
ZCode:     ~/.zcode/skills/<name>           -> <product-repository>/skills/<name>
Cursor:    <workspace>/.cursor/skills/<name>   -> <product-repository>/skills/<name>
Windsurf:  <workspace>/.windsurf/skills/<name> -> <product-repository>/skills/<name>
```

## Create a new vault

Review the initialization plan first:

```bash
python3 scripts/claude-obsidian.py init <new-vault> \
  --generated-at <ISO-UTC> --operation-id init-reviewed
```

Apply the same operation only after the destination and changed paths look
correct:

```bash
python3 scripts/claude-obsidian.py init <new-vault> \
  --generated-at <ISO-UTC> --operation-id init-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

The generated vault contains:

- `.gitignore`—privacy-safe defaults excluding `.vault-meta/` runtime state,
  Obsidian workspace state, and live `.mcp.json` launch configuration;
- `.claude-obsidian.json`—workspace identity and vault selection;
- `inbox/`—visible source intake;
- `.raw/`—immutable source payloads and legacy delta manifest;
- `wiki/`—index, log, hot cache, overview, and generated notes;
- `.obsidian/`—minimal non-destructive Obsidian defaults;
- `.vault-meta/`—ignored runtime state created when needed.

Initialization does not add an upstream Git remote or install community
plugins. Open the new directory through Obsidian's vault picker.

## Adopt an existing vault

Adoption scans an existing Obsidian directory and proposes only missing product
metadata and foundation files:

```bash
python3 scripts/claude-obsidian.py adopt <existing-vault> \
  --generated-at <ISO-UTC> --operation-id adopt-reviewed
python3 scripts/claude-obsidian.py adopt <existing-vault> \
  --generated-at <ISO-UTC> --operation-id adopt-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

It preserves existing notes and Obsidian JSON. `--force` is intentionally
separate and should be used only after inspecting replacement targets.

For older claude-obsidian layouts, add provenance ledgers and workspace config
with an additive migration:

```bash
python3 scripts/claude-obsidian.py migrate --vault <existing-vault> \
  --generated-at <ISO-UTC> --operation-id migrate-reviewed
python3 scripts/claude-obsidian.py migrate --vault <existing-vault> \
  --generated-at <ISO-UTC> --operation-id migrate-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Migration is idempotent, does not infer claims from prose, and leaves the
legacy `.raw/.manifest.json` byte-for-byte unchanged.

## Vault selection

Mutable commands use this precedence:

1. `--vault <path>`
2. `CLAUDE_OBSIDIAN_VAULT`
3. nearest `.claude-obsidian.json`
4. nearest unambiguous initialized vault from the current directory

If selection fails, the command exits without mutation. The product/plugin root
is rejected as an implicit vault.

Verify a selected vault:

```bash
python3 scripts/claude-obsidian.py doctor --vault <vault>
python3 scripts/claude-obsidian.py contracts --verify --vault <vault>
```

## Optional configuration

The portable filesystem transport always remains available. Detect an active,
supported Obsidian CLI without persisting a snapshot:

```bash
bash scripts/detect-transport.sh --peek --vault <vault>
```

Optional extensions are explicit and vault-scoped:

```bash
bash bin/setup-mode.sh --vault <vault>
bash bin/setup-retrieve.sh --vault <vault>
bash bin/setup-dragonscale.sh --vault <vault>
```

Read each script's preview before applying. Retrieval may use local BM25 alone;
model-based contextual prefixes or remote endpoints require explicit egress
consent. Optional tools such as Ollama and defuddle are capability-detected.

## First operation

Place a source in `inbox/`. Inspect the byte-capture plan:

```bash
python3 scripts/claude-obsidian.py capture plan --vault <vault>
```

Create immutable content-addressed copies only when the plan is correct:

```bash
python3 scripts/claude-obsidian.py capture apply --vault <vault> \
  --generated-at <ISO-UTC> --operation-id capture-reviewed
python3 scripts/claude-obsidian.py capture apply --vault <vault> \
  --generated-at <ISO-UTC> --operation-id capture-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Then invoke the host's `wiki-ingest` skill. Image, PDF, and EPUB semantic
extraction is not built into the core; those formats currently receive bounded
metadata unless a separately configured adapter is explicitly approved.

## Upgrade and rollback

Upgrade product code independently from the user vault. Before a migration or
large ingest, make a normal backup or snapshot. Knowledge writes are journaled;
run recovery after an interrupted operation:

```bash
python3 scripts/claude-obsidian.py transaction recover --vault <vault>
```

Recovery conservatively preserves stale or foreign lock identities. Only after
confirming no writer is active may an operator add `--force-stale-lock`.

Git history is optional and never automatic. To checkpoint exactly one
completed transaction:

```bash
python3 scripts/claude-obsidian.py checkpoint <operation-id> --vault <vault> \
  --as-of YYYY-MM-DD
```

Checkpointing uses a temporary index, verifies exact Git blob bytes, refuses
pre-existing staged state, and resumes an interrupted ref/index finalization
from its vault-local pending record.

## Uninstall

Remove the host integration, not the vault:

```bash
claude plugin uninstall claude-obsidian@agricidaniel-claude-obsidian
claude plugin marketplace remove agricidaniel-claude-obsidian
```

For portable hosts, remove only the per-skill links that the installer reported.
User notes, sources, ledgers, and Obsidian settings remain untouched.

## Troubleshooting

| Symptom | Check |
|---|---|
| Skill is not discovered | Confirm `<host-skill-root>/<name>/SKILL.md` resolves to the matching product skill; rerun installer `--check`. |
| Command says no vault selected | Run from the vault, pass `--vault`, or set `CLAUDE_OBSIDIAN_VAULT`. |
| Plugin-root refusal | Select a separate user vault; plugin cache writes are unsupported. |
| Transaction conflict / exit 75 | Another operation is active or a target changed; reread, rebuild, and inspect a new bundle. |
| Obsidian CLI is unavailable | Use filesystem reads; start/update Obsidian before retrying CLI transport. |
| Capture adapter is not implemented | Inspect `capture adapters`; configure a separate runner only with explicit consent. |

Run `make test` in the product repository when developing or packaging changes.
