# Personalização visual

Aplique durante o scaffold. Isso torna o explorador de arquivos com cores por
tipo de pasta e adiciona estilos de callout personalizados.

---

## CSS snippet

Crie este arquivo em `.obsidian/snippets/vault-colors.css` dentro do vault:

```css
:root {
  --wiki-1: #4fc1ff;
  --wiki-2: #c586c0;
  --wiki-3: #dcdcaa;
  --wiki-4: #ce9178;
  --wiki-5: #6a9955;
  --wiki-6: #d16969;
  --wiki-7: #569cd6;
}

/* Folder colors in file explorer */
.nav-folder-title[data-path^="wiki/domains"]     { color: var(--wiki-1); }
.nav-folder-title[data-path^="wiki/entities"]    { color: var(--wiki-2); }
.nav-folder-title[data-path^="wiki/concepts"]    { color: var(--wiki-3); }
.nav-folder-title[data-path^="wiki/sources"]     { color: var(--wiki-4); }
.nav-folder-title[data-path^="wiki/questions"]   { color: var(--wiki-5); }
.nav-folder-title[data-path^="wiki/comparisons"] { color: var(--wiki-6); }
.nav-folder-title[data-path^="wiki/meta"]        { color: var(--wiki-7); }
.nav-folder-title[data-path=".raw"]              { color: #808080; opacity: 0.6; }

/* Custom callouts */
.callout[data-callout='contradiction'] {
  --callout-color: 209, 105, 105;
  --callout-icon: lucide-alert-triangle;
}
.callout[data-callout='gap'] {
  --callout-color: 220, 220, 170;
  --callout-icon: lucide-help-circle;
}
.callout[data-callout='key-insight'] {
  --callout-color: 79, 193, 255;
  --callout-icon: lucide-lightbulb;
}
.callout[data-callout='stale'] {
  --callout-color: 128, 128, 128;
  --callout-icon: lucide-clock;
}
```

---

## Habilite o snippet

Diga ao usuário: Settings > Appearance > CSS Snippets > open folder > cole o arquivo > clique no ícone de refresh > ative-o.

---

## Grupos no Graph View

Oriente o usuário a definir estes nas configurações do Graph View (clique no ícone de configurações na visualização de grafo):

| Query | Cor |
|-------|-----|
| `path:wiki/domains` | Azul (`#4fc1ff`) |
| `path:wiki/entities` | Roxo (`#c586c0`) |
| `path:wiki/concepts` | Amarelo (`#dcdcaa`) |
| `path:wiki/sources` | Laranja (`#ce9178`) |
| `path:wiki/questions` | Verde (`#6a9955`) |
| `path:.raw` | Cinza (esmaecido) |

---

## Callouts personalizados

Este vault define **quatro tipos de callout personalizados** além do conjunto nativo do Obsidian (`note`, `tip`, `warning`, `info`, `todo`, `success`, `question`, `failure`, `danger`, `bug`, `example`, `quote`). Eles renderizam corretamente **somente quando `vault-colors.css` está habilitado**. Sem o snippet, caem no estilo de callout padrão (ainda legível, apenas sem formatação).

| Callout personalizado | Cor | Ícone | Usar para |
|---|---|---|---|
| `contradiction` | marrom-avermelhado (rgb 209,105,105) | `lucide-alert-triangle` | Nova fonte conflita com uma afirmação existente |
| `gap` | bege (rgb 220,220,170) | `lucide-help-circle` | Tópico ainda não tem fonte |
| `key-insight` | azul vivo (rgb 79,193,255) | `lucide-lightbulb` | Conclusão importante que vale destacar |
| `stale` | cinza (rgb 128,128,128) | `lucide-clock` | A afirmação pode estar desatualizada, fonte mais antiga que o limite |

### Uso

Use estes em páginas do wiki para sinalizar estados importantes:

```markdown
> [!contradiction] Title
> [[Page A]] claims X. [[Page B]] says Y. Needs resolution.

> [!gap] Title
> This topic has no source yet. Consider finding one.

> [!key-insight] Title
> The most important takeaway from this section.

> [!stale] Title
> This claim may be outdated. Source was from 2022.
```

### Por que callouts personalizados (em vez de nativos)

Os quatro tipos personalizados mapeiam para conceitos específicos do wiki que não
cabem de forma limpa no conjunto padrão do Obsidian:

- `contradiction` é mais específico que `warning`: sinaliza um **conflito resolvível** entre duas páginas do wiki, não um aviso genérico.
- `gap` é mais específico que `question`: sinaliza uma **fonte ausente**, uma melhoria acionável.
- `key-insight` é mais específico que `tip`: marca **a** conclusão mais importante de uma seção, usado com parcimônia.
- `stale` não tem equivalente nativo: sinaliza o decaimento temporal de uma afirmação.

Se você não quiser callouts personalizados, substitua-os por nativos:
- `[!contradiction]` → `[!warning] Contradiction`
- `[!gap]` → `[!question] Gap`
- `[!key-insight]` → `[!tip] Key insight`
- `[!stale]` → `[!warning] Stale`

---

## Compatibilidade de tema

O snippet usa variáveis CSS padrão e não exige um tema da comunidade.
Se o usuário escolher um tema, verifique o contraste e o comportamento dos
seletores na versão instalada do Obsidian antes de recomendá-lo para trabalho
sensível a acessibilidade.