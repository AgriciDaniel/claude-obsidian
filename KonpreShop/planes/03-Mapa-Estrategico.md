# Mapa Estratégico KonpreShop — Qué tenemos, qué está roto, dónde está la oportunidad

> Análisis completo del catálogo (585 productos, 195 colecciones) hecho el **2026-06-13**.
> Esto responde 3 cosas: (1) **qué tenemos**, (2) **qué está mal/duplicado**, (3) **cómo acomodarlo y segmentar para vender más + generar imágenes con nano-banana**.

---

## PARTE 1 — Qué tenemos (el inventario, en limpio)

**585 productos · 579 activos · 2,260 imágenes (3.86 por producto)**

### Las 4 tiendas vivas
| Tienda | Productos | Precio típico | Lo que la define |
|---|---|---|---|
| **OutletShop** | 235 | $149–$3,399 (med. $869) | Ropa de marca con descuento: Levi's, Dockers, Vans, Columbia |
| **UniformesShop** | 145 | $74–$1,230 (med. $539) | Ropa de trabajo: My Land, Bibo, Dickies, Unitam |
| **FraganciasShop** | 47 | $620–$3,070 (med. $1,345) | Perfumes originales: Lattafa, Valentino, YSL |
| **CapShop** | 44 | $90–$3,199 (med. $1,200) | Gorras: JC Hats, Toto, El Barbas, Yupoong |

### Dimensiones para segmentar (lo que ya vive en la data)
- **Marcas fuertes:** Dockers (42), Pavini (39), Levi's (37), Victorinox (36), My Land (29), Soul & Blues (27), 5.11 (24), Lee Hanton (20).
- **Categorías top:** Camisa (68), Gorra (50), Pantalón (47), Fragancia (47), Blusa (39), Playera (32), Navaja (27), Chamarra (21).
- **Color dominante:** negro (153), azul marino (81), blanco (67), rojo (59) → la paleta natural de la tienda.
- **Precio:** desde $74 (uniforme básico) hasta $6,119 (artículo huérfano) — hay para todos los bolsillos.

---

## PARTE 2 — Lo que está ROTO (conflictos y errores a arreglar)

### 🔴 A. El desmadre de colecciones (lo más grave)
**195 colecciones para 585 productos.** Eso es 1 colección por cada 3 productos — demasiadas, y muchas basura:
- **~42+ colecciones VACÍAS** (0 productos). Ejemplos: `505`, `510`, `shorts`, `crop-tops`, `biker-shorts`, `prueba-de-etiqueta`, `.` (literal punto), `masculino`, `plumas`, `mochilas`, `agendas`, `hieleras`…
- **Colecciones DUPLICADAS** (mismo nombre, distinta colección):
  - "Dickies" ×3 (`dickies`=15, `dickies-1`=18, `dickies-2`=6)
  - "PAVINI" ×3 (`pavini`=30, `carteras-pavini`=7, `pavini-1`=0)
  - "FashionShop" ×2 (ambas vacías)
  - "UniformeShop-Mujer-Blusa" ×2 (una en 0, otra con 32)
  - "OutletShop Calzado" ×2 idénticas (31 c/u)
- **Gorras fragmentadas y solapadas:** `gorras`=66, `capshop-gorras`=66, `outletshop-hombre-gorras-y-accesorios`=130 → el mismo producto contado en 3 lados.
- **Levi's despedazado:** `501`/`505`/`510`/`511`/`514`/`levis-caballero`/`levis-hombre`/`pantalones-levis-hombre` → 8 colecciones para una marca.

### 🟠 B. "Shops fantasma" (arquitectura creada, nunca llenada)
La tienda fue diseñada para MÁS de 4 tiendas, pero quedaron vacías:
- **REACTIVESHOP (deportes):** 7 subcolecciones (básquet, fútbol, vóley, béisbol, pádel, travesía) → TODAS en 0.
- **MYLANDSHOP:** 5 subcolecciones en 0 — aunque la marca My Land SÍ tiene 29 productos (hoy metidos en UniformesShop).
- **SERVICIOSHOP:** 0.
- **PROMOSSHOP:** 14 productos, pero subcolecciones (termos, tazas) casi vacías.
> **Decisión:** o se activan estas tiendas (si vas a meter producto) o se borran para no confundir.

### 🟡 C. Errores de producto puntuales
- **2 productos a $0** ("PANTALON" y "PANTALON MYLAND") → sin precio y sin tienda. Arreglar o archivar.
- **9 productos en 2 tiendas a la vez** (OutletShop + UniformesShop) — ej. camisas Dickies/Gameguard, chamarras Lee Hanton. Decidir su casa.
- **6 productos archivados** que aún tienen tags de tienda (3 son camisas Dockers) → no salen, pero ensucian.
- **49 productos con la marca puesta como "categoría"** (productType = Vans, Soul & Blues, Pavini…) → rompe los filtros por tipo.
- **13 productos sin categoría** (productType vacío).
- **407 productos (69%) SIN etiqueta de género** → no se pueden filtrar por Hombre/Mujer, y eso es CLAVE para segmentar ads e imágenes.
- **123 productos huérfanos** sin tienda (Victorinox 36, gorras sin tag 29, promocionales 16).

---

## PARTE 3 — Cómo acomodarlo (arquitectura propuesta)

### Limpieza (orden sugerido)
1. **Borrar las ~42 colecciones vacías** + las duplicadas (quedarte con 1 por concepto). Meta: bajar de 195 a ~60 colecciones limpias.
2. **Decidir las shops fantasma:** activar REACTIVESHOP si hay plan deportivo, si no, borrar todo ese árbol.
3. **Etiquetar género** en los 407 sin marcar (se puede hacer en lote con reglas: si está en colección "Mujer/Dama" → tag mujer, etc.).
4. **Reubicar los 123 huérfanos:** gorras sueltas → CapShop; Victorinox + carteras + mochilas → nueva sección **"Accesorios"** (o ProMosShop si son regalo corporativo).
5. **Arreglar productType** de los 49 marca-como-tipo y los 13 vacíos.

### Segmentación estratégica (las "rebanadas" para vender + para imágenes)
Más allá de las 4 tiendas, el catálogo se puede rebanar en ejes que sirven para **colecciones, ads y conjuntos de imágenes**:

| Eje | Rebanadas | Para qué sirve |
|---|---|---|
| **Género** | Hombre / Mujer / Unisex | Ads segmentados, mega menú, personas de imagen |
| **Ocasión** | Trabajo · Casual/Outlet · Arreglado/Vestir · Regalo (fragancias+promos) | Banners temáticos, bundles |
| **Precio** | Económico (<$500) · Medio ($500–1500) · Premium (>$1500) | Ads por presupuesto, "regalo premium" |
| **Marca destacada** | Levi's · Dockers · Victorinox · Lattafa | Landing por marca, co-branding |
| **Temporada** | Invierno (chamarras, sudaderas — ya hay 54 en "MODA INVERNAL") · Verano | Hero estacional |

---

## PARTE 4 — Dirección creativa para nano-banana (personajes, stylist y look editorial)

> Aquí está lo que te emocionaba: usar nano-banana como **director creativo + stylist**, no solo para recortar fondos.

### 4.1 — Crear PERSONAJES recurrentes (personas de marca)
En vez de modelos al azar cada vez, definimos **3–4 personajes fijos** que reaparecen en toda la web/ads. Esto da consistencia (la gente reconoce "la cara" de KonpreShop) y es justo donde nano-banana brilla: puede mantener el mismo personaje en muchas escenas.

| Personaje | Para qué tienda | Descripción base (prompt seed) |
|---|---|---|
| **"El Trabajador"** | UniformesShop | Hombre 30s, complexión real, en entorno laboral (taller, gasolinera, obra) |
| **"La Profesional"** | UniformesShop / OutletShop mujer | Mujer 30s, uniforme limpio o blusa, ambiente hotel/restaurante/oficina |
| **"El Casual"** | OutletShop / CapShop | Hombre 20s–30s estilo norteño/urbano, jeans + camisa + gorra |
| **"Ella Casual"** | OutletShop mujer | Mujer 20s–30s, look casual de día |
*(Para fragancias se usa producto solo + manos/ambiente premium, sin personaje fijo.)*

> Receta: se genera UN retrato base por personaje, se guarda, y se reusa como referencia en cada imagen nueva ("mismo personaje que la referencia, ahora usando X").

### 4.2 — El stylist: CONJUNTOS / outfits (combinaciones reales del catálogo)
nano-banana arma el look completo. Combos que tienen sentido con TU inventario:
- **Outfit trabajo (UniformesShop):** Camisa Dickies + Pantalón + Botas → "uniforme completo".
- **Outfit casual norteño (Outlet+Cap):** Camisa Pavini/Soul&Blues + Jeans Levi's + Gorra JC Hats.
- **Outfit dama casual (Outlet):** Blusa My Land + Jeans + accesorio.
- **Set de regalo (Fragancias+Promos):** Perfume Lattafa + termo/cartera Pavini → "regalo Día del Padre".
- **Look invierno:** Chamarra Lee Hanton + sudadera + gorra.

Cada conjunto = 1 imagen para card/banner/ad, donde se ven varios productos juntos (sube el ticket: compran el combo, no la pieza).

### 4.3 — El look "estudio editorial" para fotos de PRODUCTO
Para que las fichas NO se vean "bajadas de internet". Spec del estilo KonpreShop:
- **Fondo:** estudio limpio (blanco roto / gris claro degradado), no blanco plano aburrido.
- **Luz:** suave, tipo softbox, con sombra de contacto sutil debajo (le da peso real, no recortado).
- **Material:** que se note la textura real (mezclilla, algodón, piel de cartera, metal de navaja).
- **Encuadre:** producto centrado, aire alrededor, alta resolución.
- **Consistencia:** misma luz y fondo en TODAS las fichas de una tienda → catálogo que se ve de marca seria.
- **Prompt base:** *"Foto de producto editorial de [PRODUCTO], fondo de estudio gris claro degradado, iluminación softbox suave, sombra de contacto sutil, textura de material visible, fotorealista, alta resolución, estilo catálogo premium."*

### 4.4 — Dónde se usa cada tipo de imagen
| Destino | Tipo de imagen | Personaje/Estilo |
|---|---|---|
| Hero / banners web | Lifestyle con personaje | Personaje fijo + escena |
| Cards de producto (ficha) | Producto editorial | Estudio limpio, sin persona |
| Mega menú / portadas tienda | Lifestyle o conjunto | Personaje + look |
| Ads (Meta) | Lifestyle o conjunto, formato story/feed | Personaje + producto, con regla catbox del skill de ads |
| "Arma tu look" | Conjunto/outfit | Stylist multiproducto |

---

## Siguiente paso
Cuando des luz verde generamos, en este orden:
1. Los **4 retratos base de personajes** (semilla que se reusa siempre).
2. El **Grupo A de la auditoría** (hero + mega menú + portadas) usando esos personajes.
3. Look editorial sobre los **82 productos con 0–1 foto**.
4. Conjuntos/outfits para los productos estrella → cards y ads.

> Antes de generar para ads, recordar el skill `konpreshop-ads-preflight` (regla catbox.moe).
