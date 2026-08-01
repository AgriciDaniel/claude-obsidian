# Investigación: Prompting Realista en Nano-Banana para Fashion Ecommerce

> Investigación hecha el 2026-06-15 (web + skill banana) para resolver el "plastic skin" y subir el nivel de realismo. **Este es el estándar de prompting de KonpreShop.**

---

## 1. El "weighting" — la verdad sobre `(palabra:1.5)`

El weighting numérico tipo `(palabra:1.5)` o `concepto::2` es de **Midjourney / Stable Diffusion**. **Gemini / nano-banana NO lo interpreta** — si lo escribes, lo ignora o lo mete como texto.

**Cómo se "pesa" en nano-banana (los equivalentes que SÍ funcionan):**
| Técnica | Cómo |
|---|---|
| **Orden de tokens** | Lo más importante va PRIMERO. El modelo da más peso a lo que aparece al inicio. Si la piel realista importa más, va antes que el fondo. |
| **Mayúsculas para lo crítico** | `RAW UNRETOUCHED SKIN`, `NEVER include text`, `MUST keep the exact color`. |
| **Repetición** | Mencionar el rasgo clave 2 veces en la frase (ej. "visible pores… natural skin texture, no airbrushing"). |
| **Frases naturales, no listas de tags** | Gemini lee oraciones con preposiciones, no `piel, poros, luz, cámara`. |
| **"prominently displayed"** | Para asegurar que el producto/cara no quede escondido. |

---

## 2. La receta anti-"plastic skin" (lo que arregló a Marco)

Marco v1 salió plástico por **2 razones**: (a) faltaban micro-detalles de piel, y (b) **la luz softbox plana y pareja borra la textura**. El realismo viene de **luz direccional dura** que "raspa" la piel.

**Bloque de piel realista (copiar/pegar y adaptar):**
```
RAW UNRETOUCHED SKIN with clearly visible pores, natural skin texture,
fine facial vellus hair, realistic subsurface scattering, a few natural
imperfections and faint freckles, a light natural sheen — absolutely NO
airbrushing, NO smoothing, NO plastic skin.
```

**Luz que revela textura (clave):**
- ✅ `harsh directional key light raking across the face from camera-left` → revela poros y volumen.
- ✅ `soft fill on the shadow side` + `subtle rim light` → controla, no aplana.
- ❌ Evitar luz softbox grande, frontal y pareja → es lo que causa cara de cera.

**Cámara/lente para realismo:**
- `Hasselblad medium format` (profundidad editorial), `Canon 85mm f/1.4-f/2.0` (retrato/bokeh), `35mm film` (ambiente/lifestyle).
- Anclas de prestigio (mejoran composición): `Vanity Fair editorial portrait`, `National Geographic`.

**Un detalle de imperfección = realismo:** arrugas naturales de tela, mechón fuera de lugar, sudor leve. Quita el look "demasiado perfecto de IA".

---

## 3. Casting de modelos: atractivos PERO reales (no plástico)

En vez de "a man" o "a model" (genérico → plástico), se construye como **brief de casting de agencia**:
- **Edad + etnia + rasgos específicos:** "Mexican man, early 30s, strong defined jawline, high cheekbones, warm approachable dark eyes".
- **Vibe de casting real:** `street-cast male model`, `Mango menswear campaign casting`, `Zara lookbook casting` → da atractivo creíble, no maniquí.
- **Grooming detallado:** "short well-groomed beard with individual hair strands", "faded sides".
- Atractivo + textura **no se pelean**: pides buena estructura ósea Y piel real con poros. Ese es el look editorial caro.

> Roster completo de personajes KonpreShop en `04-Direccion-Creativa-Banana.md` — a cada uno se le aplica este bloque de piel + casting.

---

## 4. Fashion ecommerce — Do's & Don'ts (de la investigación)

**DO:**
- **Describir la TELA antes que el estilo:** "fitted heather-gray cotton tee, ribbed collar" > "nice shirt". El material + cómo reacciona a la luz = realismo.
- **Color exacto** y `color-accurate`.
- **Ficha de catálogo:** `ghost mannequin`, `85% frame fill`, fondo limpio (gris degradado para marca, o `pure white #FFFFFF` si es para marketplace tipo Amazon/Mercado Libre).
- **Consistencia de personaje** entre tomas (mismo rostro vía `continue_editing` / referencia).
- **Editar la foto REAL** del producto (no generar de cero) cuando el cliente debe ver el SKU exacto → preserva fidelidad.

**DON'T:**
- ❌ Descriptores genéricos: "nice dress", "stylish outfit".
- ❌ Señales de estilo contradictorias: "casual streetwear editorial haute couture".
- ❌ Sobre-accesorizar → degrada el render.
- ❌ Texto/logos sobre la prenda → la IA los renderiza inconsistentes.
- ❌ Palabras prohibidas (bajan calidad): `8K`, `ultra-realistic`, `hyperrealistic`, `masterpiece`, `photorealistic`, `best quality`, `award winning`. → usar cámara/film + anclas de revista.
- ⚠️ **Límite honesto:** para el SKU exacto, la IA generada desde cero NO igualará el producto físico al 100%. Para fichas de venta: editar la foto real. Para hero/ads/lookbook/lifestyle: generar libre.

---

## 5. Plantillas actualizadas (reemplazan las del doc 04)

**Retrato base de personaje (realista):**
```
Candid editorial portrait of a [handsome/striking] [etnia] [género] in their [edad],
street-cast model with [rasgos: jawline/cheekbones/eyes], [grooming/hair].
RAW UNRETOUCHED SKIN with visible pores, natural texture, fine vellus hair,
subsurface scattering, faint freckles, light sheen — NO airbrushing, NO plastic skin.
[Build]. [Pose], wearing [tela + prenda], against [fondo]. [Encuadre].
Shot on Hasselblad medium format / Canon 85mm f/1.4, harsh directional key light
raking from camera-left, soft fill, subtle rim light. Vanity Fair editorial,
[marca] campaign casting.
```

**Ficha de producto (editar foto real, ghost mannequin):**
```
Ghost-mannequin product photograph showing ONLY the [producto] — remove person.
Keep EXACT same [color] color, [tela] texture, fit, stitching. Natural 3D shape
with realistic folds. Light-gray gradient studio sweep, soft contact shadow.
Soft diffused light, crisp separation, color-accurate. NEVER include person, logo,
text, watermark. Commercial product photography, Wallpaper* editorial.
```

---

## 6. Códigos visuales Banana Republic (confirmados de screenshots reales)

Lo que de verdad hace que se vea "tienda real" (verificado contra capturas del sitio):
1. **Paleta CÁLIDA y terrosa** — crema, terracota, arena, madera. **Nunca gris frío.** (Mi error inicial: fondos neutros/fríos.)
2. **Grano de película (Kodak Portra 400, fine film grain, soft halation)** — la clave #1 anti-IA. El "digital limpio" delata; el grano analógico convence.
3. **Fondo de yeso/plaster texturizado en terracota** con juego de luz diagonal → look de tile de campaña premium (mucho mejor que gris plano).
4. **Catálogo on-model:** fondo crema cálido, cuerpo completo, luz suave pareja, poses relajadas.
5. **Lifestyle/hero:** sol natural (golden hour), candid (caminando/sonriendo), grano de film.

**🏆 Receta ganadora (validada en `assets/pruebas/marco_BR_getaway_terracota.png`):**
```
[personaje, piel RAW con poros]. Dress in [producto real ref]. POSE: relaxed
editorial three-quarter, hand in pocket. BACKDROP: hand-textured warm
terracotta-clay painted studio backdrop with subtle mottling. LIGHTING: soft
warm directional daylight, golden temperature, diagonal light-and-shadow play.
Shot on Kodak Portra 400, 50mm, fine natural film grain, warm analog grade,
soft halation. RAW UNRETOUCHED SKIN. Banana Republic 'Getaway Edit' campaign.
```

## 7. EL desbloqueo de realismo extremo (candid > estudio)

Aprendizaje clave (validado en `assets/pruebas/REALISMO_reportaje_workshop.png`):
**El look "AI" venía del ENFOQUE, no solo del modelo.** Foto limpia de estudio + pose perfecta = se ve IA. El realismo extremo viene de tratarlo como **fotografía documental/reportaje:**
- **Candid, no posado:** "caught mid-step as if unaware of the camera", encuadre snapshot ligeramente descentrado.
- **Luz dura natural** (no softbox): "harsh late-afternoon sun raking from the left, deep contrasty shadows, dust in the light".
- **Grano de film pesado + defectos de lente:** "heavy organic film grain, lens vignette, chromatic aberration", "Leica M6 + 35mm, expired Kodak Portra 400".
- **Imperfecciones humanas reales:** "NOT a polished model", oily T-zone shine, razor bumps, tired eyes, scar, asymmetry.
- **Entorno con profundidad real** detrás del sujeto (taller con herramientas/camioneta desenfocadas), no fondo de estudio.
- **Ligero motion blur** en una mano = movimiento real.

### El lever de MODELO (pendiente de API key)
El MCP conectado usa **`gemini-2.5-flash-image` (Nano Banana 1, 1K)** — techo de realismo. Para subir más:
- Modelo: **`gemini-3.1-flash-image-preview` (Nano Banana 2)** vía `scripts/generate.py --resolution 2K --thinking high`.
- Requiere la API key en el entorno del shell (`--api-key` o `GOOGLE_AI_API_KEY`). El MCP la tiene en su proceso pero el shell no — pendiente que Eric la provea para ese salto extra.

### Dos direcciones estéticas (elegir por espacio)
- **Reportaje real (gritty):** hero, storytelling de marca, "trabajador real". Súper realista, moody.
- **Campaña limpia cálida (BR/terracota):** tiles, catálogo, fichas. Más brillante y producido.

## Fuentes
- [Gemini vs Midjourney prompt weighting](https://geminiprompt.id/blog/google-gemini-vs-midjourney-v6-which-is-more-realistic-in-2026)
- [Nano Banana prompt formulas para fashion (Fibre2Fashion)](https://emerge.fibre2fashion.com/blogs/10806/best-nano-banana-prompt-formulas-for-apparel-lookbooks-catalog-shots-and-campaign-banners)
- [Nano Banana fashion prompts (Morphed)](https://morphed.app/blog/nano-banana-prompts-for-fashion)
- [Nano Banana product photography guide (Medium)](https://medium.com/ai-product-photography/how-to-use-nano-banana-for-product-photography-2025-guide-a0b91c6c928f)
- skill banana → `references/prompt-engineering.md` (alineado con Google "Ultimate Prompting Guide", Mar 2026)
