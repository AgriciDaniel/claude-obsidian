---
name: Feature request
about: Suggest an idea, new skill, or enhancement
title: "[feature] "
labels: enhancement
assignees: ''
---

## Problem
What user need or workflow gap motivates this request? Be specific about the situation where today's behavior falls short.

## Proposed solution
Describe what you'd like to see. New skill? New agent? Change to an existing one? Sketch the interface (slash command, trigger phrases, expected output).

## Alternatives considered
What other approaches did you think about, and why is this one preferred?

## Scope
Which existing surface(s) does this touch?
- [ ] A new skill (`skills/<name>/`)
- [ ] A new agent (`agents/<name>.md`)
- [ ] A new script (`scripts/<name>`)
- [ ] Change to existing skill: (which?)
- [ ] Change to plugin manifest / hooks / setup scripts
- [ ] Documentation only

## Compatibility
- Does this change behavior for existing v1.x vaults? Yes / No
- Does it require a new opt-in (`bin/setup-*.sh`)? Yes / No
- Does it introduce a new dependency? Yes / No

## Testing
How would this be tested hermetically? (No network, no external services.)

## Additional context
Links, examples, or references to similar features in other tools.
