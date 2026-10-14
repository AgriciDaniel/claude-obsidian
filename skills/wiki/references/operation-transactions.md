# Transações de operação

Use esta referência sempre que uma skill for mudar o estado do vault.

## Contrato

Uma operação lógica produz um transaction bundle versionado e um apply
recuperável. Workers paralelos podem ler e redigir, mas somente o orquestrador
aplica mutações no vault.

Resolva a raiz do produto instalado a partir da própria localização da skill
invocadora, e não a partir do diretório de trabalho do vault do usuário:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

Nunca use o helper `wiki-lock.sh` por arquivo, descontinuado, para trabalho novo.
Nunca faça commit a partir de um hook de ciclo de vida genérico.

## Workflow

1. Resolva um vault do usuário. Prefira `--vault`, depois `CLAUDE_OBSIDIAN_VAULT`, depois
   `.claude-obsidian.json`, depois descoberta inequívoca do diretório atual.
2. Leia cada alvo esperado e registre seu SHA-256, ou `null` quando ele precisa estar ausente.
3. Faça os workers retornarem rascunhos e evidências. Workers não editam o estado
   compartilhado do vault.
4. Construa um bundle JSON `claude-obsidian.transaction.v1`.
5. Rode `python3 "$CORE" transaction inspect BUNDLE --vault VAULT`.
6. Mostre ao usuário as propostas destrutivas, externas ou de merge canônico antes
   de aplicá-las.
7. Passe o `approval_sha256` exato do resultado do inspect, que vincula o plano expandido
   à raiz canônica resolvida do vault e não pode ser reutilizado para outro
   vault:
   `python3 "$CORE" transaction apply BUNDLE --vault VAULT --approved-plan-sha256 HASH`.
8. Relate o ID da operação resultante e as changed paths.
9. Se o usuário quiser histórico Git, rode o comando de checkpoint explícito e separado.

## Formato do bundle

```json
{
  "schema": "claude-obsidian.transaction.v1",
  "operation_id": "save-20260711-example",
  "operation_type": "save",
  "expected_hashes": {
    "wiki/concepts/Example.md": null
  },
  "writes": [
    {
      "path": "wiki/concepts/Example.md",
      "mode": "create",
      "content_file": "drafts/example.md",
      "sha256": "<sha256>"
    }
  ],
  "address_requests": [],
  "source_manifest_updates": {}
}
```

`content` pode substituir `content_file` para rascunhos pequenos. Use exatamente um.
Payloads brutos de fonte são apenas para create. `.raw/.manifest.json` e o contador
de endereços são expandidos e journalados pelo motor de transação quando há
requisições gerenciadas presentes. Somente `ingest` e `autoresearch` possuem
requisições gerenciadas não vazias; `setup` e `migration` podem inicializar
diretamente os arquivos gerenciados. Outros operation types não podem ter esses
alvos.

Os operation types são autoridades verificadas, não rótulos: `base` escreve apenas
`wiki/**/*.base`; `canvas` escreve canvases em `wiki/canvases/` e seu `index.md`
opcional; `fold` escreve exatamente uma página `wiki/folds/*.md` mais
`wiki/index.md` e `wiki/log.md`; `configuration` escreve apenas
`.vault-meta/mode.json`; e `capture` cria apenas payloads `.raw/captured/*`.
Save, Markdown, reparo de lint e bundles de extensão genérica permanecem
confinados a `wiki/`. `setup` e `migration` aceitam somente os caminhos exatos de
vault-template, ledger e bootstrap DragonScale rastreados, declarados pelo contrato
do produto; eles não são escotilhas de fuga para arquivos arbitrários de raiz,
plugin, snippet, metadados ou wiki. Caminhos que colidem por caixa são rejeitados
para portabilidade em macOS.

Um arquivo de conteúdo ou de predecessor pode ter no máximo 64 MiB, e o novo
conteúdo ou os backups de recuperação de uma operação podem somar no máximo
128 MiB. Divida um trabalho maior em um limite lógico antes da inspeção; o motor
rejeita uma operação que não conseguiria desfazer sob os mesmos limites.

Uma operação pode conter no máximo 1.024 writes. Cada caminho canônico relativo ao
vault pode usar no máximo 1.024 bytes UTF-8. Transaction bundles em arquivo devem
ser arquivos regulares no-follow e podem usar no máximo 136 MiB; journals e
resultados concluídos são pré-verificados contra o mesmo teto de 8 MiB usado pela
recuperação. Esses limites garantem que toda operação aceita permaneça legível e
recuperável.

O lock retém os descritores do vault selecionado e do diretório `.vault-meta` por
toda a operação. Alvos, journals, resultados, backups, filas de captura,
checkpoints e publicações de recuperação derivadas usam I/O baseado em descritor
no-follow, então substituir uma entrada pública de raiz, metadados, transação,
operação ou backup não pode redirecionar leituras, escritas, rollback ou limpeza
para fora do vault selecionado.Esse confinamento requer descritores de diretório
POSIX e `fcntl.flock`; usuários de Windows devem rodar a skill sob WSL em vez de
Windows nativo ou Git Bash (setup e troubleshooting: `docs/windows-wsl.md`).

## Writes acoplados obrigatórios

- Save: nota, index, log, hot cache.
- Ingest: captura de fonte quando aplicável, páginas, registros de ingestão/evidência,
  indexes ou MOCs, log, hot cache e overview opcional.
- Autoresearch: páginas de pesquisa citadas e registros de evidência. O merge canônico
  é uma transação aprovada separada.
- Fold: página de fold, index, log.
- Canvas: canvas mais somente os metadados de catálogo, quando esses metadados mudam.
- Reparo de lint: correções aprovadas mais relatório/index regenerados.
- Query: somente leitura. Delegue a persistência ao Save.

## Comportamento em falha

- Exit 75 significa que o vault mudou ou que outra operação detém o lock de mutação.
  Releia, reconstrua e inspecione um novo bundle.
- Falha de validação significa que nenhuma escrita no vault ocorreu.
- Um apply interrompido é recuperado ou revertido pelo próximo apply, ou pelo
  `transaction recover`.
- A recuperação nunca rouba um lock antigo só porque sua idade passou. Depois de
  confirmar independentemente que nenhum writer está ativo, um operador pode usar
  `transaction recover --force-stale-lock`; o mesmo override explícito existe para
  `capture queue recover`. Não automatize nenhum dos dois overrides.
- Nunca masque uma falha de transação com `|| true`.

## Checkpoint explícito

```bash
python3 "$CORE" checkpoint OPERATION_ID --vault VAULT \
  --as-of YYYY-MM-DD
```

Fazer checkpoint nunca é automático. Ele recusa todo estado de stage pré-existente,
verifica os bytes de blob da árvore candidata contra os hashes da transação, roda
lint determinístico por padrão e exclui payloads brutos de fonte a menos que o
usuário aceite explicitamente. `--as-of` fixa e registra a data de auditoria de
proveniência em UTC; um registro pending retoma o mesmo commit e a mesma data fixa
após uma interrupção.