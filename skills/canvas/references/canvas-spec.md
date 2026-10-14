# Especificação JSON do Obsidian Canvas

Arquivos canvas são JSON com duas chaves de nível superior: `nodes` (array) e `edges` (array).
O Obsidian lê e escreve esses arquivos como arquivos JSON UTF-8 com extensão `.canvas`.

Esta referência está alinhada com a [especificação aberta JSON Canvas 1.0](https://jsoncanvas.org/spec/1.0/). Todas as estruturas suportam campos adicionais arbitrários (`[key: string]: any`) para compatibilidade futura. O Obsidian preserva campos desconhecidos ao ler e escrever arquivos canvas.

**Formato de ID**: o JSON Canvas 1.0 exige que o ID de cada node e de cada edge seja uma string
única; não prescribe comprimento nem conjunto de caracteres. Como convenção de produto,
novas mutações desta skill preferem IDs hexadecimais minúsculos aleatórios de 16 caracteres
(por exemplo, `"a1b2c3d4e5f67890"`) e verificam a unicidade.
IDs descritivos nos exemplos mais longos abaixo são apenas rótulos de legibilidade, não a regra de geração.

---

## Sistema de coordenadas

```
        x increases →
   ┌─────────────────────────────────
   │  (-920, -2400)      (0, -2400)
   │
y  │  (-920, 0)          (0, 0) ← origin
↓  │
   │  (-920, 540)        (500, 540)
```

- **Origem** (0, 0) é o centro da viewport do canvas.
- **x aumenta para a direita.** x negativo = à esquerda do centro.
- **y aumenta para baixo.** y negativo = acima do centro.
- `x` e `y` do node são o **canto superior esquerdo** do node, não o centro.
- O Obsidian faz pan para enquadrar todos os nodes na primeira abertura.

---

## Tipos de node

### Node de texto

Renderiza conteúdo markdown como um cartão estilizado.

```json
{
  "id": "text-title-4821",
  "type": "text",
  "text": "# Heading\n\nParagraph with **bold** and `code`.",
  "x": -400,
  "y": -300,
  "width": 400,
  "height": 120,
  "color": "6"
}
```

- `text`: string markdown. Use `\n` para quebras de linha.
- Tamanho mínimo legível: width ≥ 200, height ≥ 60.
- `color` é opcional. Omita para o padrão (sem cor).

---

### Node de arquivo

Renderiza uma imagem, PDF, nota markdown ou outro arquivo do vault embutido.

```json
{
  "id": "img-cover-7823",
  "type": "file",
  "file": "_attachments/images/example.png",
  "x": -900,
  "y": -100,
  "width": 420,
  "height": 236
}
```

- `file`: **caminho relativo ao vault** (não absoluto, não `~/`).
- Suportados: `.png` `.jpg` `.webp` `.gif` `.pdf` `.md` `.canvas`
- Para arquivos `.md`: renderiza como cartão de pré-visualização.
- Para arquivos `.pdf`: renderiza a primeira página como pré-visualização.
- Como todo node genérico, um node de arquivo pode incluir o campo opcional `color`.
  Omita-o para a aparência padrão.

---

### Node de grupo (Zone)

Uma região retangular rotulada. Não recorta nem contém nodes. É um guia visual.
Nodes colocados "dentro" de um grupo apenas estão posicionados dentro de sua bounding box.

```json
{
  "id": "zone-branding-3391",
  "type": "group",
  "label": "Brand Identity",
  "x": -920,
  "y": -880,
  "width": 1060,
  "height": 290,
  "color": "6",
  "background": "_attachments/images/grid-bg.png",
  "backgroundStyle": "cover"
}
```

- `label`: exibido no topo da caixa do grupo.
- `color`: colore a borda e o rótulo do grupo.
- `background` *(opcional)*: caminho relativo ao vault de uma imagem de fundo para o grupo.
- `backgroundStyle` *(opcional)*: como o fundo é renderizado.
  - `"cover"`: preenche o grupo, cortando se necessário (comportamento padrão)
  - `"ratio"`: preserva a proporção de aspecto, cabendo dentro do grupo
  - `"repeat"`: repete a imagem em mosaico
- Grupos não afetam o layout automático: são puramente contêineres visuais.

---

### Node de link

Renderiza uma URL da web como um cartão de pré-visualização embutido.

```json
{
  "id": "link-karpathy-2233",
  "type": "link",
  "url": "https://github.com/karpathy",
  "x": 200,
  "y": -300,
  "width": 400,
  "height": 120
}
```

- `url`: deve ser uma URL `https://` válida.
- O Obsidian busca a pré-visualização do Open Graph (título, descrição, miniatura).
- Escrever o node em si não faz nenhum fetch. Abrir ou renderizá-lo no
  Obsidian pode contatar o host da URL, então divulgue essa saída de rede antes e use
  um node de texto quando a busca da pré-visualização não for aceitável.

---

## Edges

Conexões entre nodes. Normalmente vazias em canvases de humor.

```json
{
  "id": "e-hub-cidx",
  "fromNode": "hub",
  "fromSide": "right",
  "fromEnd": "none",
  "toNode": "c-idx",
  "toSide": "left",
  "toEnd": "arrow",
  "label": "concepts",
  "color": "5"
}
```

**Campos obrigatórios**: `id`, `fromNode`, `toNode`. Todo o resto é opcional.

- `fromNode` / `toNode`: IDs dos nodes de origem e de destino.
- `fromSide` / `toSide` *(opcional)*: `"top"` `"bottom"` `"left"` `"right"`. Se omitido, o Obsidian calcula automaticamente o melhor lado com base nas posições relativas dos nodes.
- `fromEnd` *(opcional)*: terminação no lado de origem. O padrão é `"none"`. Valores: `"none"` | `"arrow"`.
- `toEnd` *(opcional)*: terminação no lado de destino. **O padrão é `"arrow"`**: observe o padrão assimétrico em relação a `fromEnd`. Valores: `"none"` | `"arrow"`.
- `label` *(opcional)*: texto exibido sobre o edge.
- `color` *(opcional)*: a mesma paleta de cores dos nodes (`"1"`–`"6"` ou hex).

A maioria dos edges representa relações dirigidas, então os padrões assimétricos (`fromEnd: "none"`, `toEnd: "arrow"`) produzem uma única seta apontando da origem para o destino sem especificar nada explicitamente.

---

## Referência de cores

| Código | Cor | Hex (aprox.) | Caso de uso |
|------|-------|-------------|-------------|
| `"1"` | Vermelho / Tomate | #e03e3e | Avisos, arquivo |
| `"2"` | Laranja | #d09035 | Trabalho em andamento |
| `"3"` | Amarelo / Ouro | #d0a023 | WIP, notas |
| `"4"` | Verde / Teal | #448361 | Conteúdo, fontes |
| `"5"` | Azul / Ciano | #3ea7d3 | Navegação, informação |
| `"6"` | Roxo / Violeta | #9063d2 | Título, identidade |

Omita `color` inteiramente para o padrão (sem cor de borda, rótulo transparente).

---

## Diretrizes de dimensionamento de imagens

Calcule a partir das dimensões reais da imagem usando PIL ou `identify`:

```bash
python3 -c "from PIL import Image; img=Image.open('path.png'); print(img.width, img.height)"
# or
identify -format '%w %h' path.png
```

| Proporção de aspecto | Condição | Largura no canvas | Altura no canvas |
|----------------------|-----------|--------------------|-------------------|
| 16:9 (panorâmico) | proporção 1.6–2.0 | 420 | 236 |
| 2:1 (ultrapanorâmico) | proporção > 2.0 | 440 | 220 |
| 4:3 | proporção 1.2–1.6 | 380 | 285 |
| 1:1 (quadrado) | proporção 0.9–1.1 | 280 | 280 |
| 3:4 | proporção 0.6–0.9 | 240 | 320 |
| 9:16 (retrato) | proporção < 0.6 | 200 | 356 |
| PDF | qualquer | 400 | 520 |
| Desconhecida | fallback | 320 | 240 |

---

## Pseudocódigo de posicionamento automático

```
function place_node(canvas, zone_label, new_w, new_h):
  zone = find group node where label == zone_label
  padding = 20

  if zone not found:
    max_y = max(n.y + n.height for n in canvas.nodes) + 60
    return (-400, max_y)

  # Nodes visually inside zone
  inside = [n for n in canvas.nodes
            if n.type != 'group'
            and zone.x <= n.x < zone.x + zone.width
            and zone.y <= n.y < zone.y + zone.height]

  if inside is empty:
    return (zone.x + padding, zone.y + padding)

  # Rightmost point in zone
  rightmost = max(n.x + n.width for n in inside)
  next_x = rightmost + 40

  if next_x + new_w > zone.x + zone.width - padding:
    # Overflow → new row
    bottom_of_row = max(n.y + n.height for n in inside)
    return (zone.x + padding, bottom_of_row + padding)

  # Same row
  row_y = min(n.y for n in inside)  # align to top of existing row
  return (next_x, row_y)
```

---

## Exemplo completo: canvas com duas zones

```json
{
  "nodes": [
    {
      "id": "title-0001",
      "type": "text",
      "text": "# Brand Reference\n\n**AI Marketing Hub** visual assets",
      "x": -920, "y": -2440, "width": 560, "height": 180, "color": "6"
    },
    {
      "id": "zone-logos",
      "type": "group",
      "label": "Logos & Icons",
      "x": -920, "y": -2200, "width": 1800, "height": 320, "color": "6"
    },
    {
      "id": "img-logo-pro",
      "type": "file",
      "file": "_attachments/images/example.png",
      "x": -900, "y": -2180, "width": 420, "height": 236
    },
    {
      "id": "img-icon-free",
      "type": "file",
      "file": "_attachments/images/example-icon.png",
      "x": -440, "y": -2180, "width": 280, "height": 280
    },
    {
      "id": "zone-covers",
      "type": "group",
      "label": "Skill Covers",
      "x": -920, "y": -1820, "width": 1800, "height": 340, "color": "3"
    },
    {
      "id": "img-seo",
      "type": "file",
      "file": "_attachments/images/example-cover.png",
      "x": -900, "y": -1800, "width": 420, "height": 236
    }
  ],
  "edges": []
}
```

---

## Erros comuns

- **Formato de caminho errado**: use `_attachments/images/file.png`, não um caminho absoluto do host
- **Colisão de ID**: sempre leia os IDs existentes antes de gerar um novo
- **Confusão com y negativo**: `y: -2400` está ACIMA de `y: -1000` (mais negativo = mais alto)
- **Grupo não recorta**: colocar um node "dentro" de um grupo é apenas posicioná-lo dentro da bounding box do grupo: não há relação pai-filho no JSON
- **height ausente em nodes de texto**: o Obsidian renderiza o texto mas pode cortá-lo se o height for pequeno demais. Use height ≥ linhas-de-conteúdo × 24.