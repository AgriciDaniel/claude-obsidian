<p align="center">
  <img src="assets/cover.png" alt="claude-obsidian cover featuring an astronaut, the Obsidian crystal, and a connected knowledge graph" width="100%">
</p>

<h1 align="center">claude-obsidian</h1>

<p align="center">
  <strong>Construa uma base de conhecimento Obsidian que se torna mais útil a cada uso.</strong><br>
  Capture fontes, crie notas conectadas, recupere respostas fundamentadas e mantenha o vault saudável — sem abrir mão da propriedade dos seus arquivos.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2563eb.svg" alt="MIT license"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent%20Skills-compatible-2563eb" alt="Agent Skills compatible"></a>
  <a href="https://code.claude.com/docs/en/plugins"><img src="https://img.shields.io/badge/Claude%20Code-plugin-7c3aed" alt="Claude Code plugin"></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/release-v2.2.0-d97745" alt="Release v2.2.0"></a>
</p>

<p align="center">
  <a href="#from-source-to-living-knowledge">Veja o fluxo de trabalho</a> ·
  <a href="#quick-start">Início rápido</a> ·
  <a href="#15-skills-one-system">Explore as skills</a> ·
  <a href="docs/install-guide.md">Guia de instalação</a> ·
  <a href="docs/windows-wsl.md">Windows &amp; WSL</a>
</p>

claude-obsidian é um sistema de conhecimento local-first para Claude Code e hosts
compatíveis com [Agent Skills](https://agentskills.io). Ele transforma material
fonte em páginas Obsidian com links e citações de fonte; responde a partir das
evidências já presentes no vault; e fornece fluxos de trabalho explícitos para
pesquisa, recuperação, manutenção e mapeamento visual.

Seu vault permanece um diretório normal de arquivos Markdown, JSON e fontes. Não
está oculto em um cache de plugin, trancado em um banco de dados na nuvem, ou
silenciosamente enviado a um modelo.

## Da fonte ao conhecimento vivo

A maioria dos fluxos de anotação com IA para após salvar o texto. claude-obsidian
é organizado em torno de um loop repetível: reter a fonte, fundamentar as
afirmações, conectar o conhecimento e depois colocá-lo de volta em uso.

![The claude-obsidian compounding knowledge loop](assets/diagrams/knowledge-loop.svg)

- **Capture com contexto.** Traga fontes locais através de uma inbox visível e
  preserve cópias imutáveis endereçadas por conteúdo antes da síntese.
- **Fundamente cada afirmação importante.** Ledgers de fonte e de afirmação retêm
  autoridade, frescor, suporte, contradição, confiança e estado de revisão.
- **Conecte o que você aprenda.** Construa páginas com links, índices, Mapas de
  Conteúdo, estruturas que reconhecem metodologias e visões em Obsidian Canvas.
- **Use o vault novamente.** Pesquise, recupere, linte e dobre o que já é conhecido
  em vez de começar cada conversa do zero.

## Veja o vault

A saída deve permanecer útil com ou sem um agente: Markdown puro para
portabilidade, Obsidian para navegação e exploração visual.

<p align="center">
  <img src="assets/screenshots/graph-view.png" alt="Example claude-obsidian vault in Obsidian Graph view" width="49%">
  <img src="assets/screenshots/wiki-map-view.png" alt="Example claude-obsidian knowledge map in Obsidian Canvas" width="49%">
</p>

<p align="center">
  <sub>Conhecimento conectado na visão Graph · Um mapa visual do conhecimento em Obsidian Canvas</sub>
</p>

## Por que parece diferente

- **Local por padrão.** O vault pertence ao usuário e funciona como arquivos
  comuns. A egresso de rede é uma decisão separada e explícita.
- **As fontes sobrevivem ao resumo.** As notas apontam de volta para evidências
  duráveis; afirmações sem suporte e contraditórias permanecem visíveis.
- **O conhecimento compõe deliberadamente.** Ingestão, consulta, lint, recuperação,
  pesquisa e rollups compartilham um modelo que reconhece procedência.
- **Agentes paralelos não correm contra o vault.** Workers retornam rascunhos. Um
  orquestrador inspeciona e aplica uma transação recuperável.
- **Capacidades são declaradas honestamente.** Ferramentas opcionais são
  detectadas, maturidade é declarada e adaptadores ausentes degradam de forma
  clara em vez de simulados.

Isto não é um gravador automático de transcrições, um serviço de sincronização
em nuvem, um oráculo factual, ou um substituto para backups e controle de fonte.

## Início rápido

A primeira execução mais segura usa um checkout do fonte e um vault de usuário
separado. Todo comando de configuração que altera dados visualiza sua operação
exata antes de aplicá-la.

### 1. Obtenha o produto

```bash
git clone https://github.com/AgriciDaniel/claude-obsidian.git
cd claude-obsidian
```

O checkout contém o produto. Não é seu vault de conhecimento.

### 2. Inicialize um vault separado

```bash
export GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
export OPERATION_ID="init-reviewed"

python3 scripts/claude-obsidian.py init "$HOME/Documents/MyKnowledgeVault" \
  --generated-at "$GENERATED_AT" --operation-id "$OPERATION_ID"
```

Reveja o plano JSON e copie seu `approved_plan_sha256`, depois aplique essa
operação exata:

```bash
python3 scripts/claude-obsidian.py init "$HOME/Documents/MyKnowledgeVault" \
  --generated-at "$GENERATED_AT" --operation-id "$OPERATION_ID" \
  --approved-plan-sha256 "<sha256-from-the-plan>" --apply
```

Para um vault Obsidian existente, use o fluxo `adopt` não destrutivo
descrito no [guia de instalação](docs/install-guide.md#adopt-an-existing-vault).

### 3. Comece a partir do vault

Abra o novo diretório no Obsidian, depois execute Claude Code a partir desse
diretório com o plugin local:

```bash
cd "$HOME/Documents/MyKnowledgeVault"
claude --plugin-dir /absolute/path/to/claude-obsidian
```

Comece com:

```text
/claude-obsidian:wiki
```

Depois coloque uma fonte em `inbox/` e invoque
`/claude-obsidian:wiki-ingest`. Salve uma resposta explicitamente com
`/claude-obsidian:save`; pergunte ao vault com `/claude-obsidian:wiki-query`.

Para Codex, OpenCode, Gemini ou ZCode, visualize e depois aplique as skills
portáteis do checkout do produto:

```bash
bash scripts/setup-multi-agent.sh --host codex
bash scripts/setup-multi-agent.sh --host codex --apply
```

Cursor e Windsurf usam descoberta de skills no workspace. Configuração de
marketplace, todos os hosts suportados, adoção de vault, upgrades e passos de
desinstalação estão cobertos no [guia de instalação completo](docs/install-guide.md).

## 15 skills, um sistema

As skills são pequenas o suficiente para invocação direta e coordenadas o
suficiente para compartilhar as mesmas evidências, seleção de vault e regras de
mutação.

### Construa e use a wiki

| Skill | O que faz |
|---|---|
| `wiki` | Inicializa ou adota um vault, diagnostica prontidão e roteia trabalho |
| `save` | Salva uma resposta ou insight com escopo — nunca uma transcrição automática |
| `wiki-ingest` | Transforma fontes capturadas em páginas conectadas e registros de procedência |
| `wiki-query` | Responde em modo somente leitura a partir de evidências relevantes do vault |
| `wiki-lint` | Reporta links mortos, órfãos, lacunas de metadados, índices desatualizados e seções vazias |

### Estenda o fluxo de trabalho

| Skill | O que adiciona |
|---|---|
| `autoresearch` | Pesquisa web delimitada com egresso explícito e merge canônico separado |
| `canvas` | Criação e manutenção de Obsidian Canvas com escopo na wiki |
| `defuddle` | Conteúdo web limpo e legível antes da ingestão |
| `wiki-fold` | Rollups extrativos e rastreáveis do log de operações |
| `wiki-mode` | Convenções de arquivamento Generic, LYT, PARA ou Zettelkasten |
| `wiki-retrieve` | Prefixos contextuais, BM25 e reranking por cosseno opcional |
| `wiki-cli` | Leitura e busca via Obsidian CLI com escritas seguras por transação |

### Skills de referência

| Skill | O que fornece |
|---|---|
| `obsidian-markdown` | Markdown Obsidian correto, links, embeds e callouts |
| `obsidian-bases` | Tabelas nativas `.base`, cards, filtros, fórmulas e resumos |
| `think` | Um loop de revisão estruturado: observar, ouvir, conectar, criar e crescer |

Claude Code expõe invocações com namespace como
`/claude-obsidian:wiki-lint`; outros hosts usam sua invocação nativa de Agent
Skills. Frases-gatilho e contratos exatos vivem em cada
`skills/<name>/SKILL.md`.

## Confiança faz parte da arquitetura

![The claude-obsidian product and vault trust boundary](assets/diagrams/product-vault-boundary.svg)

O produto nunca trata um checkout do fonte, cache de plugin ou estado de
contribuidor como o vault padrão. Um vault é selecionado explicitamente, através de
`CLAUDE_OBSIDIAN_VAULT`, pelo `.claude-obsidian.json` mais próximo, ou por um
ancestral inicializado inequívoco. Se a seleção for incerta, o comando sai sem
escrever.

Uma operação lógica de conhecimento é uma transação recuperável:

1. Leia cada alvo e registre seu SHA-256 esperado.
2. Permita que workers paralelos retornem apenas rascunhos e evidências.
3. Funda a mudança completa em um bundle de operação.
4. Inspecione o bundle, depois aplique-o uma vez.
5. Reporte o ID da operação e os paths exatos alterados.

O núcleo mantém um lock de vault por tempo de vida do processo, journals de
backups, usa substituição atômica e restaura o estado anterior se uma aplicação
não puder terminar. Um alvo alterado é um conflito, nunca uma sobrescrita
silenciosa. Checkpoints do Git, reparos destrutivos, egresso de rede e merges
de pesquisa canônica permanecem operações explícitas.

Leia o [contrato de transação](skills/wiki/references/operation-transactions.md),
[contrato de procedência](skills/wiki/references/provenance.md) e
[arquitetura Compound Vault](docs/compound-vault-guide.md) para detalhes
legíveis por máquina.

## Limites honestos de capacidade

| Entrada ou capacidade | Suporte atual |
|---|---|
| Fontes do filesystem local | Captura delimitada e endereçada por conteúdo implementada |
| Imagens | Metadados, hash, tamanho e dimensões delimitadas quando disponíveis |
| PDF e EPUB | Metadados, hash e tamanho; sem extração semântica embutida |
| URL e YouTube | Planos de consentimento validados; requer runner externo configurado |
| OCR | Plano de consentimento para arquivo local; requer runner externo configurado |
| Recuperação BM25 | Local e determinística |
| Prefixos contextuais ou modelos remotos | Opcionais e condicionados a consentimento explícito de egresso |
| Obsidian CLI | Opcional para leitura/busca; transporte por filesystem permanece disponível |

Afirmações aceitas de alto risco requerem duas fontes independentes. Evidência
sem suporte ou contraditória permanece visível, e uma recusa fundamentada é
preferível a uma citação inventada. A recuperação baseada em modelo cai para BM25
determinístico quando o estágio de embedding ou reranking não pode ser
confiado.

## Modele o vault ao seu jeito de pensar

`wiki-mode` pode rotear novas notas usando quatro metodologias sem mover em
massa o conhecimento existente:

| Modo | Princípio de arquivamento |
|---|---|
| Generic | Fontes, conceitos, entidades e sessões |
| LYT | Mapas de Conteúdo e notas atômicas conectadas |
| PARA | Projetos, Áreas, Recursos e Arquivos |
| Zettelkasten | Identificadores estáveis, notas atômicas e links densos |

Generic é o padrão quando nenhum modo está configurado. Mudar de modo altera
como novas notas são roteadas; não reorganiza silenciosamente as antigas. Veja
o [guia de modos de metodologia](docs/methodology-modes-guide.md).

## Referência do operador

<details>
<summary><strong>CLI portátil</strong></summary>

O wrapper é `python3 scripts/claude-obsidian.py`.

| Comando | Efeito |
|---|---|
| `doctor --vault PATH` | Mostra seleção do vault e prontidão |
| `init PATH [--approved-plan-sha256 HASH --apply]` | Planeja ou cria um vault separado |
| `adopt PATH [--approved-plan-sha256 HASH --apply]` | Planeja ou adota um vault Obsidian existente |
| `migrate --vault PATH [--approved-plan-sha256 HASH --apply]` | Adiciona ledgers e configuração v1 sem reescrever dados legados |
| `transaction inspect BUNDLE --vault PATH` | Valida um bundle de escrita sem mutação |
| `transaction apply BUNDLE --vault PATH --approved-plan-sha256 HASH` | Aplica uma operação inspecionada e recuperável |
| `transaction recover --vault PATH [--force-stale-lock]` | Restaura uma operação interrompida |
| `lint --vault PATH [--as-of YYYY-MM-DD] [--exclude GLOB]...` | Emite achados determinísticos para a data UTC declarada |
| `contracts --verify --vault PATH` | Executa contratos de prontidão de capacidade |
| `capture plan --vault PATH [SOURCE ...]` | Executa um preflight de captura local sem escritas |
| `capture apply --vault PATH [SOURCE ...]` | Planeja ou cria cópias imutáveis endereçadas por conteúdo |
| `checkpoint OPERATION_ID --vault PATH` | Commita explicitamente uma operação concluída |
| `package validate` | Verifica coerência de skills, hooks, manifests e documentação |
| `release build --output FILE.zip` | Constrói e autoaudita um artefato público determinístico |
| `release audit FILE.zip` | Audita um artefato sem extraí-lo ou publicá-lo |

Planejadores de mutação de alto nível emitem `approved_plan_sha256`. Fixe
`--generated-at` e `--operation-id`, reveja a operação JSON e passe esse hash
exato com `--apply`. Drift de filesystem ou de bundle gerado falha antes de uma
escrita no vault.

</details>

<details>
<summary><strong>Layout do repositório e do vault</strong></summary>

```text
product repository/                user vault/
├── claude_obsidian/               ├── .gitignore
├── skills/                        ├── .claude-obsidian.json
├── hooks/                         ├── inbox/
├── scripts/                       ├── .raw/
├── templates/vault/               ├── wiki/
├── config/                        ├── .obsidian/
├── assets/                        └── .vault-meta/   # ignored runtime state
└── tests/
```

Artefatos públicos contêm código do produto, templates determinísticos e
assets de README revisados. Rejeitam estado hot/log de contribuidor, fontes raw
raiz, metadados de runtime, paths privados, endereços de email pessoal
reconhecíveis, segredos, symlinks, entradas de archive inseguras e binários
não revisados.

O checkout de desenvolvimento privadamente não tem catálogo de marketplace. O
construtor de release injeta o catálogo revisado apenas no artefato limpo para
distribuição. Um branch público padrão deve ser preenchido a partir dessa
árvore auditada, nunca enviando estado de vault de contribuidor.

</details>

<details>
<summary><strong>Upgrade, rollback e desinstalação</strong></summary>

Atualize o produto independentemente do vault. Para um vault mais antigo,
primeiro visualize a migração aditiva e idempotente:

```bash
python3 scripts/claude-obsidian.py migrate --vault /path/to/vault \
  --generated-at "$GENERATED_AT" --operation-id migrate-reviewed
```

Reveja seu hash e execute novamente com `--approved-plan-sha256 HASH --apply`.
A migração preserva o manifesto raw legado byte a byte e não infere afirmações
de prosa.

Após uma operação interrompida, execute:

```bash
python3 scripts/claude-obsidian.py transaction recover --vault /path/to/vault
```

Remover o plugin ou links de host nunca remove o vault. Delete apenas a
integração que você instalou; notas de usuário, fontes, ledgers e configurações
do Obsidian permanecem seus.

</details>

## Requisitos

- Python 3.11 ou mais recente para o núcleo portátil
- Obsidian para a experiência visual do vault; Markdown puro permanece utilizável
  sem ele
- Bash para configuração, extensões opcionais e suítes de teste em shell
- Git apenas para desenvolvimento, releases ou um checkpoint explícito de
  conhecimento
- Uma release atual do Claude Code para o caminho do plugin Claude Code: o hook
  de comando `args` em formato exec e o matcher `SessionStart` `compact` usados
  por `hooks/hooks.json` precisam dele (veja o
  [contrato de hooks do Claude Code](https://code.claude.com/docs/en/hooks)). Outros
  hosts suportados e o CLI portátil não têm dependência de versão do Claude Code.

CI exercita Linux e macOS, além de um job smoke de Windows nativo para a
superfície portátil. No Windows nativo (incluindo Git Bash), inspeção em modo
somente leitura e comandos dry-run funcionam; escritas no vault requerem WSL e
falham fechadas com erro `UNSUPPORTED_PLATFORM` caso contrário. Hashes de
aprovação vinculam-se ao ambiente de revisão, então reveja dentro do WSL quando
a aplicação ocorrerá lá. Detalhes de plataforma, a matriz de suporte e a solução
de problemas de hang WSL com limites de evidência vivem no
[guia de Windows e WSL](docs/windows-wsl.md). Os scripts de configuração bash e
suítes de teste em shell permanecem apenas POSIX. Ferramentas opcionais como
Obsidian CLI, Ollama e defuddle são detectadas por capacidade e afetam apenas seu
fluxo de trabalho dependente.

## Desenvolvimento e release

```bash
make test
```

O alvo de teste executa cada suíte Python e shell hermética, contratos de
produto e capacidade, validação de skills e hooks, verificações de manifest e
limites de pacote. CI repete a suíte em combinações Linux e macOS/Python
suportadas e verifica um build de release byte-reproduzível.

Construa e audite localmente sem publicar:

```bash
python3 scripts/claude-obsidian.py release build --output dist/claude-obsidian.zip
python3 scripts/claude-obsidian.py release audit dist/claude-obsidian.zip
```

Nenhum comando faz push, tag, publicação, abre issues ou cria releases
automaticamente. Veja [CONTRIBUTING.md](CONTRIBUTING.md),
[SECURITY.md](SECURITY.md) e [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Linhagem, licença e atribuição

O design segue
[o padrão LLM Wiki de Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
e usa [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)
como substrato de referência para sintaxe de Obsidian Markdown, Bases e JSON
Canvas.

Licenciado sob MIT. Veja [ATTRIBUTION.md](ATTRIBUTION.md) e
[CITATION.cff](CITATION.cff).
