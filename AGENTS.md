# claude-obsidian: Instruções para agentes

claude-obsidian é um pacote Agent Skills local-first para construir bases de
conhecimento Obsidian com citações de fonte e efeito composto. Também entrega
um adaptador de plugin Claude Code. O fluxo de trabalho portátil é implementado
em `skills/` e no núcleo `claude_obsidian/` da biblioteca padrão; hooks de
host nunca definem comportamento de conhecimento.

## Limites do produto e do vault

- Este repositório é o fonte do produto. Não é o vault de usuário padrão.
- Um vault de usuário é o diretório contendo `.claude-obsidian.json`, `wiki/`
  e `.raw/`. Estado mutável sempre pertence a ele.
- `templates/vault/` é a semente distribuível. `wiki/`, `.raw/` e
  `.vault-meta/` raiz são estado de contribuidor e são excluídos de artefatos
  públicos.
- Nunca deduza um vault de usuário a partir do cache do plugin ou
  `${CLAUDE_PLUGIN_ROOT}`.
- Um checkout contendo estado de vault de contribuidor não tem catálogo de
  marketplace. `config/public-marketplace.json` é injetado como
  `.claude-plugin/marketplace.json` apenas dentro do artefato de release
  auditado. Um artefato limpo para distribuição extraído pode reter esse
  manifesto exato e reconstruir idempotentemente. Um branch público padrão deve
  ser preenchido a partir do artefato limpo, nunca enviando estado de vault de
  contribuidor.

Resolva um vault nesta ordem: `--vault` explícito,
`CLAUDE_OBSIDIAN_VAULT`, `.claude-obsidian.json` mais próximo, depois um vault
inequívogo no diretório atual ou acima. Falhe fechado quando nenhum vault é
selecionado.

## Bootstrap

1. Leia este arquivo. Em um checkout de desenvolvimento, também leia o
   `CLAUDE.md` raiz apenas-do-host quando presente; artefatos de release
   intencionalmente o omitem.
2. Leia a skill selecionada completamente.
3. Leia apenas as referências que essa skill roteia.
4. Resolva o vault de usuário. Se `wiki/hot.md` existir, leia-o silenciosamente.
5. Para um novo vault, execute `python3 scripts/claude-obsidian.py init PATH`
   primeiro; aplique apenas após revisar o dry run. Use `adopt` para um vault
   existente.

## Skills canônicas

Todas as 15 skills vivem em `skills/<name>/SKILL.md`. Elas usam o subconjunto de
frontmatter Agent Skills portátil: exatamente `name` e `description`. Não
adicione arquivos espelhados em `commands/`; o Claude invoca skills de plugin
por nomes com namespace como `/claude-obsidian:wiki`.

Os fluxos de trabalho centrais são `wiki`, `save`, `wiki-ingest`, `wiki-query`
e `wiki-lint`. Extensões são `autoresearch`, `canvas`, `defuddle`, `wiki-fold`,
`wiki-mode`, `wiki-retrieve` e `wiki-cli`. Skills de referência são
`obsidian-markdown`, `obsidian-bases` e `think`.

## Protocolo de mutação

Uma operação lógica de conhecimento é uma transação recuperável:

1. Leia os alvos e registre valores SHA-256 esperados.
2. Permita que workers paralelos retornem apenas rascunhos e evidências.
3. Funda os rascunhos em um bundle `claude-obsidian.transaction.v1`.
4. Inspecione o bundle, depois aplique-o uma vez através de
   `scripts/claude-obsidian.py`.
5. Reporte o ID da operação e os paths exatos alterados.

Não use escritas compartilhadas diretas, o helper `wiki-lock.sh` deprecado, ou
auto-commits genéricos de lifecycle. Checkpoint do Git é separado e explícito.
Payloads raw de fonte são apenas-criação; `.raw/.manifest.json` é o único
arquivo de metadados raw legado mutável. Reparos destrutivos, egresso remoto e
merges de pesquisa canônica requerem consentimento explícito.

## Convenções do vault

- `inbox/`: entrada visível de captura; nunca deletada automaticamente.
- `.raw/`: payloads de fonte imutáveis e manifesto delta legado.
- `wiki/`: páginas de conhecimento geradas.
- `wiki/meta/ledgers/`: procedência de fontes e afirmações.
- `wiki/hot.md`: contexto recente delimitado, nunca uma transcrição.
- `wiki/log.md`: histórico de operações, mais recente primeiro.
- `.vault-meta/`: locks, journals, índices, filas e config de runtime ignorados.

Use Markdown Obsidian: propriedades YAML planas, datas `YYYY-MM-DD`, wikilinks,
embeds e callouts válidos. Nunca fabrique localizadores de evidência, citações,
números de página ou confiança.

## Verificação

Execute `make test` após mudanças comportamentais. Ele executa cada suíte
Python e shell, além dos contratos de produto, capacidade, pacote, hook e
manifest. Artefatos públicos são construídos localmente com `release build` e
auditados sem publicar. Nenhum agente pode fazer push, tag, abrir ou mutar
issues, ou publicar um release sem aprovação explícita do proprietário.

A injeção de contexto SessionStart do Claude está desativada por padrão. Trate
`CLAUDE_OBSIDIAN_SESSION_CONTEXT=1` como consentimento explícito do usuário
para colocar dados delimitados de `wiki/hot.md` no contexto do modelo; nunca
defina-o automaticamente. Um vault configurado no workspace fora do projeto
também requer um path `CLAUDE_OBSIDIAN_SESSION_CONTEXT_VAULT` exato.

## Referência

- Repositório canônico público: https://github.com/AgriciDaniel/claude-obsidian
- Padrão LLM Wiki: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Primitivos Obsidian: https://github.com/kepano/obsidian-skills
