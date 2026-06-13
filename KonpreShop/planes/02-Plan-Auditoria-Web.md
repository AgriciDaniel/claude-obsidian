# Plan de Auditoría Web — Hero, Mega Menú y Portadas

> **Estado: SOLO PLAN.** Aquí aterrizamos los 3 hallazgos de tu auditoría con estructura concreta usando los productos reales del catálogo.
> Las recetas de imagen viven en `01-Workflows-Generacion-Imagenes.md` (W1, W2, W3).

---

## Hallazgo 1 — Hero banners (carrusel principal)

**Problema:** ahora muestran gráficos de "35% off" y Aplazo. Se ve a publicidad barata, no a tienda seria.

**Solución:** 3–5 slides con **foto real de producto/persona** + título + botón CTA encima.

**Propuesta de slides (1 por tienda + 1 oferta):**

| Slide | Producto sugerido (con stock) | Título | Botón (CTA) |
|---|---|---|---|
| 1 | Look OutletShop (Levi's + Dockers) | "Tu estilo, sin pagar de más" | Ver OutletShop |
| 2 | Uniforme completo (camisa + pantalón + botas) | "Uniformes que aguantan el turno" | Ver UniformesShop |
| 3 | Perfume premium (Lattafa / Valentino) | "Fragancias originales, precio real" | Ver FraganciasShop |
| 4 | Gorra destacada (JC Hats / Toto) | "Gorras que combinan con todo" | Ver CapShop |

- **Imagen:** receta **W1**, horizontal 16:9 (~1920×1080), con espacio limpio para el texto.
- **Regla:** solo productos con inventario > 0 (los 29 agotados están listados en el resumen).

---

## Hallazgo 2 — Mega menú con imágenes

**Problema:** al pasar el cursor sobre una tienda no se abre nada visual.

**Solución:** menú de **4 columnas** por tienda: `Trending` · `Categorías` · `Marcas` · `2 fotos destacadas`.
Esto se arma en **Shopify → Tienda online → Navegación → sub-ítems bajo cada tienda.**

### Estructura concreta (sacada de tu catálogo real):

**OutletShop** (235 productos)
- *Categorías:* Camisas (36) · Pantalones (30) · Playeras · Chamarras (10) · Calzado/Vans (16)
- *Marcas:* Levi's (32) · Dockers (40) · Vans (17) · Columbia (16)
- *2 fotos:* look casual + chamarra destacada → receta **W2**

**UniformesShop** (145 productos)
- *Categorías:* Camisas (36) · Blusas (32) · Playeras (29) · Pantalones (13) · Botas (10) · Chalecos
- *Marcas:* My Land (29) · Bibo (18) · Unitam (15) · Dickies (11)
- *2 fotos:* uniforme completo + botas de trabajo → **W2**

**FraganciasShop** (47 productos)
- *Categorías:* Hombre (23) · Mujer (19) · Unisex (5)
- *Marcas:* Lattafa (10) · Valentino · YSL · Carolina Herrera
- *2 fotos:* perfume hombre + perfume mujer → **W2**

**CapShop** (44 productos)
- *Categorías:* Gorras planas · Gorras curvas · Accesorios
- *Marcas:* JC Hats (8) · Toto Caps (6) · El Barbas (6) · Yupoong
- *2 fotos:* gorra urbana + flat-lay de varias → **W2**

> **Pendiente de decisión:** las 4 tiendas dejan **123 productos huérfanos** (Victorinox, gorras sin tag, promocionales). Hay que decidir si:
> (a) se reparten en las tiendas existentes (gorras → CapShop, Victorinox → ¿UniformesShop?), o
> (b) se crea una 5ª sección tipo "Accesorios / Victorinox". Ver `RESUMEN-CATALOGO.md`.

---

## Hallazgo 3 — Sección "4 Tiendas" necesita imágenes

**Problema:** ahora son solo botones de texto.

**Solución:** una **foto de portada** por tienda (receta **W3**), horizontal, con la zona limpia para el nombre.

| Tienda | Concepto de la portada |
|---|---|
| OutletShop | Ropa casual de marca, vibra "buen precio sin verse barato" |
| UniformesShop | Ambiente de trabajo/laboral, profesional |
| FraganciasShop | Perfumes elegantes, fondo premium oscuro |
| CapShop | Gorras, vibra urbana/streetwear |

---

## Dónde van las secciones nuevas (instrucción para Claude Design)
- Mantener **exactamente** el orden de `templates/index.json` que ya existe.
- Añadir las secciones nuevas (portadas de tienda + destacados) **entre la sección "tiendas" y la sección "featured"**.

## Lo que NO se toca
Estructura de las 4 tiendas ✔ · Announcement bar ✔ · Secciones de trust/value props ✔
