# Instalar o claude-obsidian

O claude-obsidian tem duas partes independentes:

1. o pacote do produto — skills, núcleo portátil, adaptador Claude e
   templates;
2. um vault do Obsidian de propriedade do usuário contendo conhecimento
   mutável.

Não use um cache de plugin instalado como o vault. Um clone de fonte é
adequado para desenvolvimento, mas um vault normal de usuário deve ser um
diretório separado.

## Requisitos

- Python 3.11 ou mais recente
- um host compatível com Agent Skills, ou Claude Code para o adaptador de
  plugin
- Obsidian quando você quiser seu editor visual
- Bash para o instalador e scripts de extensão legada opcionais
- Git apenas para desenvolvimento de fonte, builds de release ou checkpoints
  explícitos
- No Windows: WSL para escritas no vault; Windows nativo suporta inspeção
  somente-leitura e dry-runs — veja o [guia Windows e WSL](windows-wsl.md)

## Marketplace Claude Code

Adicione o catálogo público com artefato limpo e instale o plugin com
namespace:

```bash
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian@agricidaniel-claude-obsidian
claude plugin list
```

A árvore privada de desenvolvimento deliberadamente não tem
`.claude-plugin/marketplace.json`; ela pode conter estado de vault de
contribuidores e não deve ser adicionada como marketplace. O construtor
determinístico de release injeta esse manifest apenas em sua saída auditada.
O branch público default deve ser promovido a partir do artefato auditado
extraído antes que esses comandos de marketplace sejam anunciados para uma
nova versão.

Invoque skills como `/claude-obsidian:wiki`, `/claude-obsidian:wiki-ingest` e
`/claude-obsidian:save`.

O cache de plugin contém ativos de produto somente-leitura. Execute Claude a
partir do vault do usuário, defina `CLAUDE_OBSIDIAN_VAULT`, ou passe `--vault`
para comandos portáteis.

## Desenvolvimento local de plugin Claude

A partir de um clone do produto:

```bash
claude --plugin-dir <product-repository>
```

Este modo é para testar alterações não instaladas. Skills permanecem com
namespace. Ele não converte o repositório do produto em um vault de usuário.

## Hosts Agent Skills portáteis

O instalador default para uma pré-visualização sem escrita para Codex, OpenCode
e Gemini:

```bash
bash scripts/setup-multi-agent.sh
bash scripts/setup-multi-agent.sh --apply
```

Ele liga cada diretório canônico `skills/<name>/` no layout de descoberta
direto `<skill-root>/<name>/SKILL.md` do host. Destinos são criados apenas
quando ausentes; uma skill ou link existente nunca é substituído. Verifique a
prontidão sem escrever:

```bash
bash scripts/setup-multi-agent.sh --check
```

Cursor e Windsurf usam descoberta local ao workspace e exigem um workspace
explícito:

```bash
bash scripts/setup-multi-agent.sh --host cursor --host windsurf \
  --workspace <workspace> --apply
```

ZCode é opt-in e de nível de usuário (sem necessidade de `--workspace`):

```bash
bash scripts/setup-multi-agent.sh --host zcode
bash scripts/setup-multi-agent.sh --host zcode --apply
```

Você também pode criar links equivalentes por skill manualmente. Para cada
`<name>` sob o diretório `skills/` do produto, ligue esse diretório em:

```text
Codex:     ~/.agents/skills/<name>          -> <product-repository>/skills/<name>
OpenCode:  ~/.config/opencode/skills/<name> -> <product-repository>/skills/<name>
Gemini:    ~/.gemini/skills/<name>          -> <product-repository>/skills/<name>
ZCode:     ~/.zcode/skills/<name>           -> <product-repository>/skills/<name>
Cursor:    <workspace>/.cursor/skills/<name>   -> <product-repository>/skills/<name>
Windsurf:  <workspace>/.windsurf/skills/<name> -> <product-repository>/skills/<name>
```

## Criar um novo vault

Revise primeiro o plano de inicialização:

```bash
python3 scripts/claude-obsidian.py init <new-vault> \
  --generated-at <ISO-UTC> --operation-id init-reviewed
```

Aplique a mesma operação apenas após o destino e os paths alterados
parecerem corretos:

```bash
python3 scripts/claude-obsidian.py init <new-vault> \
  --generated-at <ISO-UTC> --operation-id init-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

O vault gerado contém:

- `.gitignore` — defaults seguros para privacidade excluindo o estado de tempo
  de execução `.vault-meta/`, estado de workspace do Obsidian e configuração
  de launch `.mcp.json` live;
- `.claude-obsidian.json` — identidade de workspace e seleção de vault;
- `inbox/` — entrada de fontes visível;
- `.raw/` — payloads de fonte imutáveis e manifest legado de deltas;
- `wiki/` — índice, log, cache de hot, overview e notas geradas;
- `.obsidian/` — defaults mínimos e não-destrutivos do Obsidian;
- `.vault-meta/` — estado de tempo de execução ignorado criado quando
  necessário.

A inicialização não adiciona um remote Git upstream nem instala plugins da
comunidade. Abra o novo diretório através do seletor de vault do Obsidian.

## Adotar um vault existente

A adoção escaneia um diretório existente do Obsidian e propõe apenas metadata
de produto e arquivos de fundação ausentes:

```bash
python3 scripts/claude-obsidian.py adopt <existing-vault> \
  --generated-at <ISO-UTC> --operation-id adopt-reviewed
python3 scripts/claude-obsidian.py adopt <existing-vault> \
  --generated-at <ISO-UTC> --operation-id adopt-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Ela preserva notas existentes e JSONs do Obsidian. `--force` é
intencionalmente separado e deve ser usado apenas após inspecionar os alvos
de substituição.

Para layouts mais antigos do claude-obsidian, adicione ledgers de
proveniência e configuração de workspace com uma migração aditiva:

```bash
python3 scripts/claude-obsidian.py migrate --vault <existing-vault> \
  --generated-at <ISO-UTC> --operation-id migrate-reviewed
python3 scripts/claude-obsidian.py migrate --vault <existing-vault> \
  --generated-at <ISO-UTC> --operation-id migrate-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

A migração é idempotente, não infere claims a partir de prosa, e deixa o
`.raw/.manifest.json` legado byte a byte inalterado.

## Seleção de vault

Comandos mutáveis usam esta precedência:

1. `--vault <path>`
2. `CLAUDE_OBSIDIAN_VAULT`
3. `.claude-obsidian.json` mais próximo
4. vault inicializado inequívoco mais próximo a partir do diretório atual

Se a seleção falhar, o comando sai sem mutação. A raiz do produto/plugin é
rejeitada como um vault implícito.

Verifique um vault selecionado:

```bash
python3 scripts/claude-obsidian.py doctor --vault <vault>
python3 scripts/claude-obsidian.py contracts --verify --vault <vault>
```

## Configuração opcional

O transporte portátil de filesystem sempre permaneça disponível. Detecte uma
CLI do Obsidian ativa e suportada sem persistir um snapshot:

```bash
bash scripts/detect-transport.sh --peek --vault <vault>
```

Extensões opcionais são explícitas e com escopo no vault:

```bash
bash scripts/setup-mode.sh --vault <vault>
bash scripts/setup-retrieve.sh --vault <vault>
bash scripts/setup-dragonscale.sh --vault <vault>
```

Leia a pré-visualização de cada script antes de aplicar. A recuperação pode
usar apenas BM25 local; prefixos contextuais baseados em modelo ou endpoints
remotos exigem consentimento explícito de egress. Ferramentas opcionais como
Ollama e defuddle são detectadas por capacidade.

## Primeira operação

Coloque uma fonte em `inbox/`. Inspecione o plano de captura de bytes:

```bash
python3 scripts/claude-obsidian.py capture plan --vault <vault>
```

Crie cópias imutáveis endereçadas por conteúdo apenas quando o plano estiver
correto:

```bash
python3 scripts/claude-obsidian.py capture apply --vault <vault> \
  --generated-at <ISO-UTC> --operation-id capture-reviewed
python3 scripts/claude-obsidian.py capture apply --vault <vault> \
  --generated-at <ISO-UTC> --operation-id capture-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

Então invoque a skill `wiki-ingest` do host. Extração semântica de imagem,
PDF e EPUB não é embutida no núcleo; esses formatos atualmente recebem
metadados limitados a menos que um adapter separadamente configurado seja
explicitamente aprovado.

## Upgrade e rollback

Faça upgrade do código do produto independentemente do vault do usuário. Antes
de uma migração ou ingest grande, faça um backup ou snapshot normal. Escritas
de conhecimento são registradas em journal; execute a recuperação após uma
operação interrompida:

```bash
python3 scripts/claude-obsidian.py transaction recover --vault <vault>
```

A recuperação preserva conservadoramente identidades de lock obsoletas ou
alheias. Somente após confirmar que nenhum escritor está ativo, um operador
pode adicionar `--force-stale-lock`.

O histórico Git é opcional e nunca automático. Para fazer checkpoint de
exatamente uma transação concluída:

```bash
python3 scripts/claude-obsidian.py checkpoint <operation-id> --vault <vault> \
  --as-of YYYY-MM-DD
```

O checkpoint usa um índice temporário, verifica bytes exatos de blob Git,
recusa estado staged pré-existente e retoma uma finalização de ref/index
interrompida a partir de seu registro pending local ao vault.

## Desinstalar

Remova a integração do host, não o vault:

```bash
claude plugin uninstall claude-obsidian@agricidaniel-claude-obsidian
claude plugin marketplace remove agricidaniel-claude-obsidian
```

Para hosts portáteis, remova apenas os links por skill que o instalador
reportou. Notas do usuário, fontes, ledgers e configurações do Obsidian
permanecem intactos.

## Solução de problemas

| Sintoma | Verificação |
|---|---|
| Skill não é descoberto | Confirme que `<host-skill-root>/<name>/SKILL.md` resolve para a skill do produto correspondente; rode novamente o instalador `--check`. |
| Comando diz nenhum vault selecionado | Execute a partir do vault, passe `--vault`, ou defina `CLAUDE_OBSIDIAN_VAULT`. |
| Recusa da raiz do plugin | Selecione um vault de usuário separado; escritas no cache de plugin não são suportadas. |
| Conflito de transação / exit 75 | Outra operação está ativa ou um alvo mudou; releia, reconstrua e inspecione um novo bundle. |
| CLI do Obsidian indisponível | Use leituras de filesystem; inicie/atualize o Obsidian antes de tentar o transporte CLI. |
| Adapter de captura não implementado | Inspecione `capture adapters`; configure um runner separado apenas com consentimento explícito. |
| Escritas recusadas com `UNSUPPORTED_PLATFORM` no Windows | A mutação do vault exige WSL; veja o [guia Windows e WSL](windows-wsl.md). |
| WSL instalado mas `wsl --status` trava | Siga o fluxo de diagnóstico e reporte da Microsoft no [guia Windows e WSL](windows-wsl.md#wsl-troubleshooting); não assuma uma causa sem evidência. |
| Aprovação de dry-run nativa falha dentro do WSL com `PLAN_CHANGED` | Hashes de aprovação vinculam o ambiente de revisão; refaça o dry-run dentro do WSL ([detalhes](windows-wsl.md#wsl-troubleshooting)). |

Execute `make test` no repositório do produto ao desenvolver ou empacotar
alterações.
