# claude-obsidian: regras do Windsurf

Leia `AGENTS.md` como o contrato canônico neutro em relação ao host.
Pré-visualize e depois instale os links de skill do Cascade com
`bash scripts/setup-multi-agent.sh --host windsurf --workspace "$PWD"`
seguido do mesmo comando com `--apply`, e carregue o
`skills/<name>/SKILL.md` correspondente quando uma solicitação o disparar.

O clone do produto e o vault do usuário são separados. Resolva o vault do
usuário antes de ler o contexto quente ou mutar conhecimento. Payloads brutos
são somente de criação; trabalhadores paralelos retornam rascunhos; um
orquestrador inspeciona e aplica uma transação recuperável. Queries e lint
permanecem somente-leitura. Egress de rede, reparo destrutivo e checkpoints do
Git exigem consentimento explícito do usuário.

Public canonical: https://github.com/AgriciDaniel/claude-obsidian
