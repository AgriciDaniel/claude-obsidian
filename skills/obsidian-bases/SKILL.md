---
name: obsidian-bases
description: "Explique, redija e valide arquivos .base do Obsidian Bases, com filtros, fórmulas, properties, summaries e views de tabela, cards ou lista. Use para Obsidian Bases, visualizações de vault parecidas com banco de dados, tabelas dinâmicas, listas de leitura, rastreadores de tarefas, filtros, fórmulas, summaries e edições de arquivos .base."
---

# Obsidian Bases

Use isto como um workflow compacto e referência de sintaxe de fallback. Prefira
a skill `obsidian-bases` de `kepano/obsidian-skills` instalada separadamente e
depois a [sintaxe oficial do Bases](https://help.obsidian.md/bases/syntax)
atual, para campos e funções detalhados ou sensíveis a versão.

Responda a perguntas de design e de sintaxe em modo somente leitura. Para uma
edição `.base` solicitada, resolva o vault do usuário e use uma única transação
inspecionada; nunca escreva o arquivo diretamente.

Resolva a raiz do produto instalado a partir da localização desta skill, e não
do vault ou do diretório de trabalho atual:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

Todo link `../wiki/references/` neste arquivo resolve da mesma forma, relativo
ao diretório desta skill sob `$PRODUCT_ROOT`, nunca relativo ao diretório
`wiki/` do vault selecionado.

## Workflow

1. Inspecione as properties representativas das notas e qualquer arquivo `.base`
   existente.
2. Defina o menor filtro que seleciona as notas pretendidas.
3. Adicione fórmulas apenas para valores que precisam ser calculados.
4. Escolha as views e a ordem de exibição. Não assuma que um tipo de view ou
   opção é suportado pela versão do Obsidian do usuário ou pelos plugins
   instalados.
5. Valide o YAML, o quoting das expressões, os nomes de property, as referências
   de fórmula e o tratamento de nulos.
6. Pré-visualize o arquivo completo e o conjunto de resultados esperado antes de
   uma mutação.
7. Se uma edição foi solicitada, leia
   [operation-transactions.md](../wiki/references/operation-transactions.md),
   mantenha o arquivo `.base` sob `wiki/` e construa um único bundle
   `claude-obsidian.transaction.v1` com `operation_type: base`. Inspecione-o e
   então defina `APPROVAL_SHA256` para o `approval_sha256` retornado somente
   após a revisão e aplique uma vez:

   ```bash
   python3 "$CORE" transaction inspect "$BUNDLE" --vault "$VAULT"
   python3 "$CORE" transaction apply "$BUNDLE" --vault "$VAULT" \
     --approved-plan-sha256 "$APPROVAL_SHA256"
   ```
8. Peça ao usuário que renderize o Base no Obsidian quando o comportamento em
   nível de aplicação não puder ser verificado localmente.

## Schema compacto

Arquivos `.base` são YAML. As chaves de nível superior mais comuns são `filters`,
`formulas`, `properties`, `summaries` e `views`.

```yaml
filters:
  and:
    - file.inFolder("wiki")
    - 'status != "archived"'

formulas:
  age_days: '((now() - file.ctime) / 86400000).round(0)'
  status_label: 'if(status == "mature", "Ready", "Review")'

properties:
  status:
    displayName: "Status"
  formula.age_days:
    displayName: "Age (days)"

views:
  - type: table
    name: "Wiki pages"
    order:
      - file.name
      - type
      - status
      - updated
      - formula.age_days
```

Filtros globais se aplicam a todas as views. Uma view também pode definir seus
próprios `filters`. Objetos de filtro recursivos usam um entre `and`, `or` ou
`not` em cada nível.

```yaml
filters:
  or:
    - file.hasTag("concept")
    - and:
        - file.hasTag("source")
        - 'status == "active"'
```

Use properties de nota pelo nome, metadados de arquivo como `file.name`,
`file.path`, `file.folder`, `file.ext`, `file.ctime`, `file.mtime` ou
`file.tags`, e properties computadas como `formula.<name>`.

## Regras de fórmula e YAML

- Coloque aspas em expressões que contenham operadores, dois-pontos ou aspas de
  string aninhadas.
- Proteja properties anuláveis com `if()`.
- Subtrair duas datas retorna um número em milissegundos. Divida por `86400000`
  antes de arredondar quando a intenção for uma contagem de dias inteiros.
- Defina todo `formula.<name>` antes de referenciá-lo em uma view ou na
  configuração de exibição de uma property.
- Não transplante chaves exclusivas do Dataview, como `from` ou `where`, para um
  Base.
- Não invente properties ausentes das notas selecionadas sem explicar que a
  coluna resultante ficará vazia.

```yaml
formulas:
  days_until: 'if(due_date, ((date(due_date) - today()) / 86400000).round(0), "")'
```

Views de tabela, cards e lista são comuns:

```yaml
views:
  - type: cards
    name: "Reading list"
    order:
      - file.name
      - author
      - status
  - type: list
    name: "Quick list"
    order:
      - file.name
      - status
```

Insira um Base, ou uma view nomeada, em uma nota Markdown:

```markdown
![[Dashboard.base]]
![[Dashboard.base#Wiki pages]]
```

Depois de uma edição aplicada, reporte o operation ID, o path exato alterado, a
validação realizada e o que ainda exige renderização no Obsidian. Não faça
commit no Git.
