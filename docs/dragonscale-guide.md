# Extensão de compatibilidade DragonScale

DragonScale é um conjunto opcional de experimentos de manutenção de memória.
O vault base não o exige. A extensão consiste em quatro ideias independentes;
sua maturidade e dependências diferem.

## Provisionamento

Pré-visualize a transação de setup apenas-create:

```bash
bash scripts/setup-dragonscale.sh --vault <vault>
```

Aplique apenas após revisar os paths ausentes:

```bash
bash scripts/setup-dragonscale.sh --vault <vault> \
  --generated-at <ISO-UTC> --approved-plan-sha256 <reviewed-sha256> --apply
```

O setup cria apenas arquivos ausentes de address-counter, tiling-threshold,
legacy-exception e legacy-manifest. Ele nunca substitui valores existentes,
baixa um modelo, altera scripts do produto, sonda um serviço ou modifica notas.

## 1. Folds extrativos de log

`wiki-fold` cria um rollup limitado a partir de entradas recentes do
`wiki/log.md`. Um fold deve ser:

- extrativo — cada afirmação aponta para uma entrada filha;
- aditivo — os filhos permanecem inalterados;
- estruturalmente idempotente — o mesmo conjunto de entrada produz a mesma
  identidade de fold;
- pré-visualizado antes de uma transação aplicar o fold, o índice e a
  atualização do log.

Folds são auxílios de navegação, não novas evidências. Apenas a operação de
fold deve ser apagada ou revertida se um rollup for inútil.

## 2. Endereços estáveis

Operações modernas solicitam endereços através do bundle principal de
transação. O motor aloca o contador, injeta o frontmatter da página e
atualiza o mapa de endereços legado dentro do mesmo journal. Não chame o
alocador legado para novos fluxos de ingestão.

`scripts/allocate-address.sh` permanece um diagnóstico de compatibilidade
somente-leitura para vaults mais antigos. Ele aceita um vault explícito e
nunca cria nem adquire um lock. Sua saída não substitui as garantenas de
hash esperado, alocação, concorrência ou rollback do motor de transação.

## 3. Diagnósticos de tiling semântico

`scripts/tiling-check.py` embeda páginas elegíveis através de um modelo
Ollama e compara cada par distinto de páginas para possível duplicação. É
opcional e seus limiares de seed não são calibrados. Uma pontuação é um sinal
de revisão, não prova de que duas páginas devem ser mescladas.

Pré-visualize sem escrever um relatório:

```bash
python3 scripts/tiling-check.py --vault <vault> --peek
```

Hosts remotos de Ollama são recusados a menos que `--allow-remote-ollama` seja
fornecido. Calibre os limiares em exemplos rotulados do vault selecionado
antes de usá-los como política. Se Ollama ou o modelo estiver ausente,
reporte esse estado de capacidade; não implique que a verificação rodou.

## 4. Pontuação de fronteira

`scripts/boundary-score.py` classifica páginas que podem merecer mais
pesquisa usando a estrutura atual do grafo e a recência. É determinístico e
somente-leitura:

```bash
python3 scripts/boundary-score.py --vault <vault> --json --top 10
```

A pontuação propõe atenção; ela não estabelece importância ou verdade. Use
um candidato como tópico de autoresearch apenas após revisar seus links
subjacentes e o orçamento de pesquisa.

## Falha e recuperação

- Um conflito de setup significa que um path esperado mudou; gere um novo
  plano.
- Um setup interrompido usa o comando normal de recuperação de transação.
- Um contador legado corrompido deve ser reconstruído a partir dos endereços
  observados apenas após verificar duplicatas e o mapa de endereços.
- Um cache de tiling ou índice BM25 é derivado e pode ser regenerado. Páginas
  de fonte e ledgers de proveniência não são caches derivados.
- Desabilitar DragonScale não exige reescrita em massa. Pare de invocar os
  helpers opcionais; as páginas de fold e endereços existentes permanecem
  conteúdo normal do vault.

## Verificação

Execute os testes herméticos relevantes ou a suíte completa:

```bash
make test
```

A maturidade da capacidade é baseada em verificações executadas, não na
presença de um arquivo de setup. Mantenha cada mecanismo opcional e falhe de
forma segura quando seus pré-requisitos estiverem indisponíveis.
