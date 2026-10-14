# Programa de pesquisa padrão

Este é o padrão delimitado para `autoresearch`. Limites fornecidos pelo usuário
podem torná-lo mais restritivo. Os contratos de privacidade, proveniência e
transação da skill sempre prevalecem sobre a orientação de domínio.

## Objetivos

- Responder a uma pergunta de pesquisa precisa em vez de coletar um tema indiscriminadamente.
- Preferir fontes primárias e oficiais, depois análises independentes de alta qualidade.
- Extrair afirmações falsificáveis, entidades, conceitos, mecanismos e decisões.
- Buscar contra-evidências, contradições, dependências entre fontes e lacunas em aberto.
- Separar afirmações diretas da fonte de inferências e recomendações.
- Parar quando fontes adicionais repetirem evidências conhecidas ou não puderem mudar a resposta.

## Orçamento padrão

- Rodadas de busca: no máximo 3
- Fontes obtidas por rodada: no máximo 5
- Páginas redigidas: no máximo 15
- Workers paralelos: no máximo a concorrência segura disponível no host

Antes da saída de rede, combine também limites de tempo decorrido, custo, domínio e
privacidade. Relate o uso do orçamento após cada rodada. Alcançar uma meta de
páginas não é motivo para inventar conteúdo; registre as perguntas puladas e pare.

## Avaliação de evidências

Use os ledgers de fontes e de afirmações, não apenas um rótulo de confiança em prosa.

- `accepted`: sustentada por ao menos uma fonte nova, ativa e não sintética.
- Afirmações aceitas de alto risco: sustentadas por duas fontes independentes.
- `provisional`: útil, mas com suporte incompleto.
- `contested`: evidências confiáveis divergem.
- `unsupported`: sem evidência adequada.
- `deprecated`: substituída e mantida por histórico.

A atualidade é específica do domínio e da afirmação. Registre as datas de
publicação, obtenção e revisão quando conhecidas, defina um `refresh_due`
apropriado e nunca aplique um limite de idade universal a trabalhos fundamentais.

## Estilo de saída

- Use linguagem direta preservando a incerteza necessária.
- Cite cada afirmação material e não óbvia a um registro de fonte e localizador.
- Use páginas curtas e focadas; divida por conceito quando isso melhorar a recuperação.
- Declare `unknown`, `unsupported` ou `contested` em vez de preencher lacunas.
- Preserve citações na íntegra e mantenha-as curtas; caso contrário, parafraseie.
- Nunca fabrique autores, datas, URLs, números de página, medições ou citações.

## Seleção de fontes

A autoridade depende da pergunta:

- Software e produtos: documentação oficial atualizada, repositórios-fonte,
  especificações e testes reproduzíveis.
- Pesquisa acadêmica: artigos originais, datasets, métodos, correções e
  revisões sistemáticas quando apropriado.
- Negócios e mercados: arquivamentos, divulgações oficiais, datasets primários e
  reportagem independente; rotule material promocional.
- Temas médicos, jurídicos e financeiros: orientação autoritativa atualizada e
  evidência primária, com jurisdição, população e limitações explícitas.

Publicações de comunidade e redes sociais podem identificar experiências ou pistas,
mas não se tornam automaticamente evidência de alta autoridade. Deduplique fontes
sindicadas e registre uma `independence_key` compartilhada quando os relatos
dependem da mesma origem.

## Condições de parada

Pare e relate o limite quando ocorrer qualquer uma destas:

- a pergunta acordada estiver adequadamente sustentada;
- um orçamento for esgotado;
- o usuário interromper ou restringir o trabalho;
- os resultados restantes repetirem evidências dependentes;
- a saída de rede exceder os domínios aprovados ou expor contexto privado;
- uma afirmação-chave não puder ser verificada;
- as fontes exigirem acesso ou direitos que o usuário não forneceu.

A saída da pesquisa permanece um dossiê revisável. Mesclá-la em páginas canônicas
é uma transação aprovada separada.