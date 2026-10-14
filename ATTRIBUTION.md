# Atribuições

claude-obsidian é um trabalho original. Os seguintes padrões, ferramentas e
criadores de terceiros informaram seu design.

---

## Padrão LLM Wiki

**Autor:** Andrej Karpathy
**Fonte:** https://github.com/karpathy
**Uso:** A arquitetura central do claude-obsidian — usar um LLM para construir e manter uma wiki estruturada a partir de fontes brutas — é baseada no padrão LLM Wiki que Karpathy descreveu publicamente. claude-obsidian é uma implementação independente; nenhum código ou conteúdo dos repositórios de Karpathy foi copiado.

---

## Snippets CSS ITS

**Autor:** SlRvb
**Fonte:** https://github.com/SlRvb/Obsidian--ITS-Theme
**Licença:** GPL-2.0
**Arquivos:**
- `.obsidian/snippets/ITS-Dataview-Cards.css`
- `.obsidian/snippets/ITS-Image-Adjustments.css`

Estes snippets existem apenas no estado privado de vault do contribuidor. Não são selecionados no artefato público determinístico do produto e não são instalados pelo template do vault. O `templates/vault/.obsidian/snippets/vault-colors.css` de propriedade do projeto é o único snippet distribuído pelo claude-obsidian.

---

## Plugins históricos do vault do contribuidor

O repositório de fonte continha os seguintes plugins da comunidade Obsidian em seu estado de vault do contribuidor. Eles não estão incluídos no artefato público determinístico do produto nem são instalados pelo template do vault. Instale e revise-os através do Obsidian sob suas respectivas licenças.

| Plugin | Autor | Repositório |
|--------|--------|-----------|
| Calendar | Liam Cain | https://github.com/liamcain/obsidian-calendar-plugin |
| Thino | Boninall (Quorafind) | https://github.com/Quorafind/Obsidian-Thino |
| Obsidian Excalidraw | Zsolt Viczian | https://github.com/zsviczian/obsidian-excalidraw-plugin |
| Obsidian Banners | Danny Hernandez | https://github.com/noatpad/obsidian-banners |

`scripts/setup-vault.sh` não faz download de binários de plugin não verificados. Em vez disso, imprime orientação de instalação manual.

---

## Designs de contribuidor adotados

Dois pull requests da comunidade diagnosticaram bugs de recuperação e propuseram correções que a refundação v2.0.0 implementou em forma quase idêntica. Os pull requests não foram mergeados como submetidos porque os arquivos ao redor foram reescritos, mas os designs são deles.

| Mudança | Contribuidor | Pull request |
|--------|-------------|--------------|
| Prefixos de task `search_query` e `search_document` no reranker, incluindo o helper `with_task_prefix` e invalidação de cache-scheme | maartengoet | https://github.com/AgriciDaniel/claude-obsidian/pull/77 |
| Ordem de fallback BM25 preservada em caminhos no-op do reranker (`bm25_score` antes de `score`) | vinsocci | https://github.com/AgriciDaniel/claude-obsidian/pull/62 |

---

## claude-obsidian

**Autor:** AgriciDaniel / AI Marketing Hub
**Licença:** MIT (veja [LICENSE](LICENSE))
**Repositório (canônico público):** https://github.com/AgriciDaniel/claude-obsidian
**Espelho comunitário de acesso antecipado (Pro):** https://github.com/AI-Marketing-Hub
