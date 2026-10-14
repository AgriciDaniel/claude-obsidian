---
name: wiki-fold
description: "Crie um rollup delimitado, extrativo e estruturalmente idempotente de entradas recentes do log do wiki Obsidian, com pré-visualização dry-run por padrão e uma única aplicação opcional via transação. Use para compressão manual do log sem modificar as páginas filhas. Gatilhos: dobrar o log, rodar um fold, rodar wiki-fold, rollup do log, agregar entradas de log, commitar o fold."
---

# Fold extrativo do log

Crie um rollup aditivo de entradas brutas de `wiki/log.md`. Nunca modifique,
mova ou apague entradas filhas ou suas páginas. Não faça fold de folds nem
dispare um fold automaticamente.

Resolva o núcleo portátil a partir da instalação desta skill. Resolva o vault do
usuário por `--vault` explícito, `CLAUDE_OBSIDIAN_VAULT`, config do workspace e
então descoberta no diretório atual. Nunca trate a raiz do plugin/produto como
um vault.

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

Todo link `../wiki/references/` neste arquivo resolve da mesma forma, relativo
ao diretório desta skill sob `$PRODUCT_ROOT`, nunca relativo ao diretório
`wiki/` do vault selecionado.

Esta skill não precisa de egress de rede. Não chame serviços externos.

## Selecionar um intervalo delimitado

Use o expoente de lote `k` com tamanho `2^k`; por padrão `k=4`. Um intervalo de
entradas explícito pode sobrescrevê-lo. Se existirem menos entradas do que as
solicitadas, reporte a diferença e pare em vez de dobrar um lote parcial.

Leia as entradas de log selecionadas por completo. Leia as páginas filhas
referenciadas apenas quando o log não tiver contexto suficiente: mire em 0-10
leituras, com teto rígido de 15. Páginas ausentes permanecem como registros
explícitos `page_missing`.

Derive o ID estrutural apenas a partir das entradas:

```text
fold-k{K}-from-{EARLIEST-DATE}-to-{LATEST-DATE}-n{COUNT}
```

Se `wiki/folds/{FOLD_ID}.md` já existir, retorne um no-op. Substituí-lo exige um
pedido explícito de force e uma proposta `replace` revisada separadamente.

## Elabore de forma extrativa

Siga [fold-template.md](references/fold-template.md). Toda entrada filha do log
precisa ter um `child_key` determinístico no frontmatter e exatamente uma linha
correspondente na tabela Child Entries. Não deduplique os filhos por página,
embora a lista final de links Child Pages possa ser deduplicada.

Todo outcome deve nomear sua entrada de origem. Todo número deve ser verificável
na entrada selecionada. Um tema entre entradas deve nomear pelo menos duas
entradas que contribuam. Prefira `ambiguous in source` ou `source missing` a
invenção. Quando uma página filha e a entrada de log divergirem, preserve ambas e
identifique a inconsistência; a entrada de log é a fonte primária do fold.

Rode estas verificações antes de propor qualquer escrita:

- ID determinístico e contagem exata de entradas;
- bijeção entre frontmatter e tabela;
- rastreabilidade numérica;
- citação de origem para todo outcome e tema;
- nenhuma mudança em um filho, source, ledger de source ou ledger de claim.

Um fold não adiciona nova evidência factual, então não promove avaliações de
claim nem cria registros de source. Reporte contradições descobertas para revisão
posterior em vez de editar claims canônicos.

## Pré-visualize por padrão

Retorne o rascunho completo do fold, o ID, o intervalo de filhos, o orçamento de
leituras e os caminhos alterados propostos sem modificar o vault. Agentes
paralelos podem verificar entradas filhas e devolver extrações, mas apenas o
orquestrador monta o fold; workers nunca escrevem.

Quando o usuário disser explicitamente para aplicar ou commitar o fold, construa
um bundle `claude-obsidian.transaction.v1` com `operation_type: fold`. Leia
[o contrato de transação](../wiki/references/operation-transactions.md). Acople:

- `wiki/folds/{FOLD_ID}.md` em modo `create` por padrão;
- a entrada de catálogo do fold em `wiki/index.md`;
- uma nova entrada de fold no topo do arquivo em `wiki/log.md`.

Não atualize `wiki/hot.md`. Registre pré-condições SHA-256 para os três alvos.
Não use Write/Edit do host, escritas de transporte do Obsidian, locks
depreciados, commits automáticos, nem um apply por arquivo.

Inspecione antes do único apply:

```bash
python3 "$CORE" transaction inspect /path/to/fold-bundle.json --vault /path/to/vault
# Set APPROVAL_SHA256 to the inspect result's approval_sha256 after review.
python3 "$CORE" transaction apply /path/to/fold-bundle.json --vault /path/to/vault \
  --approved-plan-sha256 "$APPROVAL_SHA256"
```

Reporte o operation ID e os caminhos exatos alterados. O bundle e o ID
idênticos são idempotentes. Em exit 75, releia e reconstrua; após interrupção,
use `transaction recover`.

O histórico Git é uma ação separada e opcional:

```bash
python3 "$CORE" checkpoint OPERATION_ID --vault /path/to/vault
```

Observe todas as entradas selecionadas, verifique a rastreabilidade e as
contagens e então cresça o rollup apenas a partir do que os filhos realmente
dizem.