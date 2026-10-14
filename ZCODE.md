# claude-obsidian: Instruções para ZCode

Leia `AGENTS.md` como o contrato canônico neutro de host. Skills vivem em
`skills/<name>/SKILL.md` e o núcleo portátil vive em `claude_obsidian/`.

ZCode lê `AGENTS.md` nativamente no escopo de workspace e usuário (conforme a
documentação de Agent do ZCode, https://zcode.z.ai/en/docs/agents), então
nenhum arquivo de regras espelhado é necessário. Skills de nível de usuário são
descobertas em `~/.zcode/skills/<skill-name>/SKILL.md` (https://zcode.z.ai/en/docs/skill).
Instale a descoberta de skills com:

```bash
bash scripts/setup-multi-agent.sh --host zcode
bash scripts/setup-multi-agent.sh --host zcode --apply
```

O primeiro comando visualiza os links; o segundo aplica esse escopo revisado.
Links chegam em `~/.zcode/skills/` (nível de usuário), então todo workspace
ZCode pode invocar as skills sem configuração por projeto.

Este repositório é fonte do produto, não o vault de usuário padrão. Crie um
vault separado com o comando `init` de dry-run primeiro ou adote um vault
existente. Resolva esse vault antes de ler `wiki/hot.md` ou executar uma skill.

Todas as mutações compartilhadas usam um bundle `claude-obsidian.transaction.v1` inspecionado.
Workers paralelos apenas rascunham. Não use escritas compartilhadas diretas,
commits automáticos ou o helper de lock por arquivo deprecado. Egresso remoto e
ações destrutivas precisam de consentimento explícito do usuário.

Canônico público: https://github.com/AgriciDaniel/claude-obsidian
