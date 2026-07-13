export const meta = {
  name: 'research-sweep',
  description: 'Multi-modal web sweep on a topic: search wide, deep-read, adversarially verify, file into the wiki',
  whenToUse:
    'The user wants a topic researched thoroughly and filed, not just answered. ' +
    'Token-expensive and opt-in: only run when the user asks for a workflow or a deep sweep.',
  phases: [
    { title: 'Sweep', detail: 'parallel searches, each from a different angle' },
    { title: 'Read', detail: 'deep-read the surfaced sources (fable)' },
    { title: 'Verify', detail: 'adversarial refutation of each claim' },
    { title: 'File', detail: 'synthesize and write wiki pages' },
  ],
}

// A single search angle finds what that angle can see and is blind to the rest.
// Four blind searchers beat one thorough one, because their blind spots differ.
const ANGLES = [
  { key: 'primary', hint: 'primary sources, official docs, specs, the thing itself' },
  { key: 'critical', hint: 'criticism, failure reports, post-mortems, what goes wrong' },
  { key: 'recent', hint: 'the last 6 months only: changes, deprecations, new releases' },
  { key: 'adjacent', hint: 'competing and adjacent approaches, what people migrate to and from' },
]

const CLAIMS = {
  type: 'object',
  properties: {
    claims: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          claim: { type: 'string' },
          url: { type: 'string' },
          quote: { type: 'string', description: 'verbatim supporting text from the source' },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['claim', 'url'],
      },
    },
  },
  required: ['claims'],
}

const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
  },
  required: ['refuted', 'reason'],
}

const topic = typeof args === 'string' ? args : args?.topic
if (!topic) throw new Error('research-sweep needs a topic. Pass it as args.')

log(`Sweeping: ${topic}`)

// Stage 1+2 pipeline: each angle deep-reads as soon as ITS search returns.
// No barrier, so a slow angle never holds up a fast one.
const perAngle = await pipeline(
  ANGLES,
  (angle) =>
    agent(
      `Search the web for "${topic}", specifically from this angle: ${angle.hint}.\n` +
        `Before EVERY fetch, run: python3 scripts/net-policy.py check-fetch <url>\n` +
        `Exit 0 = proceed. Exit 1 = skip that URL, do not fetch it. Exit 3 = skip it and note that consent is required.\n` +
        `Return the 5 to 8 most load-bearing URLs you found, with a one-line note on why each matters.`,
      { label: `sweep:${angle.key}`, phase: 'Sweep', model: 'fable' },
    ),

  (found, angle) =>
    agent(
      `Deep-read these sources on "${topic}" (angle: ${angle.hint}):\n\n${found}\n\n` +
        `Fetch each one (net-policy check-fetch first, always). If a page is JS-rendered or ` +
        `gated and comes back as an empty shell, do NOT report success on it: fall back to the ` +
        `browser skill (.vault-meta/browser.json) or drop it and say you dropped it.\n` +
        `Extract only claims a source actually supports. Quote the supporting text verbatim. ` +
        `A claim you cannot quote is a claim you do not have.`,
      { label: `read:${angle.key}`, phase: 'Read', model: 'fable', schema: CLAIMS },
    ),
)

// Barrier justified: dedupe needs every angle's claims at once, and it is much
// cheaper to refute 20 deduped claims than 60 overlapping ones.
const all = perAngle.filter(Boolean).flatMap((r) => r.claims || [])
const seen = new Set()
const deduped = all.filter((c) => {
  const k = c.claim.toLowerCase().replace(/\W+/g, ' ').trim().slice(0, 90)
  if (seen.has(k)) return false
  seen.add(k)
  return true
})
log(`${all.length} claims from ${ANGLES.length} angles, ${deduped.length} after dedupe`)

if (!deduped.length) return { topic, filed: false, reason: 'no claims survived the sweep' }

// Adversarial verify. Three skeptics per claim, each told to REFUTE it and to
// default to refuted when uncertain. A claim that survives motivated refutation
// is worth filing; one that merely was not challenged is not.
const judged = await parallel(
  deduped.map((c) => () =>
    parallel(
      ['the source does not actually say this', 'the source says it but is not credible', 'it is true but out of date'].map(
        (lens) => () =>
          agent(
            `Refute this claim. Angle of attack: "${lens}".\n\n` +
              `CLAIM: ${c.claim}\nSOURCE: ${c.url}\nQUOTED AS: ${c.quote || '(no quote provided)'}\n\n` +
              `Fetch the source and check (net-policy check-fetch first). If the quote is not ` +
              `there, or the claim overreaches what the source supports, it is REFUTED. ` +
              `Default to refuted=true when you are uncertain.`,
            { label: `refute:${c.claim.slice(0, 32)}`, phase: 'Verify', model: 'fable', schema: VERDICT },
          ),
      ),
    ).then((votes) => {
      const v = votes.filter(Boolean)
      const kills = v.filter((x) => x.refuted).length
      return { ...c, survived: v.length > 0 && kills < 2, kills, votes: v.length }
    }),
  ),
)

const confirmed = judged.filter(Boolean).filter((c) => c.survived)
const killed = judged.filter(Boolean).filter((c) => !c.survived)
log(`${confirmed.length} claims survived refutation, ${killed.length} killed`)

if (!confirmed.length) {
  return { topic, filed: false, reason: 'every claim was refuted', killed: killed.length }
}

phase('File')
const filed = await agent(
  `File research on "${topic}" into the wiki.\n\n` +
    `These claims SURVIVED adversarial refutation (3 skeptics each, majority rule). ` +
    `They are the only ones you may state as fact:\n\n` +
    confirmed.map((c) => `- ${c.claim}\n  source: ${c.url}`).join('\n') +
    `\n\nThese were REFUTED. Do NOT state them. If one is a common belief worth ` +
    `warning about, you may note it as a misconception, with the reason it fails:\n\n` +
    killed.map((c) => `- ${c.claim} (killed ${c.kills}/${c.votes})`).join('\n') +
    `\n\nFollow skills/wiki-ingest/SKILL.md. Route new pages through ` +
    `\`python3 scripts/wiki-mode.py route research "${topic}"\` so the vault's methodology ` +
    `mode decides the path. Cite every claim. Update index.md, log.md, and hot.md.`,
  { label: 'file', phase: 'File' },
)

return {
  topic,
  filed: true,
  confirmed: confirmed.length,
  refuted: killed.length,
  summary: filed,
}
