---
name: wiki
description: "Inicialize, adote e roteie o trabalho em um vault de conhecimento Obsidian separado por meio do núcleo portátil do claude-obsidian. Use para setup do vault, scaffolding, seleção de workspace, configuração entre projetos, ou para escolher a sub-skill wiki correta. Gatilhos: /wiki, configurar o wiki, criar o scaffolding do vault, criar base de conhecimento, adotar este vault, vault Obsidian, setup de segundo cérebro, wiki persistente."
---

# Orquestração do wiki

Trate o produto instalado como código e o vault do usuário selecionado como
dados. Nunca use a raiz do plugin/produto como vault, mesmo quando o diretório
atual for o checkout do produto.

Resolva o núcleo portátil a partir da instalação desta skill e invoque-o por
caminho absoluto:

```bash
CORE=/absolute/product/root/scripts/claude-obsidian.py
python3 "$CORE" --help
```

Resolva o vault nesta ordem: `--vault` explícito, `CLAUDE_OBSIDIAN_VAULT`, o
`.claude-obsidian.json` mais próximo e então um vault inicializado não ambíguo no
diretório atual ou acima dele. Falhe de forma fechada quando a seleção estiver
ausente ou ambígua.

O setup de base não exige egress de rede. Não busque templates, plugins ou
conteúdo remoto a menos que o usuário aprove separadamente os destinos e o
orçamento.

## Configurar um vault

Use os comandos de setup determinísticos. Ambos são dry-run por padrão.

Para um vault novo e separado:

```bash
python3 "$CORE" init /absolute/path/to/vault \
  --generated-at <ISO-UTC> --operation-id init-reviewed
python3 "$CORE" init /absolute/path/to/vault \
  --generated-at <ISO-UTC> --operation-id init-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Para um vault Obsidian existente:

```bash
python3 "$CORE" adopt /absolute/path/to/vault \
  --generated-at <ISO-UTC> --operation-id adopt-reviewed
python3 "$CORE" adopt /absolute/path/to/vault \
  --generated-at <ISO-UTC> --operation-id adopt-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Antes de `--apply`, mostre o caminho selecionado e a prévia de caminhos
alterados, e então passe o `approved_plan_sha256` emitido sem alterações. Não
use `--force` a menos que o usuário tenha revisado os conflitos e aprovado
explicitamente a substituição. O setup é não destrutivo por padrão e não cria
remote Git upstream.

Se o usuário pedir um scaffolding específico de domínio, estabeleça a base
primeiro e então leia [modes.md](references/modes.md). Elabore as páginas e a
configuração adicionais como uma única transação de nível de operação. Nunca
mute arquivos do vault com as ferramentas Write/Edit do host ou com um
transporte Obsidian.

## Rotear operações

Rotele a intenção do usuário sem ampliá-la silenciosamente:

| Intenção | Skill |
|---|---|
| Ingerir fontes fornecidas | `wiki-ingest` |
| Responder a partir do conhecimento existente no vault | `wiki-query` |
| Salvar um resultado específico de conversa | `save` |
| Pesquisar a web pública sob um orçamento | `autoresearch` |
| Verificar a saúde do vault | `wiki-lint` |
| Consolidar entradas de log | `wiki-fold` |
| Trabalhar com um canvas | `canvas` |

Query é somente leitura. A persistência a partir de uma query deve ser uma
operação Save explícita e de escopo separado. Nunca capture uma transcrição nem
atualize o cache quente apenas porque uma sessão terminou.

## Contrato de mutação

Leia [operation-transactions.md](references/operation-transactions.md) antes de
qualquer scaffolding customizado ou mutação. Uma operação lógica deve produzir
um único bundle `claude-obsidian.transaction.v1` inspecionado e recuperável.
Agentes paralelos podem retornar apenas rascunhos e evidências; o orquestrador
os mescla e aplica uma vez. Toda criação ou remoção de página canônica inclui
nesse bundle uma atualização de índice ativo ou MOC; atualize o overview apenas
quando o quadro estável de alto nível mudou. Payloads de fonte raw são
create-only. Não há commits automáticos.

Use [provenance.md](references/provenance.md) ao inicializar ou alterar os
ledgers de source e claim. Evidência unsupported permanece unsupported; nunca
invente uma source, citação, data, localizador ou confiança.

Após um apply bem-sucedido, reporte o operation ID e os caminhos exatos
alterados. Se o usuário quiser explicitamente um checkpoint Git, execute-o
separadamente:

```bash
python3 "$CORE" checkpoint OPERATION_ID --vault /absolute/path/to/vault
```

Em caso de conflito, releia e reconstrua. Em caso de interrupção, use
`transaction recover`. Reutilize um operation ID apenas com o bundle idêntico.

## Contexto de instalação

Leia [install-modes.md](references/install-modes.md) quando a instalação ou o
comportamento do host importar. Hooks são adaptadores opcionais; o
comportamento portátil vive no core e nas skills.

## Referências condicionais

Leia apenas a referência necessária para a solicitação atual:

- [frontmatter.md](references/frontmatter.md) ao definir ou adotar um schema de
  propriedades;
- [css-snippets.md](references/css-snippets.md) para customização visual do
  Obsidian solicitada;
- [git-setup.md](references/git-setup.md) para setup explícito de Git local ou de
  checkpoint;
- [plugins.md](references/plugins.md) ao avaliar integrações opcionais do
  Obsidian;
- [mcp-setup.md](references/mcp-setup.md) quando o usuário pede para avaliar um
  transporte externo de leitura;
- [rest-api.md](references/rest-api.md) somente quando o usuário tiver ou
  solicitar explicitamente o adaptador Local REST API.

## Pense, verifique, cresça

Antes de aplicar, pause uma vez: observe o estado existente, verifique a seleção
do vault e a evidência, e então escolha a menor operação reversível que
satisfaça a solicitação. Depois, reporte a incerteza e a próxima melhoria útil
sem executá-la automaticamente.