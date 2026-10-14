# Contribuindo com claude-obsidian

Contribuições são bem-vindas no repositório canônico público:
https://github.com/AgriciDaniel/claude-obsidian.

Para uma mudança substancial, abra uma issue que descreva o problema do
usuário, comportamento proposto, impacto de compatibilidade, implicações de
privacidade/egresso e uma estratégia de teste hermética. Relatórios de
segurança seguem [SECURITY.md](SECURITY.md), não o tracker público de issues.

## Contrato de engenharia

- Leia o comportamento afetado, chamadores, contratos e testes antes de
  editar.
- Mantenha o código do produto e o estado do vault de usuário separados.
- Prefira a menor implementação determinística com comportamento explícito de
  falha e recuperação.
- Preserve arquivos existentes do usuário a menos que o usuário revise uma
  substituição explícita ou plano destrutivo.
- Rodeie uma mutação lógica de conhecimento através de uma transação
  recuperável.
- Mantenha workers paralelos apenas-rascunho e operações query/lint em modo
  somente leitura.
- Requeira consentimento explícito para egresso remoto, reparo destrutivo e
  mudanças de estado externo.
- Não adicione alegações de capacidade, desempenho ou concorrentes sem
  evidência atual e rastreável.
- Mantenha o frontmatter das skills em exatamente `name` e `description`.

## Fluxo de trabalho local

Crie um branch focalizado a partir de um fork público. Python 3.11 ou mais
recente é requerido. O branch público padrão é uma árvore de produto
auto-validada e limpa de artefato; nunca adicione estado de vault raiz (`wiki/`,
`.raw/` ou `.vault-meta/`) a uma contribuição.

```bash
make test
```

O alvo de teste descobre cada arquivo `tests/test_*.py` e `tests/test_*.sh`,
depois executa contratos de produto/capacidade e pacote. Testes devem ser
herméticos: sem rede, servidor de modelo, paths pessoais, config global ou
estado persistente do produto. Uma integração de rede pertence atrás de um
flag de consentimento explícito e precisa de um teste duplo offline.

Mudanças comportamentais devem incluir:

1. um teste de regressão que falha para o comportamento antigo;
2. cobertura de sucesso, conflito, entrada inválida e recuperação proporcional
   ao risco;
3. documentação de usuário e de contrato atualizada;
4. uma entrada sob `## [Unreleased]` em `CHANGELOG.md`.

Execute o verificador de contexto fresco somente-leitura em `agents/verifier.md`
para mudanças não triviais. Ele pode inspecionar o worktree completo ou um
escopo de path declarado; nunca stage, commita, faz push ou modifica arquivos.
Resolva achados BLOCKER e HIGH antes de solicitar revisão.

Use Conventional Commits onde for prático. O pull request deve explicar o
problema, comportamento, história de compatibilidade/rollback, verificação
executada exata e quaisquer limitações remanescentes. Não inclua conteúdo de
vault, credenciais, estado de runtime gerado ou binários não revisados.

Ao contribuir, você concorda que sua contribuição é licenciada sob a
[MIT License](LICENSE) e regida por [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
