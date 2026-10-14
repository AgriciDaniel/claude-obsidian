---
name: canvas
description: Crie, inspecione e atualize boards Obsidian JSON Canvas com nós de texto, arquivo, link, grupo e aresta. Use para status de canvas, listas de canvas, mapas visuais, zonas, layouts espaciais, adicionar notas do vault ou mídia a um arquivo .canvas, e pedidos como criar canvas, adicionar ao canvas ou colocar isto no canvas.
---

# Canvas

Trate um canvas como um documento JSON Canvas com escopo de vault. Mantenha as
leituras somente leitura e roteie toda mutação solicitada por uma única
transação recuperável.

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

## Escolher a fonte de sintaxe

Prefira a skill `json-canvas` de `kepano/obsidian-skills` instalada
separadamente para detalhes de formato. Caso contrário, leia
[references/canvas-spec.md](references/canvas-spec.md). O padrão aberto é
[JSON Canvas 1.0](https://jsoncanvas.org/spec/1.0/).

Use esta skill para o workflow do vault e a segurança de transação, mesmo
quando uma skill de sintaxe upstream estiver disponível.

## Escopo

- Resolva o vault do usuário antes de ler. Nunca o derive de arquivos do plugin.
- Armazene os boards em `wiki/canvases/`; use `wiki/canvases/main.canvas` apenas
  como padrão quando o usuário não nomeou um board.
- Trate `wiki/canvases/index.md` como um catálogo opcional. Atualize-o somente
  quando um canvas for criado, renomeado ou removido.
- Use caminhos relativos ao vault em `file` e `background`; rejeite caminhos
  absolutos, travessia com `..`, atalhos de home e caminhos que escapem por
  symlinks.
- Referencie apenas arquivos já dentro do vault. Se uma capacidade opcional de
  captura ou mídia for detectada, componha com ela e consuma o caminho relativo
  ao vault que ela retornar. Não assuma um plugin, comando ou log de sessão
  específico, e não baixe nem copie assets nesta skill.
- Use nós `link` para URLs. Aceite apenas URLs HTTPS; um nó link não concede
  permissão para buscar a página. Criar o JSON dele não faz nenhuma requisição,
  mas abri-lo no Obsidian pode buscar metadados Open Graph do host daquela URL.
  Divulgue esse egress em tempo de renderização e confirme se é aceitável; caso
  contrário use um nó text contendo a URL.

## Operações somente leitura

Para pedidos de status ou lista, faça o parse dos arquivos `.canvas`
selecionados e reporte contagens de nós, rótulos de grupo, endpoints de aresta
quebrados e alvos de arquivo relativos ao vault que estão ausentes. Se o canvas
padrão estiver ausente, reporte esse fato e ofereça uma pré-visualização de
criação; não o crie durante um pedido de status.

## Elaborar uma mutação

1. Leia o canvas inteiro e qualquer alvo de catálogo. Registre cada SHA-256
   esperado, ou `null` para um arquivo que precisa estar ausente.
2. Preserve campos JSON desconhecidos e a ordem existente dos arrays. O array de
   nós é o z-order de baixo para cima.
3. Elabore os nós ou arestas pedidos:
   - Dê a cada nó e aresta um ID único. Prefira um ID hexadecimal minúsculo
     aleatório de 16 caracteres e verifique que ele não está em uso.
   - Exija valores inteiros `x`, `y`, `width` e `height` para cada nó.
   - Use `text`, `file`, `link` ou `group` exatamente como definidos pelo JSON
     Canvas.
   - Exija que todo `fromNode` e `toNode` referencie um nó existente ou
     recém-elaborado.
4. Posicione o novo conteúdo de propósito. Um grupo é um contêiner visual, não um
   pai. Use 20 px de padding interno e 40 px de vão, quebrar para uma nova linha
   quando necessário e pré-visualize qualquer expansão de grupo.
5. Serialize JSON UTF-8 válido com arrays de nível superior `nodes` e `edges`.

Exemplos mínimos de nó:

```json
{
  "nodes": [
    {
      "id": "6f0ad84f44ce9c17",
      "type": "text",
      "text": "# Research map\n\nA concise orientation card.",
      "x": 0,
      "y": 0,
      "width": 400,
      "height": 180
    },
    {
      "id": "a1b2c3d4e5f67890",
      "type": "file",
      "file": "wiki/concepts/Contextual Retrieval.md",
      "x": 460,
      "y": 0,
      "width": 400,
      "height": 240
    }
  ],
  "edges": []
}
```

Use `file` mais o opcional `subpath: "#Heading"` para notas, imagens, PDFs e
outros arquivos do vault. Use `url` apenas em um nó `link`. Escape quebras de
linha em strings JSON como `\n`, não como texto literal de backslash mais `n`.

## Pré-visualizar e aplicar

Valide antes de mostrar a pré-visualização:

- o JSON faz parse e usa tipos de nó suportados.
- os IDs são únicos e os endpoints de aresta existem;
- as dimensões são inteiros positivos;
- os caminhos de file e background são seguros, relativos ao vault e estão
  presentes;
- nós novos não se sobrepõem nem transbordam de forma indesejada o grupo pedido.

Construa um bundle `claude-obsidian.transaction.v1` com operation type `canvas`.
Inclua o canvas e o catálogo nesse mesmo bundle quando o catálogo mudar. Leia
[operation-transactions.md](../wiki/references/operation-transactions.md), então
inspecione o bundle antes de aplicá-lo:

```bash
python3 "$CORE" transaction inspect BUNDLE --vault VAULT
# Set APPROVAL_SHA256 to the inspect result's approval_sha256 after review.
python3 "$CORE" transaction apply BUNDLE --vault VAULT \
  --approved-plan-sha256 "$APPROVAL_SHA256"
```

Para remoções, substituições, renomeações ou outras mudanças destrutivas,
obtenha consentimento explícito após apresentar a pré-visualização. Reporte o
operation ID, os caminhos exatos alterados, o nome do board, os IDs dos nós e as
posições finais. Não faça commit no Git.