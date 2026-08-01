# Dirección Creativa con Banana (nano-banana / Gemini)

> Este doc aplica la skill **banana** (instalada en `~/.claude/skills/banana/`) a KonpreShop.
> **Estado: PLAN.** Todavía no generamos. Aquí queda el "casting" y las recetas de prompt listas.
> Preset de marca creado: `~/.banana/presets/konpreshop.json` → se carga solo en cada generación.

---

## 0. Cómo trabaja la skill (en cristiano)

La skill hace que Claude actúe como **director creativo**: nunca le manda tu texto crudo a la IA. Lo convierte en un "brief" con **5 partes** que es lo que de verdad da fotos pro:

1. **Sujeto** — quién/qué (edad, piel, ropa, expresión, material).
2. **Acción** — qué está haciendo.
3. **Lugar/Contexto** — dónde, hora del día, ambiente.
4. **Composición** — encuadre, ángulo, lente (ej. "85mm f/1.4").
5. **Estilo + Luz** — cámara real (ej. "Sony A7R IV"), tipo de luz, referencia de revista.

**Reglas de oro (vienen de la skill):**
- Se nombran **cámaras reales** y **marcas reales** → la IA "ancla" a algo concreto y se ve real.
- **PROHIBIDO** escribir "8K", "ultra realista", "photorealistic", "masterpiece" → bajan la calidad. En su lugar: anclas tipo *"Vanity Fair editorial"*, *"National Geographic cover"*.
- Nada de prompts negativos ("sin fondo"); se dice en positivo ("fondo blanco limpio").
- Los prompts se escriben **en inglés** (Gemini rinde mejor), aunque tú y yo hablemos español.
- Para texto en la imagen: máx ~25 caracteres y entre comillas.

---

## 1. El casting — personajes recurrentes de KonpreShop

> La gracia de nano-banana: generas UN retrato base de cada personaje y lo **reúsas** (vía `/banana chat`) en muchas escenas. Así toda la web/ads tienen "las mismas caras" = marca reconocible. Contexto: norte de México (Sonora/Caborca).

| # | Personaje | Tienda / uso | Semilla (Sujeto base) |
|---|---|---|---|
| 1 | **Marco — "El Trabajador"** | UniformesShop (H) | Hombre mexicano 30s, complexión robusta, barba corta, piel trigueña curtida por el sol |
| 2 | **Lupita — "La Profesional"** | UniformesShop / servicios (M) | Mujer mexicana 30s, cabello recogido, expresión amable y segura |
| 3 | **Diego — "El Casual Norteño"** | OutletShop + CapShop (H) | Hombre 25, fresco, estilo norteño urbano, fade y gorra |
| 4 | **Sofía — "Ella Casual"** | OutletShop (M) | Mujer 24, cabello castaño ondulado, look de día relajado |
| 5 | **Don Rafa — "El Patrón"** | FraganciasShop premium / Día del Padre (H) | Hombre 50s distinguido, canas, porte elegante |
| 6 | **Camila — "La Dama Fragancia"** | FraganciasShop (M) | Mujer 28 elegante, piel luminosa, estilo sofisticado |
| 7 | **Tavo — "El Streetwear/Gallero"** | CapShop premium (1IRONTRENDY/Bélico/artista) (H) | Hombre 23, estilo corridos tumbados, cadenas, actitud |

*(Para fichas de producto puro NO se usa personaje — solo el producto en estudio.)*

### Brief semilla de ejemplo (Marco — se genera 1 vez y se reúsa)
```
Mexican working-class man in his early 30s, sturdy build, short dark beard,
sun-weathered tan skin, calm confident expression, looking slightly off-camera.
Standing relaxed with arms crossed, in a clean auto workshop with soft daylight
from a large doorway camera-left. Medium shot, waist up, shot on a Canon EOS R5
with 50mm lens at f/2.8, soft natural daylight with a gentle fill, grounded and
authentic. National Geographic working-life documentary aesthetic.
```
> Luego, en `/banana chat`: *"same man, now wearing [PRODUCTO], in [escena]"* y mantiene la cara.

---

## 2. Qué modo (lente de experto) usa cada cosa

La skill tiene "modos de dominio". Asignación para KonpreShop:

| Activo | Modo banana | Ratio | Personaje |
|---|---|---|---|
| Ficha de producto (las 585) | **Product** | 1:1 | — (solo producto) |
| Hero banner web | **Editorial** | 16:9 | sí |
| Portada de tienda | **Editorial** | 16:9 / 4:1 | sí |
| Mega menú (fotos destacadas) | **Product / Editorial** | 1:1 | a veces |
| Ad Meta — Feed | **Editorial** | 1:1 / 4:5 | sí |
| Ad Meta — Story/Reel | **Editorial** | 9:16 | sí |
| Conjunto / "Arma tu look" | **Editorial** | 4:5 | sí |
| Fragancias (producto premium) | **Product** | 1:1 / 3:4 | — |

---

## 3. Recetas listas (Reasoning Briefs reales con tu catálogo)

### A) Ficha de producto — look "estudio editorial" (Product mode, 1:1)
Para que NO se vean bajadas de internet. Ejemplo con una camisa:
```
A men's plaid flannel shirt by Dockers, neatly presented on an invisible
mannequin, fabric texture and weave clearly visible, buttons and collar crisp.
Set on a smooth light-gray gradient studio sweep with a subtle soft contact
shadow beneath. Straight-on hero angle, centered with breathing room. Soft
diffused softbox lighting from above with a fill card, clean separation.
Commercial product photography for an advertising campaign, Wallpaper* design
editorial.
```

### B) Hero / portada OutletShop (Editorial, 16:9, personaje Diego)
```
The same young man (Diego): Mexican, 25, fresh fade and a flat-brim cap,
wearing a Levi's denim jacket over a white tee and Vans sneakers, leaning
casually against a sunlit adobe wall in a northern-Mexico town at golden hour.
Relaxed confident half-smile. Wide editorial shot with the subject on the right
third, generous clean negative space on the left for headline text. Shot on
Sony A7R IV, 35mm at f/2.8, warm natural golden-hour light. GQ Mexico street
style editorial.
```

### C) Conjunto "uniforme completo" — sube ticket (Editorial, 4:5, Marco)
```
The same working man (Marco) wearing a full work uniform: Dickies work shirt,
matching work pants, and dielectric safety boots, holding a hard hat at his
side, standing in a clean industrial yard at mid-morning. Confident grounded
stance. Three-quarter full-body shot, subject centered, shallow depth of field
softening the background. Shot on Canon EOS R5, 50mm at f/2.8, natural daylight.
National Geographic documentary aesthetic.
```

### D) Ad Día del Padre — fragancia premium (Editorial/Product, 9:16, Don Rafa)
```
The same distinguished man (Don Rafa), 50s, silver hair, navy blazer, holding
a bottle of Valentino Uomo cologne, the bottle and label prominently displayed
in the foreground in sharp focus, his approving expression softly blurred
behind. Warm low-key library setting. Vertical story composition, product in
lower third, room for a short headline up top. Shot on Sony A7R IV, 85mm at
f/1.8, warm directional light. Esquire fragrance feature aesthetic.
```
> ⚠️ Para ads recordar el skill `konpreshop-ads-preflight` y la regla **catbox.moe** (Shopify CDN no jala con Meta).

---

## 4. El método de consistencia (lo más importante para que se vea pro)
1. Generar el **retrato base** de cada personaje (1 vez) → guardar en `assets/personajes/`.
2. Usar `/banana chat` y referir *"the same [personaje]"* + 2-3 rasgos clave + el producto nuevo.
3. nano-banana mantiene cara/estilo entre tomas → catálogo y ads se ven de una sola marca.

---

## 5. Orden cuando demos luz verde
1. 7 retratos base de personajes (la semilla reusable).
2. Grupo A auditoría (hero + portadas + mega menú) con esos personajes.
3. Look editorial de producto sobre los 82 con 0–1 foto.
4. Conjuntos/outfits de los productos estrella → cards + ads.

> Para generar: `/banana generate ...` (usa el preset `konpreshop` automáticamente). Falta solo la API key de Gemini (gratis en aistudio.google.com/apikey) → `/banana setup`.
