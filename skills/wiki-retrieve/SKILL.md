---
name: wiki-retrieve
description: "Construa e consulte um índice de recuperação BM25 contextual local do vault, com reranking cosine multilíngue opcional da Nomic; use para retrieve, recuperação híbrida, BM25, rerank, recuperação contextual, busca de chunks, busca no vault, busca semântica, encontrar passagens relevantes, ou diagnóstico de recuperação. Os caches derivados ficam sob .vault-meta, o egress remoto exige consentimento explícito, e um reranking indisponível cai de forma determinística."
---

# Recuperar passagens relevantes

Esta extensão deriva dados de busca de `wiki/` para `.vault-meta/`. Ela nunca
altera notas canônicas. Passe sempre o vault selecionado de forma explícita.

Resolva a raiz do produto instalado a partir da localização desta skill, e não
do vault ou do diretório de trabalho atual:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
PREFIX="$PRODUCT_ROOT/scripts/contextual-prefix.py"
BM25="$PRODUCT_ROOT/scripts/bm25-index.py"
RETRIEVE="$PRODUCT_ROOT/scripts/retrieve.py"
RERANK="$PRODUCT_ROOT/scripts/rerank.py"
test -f "$PREFIX" && test -f "$BM25" && test -f "$RETRIEVE" && test -f "$RERANK"
```

## Pipeline

1. `contextual-prefix.py` divide páginas em fronteiras de parágrafo e armazena o
   chunk bruto mais um prefixo curto em nível de página.
2. `bm25-index.py` constrói um índice BM25 local, baseado apenas na biblioteca
   padrão, sobre o texto contextualizado.
3. `retrieve.py` seleciona candidatos do BM25, opcionalmente faz rerank deles,
   rejeita registros inválidos, deduplica por página e retorna paths e snippets.
4. O chamador lê as páginas retornadas e faz a síntese; a saída da recuperação,
   por si só, não é evidência.

## Provisionar localmente

Pré-visualize primeiro, depois construa prefixes sintéticos sem egress de rede:

```bash
python3 "$PREFIX" --vault "$VAULT" --all --no-llm --peek
python3 "$PREFIX" --vault "$VAULT" --all --no-llm
python3 "$BM25" --vault "$VAULT" build
python3 "$RETRIEVE" --vault "$VAULT" "wiki" --top 1 --no-rerank --explain
```

Arquivos de chunk e de índice são estado de runtime descartável. O
prefixamento incremental pula registros cujos hashes de chunk e de página ainda
correspondem. Uma varredura completa remove os registros excedentes de páginas
excluídas, e o prefixador invalida o índice BM25 antes de mudar seu conjunto de
chunks, para que um índice misto e obsoleto não seja servido. Operações de
build de prefix e de BM25 compartilham o lock de mutação de todo o vault com
todos os outros escritores; um vault ocupado falha fechado em vez de publicar
um índice parcial.

## Privacidade do prefixo contextual

Prefixos sintéticos usam apenas frontmatter local e o texto da página. A API da
Anthropic e os níveis via subprocesso `claude` podem enviar o corpo das páginas
para fora da máquina e portanto exigem o consentimento explícito do usuário mais
`--allow-egress`. Nunca infira consentimento a partir de uma API key ou de um
binário instalado. Pré-visualize o escopo primeiro e declare qual provider vai
receber quais dados.

Endpoints remotos do Ollama também exigem aprovação explícita e
`--allow-remote-ollama`; o reranker padrão aceita apenas localhost.

## Consultar

Para uma busca estritamente somente leitura, use o índice BM25 pré-construído:

```bash
python3 "$RETRIEVE" --vault "$VAULT" "$QUERY" --top 5 --no-rerank --explain
```

Para um rerank explicitamente solicitado, omita `--no-rerank`. O padrão é o
modelo multilíngue `nomic-embed-text-v2-moe` do Ollama (aproximadamente 958 MB);
o produto nunca o baixa automaticamente. Para usar um modelo v1.5 menor e já
instalado, orientado ao inglês, passe `--model nomic-embed-text` explicitamente.
Modelos Nomic usam `search_query:` para a query e `search_document:` para o
texto candidato. O Nomic v2 tem um contexto de entrada de 512 tokens e o Ollama
trunca por padrão embeddings mais longos; o BM25 ainda pontua o chunk completo.
Embeddings são cacheados por modelo exato, esquema de entrada e hash da entrada
prefixada exata. Um serviço Ollama local ausente, um modelo selecionado ausente,
um vetor inutilizável ou qualquer falha de embedding de candidato faz o
conjunto completo de resultados cair para a ordem original do BM25; nunca se
misturam escalas de score cosine e BM25.

A entrada da query é limitada a 8.000 caracteres normalizados, e as contagens de
resultado devem ficar entre 1 e 1.000. Queries grandes demais e limites inválidos
falham com um erro de uso acionável, em vez de parecerem uma busca bem-sucedida
e vazia. Uma requisição de modelo sem tag casa apenas com o nome instalado sem
tag ou com seu alias `:latest`; selecione explicitamente qualquer outra tag.

Use diagnósticos diretos quando necessário:

```bash
python3 "$BM25" --vault "$VAULT" stats
python3 "$BM25" --vault "$VAULT" query "$QUERY" --top 10
python3 "$RERANK" --vault "$VAULT" "$QUERY" --peek
python3 "$RERANK" --vault "$VAULT" "$QUERY" --model nomic-embed-text --peek
```

## Regras de integridade

- Aceite apenas paths relativos de chunk e de página cujos alvos resolvidos
  permaneçam sob `$VAULT/.vault-meta/chunks/` e `$VAULT/wiki/`,
  respectivamente.
- Rejeite registros de chunk legados sem hash e exija que os hashes do corpo do
  chunk, da página e do índice correspondam antes de um registro cacheado poder
  ser construído ou servido.
- Rejeite paths absolutos, fugas por symlink, páginas ausentes, IDs de chunk
  divergentes, hashes de página alterados e pares de hash índice/chunk obsoletos.
- Faça rerank do conjunto completo de candidatos, depois deduplique por página e
  então aplique `--top`.
- Um índice vazio é um estado honesto de "sem resultado". Um índice ausente ou
  corrompido faz `retrieve.py` sair com código 10 junto de um comando de rebuild
  estável; os chamadores caem para o caminho padrão de query/busca de texto do
  vault e não fabricam correspondências.
- Não cite percentuais de benchmark a menos que um benchmark reproduzível e
  específico do vault os tenha produzido.

## Checkpoint

Observe a prontidão dos caches e os limites de privacidade, pense se o ranking
precisa ser lexical ou semântico, verifique os paths retornados e a atualidade
da fonte, e cresça medindo as falhas de recuperação contra um conjunto local de
queries mantido.
