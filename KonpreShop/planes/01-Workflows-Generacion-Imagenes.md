# Plan de Workflows — Generación de Imágenes KonpreShop

> **Estado: SOLO PLAN. Todavía no generamos nada.** Esto es el mapa de cómo automatizaríamos las imágenes cuando le demos luz verde.
> Motor elegido: **Nano-banana (Gemini)** para escenas/lifestyle. (Más adelante se puede meter Photoroom solo para recortar fondos si hace falta).

---

## 0. Primero lo básico — ¿qué es un "workflow" y la terminología?

Imagínate una **receta de cocina**. Siempre los mismos pasos, solo cambias el ingrediente. Eso es un *workflow*: pasos fijos que repites para cada producto.

Palabras que vas a ver (en cristiano):

| Palabra técnica | Qué significa de verdad |
|---|---|
| **Input** (entrada) | La foto que le metes a la IA. Casi siempre la foto real del producto que ya está en Shopify. |
| **Prompt** | La instrucción que le escribes a la IA, como pedirle algo por WhatsApp: *"pon esta camisa en un modelo en la calle, luz de día"*. |
| **Output** (salida) | La imagen nueva que te escupe la IA. |
| **Plantilla / template** | Un prompt "molde" donde solo cambias el nombre del producto. Lo escribes UNA vez y sirve para los 585. |
| **Batch** | Hacer muchos de jalón en vez de uno por uno. En lugar de 1 camisa, las 90 camisas seguidas. |
| **Aspect ratio** | La forma del rectángulo. Banner = acostado/horizontal (16:9). Ficha de producto = cuadrado (1:1). Story de Insta = parado/vertical (9:16). |
| **API** | Un "tubo" para que esto corra solo sin que tú aprietes botones. Por ahora ni le entres; primero a mano. |

**La idea grande:** en lugar de pagar fotógrafo y sesión para cada producto, tomamos la foto que YA tienes, y con la IA generamos las versiones que faltan (modelo usándola, fondo bonito, combinada con otras prendas, banner, etc.).

---

## 1. ¿Qué "cosas" necesitan imagen? (los 8 workflows)

Dividí TODO lo que tu tienda necesita en **8 recetas**. Cada una tiene: qué foto entra, qué le pides, qué sale y para qué sirve.

### 🟥 GRUPO A — Lo que pidió la auditoría (urgente, ~17 imágenes)
> Detalle fino de estos 3 está en `02-Plan-Auditoria-Web.md`. Aquí solo el resumen de la receta.

**W1 · Hero banners (carrusel principal)**
- **Entra:** 1 producto estrella por slide (de los que SÍ tienen inventario).
- **Le pides:** escena lifestyle real — persona usando la prenda, ambiente bonito, espacio vacío a un lado para el texto.
- **Sale:** imagen horizontal (16:9, ~1920×1080) por slide. Encima va título + botón CTA.
- **Cuántos:** 3–5 slides.

**W2 · Imágenes de mega menú**
- **Entra:** 2 productos destacados por tienda + 1 ícono por categoría.
- **Le pides:** foto limpia y consistente, mismo estilo en las 4 tiendas.
- **Sale:** 8 fotos destacadas (2 × 4 tiendas) + íconos de categoría.

**W3 · Portadas de las 4 tiendas**
- **Entra:** producto representativo de cada tienda.
- **Le pides:** una foto "portada" que represente el rollo de esa tienda (Outlet = ropa casual, Uniformes = trabajo, Fragancias = perfumes elegantes, Caps = gorras).
- **Sale:** 4 portadas horizontales.

### 🟦 GRUPO B — Nivel producto (los 585, esto es el sistema grande)

**W4 · Fondo limpio / uniforme (ficha de producto)**
- **Entra:** foto real del producto.
- **Le pides:** quitar fondo y poner uno blanco/neutro consistente para todas las fichas.
- **Sale:** imagen cuadrada 1:1 lista para la ficha.
- **Para quién:** sobre todo los **80 productos con una sola foto** y los que tienen fondos feos/disparejos.

**W5 · Fotos de ángulo extra**
- **Entra:** la única foto que existe.
- **Le pides:** generar vista de espalda, lateral, detalle de tela/logo.
- **Sale:** 2–3 fotos extra por producto.
- **Para quién:** los **80 de una sola foto** (prioridad #1) + los **2 sin ninguna foto**.

**W6 · Lifestyle (modelo usando el producto)**
- **Entra:** foto del producto.
- **Le pides:** ponerlo en un modelo realista, en contexto (calle, oficina, gym, etc. según la tienda).
- **Sale:** 1–2 fotos lifestyle por producto.
- **Ojo:** aquí es donde más brilla nano-banana. Empezar por los productos más vendidos, no por los 585 de golpe.

**W7 · Combinaciones / "Arma tu look"**  ← *esto es lo que mencionaste de "posibles combinaciones"*
- **Entra:** 2–4 productos juntos (ej. camisa + pantalón + gorra + navaja).
- **Le pides:** un solo modelo o flat-lay con todo combinado, como outfit completo.
- **Sale:** imagen de "look" que sube ticket promedio (la gente compra el combo, no solo la camisa).
- **Combos naturales según tu catálogo:**
  - OutletShop: Camisa Levi's + Pantalón Dockers + Gorra
  - UniformesShop: Camisa + Pantalón + Botas (uniforme completo de trabajo)
  - CapShop + OutletShop: Gorra + Playera (look casual)
  - FraganciasShop: perfume + bolsa de regalo (set de regalo)

**W8 · Banners de categoría / colección**
- **Entra:** 3–5 productos de una misma categoría/marca.
- **Le pides:** banner con varios productos acomodados, título de la categoría.
- **Sale:** banner horizontal por colección (ej. "Levi's", "Fragancias Hombre", "Botas de trabajo").

---

## 2. Orden recomendado (de lo más rentable a lo opcional)

1. **W3 + W2 + W1** (auditoría) → la web se ve profesional YA. ~17 imágenes.
2. **W5 + W4** sobre los **82 productos con 0–1 foto** → tapar los huecos feos del catálogo.
3. **W7 combinaciones** sobre los 15–20 productos más vendidos → sube el ticket.
4. **W6 lifestyle** masivo → cuando lo anterior ya esté.
5. **W8 banners de categoría** → al final, es el "nice to have".

> Regla de oro: **nunca uses en hero/destacados los 29 productos agotados** ni los archivados. Ya están marcados en `RESUMEN-CATALOGO.md`.

---

## 3. Cómo se ejecuta cada receta (el flujo real, paso a paso)

Para CUALQUIER workflow, los pasos son los mismos:

```
1. Sacar la(s) foto(s) del producto   →  ya están en catalog.json (campo "images")
2. Escribir/usar la plantilla de prompt de ese workflow
3. Nano-banana genera la imagen
4. Revisar (¿quedó bien? ¿se ve falso?) → si no, ajustar el prompt y repetir
5. Guardar en  KonpreShop/assets/<tienda>/<workflow>/
6. Subir a Shopify (al producto, colección, o tema) cuando esté aprobada
```

**Manual vs. automático:**
- **Fase 1 (recomendado para empezar):** a mano, producto por producto, para calibrar el estilo. Tú apruebas cada una.
- **Fase 2 (cuando el estilo ya esté afinado):** batch — le pasas la lista del `catalog.json` y genera tandas de 10–20. Tú solo revisas.
- **Fase 3 (opcional, a futuro):** conectar por API para que productos nuevos generen sus imágenes solos al crearse.

---

## 4. Plantillas de prompt base (para reusar)

Estas son los "moldes". Solo cambias lo que está en `[corchetes]`.

**W5 – ángulo extra:**
> *"Foto de producto de [PRODUCTO], misma prenda y color exactos que la imagen de referencia, mostrando [vista trasera / lateral / detalle de tela], fondo blanco de estudio, luz suave, alta resolución, fotorealista."*

**W6 – lifestyle:**
> *"Modelo [hombre/mujer] real usando [PRODUCTO] de la imagen, en [contexto según tienda], luz natural, foto editorial de catálogo, espacio negativo a la izquierda."*

**W7 – combinación:**
> *"Outfit completo: [PRODUCTO 1] + [PRODUCTO 2] + [PRODUCTO 3], en un solo modelo coherente, estilo lookbook, fondo neutro."*

**W3 – portada de tienda:**
> *"Imagen de portada para tienda [NOMBRE], que transmita [concepto: outlet casual / uniformes de trabajo / perfumes elegantes / gorras urbanas], horizontal, premium, con zona limpia para texto."*

> Cuando demos luz verde, estos prompts se afinan probando 2–3 versiones de cada uno hasta dar con el estilo KonpreShop.

---

## 5. Lo que NO vamos a tocar (de tu auditoría)
- La estructura de las 4 tiendas separadas — está bien.
- El announcement bar — está bien.
- Las secciones de trust / value props — funcionan.
- En `templates/index.json`: mantener el orden que ya tienes. Las secciones nuevas (portadas de tienda + destacados) van **entre "tiendas" y "featured"**.
