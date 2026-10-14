---
name: wiki-cli
description: "Detecte e use a interface de linha de comando oficial do Obsidian para acesso somente leitura ao vault; use para wiki-cli, Obsidian CLI, Obsidian read, Obsidian search, transporte do vault, qual transporte, detecção de transporte, backlinks, tags, ou linha de comando do Obsidian. Mutações sempre passam pelo núcleo de transações do claude-obsidian."
---

# Transporte de leitura do Obsidian CLI

Use esta skill apenas para detectar o transporte e ler ou buscar em um vault
selecionado. O executável oficial é `obsidian`; a mera presença do binário não
prova que ele está utilizável.

Resolva a raiz do produto instalado a partir da localização desta skill, e não
do vault ou do diretório de trabalho atual:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
DETECT_TRANSPORT="$PRODUCT_ROOT/scripts/detect-transport.sh"
test -f "$DETECT_TRANSPORT"
```

Todo link `../wiki/references/` neste arquivo resolve da mesma forma, relativo
ao diretório desta skill sob `$PRODUCT_ROOT`, nunca relativo ao diretório
`wiki/` do vault selecionado.

## Detectar com segurança

Sondar sem persistir estado no host:

```bash
bash "$DETECT_TRANSPORT" --peek --vault "$VAULT"
```

Confie em `available.cli.usable`, e não apenas em `present` ou no status de
saída. Uma CLI suportada ainda pode estar indisponível porque o app Obsidian não
está rodando, o acesso por linha de comando está desabilitado, ou sua resposta é
um erro. Use leituras do filesystem como fallback portátil.

Persista um `.vault-meta/transport.json` atualizado somente quando o usuário ou o
workflow de setup pedir um snapshot do transporte:

```bash
bash "$DETECT_TRANSPORT" --force --vault "$VAULT"
```

Esse arquivo é configuração de runtime derivada, não conteúdo de conhecimento.
Preserve um `manual_override` válido registrado pelo detector.

## Ler e buscar

Execute comandos oficiais da CLI a partir do vault selecionado para que o
Obsidian resolva o workspace correto. Confirme a sintaxe suportada com a CLI
instalada antes de depender de comandos opcionais. Formas típicas somente
leitura são:

```bash
(cd "$VAULT" && obsidian read path="$NOTE")
(cd "$VAULT" && obsidian search query="$QUERY")
```

Use comandos somente leitura para backlinks, tags ou resultados de Bases apenas
quando o detector reportar a CLI pronta. Caso contrário, leia os arquivos sob
`$VAULT` diretamente e use `rg` para busca. Rejeite argumentos absolutos de nota,
travessia, symlinks ou paths resolvidos fora do vault selecionado.

## Limite de mutação

Não use comandos de create, write, append, property-set, daily-append, move,
rename ou delete da CLI. Não substitua esses comandos por escritas diretas no
filesystem. Qualquer mudança de conhecimento ou configuração deve ser expressa
como uma única transação revisada através do núcleo portátil; veja
[transações de operação](../wiki/references/operation-transactions.md).

A escolha do transporte nunca muda a semântica de mutação. A CLI é uma
superfície de leitura opcional, não um gerenciador de lock, nem um motor de
transações, nem um mecanismo de checkpoint do Git.

## Checkpoint

Observe a capacidade real, pense no transporte de leitura menos complexo,
verifique se todo path resolvido permanece dentro do vault, e aceite o fallback
de filesystem quando a CLI não estiver pronta.
