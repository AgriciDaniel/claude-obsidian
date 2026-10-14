# Template de página de fold

Todo fold é extrativo, determinístico e usa propriedades planas do Obsidian.

## Frontmatter

```yaml
---
type: fold
title: "Fold k{K} from {EARLIEST-DATE} to {LATEST-DATE}, n={COUNT}"
fold_id: "fold-k{K}-from-{EARLIEST-DATE}-to-{LATEST-DATE}-n{COUNT}"
batch_exponent: {K}
entry_count: {COUNT}
range_from: "{EARLIEST-CHILD-DATE}"
range_to: "{LATEST-CHILD-DATE}"
created: "{YYYY-MM-DD}"
updated: "{YYYY-MM-DD}"
tags:
  - meta
  - fold
  - "fold/k{K}"
status: mature
child_keys:
  - "log-{YYYYMMDD}-001"
  - "log-{YYYYMMDD}-002"
related:
  - "[[log]]"
  - "[[index]]"
---
```

Gere cada `child_key` a partir da data da entrada mais sua posição baseada em um
dentro do intervalo selecionado, do mais antigo para o mais novo. A mesma chave
aparece em exatamente uma linha do corpo. Isso evita objetos YAML aninhados
preservando uma bijeção entre frontmatter e tabela. O `fold_id` determinístico
corresponde ao nome do arquivo. A ausência de qualquer propriedade obrigatória
é uma falha no dry-run.

## Corpo

Use estas seções nesta ordem.

### Escopo

Um parágrafo que declare o nível, a contagem exata, o intervalo de datas e somente
aqueles temas sustentados por ao menos duas entradas filhas.

```markdown
Level-{K} fold of {COUNT} log entries spanning {FROM} through {TO}.
```

### Entradas filhas

Uma linha por child key e por entrada de log. Preserve as entradas mesmo quando
várias linhas se referem à mesma página.

```markdown
## Child Entries

| Child key | Date | Op | Title | Page | Page state | Extractive summary |
|---|---|---|---|---|---|---|
| log-20260701-001 | 2026-07-01 | ingest | Example source filed | [[Example Source]] | present | Added one source-backed example page. |
| log-20260702-002 | 2026-07-02 | save | Example decision recorded | [[Example Decision]] | missing | Source page is missing; summary is limited to the log entry. |
```

O resumo é uma frase sustentada pela entrada de log. Use `ambiguous in
source` ou `source missing` em vez de adivinhar.

### Resultados-chave

Inclua de três a sete marcadores extrativos quando houver suporte. Cite a child
key em cada marcador e verifique cada número contra a entrada de origem.

```markdown
## Key Outcomes

- Added one source-backed example page. (child: log-20260701-001)
```

Se nenhum resultado tiver suporte, declare isso explicitamente.

### Temas entre entradas

Inclua de zero a quatro marcadores. Cada tema nomeia ao menos duas child keys.
Se nenhum padrão tiver suporte, escreva:

```markdown
## Cross-entry Themes

No cross-entry themes identified; the entries are independent within this range.
```

### Contradições ou correções

Preserve as divergências e seu status. Use `None detected` somente após verificar
todas as entradas selecionadas.

### Páginas filhas

Liste cada página de destino presente e única uma vez. Esta seção é
deduplicada por página; a tabela de Child Entries não é.

```markdown
## Child Pages

- [[Example Source]]

## Related

- [[log]] - source entries
- [[index]] - vault catalog
```

## Validação

- `entry_count`, `child_keys` e as linhas da tabela têm contagens iguais.
- Toda child key é única e aparece exatamente duas vezes: no frontmatter e em uma linha.
- Toda afirmação numérica é rastreável até seu filho citado.
- Cada tema cita pelo menos dois filhos.
- Páginas ausentes permanecem explícitas.
- Nenhuma página filha ou entrada de log selecionada é alterada.
- O corpo do fold é um rollup, não uma recontação; divida um fold
  excepcionalmente grande em vez de impor uma meta arbitrária de linhas.