---
name: wiki-mode
description: "Leia ou configure a metodologia de arquivamento do vault e sugira destinos para a criação planejada de conhecimento sob Generic, LYT, PARA ou Zettelkasten. Use para modo wiki, modo de metodologia, qual é o meu modo de vault, definir o modo do vault, mudar para PARA, usar LYT, setup do Zettelkasten, mudar de modo, configurar modo, ou roteamento por metodologia. Esta skill não salva conteúdo nem migra notas."
---

# Rotas por metodologia do vault

Esta skill retorna sugestões de arquivamento. Ela não escreve páginas de
conhecimento nem move notas existentes. Se `.vault-meta/mode.json` estiver
ausente, use `generic`. Se o arquivo existir mas for inválido, falhe fechado
(fail closed) e repare-o através de uma operação de configuração revisada antes
de sugerir rotas; nunca substitua Generic silenciosamente por uma configuração
de usuário corrompida.

Resolva a raiz do produto instalado a partir da localização desta skill, e não
do vault ou do diretório de trabalho atual:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
MODE_HELPER="$PRODUCT_ROOT/scripts/wiki-mode.py"
test -f "$CORE" && test -f "$MODE_HELPER"
```

Todo link `../wiki/references/` neste arquivo resolve da mesma forma, relativo
ao diretório desta skill sob `$PRODUCT_ROOT`, nunca relativo ao diretório
`wiki/` do vault selecionado.

## Ler e rotear com segurança

Selecione o vault sempre de forma explícita:

```bash
python3 "$MODE_HELPER" --vault "$VAULT" get
python3 "$MODE_HELPER" --vault "$VAULT" config
python3 "$MODE_HELPER" --vault "$VAULT" route concept "Concept name"
python3 "$MODE_HELPER" --vault "$VAULT" route source "Source title"
```

O helper valida o vault selecionado, confina paths, sanitiza nomes e imprime
apenas uma sugestão. Uma skill chamadora pode sobrescrever a sugestão quando o
usuário fornecer um projeto, uma área, um MOC ou uma nota-pai mais específico,
mas ainda deve aplicar suas escritas definitivas através de uma única transação
de operação.

| Mode | Intenção do roteamento |
|---|---|
| `generic` | Pastas por tipo, como sources, entities, concepts e sessions. |
| `lyt` | Notas atômicas sob `wiki/notes/`, conectadas por MOCs. |
| `para` | Projects, Areas, Resources ou Archives escolhidos por acionabilidade. |
| `zettelkasten` | Notas atômicas planas, com identificadores ordenáveis por tempo, resistentes a colisão e links explícitos. |

Use os templates sob `templates/` como orientação estrutural, não como autoridade
para sobrescrever convenções do usuário.

## Mudar o modo

Uma mudança de modo é uma única operação de configuração, primeiramente em
dry-run:

1. Leia o `.vault-meta/mode.json` atual, ou parta da config padrão do helper
   quando ele estiver ausente.
2. Valide o modo solicitado como exatamente `generic`, `lyt`, `para` ou
   `zettelkasten`. Preserve os demais settings específicos do modo.
3. Escolha e retenha um timestamp UTC fixado e um operation ID para os dois
   comandos.
4. Pré-visualize a transação de configuração canônica; o comando registra o hash
   atual do alvo e limita a escrita a `.vault-meta/mode.json`:

   ```bash
   python3 "$CORE" mode set "$MODE" --vault "$VAULT" \
     --generated-at "$GENERATED_AT" --operation-id "$OPERATION_ID"
   ```

5. Mostre o modo antigo, o modo novo, o caminho exato alterado e a
   pré-visualização completa. Copie o `approved_plan_sha256` somente após a
   revisão.
6. Aplique regenerando exatamente esse plano vinculado ao vault:

   ```bash
   python3 "$CORE" mode set "$MODE" --vault "$VAULT" \
     --generated-at "$GENERATED_AT" --operation-id "$OPERATION_ID" \
     --approved-plan-sha256 "$APPROVAL_SHA256" --apply
   ```

Siga [o contrato de transação de operação](../wiki/references/operation-transactions.md).
Não use a ação `set` de escrita direta legada de `scripts/wiki-mode.py`, nem um
script de setup para contornar este workflow.

Mudar o modo afeta o roteamento apenas de operações futuras. Nunca crie pastas
em massa, mova notas, reescreva wikilinks ou migre páginas existentes como
efeito colateral. Se a migração for solicitada depois, planeje e revise-a como
uma operação distinta, com seus próprios hashes e transação.

## Checkpoint

Observe a estrutura atual do usuário, pense em como ele recupera e age sobre as
notas, verifique algumas rotas propostas antes de mudar a configuração, e cresça
revisitando o modo apenas quando surgir um atrito real de arquivamento.
