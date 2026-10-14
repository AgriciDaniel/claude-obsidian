# Convenções de frontmatter

Preserve o vocabulário de propriedades válido de um vault existente. Para uma nova
página genérica do claude-obsidian, use propriedades YAML planas, listas em bloco e
campos de evidência explícitos onde se aplicarem.

## Propriedades comuns

```yaml
---
type: concept
title: "Human-readable title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: developing
tags:
  - concept
related:
  - "[[Related page]]"
sources:
  - "[[Source page]]"
claim_ids:
  - claim-example
---
```

Os tipos de página são declarados uma vez em `claude_obsidian/page_schema.py` e
documentados em [WIKI.md](../../../WIKI.md). Este arquivo antes repetia uma lista menor
que omitia `session` e `fold`, e é assim que um vault acaba carregando valores que
um documento chama de inválidos. Os status ainda são descritos em prosa nos dois
lugares e estão fora do escopo desta mudança. Um scaffold personalizado pode
adicionar tipos quando seu schema estiver documentado. `status` comummente progride
por `seed`, `developing`, `mature` e `evergreen`; preserve outros valores estabelecidos
em um vault adotado.

## Propriedades de fonte

```yaml
source_type: article
author: ""
date_published: YYYY-MM-DD
url: ""
source_id: ""
sha256: ""
authority: unknown
independence_key: ""
review_state: unreviewed
key_claims:
  - "No claims extracted yet."
```

Os valores de authority permitidos e a semântica de evidência estão definidas em
[provenance.md](provenance.md). Um valor ausente permanece vazio ou `unknown`; não
fabrique metadados para completar um formulário.

## Outras propriedades específicas por tipo

```yaml
# entity
entity_type: organization
role: ""
first_mentioned: "[[Source page]]"

# concept
complexity: intermediate
domain: ""
aliases:
  - Alternative name

# comparison
subjects:
  - "[[Thing A]]"
  - "[[Thing B]]"
dimensions:
  - cost
  - reliability
assessment: provisional
risk: low

# question
question: "What is being asked?"
assessment: unsupported
risk: low
```

## Regras

1. Mantenha as propriedades geradas planas; não introduza mapeamentos aninhados.
2. Escreva datas como `YYYY-MM-DD`, a menos que um schema existente exija um timestamp.
3. Use listas em bloco para propriedades geradas de múltiplos valores.
4. Coloque wikilinks entre aspas no YAML.
5. Mantenha localizadores externos nos registros de fonte; use wikilinks para
   relações internas de `related` e `sources`.
6. Atualize `updated` somente quando o conteúdo da página ou o estado avaliado mudar.
7. Preserve propriedades válidas desconhecidas durante uma edição.
8. Não trate um rótulo de confiança do frontmatter como evidência; o claim ledger
   e as fontes ativas vinculadas determinam o suporte.
9. Coloque entre aspas valores de tag puramente numéricos, por exemplo `- "2026"`,
   para que o tipo YAML deles continue sendo texto.