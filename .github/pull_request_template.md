# Pedido de pull request

## Resumo
Descrição de um parágrafo sobre o que este pull request muda e por quê.

## Tipo
- [ ] Correção de bug (`fix:`)
- [ ] Nova funcionalidade (`feat:`)
- [ ] Documentação (`docs:`)
- [ ] Refatoração (`refactor:`)
- [ ] Cobertura de testes (`test:`)
- [ ] Chore / build / manutenção (`chore:`)

## Issue relacionada
Closes #<issue-number> (se aplicável)

## Mudanças
Liste os arquivos e superfícies afetados:
- `skills/<name>/SKILL.md` — o que mudou
- `scripts/<name>.py` — o que mudou
- ...

## Auto-revisão de segurança
- [ ] Li cada arquivo antes de alterá-lo
- [ ] Novos identificadores nomeados pensando no próximo leitor
- [ ] Menor unidade que funciona (sem abstração especulativa)
- [ ] Exclusões acompanhadas de adições quando aplicável
- [ ] Novo comportamento tem cobertura de teste hermética
- [ ] Novos modos de falha têm tratamento explícito + plano de desfazer
- [ ] Código do produto e estado mutável do vault do usuário permanecem
  separados
- [ ] Gravações de conhecimento usam uma transação recuperável; trabalhadores
  só fazem rascunho
- [ ] Ações de rede/destrutivas/externas têm consentimento explícito
- [ ] Alegações e maturidade de capacidade têm suporte em evidências

## Testes
```
make test
```
Cole o final da saída aqui (ou um resumo se for muito longo):

```
All tests passed.
```

## Verificador
Para mudanças não triviais, despache `agents/verifier.md` no worktree ou escopo
de paths declarado e cole seu veredito:

- Veredito: SHIP / HOLD-FIX-FIRST / NEEDS-REWORK
- BLOCKER: N / HIGH: N / MEDIUM: N / LOW: N

## CHANGELOG
- [ ] Adicionei uma entrada em `## [Unreleased]` no `CHANGELOG.md`

## Capturas de tela / saída
Se a mudança afetar a saída visível ao usuário, cole um exemplo de
antes/depois.

## Notas para o revisor
Qualquer coisa específica que o revisor deva focar, ou contexto que não é
óbvio no diff.
