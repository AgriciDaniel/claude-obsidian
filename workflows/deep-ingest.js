export const meta = {
  name: 'deep-ingest',
  description: 'Fan out over many sources: ingest each in parallel under a lock, verify, then lint once',
  whenToUse:
    'A batch of sources needs ingesting (a full .raw/ directory, a list of URLs). ' +
    'Token-expensive and opt-in.',
  phases: [
    { title: 'Ingest', detail: 'one agent per source (fable), lock-guarded' },
    { title: 'Verify', detail: 'confirm each page was actually written' },
    { title: 'Lint', detail: 'one health check over the whole vault' },
  ],
}

// CONCURRENCY: parallel ingest is exactly the multi-writer case scripts/wiki-lock.sh
// exists for. Two agents updating index.md at once will interleave and corrupt it.
// Every writer here takes the lock. This is not optional.

const INGESTED = {
  type: 'object',
  properties: {
    source: { type: 'string' },
    pages_created: { type: 'array', items: { type: 'string' } },
    pages_updated: { type: 'array', items: { type: 'string' } },
    skipped: { type: 'boolean' },
    skip_reason: { type: 'string' },
  },
  required: ['source', 'pages_created', 'pages_updated'],
}

const VERIFIED = {
  type: 'object',
  properties: {
    ok: { type: 'boolean' },
    missing: { type: 'array', items: { type: 'string' } },
    note: { type: 'string' },
  },
  required: ['ok'],
}

const sources = Array.isArray(args) ? args : args?.sources
if (!sources?.length) {
  throw new Error('deep-ingest needs a list of sources. Pass args as an array of paths or URLs.')
}

log(`Ingesting ${sources.length} sources`)

const results = await pipeline(
  sources,

  (src) =>
    agent(
      `Ingest this source into the wiki: ${src}\n\n` +
        `Follow skills/wiki-ingest/SKILL.md exactly.\n\n` +
        `NETWORK: if the source is a URL, run \`python3 scripts/net-policy.py check-fetch ${src}\` ` +
        `FIRST. Exit 1 means do not fetch it: skip the source and say so. Exit 3 means consent ` +
        `is required: skip it and say so. Never fetch past a deny.\n\n` +
        `JS-RENDERED PAGES: if the fetch returns an empty shell, do NOT report success. ` +
        `Check .vault-meta/browser.json and use the browser skill, or skip and say you skipped.\n\n` +
        `LOCKING (mandatory, you are one of ${sources.length} concurrent writers): guard EVERY ` +
        `page write with\n` +
        `  bash scripts/wiki-lock.sh acquire <path>\n  ...write...\n  bash scripts/wiki-lock.sh release <path>\n` +
        `This includes wiki/index.md and wiki/log.md, which every one of your siblings is also ` +
        `touching right now. An unlocked write to index.md will interleave and corrupt it.\n\n` +
        `FILING: route new pages through \`python3 scripts/wiki-mode.py route source "<name>"\`.`,
      { label: `ingest:${String(src).slice(-40)}`, phase: 'Ingest', model: 'fable', schema: INGESTED },
    ),

  // Verify by execution, not by report. An ingest agent that says it wrote a page
  // and did not is the single failure this stage exists to catch, and it is not
  // rare. Do not trust the claim, stat the file.
  (res) =>
    res?.skipped
      ? { ok: true, note: `skipped: ${res.skip_reason || 'no reason given'}`, skipped: true }
      : agent(
          `The ingest agent for "${res?.source}" claims it created these pages:\n` +
            `${(res?.pages_created || []).join('\n') || '(none)'}\n` +
            `and updated these:\n${(res?.pages_updated || []).join('\n') || '(none)'}\n\n` +
            `Verify by execution, not by reading its report. For each path, actually check the ` +
            `file exists and is non-empty, and that its content genuinely corresponds to the ` +
            `source. Use \`ls -la\` and read the files.\n` +
            `Return ok=false and list anything missing, empty, or unrelated to the source.`,
          { label: `verify:${String(res?.source).slice(-32)}`, phase: 'Verify', schema: VERIFIED },
        ),
)

const checked = results.filter(Boolean)
const good = checked.filter((r) => r.ok && !r.skipped)
const skipped = checked.filter((r) => r.skipped)
const bad = checked.filter((r) => !r.ok)

log(`${good.length} ingested and verified, ${skipped.length} skipped, ${bad.length} failed verification`)

// Barrier is correct here: lint reasons over the whole vault, so it must run
// after every writer has finished. And it runs ONCE, not once per source.
phase('Lint')
const lint = await agent(
  `Run a wiki health check per skills/wiki-lint/SKILL.md.\n\n` +
    `${sources.length} sources were just ingested in parallel, so look specifically for the ` +
    `damage concurrent writers cause: duplicated index.md entries, interleaved or truncated ` +
    `log.md lines, orphan pages nobody linked, dead wikilinks.\n\n` +
    `NOTE: the vault root is the repo root, so Obsidian counts scripts/, tests/ and skills/ ` +
    `as orphans. Only report counts filtered to wiki/.\n\n` +
    `Also confirm no lock files were left behind: ls .vault-meta/locks/ 2>/dev/null`,
  { label: 'lint', phase: 'Lint' },
)

return {
  requested: sources.length,
  ingested: good.length,
  skipped: skipped.map((r) => r.note),
  failed_verification: bad.map((r) => ({ missing: r.missing, note: r.note })),
  lint,
}
