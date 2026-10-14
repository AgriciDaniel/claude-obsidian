---
name: wiki-lint
description: "Execute uma verificação de saúde determinística e somente leitura em um wiki Obsidian. Use para lint, verificação de saúde do vault, auditar a saúde do wiki, encontrar órfãs, encontrar links mortos, auditoria de frontmatter, auditoria de proveniência, ou auditoria do wiki. Reporta achados de grafo, links, frontmatter, ledger de proveniência, seções vazias e índices obsoletos; não raciocina de forma ampla nem repara arquivos (does not reason broadly or repair)."
---

# Executar o lint do wiki

Use o motor de lint portátil como fonte da verdade. O lint observa o estado do
vault; não cria relatórios, dashboards, canvases, stubs, nem correções.

Resolva a raiz do produto instalado a partir da localização desta skill, e não
do vault ou do diretório de trabalho atual:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

Todo link `../wiki/references/` neste arquivo resolve da mesma forma, relativo
ao diretório desta skill sob `$PRODUCT_ROOT`, nunca relativo ao diretório
`wiki/` do vault selecionado.

## Executar

Resolva o vault do usuário e então execute um destes:

```bash
python3 "$CORE" lint --vault "$VAULT"
python3 "$CORE" lint --vault "$VAULT" --format markdown
python3 "$CORE" lint --vault "$VAULT" --exclude "wiki/scratchpad/*"
```

A flag repetível `--exclude GLOB` escopa um caminho (por exemplo uma pasta de
scratch) para fora da varredura de páginas, resolução de links, órfãs,
frontmatter, seções vazias e índices obsoletos.

Use `--strict` apenas quando uma saída não zero por achados for útil em
automação. O comando permanece somente leitura de qualquer forma.

O parser determinístico entende wikilinks e embeds do Obsidian, links Markdown,
aliases, fragmentos de heading e de bloco, aliases escapados e code fences. Ele
pula diretórios com prefixo de ponto por padrão, espelhando o indexador do
próprio Obsidian. A resolução de links respeita arquivos `.gitignore` dentro do
vault (sem subprocesso `git`): quando um link é ambíguo entre uma página e um
arquivo ignorado pelo git, como um artefato de build, o candidato ignorado pelo
git é descartado. Ele reporta categorias como links mortos ou ambíguos, páginas
órfãs, lacunas de frontmatter obrigatórias (incluindo `title`), seções vazias,
entradas de índice obsoletas e violações de contrato nos ledgers de
source/claim. Reporte apenas as verificações e contagens presentes na saída
dele; não afirme que ele realizou análise semântica, estilística ou de
contradições em nível de prosa quando não realizou.

## Explicar os achados

1. Preserve os caminhos, números de linha, alvos, categorias e contagens do
   motor.
2. Agrupe os achados por impacto provável: navegação quebrada, resolução
   ambígua, qualidade de metadados e então manutenibilidade.
3. Explique que uma órfã pode ser intencional e que um basename ambíguo precisa
   de um link qualificado por caminho; não infira intenção apenas a partir do
   achado.
4. Trate achados em allowlist como política, não como prova de que o alvo existe.
5. Separe fatos determinísticos de remediações sugeridas.

Não escreva a renderização Markdown dentro do vault. Retorne-a no chat ou no
stdout.

## O reparo é uma operação separada

Nunca corrija automaticamente um resultado de lint. Depois que o usuário
escolher achados específicos para reparar:

1. Releia cada alvo e registre seu SHA-256 esperado.
2. Elabore apenas as mudanças selecionadas; não exclua nem mescle páginas sem
   consentimento explícito.
3. Construa um bundle de reparo com um novo operation ID.
4. Inspecione o bundle e mostre os caminhos exatos alterados.
5. Aplique apenas após essa revisão separada.
6. Reexecute o lint em modo somente leitura e compare os achados relevantes.

Siga [o contrato de transação de operação](../wiki/references/operation-transactions.md).
O lint em si nunca aplica essa transação e nunca faz commit no Git.

## Checkpoint

Observe o relatório determinístico, pense em causas raiz em vez de contagem de
achados, verifique os reparos propostos contra os hashes atuais e cresça
melhorando o workflow que produziu achados repetidos.