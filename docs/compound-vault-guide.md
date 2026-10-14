# Arquitetura do Compound Vault

O Compound Vault é o modelo operacional do claude-obsidian para uma base de
conhecimento local com fontes citadas. A base v1.10 substitui o comportamento
histórico de lock por arquivo e escrita de ciclo de vida por seleção explícita
de vault e transações de operação recuperáveis.

## Papéis

| Papel | Contém | Política de mutação |
|---|---|---|
| Pacote do produto | Skills, núcleo Python, scripts, hooks, templates | Alterado apenas pelo desenvolvimento do produto |
| Vault do usuário | Notas, fontes, ledgers, configurações do Obsidian | Alterado por operações de vault revisadas |
| Tempo de execução derivado | Locks, journals, índices de recuperação, fila de captura | Local ao vault, ignorado, recuperável/regenerável |
| Artefato público | Arquivos do produto em allowlist e amostras sintéticas | Reconstruído a partir de um snapshot limpo do Git |

Um cache de plugin instalado é sempre código do produto. Ele nunca se torna o
vault do usuário. Resolva o estado do vault através de `--vault`,
`CLAUDE_OBSIDIAN_VAULT`, configuração de workspace ou descoberta do diretório
atual.

O checkout de desenvolvimento e a raiz do marketplace público são papéis
distintos mesmo quando compartilham histórico. A fonte de desenvolvimento
armazena o template do marketplace revisado em `config/`; o construtor de
release injeta-o em `.claude-plugin/marketplace.json` apenas após selecionar e
auditar o artefato limpo. A promoção do branch público default usa o artefato
extraído e exige aprovação do proprietário.

## Camadas de conhecimento

- `inbox/` é a entrada visível e controlada pelo usuário. A captura nunca a
  apaga.
- `.raw/` armazena payloads imutáveis e o manifest legado de ingestão.
- `wiki/` armazena páginas geradas, índice, log, cache de hot e ledgers de
  evidência.
- `.vault-meta/` armazena locks de tempo de execução, journals de transação,
  filas, índices e configuração opcional.

Novos vaults incluem um `.gitignore` que exclui `.vault-meta/` por completo
porque journals, filas e chunks derivados podem conter texto de notas, paths
locais ou URLs de fontes. Vaults existentes devem adotar o mesmo default
deliberadamente sem sobrescrever sua política de ignore atual.

`wiki/hot.md` é um cache de contexto limitado, não um transcript. `wiki/log.md`
registra operações concluídas. Os ledgers de fonte e de claim mantêm a
proveniência separada do rastreamento legado de deltas.

## Uma operação, uma transação

Um save, ingest, fold, atualização de canvas, mesclagem de pesquisa ou
revisão de lint aprovada é um bundle `claude-obsidian.transaction.v1` único:

1. Ler cada alvo e registrar seu SHA-256 atual ou ausência esperada.
2. Deixar workers paralelos produzirem rascunhos e evidências sem escritas
   compartilhadas.
3. Mesclar a mudança lógica completa em um único bundle.
4. Inspecioná-lo sem mutação.
5. Obter consentimento para consequências destrutivas, externas ou de
   mesclagem canônica.
6. Aplicar uma vez sob o lock de processo com escopo do vault inteiro.
7. Reportar o ID da operação e os paths exatos alterados.

O motor registra os originais em journal, verifica hashes de conteúdo, usa
fsync e substituição atômica, e restaura o estado anterior após um apply
falho ou interrompido. Mudanças concorrentes nos alvos retornam conflito com
exit 75. Releia e construa uma nova operação; nunca force um plano antigo
por meio de transação.

Um conteúdo de transação ou arquivo predecessor é limitado a 64 MiB; o
conteúdo novo agregado e os backups de recuperação agregados são limitados a
128 MiB cada. Uma transação tem no máximo 1.024 writes e pré-verifica seu
journal/result contra o limite de leitura de 8 MiB da recuperação. A fila de
captura usa o mesmo limite para leituras e escritas (8 MiB de JSON canônico,
no máximo 4.096 entradas), preservando recuperabilidade sob recursos
limitados.

A segurança de mutação está vinculada a descritores de diretório abertos, não
a buscas posteriores por pathname. A raiz do vault, o tempo de execução de
metadata, a operação de transação, backups, fila de captura, estado de
checkpoint e publicações de recuperação permanecem fixados durante toda a
janela de mutação. A substituição concorrente de alias, portanto, falha de
forma segura ou faz rollback sem tocar uma árvore de substituição. Essas
garantias exigem WSL/Linux ou macOS suportado; Windows nativo e Git Bash
não são hosts de mutação suportados e são recusados com
`UNSUPPORTED_PLATFORM` antes de qualquer efeito colateral. Inspeção
somente-leitura e dry-runs rodam nativamente no Windows usando validação
lstat de ponto no tempo (rejeição de symlink e junction) em vez de fixação
de descritor. Especificidades da plataforma e troubleshooting de WSL estão no
[guia Windows e WSL](windows-wsl.md).

Bytes de fonte raw podem ser fornecidos através de writes binários de
`content_file` verificados por hash, mas seu modo de destino é apenas create.
Alocação de endereço, frontmatter de página, mapa de endereços, manifest de
fonte, índice, log e cache de hot podem se mover na mesma transação com
journal.

Leia a [referência de transações](../skills/wiki/references/operation-transactions.md).

## Caminhos de leitura e transporte

Leituras de filesystem são a linha de base portátil.
`scripts/detect-transport.sh` reporta a CLI oficial do Obsidian como pronta
apenas quando o comando, a aplicação e a capacidade necessária funcionam.
A detecção default para `--peek` somente-leitura.

A CLI do Obsidian pode acelerar leituras e busca. Não é um segundo caminho de
mutação: todas as escritas ainda passam pelo núcleo de transação. Isso evita
races entre Obsidian, ferramentas de agent e workers paralelos.

## Recuperação

O pipeline de recuperação opcional armazena chunks contextuais e estado
BM25 abaixo de `.vault-meta/`. O provisionamento é primeiro preview:

```bash
bash scripts/setup-retrieve.sh --vault <vault> --no-llm
bash scripts/setup-retrieve.sh --vault <vault> --no-llm --apply
```

BM25 é determinístico e local. O reranking cosseno opcional default para o
modelo multilíngue `nomic-embed-text-v2-moe` do Ollama, que tem
aproximadamente 958 MB e nunca é baixado automaticamente. Embeddings Nomic
usam prefixos de tarefa distintos `search_query:` e `search_document:`.
Usuários que já têm o modelo v1.5 menor, orientado a inglês, podem
selecioná-lo explicitamente com `--model nomic-embed-text`; vaults
multilíngues devem manter o default v2. Nomic v2 tem um contexto de entrada
de 512 tokens, e o Ollama trunca inputs de embedding mais longos por padrão;
o BM25 ainda pontua o chunk completo. Se o modelo selecionado estiver ausente
ou uma etapa de embedding falhar, os resultados voltam completamente para a
ordem e pontuação do BM25. Registros de chunk apagados, alterados ou em
fuga são rejeitados, e a deduplicação de páginas acontece antes do top-K
final.

Consultas de recuperação são limitadas a 8.000 caracteres normalizados e a
contagem de resultados de 1 a 1.000. Consultas oversized e limites inválidos
falham explicitamente. Uma requisição de modelo Ollama sem tag corresponde
apenas ao nome sem tag correspondente ou seu alias `:latest`; outras tags
instaladas devem ser selecionadas pelo nome exato.

Chamadas de modelo com prefixo contextual exigem `--allow-egress`. Ollama
remoto exige `--allow-remote-ollama`. Nenhum é inferido apenas de uma
variável de ambiente.

## Evidência

O ledger de fonte registra identidade de conteúdo, autoridade, independência,
frescor, estado de revisão e páginas vinculadas. O ledger de claim registra
claims falsificáveis, suporte, contradições, confiança, risco e avaliação.

- Claims aceitas precisam de suporte ativo, não-sintético e atual.
- Claims aceitas de alto risco precisam de duas fontes independentes.
- Fontes com uma chave de independência contam como uma linha de evidência.
- Grafias de URL equivalentes a RFC contam como uma mesma origem, incluindo
  IPv6 normalizado, IDN, codificação percent Unicode/UTF-8 e portas default.
- Contradições permanecem visíveis.
- `unsupported` é um estado válido; citações inventadas não são.

Leia a [referência de proveniência](../skills/wiki/references/provenance.md).

## Hooks

O hook `SessionStart` do Claude é silencioso por padrão. Ele emite contexto
de hot limitado e sanitizado apenas quando um vault de usuário é resolvido e
o usuário exportou explicitamente `CLAUDE_OBSIDIAN_SESSION_CONTEXT=1`; o
stdout do hook vira contexto do modelo, então este opt-in é uma decisão de
egress. O hook `Stop` reporta transações incompletas. Hooks não atualizam
notas, capturam conversas, prepara arquivos nem commita no Git. Hosts sem
hooks usam os mesmos fluxos de trabalho centrais.

## Captura

A captura de bytes do filesystem é o único adapter implementado internamente.
Ele realiza um pré-verificação completo somente-leitura, e então o CLI aplica
todas as cópias raw endereçadas por conteúdo como uma única transação
capaz de binário. Metadados de formato de imagem, PDF e EPUB são locais;
extração semântica não é embutida. Ações de URL, YouTube e OCR são planos de
consentimento inertes para um runner separadamente configurado.

## Manutenção e recuperação

```bash
python3 scripts/claude-obsidian.py doctor --vault <vault>
python3 scripts/claude-obsidian.py lint --vault <vault> --as-of YYYY-MM-DD
python3 scripts/claude-obsidian.py transaction recover --vault <vault>
```

Lint é determinístico para sua data de auditoria UTC declarada e somente-
leitura. Qualquer correção é uma transação revisada separada. O checkpoint
no Git também é separado e explícito; ele verifica bytes exatos de blob,
recusa conteúdo staged pré-existente, avança o histórico por compare-and-swap
e exclui bytes raw a menos que o usuário opte por incluir. Se um lock obsoleto
permanecer após uma falha, primeiro verifique se nenhum escritor está vivo;
só então use `transaction recover --force-stale-lock`. Nunca automatize a
substituição.

## Caminho de upgrade

Layouts existentes permanecem legíveis. Pré-visualize a migrção aditiva antes
de aplicar:

```bash
python3 scripts/claude-obsidian.py migrate --vault <vault> \
  --generated-at <ISO-UTC> --operation-id migrate-reviewed
python3 scripts/claude-obsidian.py migrate --vault <vault> \
  --generated-at <ISO-UTC> --operation-id migrate-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

A migração adiciona estado de workspace/provenance ausente, preserva o
manifest legado byte a byte, e não infere claims a partir de prosa. O
`scripts/wiki-lock.sh` permanece apenas para compatibilidade com v1 e não
deve ser usado por novos fluxos de trabalho.
