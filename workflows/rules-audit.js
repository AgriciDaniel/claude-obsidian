export const meta = {
  name: 'rules-audit',
  description: 'Audit a diff or a codebase against the rules/ packs. One auditor per rule, adversarially verified.',
  whenToUse:
    'Before a release, or on a large diff, when the user wants the code held against the ' +
    'rule packs rather than reviewed on vibes. Token-expensive and opt-in.',
  phases: [
    { title: 'Audit', detail: 'one auditor per rule (fable)' },
    { title: 'Verify', detail: 'refute each violation before reporting it' },
    { title: 'Report', detail: 'rank by severity' },
  ],
}

// One auditor per rule, not one auditor with all the rules. An agent given 20
// rules at once checks the first few properly and skims the rest. An agent given
// exactly one rule has nowhere to hide.

const VIOLATIONS = {
  type: 'object',
  properties: {
    violations: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          line: { type: 'integer' },
          summary: { type: 'string' },
          evidence: { type: 'string', description: 'the offending code, verbatim' },
          fix: { type: 'string' },
        },
        required: ['file', 'summary', 'evidence'],
      },
    },
  },
  required: ['violations'],
}

const VERDICT = {
  type: 'object',
  properties: {
    real: { type: 'boolean' },
    reason: { type: 'string' },
  },
  required: ['real', 'reason'],
}

const target = args?.target || 'git diff origin/main...HEAD'
const domain = args?.domain || 'coding'

phase('Audit')
const listing = await agent(
  `Run: python3 scripts/render-rules.py list\n` +
    `Return ONLY the rule ids in the "${domain}" domain, one per line, with severity. No prose.`,
  { label: 'load-rules', phase: 'Audit', model: 'fable' },
)

const ids = listing
  .split('\n')
  .map((l) => l.trim())
  .filter((l) => l.includes(`${domain}/`))
  .map((l) => {
    const m = l.match(/(blocker|high|medium)\s+(\S+)/)
    return m ? { severity: m[1], id: m[2] } : null
  })
  .filter(Boolean)

if (!ids.length) throw new Error(`no rules found for domain "${domain}"`)
log(`Auditing ${target} against ${ids.length} ${domain} rules`)

// Pipeline: each rule's violations get verified as soon as THAT rule's audit
// finishes. A slow rule never blocks a fast rule's verification.
const results = await pipeline(
  ids,
  (rule) =>
    agent(
      `Read the rule at rules/${rule.id}.md. Read it fully, including "Applies when".\n\n` +
        `Now audit this target against THAT ONE RULE and nothing else:\n  ${target}\n\n` +
        `Report only genuine violations of this specific rule. Cite file and line. ` +
        `Quote the offending code verbatim. If the code does not violate this rule, ` +
        `return an empty list: a clean result is a real result, and inventing a ` +
        `violation to look thorough is worse than finding nothing.`,
      { label: `audit:${rule.id}`, phase: 'Audit', model: 'fable', schema: VIOLATIONS },
    ),

  (found, rule) =>
    parallel(
      (found?.violations || []).map((v) => () =>
        agent(
          `Try to REFUTE this claimed rule violation. Default to real=false if uncertain.\n\n` +
            `RULE: rules/${rule.id}.md (read it)\n` +
            `FILE: ${v.file}${v.line ? ':' + v.line : ''}\n` +
            `CLAIM: ${v.summary}\n` +
            `EVIDENCE: ${v.evidence}\n\n` +
            `Open the file and look. Is this actually what the code does, and does the ` +
            `rule actually forbid it? A violation that does not survive you is not reported.`,
          { label: `verify:${v.file}`, phase: 'Verify', schema: VERDICT },
        ).then((verdict) => ({ ...v, rule: rule.id, severity: rule.severity, verdict })),
      ),
    ),
)

const confirmed = results
  .flat()
  .filter(Boolean)
  .filter((v) => v.verdict?.real)

const order = { blocker: 0, high: 1, medium: 2 }
confirmed.sort((a, b) => order[a.severity] - order[b.severity])

log(`${confirmed.length} violations confirmed after refutation`)

return {
  target,
  domain,
  rules_checked: ids.length,
  violations: confirmed.map((v) => ({
    severity: v.severity,
    rule: v.rule,
    file: v.file,
    line: v.line,
    summary: v.summary,
    fix: v.fix,
  })),
  blockers: confirmed.filter((v) => v.severity === 'blocker').length,
}
