# Workflow de Producción de Galería (anti-errores visuales)

> El "golden path" para generar varias tomas del MISMO producto sin que se vean inconsistentes.
> Script: `scripts/gallery.py`. Validado en `assets/lote/polo-esmeralda/` (QA ✅).

---

## Por qué este workflow evita errores

Los 4 errores típicos de IA y cómo los bloqueamos:

| Error visual | Causa | Cómo lo evita el workflow |
|---|---|---|
| **Color/tela cambia entre tomas** | generar de cero cada vez | **COLOR LOCK** — maniquí y closeup se condicionan SIEMPRE con la foto real del producto |
| **Modelo distinto en cada foto** | generar cada on-model por separado | **MODEL ANCHOR** — se genera 1 frente y la espalda se deriva de ÉL ("mismo hombre, de espaldas") |
| **Estética dispareja** | prompts distintos | **TEMPLATE COMPARTIDO** — mismos bloques STUDIO + REALISM en todas las tomas |
| **Manos deformes / texto basura / piel plástica** | prompt sin guardas | **CLÁUSULAS ANTI-ERROR fijas** — manos en bolsa, "no text/logo", piel real con poros |

Motor: **Nano Banana 2 (`gemini-3.1-flash-image-preview`) @ 2K** (el realista). Estética: Gap limpio para producto.

---

## Los 4 shots estándar por producto

1. **01-frente-onmodel** — modelo guapo sonorense con el producto (héroe), estudio high-key.
2. **02-espalda-onmodel** — MISMO modelo de espaldas (derivado del 01).
3. **03-maniqui** — ghost mannequin limpio (desde foto real → color lock).
4. **04-closeup** — macro de tela/detalle (desde foto real).

> Opcional 05: lifestyle en contexto, o lateral. Para hero/banner se usa el modo **reportaje gritty** (doc 05), no este.

---

## Cómo correrlo

```bash
KEY='<gemini key>'
python3 ~/claude-obsidian/KonpreShop/scripts/gallery.py \
  --slug <nombre-producto> \
  --product-image <ruta a la foto real del producto> \
  --gender h|m \
  --garment "descripción corta y factual de la prenda" \
  [--front <frente ya aprobado, para reusar el mismo modelo>] \
  --key "$KEY"
```
Salida ordenada en `assets/lote/<slug>/` + `manifest.json`.

---

## ✅ Checklist QA (revisar SIEMPRE antes de aceptar — lo hace Claude viendo cada imagen)

- [ ] **Color** del producto idéntico en las 4 tomas y fiel a la foto real.
- [ ] **Mismo modelo** en frente y espalda (cara/cuerpo/piel consistentes).
- [ ] **Manos** con anatomía correcta (sin dedos de más/menos).
- [ ] **Sin texto/logo basura** inventado sobre la prenda o el fondo.
- [ ] **Piel real** (poros, no plástica) y modelo atractivo, limpio (no puerco).
- [ ] **Fondo/luz** consistentes (mismo estudio en todas).
- [ ] **Detalles de la prenda** correctos (cuello, botones, bolsas, costuras).
- [ ] Para SKU crítico: la prenda se parece de verdad al producto real.

**Si algo falla → re-generar SOLO esa toma** (el script es idempotente por archivo). No se acepta la galería hasta que las 4 pasen.

---

## Consistencia entre productos (toda la campaña)
- Mismo `STUDIO` + `REALISM` para todas las fichas → catálogo uniforme.
- Se puede variar **edad y cuerpo** del modelo entre productos (siempre atractivos), pero dentro de un producto el modelo NO cambia.
- Hero/banner = modo reportaje gritty (otra receta, doc 05), reservado para storytelling.

## ⚠️ Estilo POR TIENDA (no todo usa este workflow)

Este workflow Gap-limpio aplica SOLO a ropa de:
- **OutletShop** y **UniformesShop** → `gallery.py` (on-model galán/modelo + maniquí + closeup).

Las otras dos tiendas tienen lenguaje propio (NO usar el Gap-clean de ropa):
- **CapShop** → estilo **streetwear/urbano**, vibe de colab de artista; la gorra es el héroe (on-model waist-up urbano o producto sobre superficie con textura). Receta aparte.
- **FraganciasShop** → **producto premium oscuro/lujo** (fondo charcoal, reflejo, glow — como `pruebas/lattafa_yara_editorial.png`), sin modelo de ropa. Receta aparte.

Casting masculino actual = "modelo internacional GQ, extremadamente guapo, piel real". Femenino = atractiva real. Se puede variar edad/cuerpo entre productos, siempre atractivos.

## Estado
- ✅ `polo-esmeralda` (galería de 4, QA pasada).
- ⏭️ Siguientes en cola: blusa dama, gorra, camisa, y los 82 productos con 0-1 foto.
