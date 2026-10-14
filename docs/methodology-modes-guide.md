# Modos de metodologia

O modo de metodologia é uma preferência de roteamento local ao vault para novas
notas. Ele não altera as regras de evidência, a segurança de transação ou os
arquivos existentes.

## Modos

| Modo | Princípio | Rotas típicas |
|---|---|---|
| Generic | Pastas tipadas familiares sem uma metodologia nomeada | `wiki/sources/`, `entities/`, `concepts/`, `sessions/` |
| LYT | Mapas de Conteúdo conectam notas atômicas | `wiki/mocs/`, `wiki/notes/` |
| PARA | Organizar pela atualidade da ação | `wiki/projects/`, `areas/`, `resources/`, `archives/` |
| Zettelkasten | IDs estáveis, notas atômicas, links densos | `wiki/<id>-<slug>.md` plano |

Configuração ausente significa Generic. Escolha com base nos hábitos de
recuperação e manutenção, não em prestígio:

- Use Generic quando tipos são suficientes e o custo de migração deve
  permanecer baixo.
- Use LYT quando mapas curados são a superfície primária de navegação.
- Use PARA quando o status de projeto/ação deve controlar o arquivamento.
- Use Zettelkasten quando atomicidade e links densos são praticados
  consistentemente.

## Ler o modo atual

```bash
python3 scripts/claude-obsidian.py mode get --vault <vault>
```

O roteador de compatibilidade pode pré-visualizar um destino sem escrever:

```bash
python3 scripts/wiki-mode.py --vault <vault> route concept "Example concept" --mode lyt
```

Trate a saída do roteador como uma proposta. Valide-a como um path relativo ao
vault e inclua o path escolhido no preview da operação.

## Configurar com segurança

Mudanças de modo usam uma única transação de configuração e default para
dry-run:

```bash
python3 scripts/claude-obsidian.py mode set para --vault <vault> \
  --generated-at <ISO-UTC> --operation-id mode-reviewed
python3 scripts/claude-obsidian.py mode set para --vault <vault> \
  --generated-at <ISO-UTC> --operation-id mode-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

O wrapper de compatibilidade tem o mesmo comportamento:

```bash
bash scripts/setup-mode.sh --vault <vault> --mode para
bash scripts/setup-mode.sh --vault <vault> --mode para \
  --generated-at <ISO-UTC> --approved-plan-sha256 <reviewed-sha256> --apply
```

Configurações de rota customizada existentes são preservadas. O comando não
cria pastas, move notas, reescreve links ou migra conteúdo antigo.

O alocador Zettelkasten tem um formato canônico: `YYYYMMDDHHMMSSffffff-UUID4HEX`.
Um `id_format` legado somente com timestamp é normalizado na saída de leitura
e na próxima transação `mode set` revisada; filenames existentes não são
renomeados. Componentes de filename roteados são limitados a 255 bytes UTF-8
com um sufixo de hash determinístico quando um título precisa ser encurtado.

## Mudar de modo

A mudança afeta apenas o roteamento posterior. Antes de mudar:

1. identifique quais fluxos de trabalho consomem rotas;
2. pré-visualize nomes representativos de fonte, entidade, conceito, sessão
   e pesquisa;
3. verifique colisões de filename ou basename;
4. aplique a transação de configuração;
5. execute o linter determinístico após a primeira operação no novo modo.

A reorganização em massa é um projeto de migração separado. Ela precisa de
um mapa completo de mudança, plano de reescrita de links, hashes esperados,
tratamento de colisões, rollback e aprovação explícita do usuário. Nunca a
torne um efeito colateral do `mode set`.

## Como as skills consomem o modo

`wiki-ingest`, `save` e `autoresearch` podem chamar o roteador durante a
elaboração. Workers incluem a rota proposta em seu pacote de rascunho; o
orquestrador pai decide e aplica o path final. Query, lint e recuperação não
alteram comportamento com base no modo de metodologia.

O modo é metadado organizacional, não evidência. A pasta de uma nota não
eleva sua autoridade, frescor ou confiança.

## Solução de problemas

| Sintoma | Resposta |
|---|---|
| Configuração ausente | Generic está ativo; nada está quebrado. |
| JSON inválido | Repare ou substitua-o através de uma transação revisada; o roteador falha de forma segura. |
| Rota inesperada | Pré-visualize com um `--mode` explícito, inspecione configurações customizadas e sanitize o nome. |
| Layout antigo/novo misturado | Esperado após a mudança; não mova notas antigas automaticamente. |
| Preocupação com ID Zettelkasten | Novos IDs combinam um prefixo UTC microsecond ordenável com um nonce UUIDv4. IDs legados somente com timestamp permanecem válidos; ainda detecte colisões de alvo antes do apply. |
