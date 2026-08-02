---
date: 2026-08-02
project: agent-nudge
type: architecture-research
status: current
---
# Agent Nudge ingestion architecture research

## Findings
- Plan-and-Solve supports separating decomposition from execution, but it does not prescribe JSON, AutoGPT, or LangChain. Agent Nudge should adopt the separation without inheriting a framework.
- Structured output constrains syntax, not graph meaning. Provider JSON Schema must be followed by local Zod validation for unique IDs, valid references, topological ordering, and acyclicity.
- Vercel AI SDK's current API is `generateText` with `Output.object`; `generateObject` is deprecated. Agent Nudge already has a smaller provider-neutral model boundary, so adding the SDK would increase coupling without improving the contract.
- Whisper distinguishes transcription mistakes from text-standardization differences. De-janking should therefore be conservative and auditable: preserve the exact raw note, correct likely phonetic errors, and never silently summarize or expand intent.
- The model should not echo `originalText`. The trusted application attaches it after generation, reducing tokens and guaranteeing exact provenance.

## Resulting contract
- Graph: `originalText`, `cleanedText`, `tasks`.
- Task: `id`, `title`, `objective`, `suggestedMode`, `dependencies`.
- Modes: `RESEARCH | PLAN | BUILD`.
- Dependencies must point only to earlier tasks, producing a directly executable topological order.
- Tasks should be vertical tracer bullets; setup belongs with its first proof unless it is independently valuable.

## Sources
- Plan-and-Solve Prompting: https://arxiv.org/abs/2305.04091
- Least-to-Most Prompting: https://arxiv.org/abs/2205.10625
- Whisper paper: https://cdn.openai.com/papers/whisper.pdf
- OpenAI structured outputs reference: https://platform.openai.com/docs/api-reference/responses-streaming/response/content_part
- AI SDK 6 migration guide: https://ai-sdk.dev/docs/migration-guides/migration-guide-6-0
- Ollama structured outputs: https://docs.ollama.com/capabilities/structured-outputs

## Implementation
- Branch: `agents/ingest-loop`
- PR: https://github.com/manazoid4/agent-nudge/pull/29
- Full research pack: `C:/Users/manaz/Projects/agent-nudge-ingest/docs/INGESTION-RESEARCH.md`
