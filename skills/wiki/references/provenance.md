# Evidência e proveniência

Mantenha o estado de ingestão, a evidência de fonte e a avaliação de afirmações
separados.

Resolva a raiz do produto instalado a partir da própria localização da skill
invocadora, e não a partir do diretório de trabalho do vault do usuário:

```bash
PRODUCT_ROOT=/absolute/path/to/installed/claude-obsidian
CORE="$PRODUCT_ROOT/scripts/claude-obsidian.py"
test -f "$CORE"
```

## Ledgers

- `.raw/.manifest.json`: hashes de ingestão compatíveis com o legado, páginas
  geradas, mapa de endereços e último resultado de processamento.
- `wiki/meta/ledgers/source-ledger.json`: identidades estáveis de fonte, authority,
  SHA-256, obtenção/atualidade, review_state e páginas vinculadas.
- `wiki/meta/ledgers/claim-ledger.json`: afirmações falsificáveis, localizações de
  nota, support, contradict, confidence, risk e review_state.

Não sobrecarregue um único ledger com as três funções.

## Regras de fonte

- Use SHA-256 para nova identidade de fonte e verificação de delta.
- Localizadores de arquivo são relativos ao vault. Localizadores remotos são URLs
  HTTPS absolutas.
- A authority de fonte é uma entre `official`, `primary`, `secondary`, `community`,
  `synthetic` ou `unknown`.
- O review_state é `unreviewed`, `active`, `superseded` ou `rejected`.
- Calcule a obsolescência a partir de `refresh_due`; não armazene uma segunda flag de stale.
- Fontes que compartilham uma `independence_key` não contam como corroboração independente.
- Fontes que resolvem para a mesma origem de URL canônica não contam como independentes
  apenas porque a grafia difere em IPv6, IDN, Unicode, segmento de ponto, porta padrão
  ou codificação percentual. Bytes reservados de path/query escapados permanecem
  distintos porque podem identificar um recurso diferente.

## Regras de afirmação

- A assessment é `accepted`, `provisional`, `contested`, `unsupported` ou
  `deprecated`.
- Afirmações aceitas precisam de ao menos uma fonte nova, ativa e não sintética.
- Afirmações aceitas de alto risco precisam de duas fontes independentes.
- Preserve evidência contraditória. Não escolha um vencedor silenciosamente.
- `unsupported` é o estado canônico de ausência de dados. Uma recusa fundamentada é
  melhor que uma invenção confiante.
- Nunca fabrique citações, números de página, datas ou localizadores de evidência.

## Migração

Rode a migração primeiro como dry-run:

```bash
python3 "$CORE" migrate --vault VAULT \
  --generated-at <ISO-UTC> --operation-id migrate-reviewed
python3 "$CORE" migrate --vault VAULT \
  --generated-at <ISO-UTC> --operation-id migrate-reviewed \
  --approved-plan-sha256 <reviewed-sha256> --apply
```

A migração deixa `.raw/.manifest.json` inalterado byte a byte, cria ledgers
ausentes, preenche honestamente campos de evidência desconhecidos e nunca extrai
afirmações automaticamente de prosa do legado. Uma source key legada que resolve
para um arquivo regular permanece uma fonte de arquivo com seu SHA-256 computado.
Uma key válida sem arquivo é preservada como uma fonte manual não revisada com
authority desconhecida e sem hash de payload verificado. Esse registro não
resolvido preserva a identidade, a data e os links de página legados; ele não prova
uma relação entre lote e arquivo. A migração nunca enumera payloads brutos para
inventar essa relação nem promove o hash curto legado para SHA-256.
O bundle de migração revisado também fixa o estado de arquivo observado de cada
localizador legado. O apply falha se um rótulo não resolvido aparecer, ficar
inseguro, não puder ser inspecionado, ou se uma fonte de arquivo mudar após a revisão.