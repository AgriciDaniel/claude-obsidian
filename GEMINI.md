# claude-obsidian: Instruções para Gemini

Leia `AGENTS.md` como o contrato canônico neutro de host. Skills vivem em
`skills/<name>/SKILL.md` e o núcleo portátil vive em `claude_obsidian/`.

Instale a descoberta de skills com:

```bash
bash scripts/setup-multi-agent.sh --host gemini
bash scripts/setup-multi-agent.sh --host gemini --apply
```

O primeiro comando visualiza os links; o segundo aplica esse escopo revisado.

Este repositório é fonte do produto, não o vault de usuário padrão. Crie um
vault separado com o comando `init` de dry-run primeiro ou adote um vault
existente. Resolva esse vault antes de ler `wiki/hot.md` ou executar uma skill.

Todas as mutações compartilhadas usam um bundle `claude-obsidian.transaction.v1` inspecionado.
Workers paralelos apenas rascunham. Não use escritas compartilhadas diretas,
commits automáticos ou o helper de lock por arquivo deprecado. Egresso remoto e
ações destrutivas precisam de consentimento explícito do usuário.

Canônico público: https://github.com/AgriciDaniel/claude-obsidian
