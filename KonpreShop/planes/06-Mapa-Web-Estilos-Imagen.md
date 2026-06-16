# Mapa de la Web KonpreShop → qué estilo de imagen va en cada espacio

> Revisión de www.konpreshop.mx (home) + estilo objetivo: **Banana Republic** (cálido, limpio, premium) + **Drip Moda** (on-model, urbano). Norte: que se vea tienda real.
> Estándares de prompting en `05-Investigacion-Prompting-Realista.md`.

---

## Estilo objetivo (de la investigación de referentes)

- **Banana Republic / Gap studio:** fotos pensadas para evaluar **fit, largo y textura de tela**. Lifestyle en interiores modernos bien iluminados con **luz natural de ventana**, props neutros (madera, concreto), lente 50mm, **temperatura cálida**. Studio: high-key, luz suave a 45° + relleno.
- **Drip Moda:** on-model, urbano, premium smart-casual, 5 imágenes por producto (varios ángulos).
- **Regla de oro de luz:** ficha de producto = luz **suave y pareja** (enfocada en tela/fit). Lifestyle/hero = luz **natural lateral de ventana** (más mood y realismo).

---

## Espacios de imagen en el HOME (lo que detecté en vivo)

| # | Espacio | Hoy | Estilo de imagen a meter | Personaje | Ratio |
|---|---|---|---|---|---|
| 1 | **Hero slider** (Banner 1, Banner 2 + versiones móvil) | Banners desktop 1900px + móvil 1000px | **Lifestyle editorial** con personaje en escenario real + zona limpia para título/CTA. Estilo BR cálido. | sí (Diego/Sofía/Marco según slide) | 16:9 desktop · 9:16 móvil |
| 2 | **Banners promo** (EXPORTACIÓN, Envío, MARCAS) | Banners informativos | Mixto: franja lifestyle de fondo + texto. Para "MARCAS" un flat-lay premium de producto multimarca. | a veces | 4:1 / 8:1 (franja) |
| 3 | **Tiles de categoría** (Pantalones H, Camisas Dockers, Chamarras H, Gorras) | Portadas con cover | **On-model 3/4** (BR) o producto hero limpio. Misma luz y fondo entre los 4 = se ve de marca. | sí (3/4 o detalle) | 4:5 / 1:1 |
| 4 | **"Estos productos vuelan"** (destacados, doble imagen al hover) | 2 imágenes por producto (cambia al pasar cursor) | **Imagen 1:** ficha editorial (maniquí/limpia). **Imagen 2:** on-model o ángulo. Aprovecha el swap del tema. | imagen 2 sí | 1:1 / 4:5 |
| 5 | **Logos de marca** (Levi's, Dockers, Pavini, Vans, Lattafa…) | Logos | Dejar como logos (no tocar). | — | — |

> Pendiente confirmar: portadas de las **4 tiendas** y **mega menú** (estaban en la auditoría original, doc 02). Si el tema los tiene aparte del home, aplican estilos de `02-Plan-Auditoria-Web.md`.

---

## Receta por espacio (pose · escenario · luz · cámara)

**1 · Hero lifestyle (estilo BR):**
- Pose: 3/4 angulado, mano en bolsa o mid-stride; mirada fuera de cuadro.
- Escenario: interior minimalista madera+concreto, o muro urbano del norte a golden hour.
- Luz: natural lateral de ventana, cálida, relleno suave.
- Cámara: 35mm f/2.8 full-length, espacio negativo a un lado para el texto.

**3 · Tile de categoría / on-model (estilo BR/Drip):**
- Pose: 3/4 de cuerpo (de rodillas hacia arriba), un hombro al frente.
- Escenario: fondo neutro cálido o seamless.
- Luz: tres puntos (key revela textura, fill suaviza, back separa) o ventana lateral.
- Cámara: 50mm, fit y tela visibles.

**4 · Ficha de producto (imagen 1):**
- Ghost mannequin / solo prenda, fondo gris degradado, sombra de contacto.
- Luz suave pareja, color exacto. (ya validado con el Dickies)

---

## Pruebas que ya validamos (carpeta `assets/pruebas/`)
- `dickies874_solo_prenda.png` → estándar **ficha** (espacio 4, img 1). ✅
- `lattafa_yara_editorial.png` → ficha **fragancias** (premium oscuro). ✅
- `marco_v2_realista.png` → **retrato base** de personaje con piel real. ✅
- `marco_lifestyle_BR_v2.png` → **hero / tile lifestyle** estilo Banana Republic. ✅ (el más cercano a "tienda real")

## Siguiente
- Subir el realismo otro escalón (probar golden hour exterior, o más grano de cámara/film).
- Definir el estándar final por espacio y empezar a producir en lote.
