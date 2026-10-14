---
name: defuddle
description: Planeje e, com consentimento explícito de rede, use um limpador Defuddle externo opcional para extrair páginas HTTPS em forma de artigo como Markdown. Use para defuddle, limpar esta URL, remover o clutter da página, Markdown legível a partir de uma página web, ou preparar uma fonte web para ingestão posterior no wiki.
---

# Defuddle

Trate o Defuddle como um extrator externo opcional, não como uma capacidade
interna. Limpeza, captura bruta e ingestão no wiki são operações distintas.

Resolva a raiz do produto instalado a partir da localização desta skill, nunca a
partir do vault selecionado ou do diretório de trabalho do processo:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

Todo link `../wiki/references/` neste arquivo resolve da mesma forma, relativo
ao diretório desta skill sob `$PRODUCT_ROOT`, nunca relativo ao diretório
`wiki/` do vault selecionado.

Se a skill `defuddle` de `kepano/obsidian-skills` instalada separadamente
estiver disponível, prefira-a para as flags atuais da CLI. Mantenha nesta skill
as regras de privacidade, consentimento e transação.

## Contrato de segurança

- Aceite entradas remotas apenas como URLs HTTPS.
- Rejeite credenciais em URLs, fragmentos, hosts privados ou locais, endereços IP
  não públicos, caracteres de controle e parâmetros de query sensíveis.
- Nunca interpole uma URL em uma string de shell. Passe-a como um único elemento
  de argv.
- Trate redirecionamentos para um host diferente como negados até que esse host
  seja explicitamente aprovado.
- Declare que a URL e os metadados da requisição sairão da máquina. O acesso à
  rede exige consentimento explícito na requisição atual ou uma confirmação
  separada.
- Não instale um limpador, não execute um runner placeholder e não troque
  silenciosamente por outro fetcher de rede.
- Não afirme uma redução fixa de tokens ou uma qualidade de extração. Inspecione
  a saída real.

## Planeje primeiro

Crie um plano de URL inerte. Isso valida a URL e não executa nenhuma chamada de
rede:

```bash
python3 "$CORE" capture external-plan url "HTTPS_URL"
```

Reporte o host normalizado, o egress de rede, a política de redirecionamento, a
dependência externa opcional e `execute: false`. Então inspecione se este
pacote consegue encontrar um executável Defuddle configurado:

```bash
python3 "$CORE" contracts --verify --capability defuddle --vault VAULT
```

Um estado `available` significa que nenhum executável foi encontrado; pare com o
plano inerte. Um estado `configured` significa que o executável foi
descoberto, mas este pacote não tem um verificador comportamental embutido para
ele. Mostre esse estado e o motivo, identifique o caminho do executável resolvido
e exija revisão manual da proveniência, versão e argv exato antes da execução.
Nunca rotule `configured` como `verified`.

Quando indisponível ou quando a revisão manual for recusada, ofereça estes
fallbacks honestos: deixar o usuário instalar ou configurar um runner externo,
aceitar um arquivo HTML ou Markdown local em `inbox/`, ou deixar a URL na fila
para depois. Não afirme que o conteúdo foi limpo, capturado ou ingerido.

## Execute após o consentimento

Após o consentimento de rede, a detecção do estado configured e a revisão manual
do executável, invoque o executável aprovado com um argv equivalente a:

```text
defuddle parse HTTPS_URL --md
```

Capture stdout limitado em um rascunho temporário fora do estado compartilhado do
vault. Feche com falha em saída não zero, saída vazia, saída binária
inesperada, um redirecionamento não aprovado ou uma resposta que seja
claramente uma página de autenticação/erro. Preserve headings, links, code
fences, tabelas, citações e a redação da fonte; não invente conteúdo ausente.

Pré-visualize o Markdown limpo e reporte as limitações da extração. Se o usuário
pediu apenas para ler ou analisar, mantenha o resultado transitório.

## Captura bruta opcional

Quando o usuário pedir para reter a fonte limpa:

1. Resolva o vault do usuário.
2. Faça o hash dos bytes exatos e limpos com SHA-256.
3. Elabore um novo payload imutável, como `.raw/captured/<sha256>.md` e, quando
   forem necessários metadados de proveniência, um novo sidecar create-only com a
   URL normalizada, a data de recuperação, o nome e a versão do extrator, e o
   hash do conteúdo.
4. Use `expected_hashes: null` e `mode: create`. Se esse payload endereçado por
   conteúdo já existir com os mesmos bytes, reporte um no-op; nunca o
   sobrescreva.
5. Construa, inspecione e aplique um bundle de captura
   `claude-obsidian.transaction.v1` como descrito em
   [operation-transactions.md](../wiki/references/operation-transactions.md).

Não crie páginas do wiki, não atualize índices, não avalie claims e não marque a
fonte como ingerida. Invoque `wiki-ingest` como uma operação solicitada distinta
se o usuário quiser incorporar o payload capturado à base de conhecimento.