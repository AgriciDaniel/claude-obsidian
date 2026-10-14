# Esquema de vault claude-obsidian

Este é o esquema compacto legível por humanos para um vault de usuário.
Detalhes operacionais vivem nas skills e contratos executáveis. Código do
produto e dados do vault de usuário devem permanecer separados.

## Layout raiz

```text
vault/
├── .gitignore                  # excludes vault-local runtime/session state
├── .claude-obsidian.json       # workspace identity and vault selection
├── inbox/                      # visible source intake; never auto-deleted
├── .raw/                       # immutable source bytes
│   └── .manifest.json          # backward-compatible delta/address metadata
├── wiki/                       # generated, user-owned knowledge
│   ├── index.md                # catalog and navigation
│   ├── log.md                  # completed operation history, newest first
│   ├── hot.md                  # bounded recent context, not a transcript
│   ├── overview.md             # high-level synthesis
│   ├── sources/
│   ├── entities/
│   ├── concepts/
│   ├── questions/
│   ├── canvases/
│   └── meta/ledgers/
│       ├── source-ledger.json
│       └── claim-ledger.json
├── .obsidian/                  # user-controlled Obsidian settings
└── .vault-meta/                # ignored locks, journals, indexes, queue/config
```

Modos LYT, PARA ou Zettelkasten podem rotear novas páginas de forma diferente.
Mudanças de modo não migram notas antigas nem alteram semântica de evidência.

## Invariantes de fonte

- Payloads de fonte existentes abaixo de `.raw/` nunca são substituídos.
- `.raw/.manifest.json` é metadado mutável e muda apenas dentro da mesma
  transação da operação que registra.
- Nova captura de bytes é endereçada por conteúdo via SHA-256.
- Um arquivo em `inbox/` permanece até que o usuário o remova. O núcleo pode
  propor deleção mas nunca a executa.
- Localizadores remotos usam HTTPS validado. Credenciais não pertencem a URLs,
  notas de fonte, bundles, filas ou configuração rastreada.

## Frontmatter de página Markdown

Use YAML plano com chaves plurais e datas `YYYY-MM-DD`:

```yaml
---
type: concept
title: Source-grounded notes
status: developing
created: 2026-07-11
updated: 2026-07-11
tags:
  - knowledge
  - evidence
aliases: []
address: c-000001
---
```

Propriedades de linha de base requeridas são `type`, `title`, `status`,
`created`, `updated` e `tags`. `aliases` e `address` são opcionais a menos que
uma política de vault configurada os requeira.

Tipos de página comuns:

| Tipo | Propósito |
|---|---|
| `source` | Resumo rastreável de uma identidade de fonte |
| `entity` | Pessoa, organização, produto, projeto ou outra coisa nomeada |
| `concept` | Ideia, framework, mecanismo ou definição |
| `question` | Uma resposta delimitada com status de evidência visível |
| `comparison` | Contraste baseado em critérios com suporte citado |
| `session` | Resumo aprovado pelo usuário de conteúdo selecionado de conversa |
| `overview` | Mapa de alto nível de um domínio ou vault |
| `meta` | Índice, log, cache, convenção ou página de manutenção |
| `fold` | Rollup extrativo de entradas de log identificadas |

`claude_obsidian/page_schema.py` é a declaração única deste vocabulário. A
tabela acima o documenta para um leitor; o código lê o módulo em vez de
repetir os valores, e um teste assegura que os dois permaneçam em sincronia.

`source`, `entity`, `concept`, `question` e `session` são *roteáveis*: o
roteador de metodologia pode colocar uma nova página desse tipo. `comparison`,
`overview`, `meta` e `fold` são frontmatter válido e não roteáveis, porque o
produto os cria através de uma operação dedicada em vez de arquivar uma nova
nota.

Status comuns são `seed`, `active`, `developing`, `evergreen`, `answered`,
`provisional`, `contested`, `deprecated` e `archived`. Use apenas status que os
dashboards e convenções do vault entendam.

## Sintaxe Obsidian

- Referências internas usam `[[Target]]` ou `[[Target|Alias]]`.
- Headings e referências de bloco usam `[[Target#Heading]]` e `[[Target#^block]]`.
- Embeds usam `![[Attachment.ext]]`.
- Callouts usam `> [!type] Title`.
- Código cercado é dados; texto parecido com link dentro dele não é uma aresta
  do grafo.
- Prefira links por basename apenas quando o basename for único. Use um path
  relativo ao vault quando duplicatas seriam ambíguas.

Não fabrique um backlink meramente para tornar o grafo simétrico. Adicione
links que ajudem um leitor a navegar ou entender uma relação.

## Páginas centrais

### `wiki/index.md`

O índice é um catálogo curado. Todo alvo linkado deve resolver. Uma entrada de
índice não é evidência por si só. Toda criação ou remoção de página canônica
atualiza pelo menos um catálogo ativo ou MOC (active catalog or MOC) na mesma
transação. Atualize `wiki/index.md` quando for esse catálogo ativo; MOCs
específicos de metodologia podem satisfazer o invariante de navegação em vez
disso.

### `wiki/log.md`

O registro grava operações lógicas concluídas, não escritas de arquivo
individuais. Coloque a entrada mais recente primeiro e inclua o ID da operação,
tipo de operação, páginas principais e um resultado fundamentado. Não reescreva
entradas filhas históricas ao criar um fold.

### `wiki/hot.md`

Contexto quente é curto, sanitizado e útil para a próxima sessão. Pode incluir
fatos recentes, páginas alteradas, threads ativas e questões não resolvidas. Não
deve conter segredos, transcrições brutas, instruções de ferramenta ou
afirmações que careçam da mesma qualificação encontrada em páginas canônicas.

Hooks podem ler e emitir este arquivo como dados delimitados. Eles não o
atualizam.

### `wiki/overview.md`

A visão geral sintetiza estrutura estável de alto nível e liga a páginas de
suporte. Muda menos frequentemente que o contexto quente.

## Ledgers de procedência

O ledger de fonte separa identidade de evidência de prosa. Cada registro de
fonte pode incluir:

- ID estável e SHA-256;
- localizador de arquivo relativo ao vault ou localizador HTTPS;
- autoridade: `official`, `primary`, `secondary`, `community`, `synthetic` ou
  `unknown`;
- chave de independência;
- timestamps de recuperação/revisão e `refresh_due`;
- estado de revisão: `unreviewed`, `active`, `superseded` ou `rejected`;
- páginas linkadas.

O ledger de afirmação registra uma afirmação falsificável, localização da nota,
IDs de fontes de suporte e contrários, confiança, risco, estado de revisão e
avaliação: `accepted`, `provisional`, `contested`, `unsupported` ou
`deprecated`.

Afirmações aceitas precisam de suporte ativo, fresco e não sintético. Afirmações
aceitas de alto risco precisam de duas fontes independentes. Preserve
contradições e linhagem de fonte; não selecione silenciosamente um vencedor.

## Transação de operação

Uma mutação lógica é um bundle:

```json
{
  "schema": "claude-obsidian.transaction.v1",
  "operation_id": "ingest-example",
  "operation_type": "ingest",
  "expected_hashes": {
    "wiki/sources/Example.md": null
  },
  "writes": [
    {
      "path": "wiki/sources/Example.md",
      "mode": "create",
      "content_file": "drafts/example.md",
      "sha256": "DRAFT_SHA256"
    }
  ],
  "address_requests": [
    {"path": "wiki/sources/Example.md", "prefix": "c"}
  ],
  "source_manifest_updates": {}
}
```

`content` inline é texto UTF-8. `content_file` pode conter texto ou bytes
binários e deve corresponder ao seu hash declarado. Paths de payload raw são
apenas-criação.

Inspecione antes de aplicar:

```bash
python3 scripts/claude-obsidian.py transaction inspect <bundle> --vault <vault>
python3 scripts/claude-obsidian.py transaction apply <bundle> --vault <vault> \
  --approved-plan-sha256 <approval_sha256>
```

Use o `approval_sha256` exato do resultado da inspeção. Ele vincula o plano
expandido à raiz canônica resolvida do vault, então a aprovação para um vault
não pode ser reutilizada contra outro vault.

Workers paralelos nunca aplicam bundles ou editam páginas compartilhadas. Eles
retornam pacotes de rascunho com evidências, paths de destino e hashes esperados
para um orquestrador.

## Contratos de fluxo de trabalho

### Ingest

Uma operação de ingestão pode incluir captura raw apenas-criação, resumo de
fonte, páginas de entidade/conceito, registros de procedência, atualizações de
índice/MOC, log, cache quente e visão geral. Toda criação ou remoção canônica
atualiza um índice ativo ou MOC; mudanças de visão geral permanecem condicionais
a uma imagem de alto nível alterada. Toda afirmação extraída permanece
rastreável à fonte. Orçamentos de lote delimitam contagem de fontes, bytes
totais, páginas, links e trabalho decorrido.

### Query

Query é somente leitura. Recupere o menor conjunto de evidências relevantes,
distinga afirmações aceitas/provisionais/contestadas/sem suporte/desatualizadas,
cite páginas do vault e registros de fonte, e declare lacunas. Se o usuário pedir
para guardar a resposta, invoque uma operação Save separada.

### Save

Salve apenas conteúdo que o usuário selecionou explicitamente. Não capture uma
conversa inteira por padrão. A nota salva, procedência quando necessária,
índice, log e cache quente formam uma transação.

### Autoresearch

Pesquisa tem uma questão explícita, política de fonte, consentimento de
egresso e orçamento de parada. Resultados web primeiro se tornam um dossiê de
pesquisa citado. Fundi-los em páginas canônicas é uma operação revisada
separada.

### Lint

Lint é determinístico e somente leitura. Reporta links mortos/ambíguos,
basenames duplicados, órfãos, frontmatter ausente, seções vazias, entradas de
índice desatualizadas, erros de configuração/leitura e violações de contrato
dos ledgers de fonte/afirmação. Reparos são propostas de transação separadas.

## Segurança e manutenção

- Execute `doctor` para verificar a seleção do vault.
- Execute `lint` após lotes de operações significativos.
- Execute `transaction recover` após uma aplicação interrompida.
- Use `checkpoint` explícito apenas quando o histórico Git for desejado.
- Mantenha backups independentes dos journals de transação.
- Nunca trate o repositório do produto, cache do plugin, uma verificação de
  existência de arquivo de configuração, ou uma afirmação de IA como prova de
  que uma capacidade está verificada.
- `configured` significa que pré-requisitos estão presentes. `verified`
  requer que um verificação comportamental declarada passe; um schema/auto-check
  não pode promover o estado. Quando nenhum verificador automatizado existe, a
  capacidade permanece configurada e reporta a razão rastreada.

Os contratos executáveis em `config/` e testes são a fonte de verdade quando
esta prosa e o comportamento discordarem.
