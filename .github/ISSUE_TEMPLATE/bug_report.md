---
name: Bug report
about: Something is broken or behaves unexpectedly
title: "[bug] "
labels: bug
assignees: ''
---

## O que aconteceu
Uma descrição clara do comportamento inesperado.

## Comportamento esperado
O que você esperava que acontecesse em vez disso.

## Passos para reprodução
1. ...
2. ...
3. ...

## Ambiente
- Versão do produto: (execute `python3 scripts/claude-obsidian.py --version`)
- Versão do Claude Code: (execute `claude --version`)
- SO: (ex.: macOS 14.5, Pop!_OS 24.04, Windows 11)
- Versão do Obsidian: (se relevante)
- Fonte de seleção do vault: (saída de `doctor --vault <vault>`, com paths privados redigidos)
- Estado do transporte: (saída de `bash scripts/detect-transport.sh --peek --vault <vault>`)

## Skill / agent / script envolvido
Qual superfície é afetada? (ex.: `/wiki-ingest`, `scripts/wiki-mode.py`, `agents/verifier.md`)

## Logs / saída
```
Paste relevant terminal output or error messages here.
```

## O que você tentou
- [ ] Executei o teste de regressão relevante ou `make test` — Sim / Não
- [ ] Confirmei que o repositório do produto e o vault do usuário são separados — Sim / Não
- [ ] Verifiquei o CHANGELOG em busca de problemas conhecidos na minha versão
- [ ] Pesquisei issues existentes por relatos similares

## Contexto adicional
Qualquer outra coisa que possa ajudar (capturas de tela, issues relacionadas, mudanças recentes).
