# Perfis de scaffold por domínio

Inicialize ou adote primeiro o vault baseline. Um perfil adiciona pastas, tipos de
página e seções de índice em uma única transação inspecionada; ele não substitui a
metodologia organizacional selecionada (`generic`, `lyt`, `para` ou
`zettelkasten`). Preserve notas e rotas existentes.

Todo perfil mantém estes invariantes:

- fontes capturadas imutáveis em `.raw/`;
- conhecimento gerado em `wiki/`;
- `wiki/index.md`, `wiki/log.md` e `wiki/hot.md` como páginas canônicas de ciclo
  de vida;
- ledgers de evidência e de afirmações em `wiki/meta/ledgers/`;
- uma transação de nível de operação para um scaffold solicitado;
- nenhum remote, plugin, egress ou setup de Git sem aprovação separada.

## Website ou sistema de conteúdo

Rotas sugeridas: `wiki/pages/`, `wiki/structure/`, `wiki/audits/`,
`wiki/keywords/` e `wiki/entities/`.

Propriedades de página úteis incluem a URL da fonte, o status de ciclo de vida, a
URL canônica, a data da última verificação e as contagens de links internos.
Trate exports de crawl e de analytics como fontes; não afirme indexação ao vivo nem
status HTTP sem evidência atual.

## Repositório de software

Rotas sugeridas: `wiki/modules/`, `wiki/components/`, `wiki/decisions/`,
`wiki/dependencies/` e `wiki/flows/`.

Registre caminhos relativos ao repositório, propósito, status, relações de
dependência e evidência vinda de código, testes, issues ou documentação primária.
Páginas de arquitetura geradas devem distinguir comportamento observado de
inferência.

## Negócio ou projeto

Rotas sugeridas: `wiki/stakeholders/`, `wiki/decisions/`,
`wiki/deliverables/`, `wiki/intel/` e `wiki/meetings/`.

Registre data da decisão, responsável, status, justificativa e registro de fonte.
Preserve lembranças conflitantes como evidência contestada em vez de reescrever o
histórico.

## Vault de conhecimento pessoal

Rotas sugeridas: `wiki/goals/`, `wiki/learning/`, `wiki/people/`,
`wiki/areas/` e `wiki/resources/`.

Use processamento somente local por padrão. Confirme privacidade e retenção antes
de capturar mensagens, dados de saúde, finanças, relacionamentos ou voz. Não salve
uma conversa inteira quando o usuário pediu para preservar apenas um insight.

## Pesquisa

Rotas sugeridas: `wiki/papers/`, `wiki/concepts/`, `wiki/entities/`,
`wiki/syntheses/` e `wiki/gaps/`.

Acompanhe suporte de afirmações, contradições, autoridade, independência,
atualidade e risco nos ledgers. Um resumo de artigo é secundário em relação ao
artigo capturado e não valida automaticamente suas afirmações.

## Companion de livro ou curso

Rotas sugeridas: `wiki/chapters/`, `wiki/concepts/`, `wiki/people/`,
`wiki/exercises/` e `wiki/reflections/`.

Capture apenas material que o usuário está autorizado a armazenar. Prefira notas
concisas com ligação à fonte a reproduzir capítulos ou transcrições com copyright.

## Aplicando um perfil

1. Inspecione a metodologia atual e as notas representativas.
2. Redija um mapa de pastas/páginas/propriedades e identifique conflitos de nomenclatura.
3. Mostre os caminhos propostos e quaisquer adições de schema.
4. Aplique as adições aprovadas uma única vez através do núcleo de transações.
5. Rode o lint determinístico e relate os achados não resolvidos.
6. Deixe o uso real determinar refinamentos posteriores em vez de pré-construir uma
   hierarquia vazia.