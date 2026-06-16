# KonpreShop — Catálogo + Plan de Imágenes

> Carpeta creada el **2026-06-13**. Aquí vive todo el inventario exportado de Shopify y los planes para automatizar la generación de imágenes.
> **Estado general: catálogo descargado y ordenado ✔ · imágenes nuevas: NO generadas todavía (solo plan).**

## ¿Qué hay en cada archivo?

### 📊 Datos (carpeta `data/`)
| Archivo | Qué es |
|---|---|
| `catalog-raw.jsonl` | Exportación cruda de Shopify (1 línea por producto + 1 por imagen). El original sin tocar. |
| `catalog.json` | **El bueno.** 585 productos limpios con todas sus imágenes agrupadas, tienda, marca, precio, inventario, links. |
| `catalog.csv` | Lo mismo pero en hoja de cálculo (se abre en Excel/Numbers). |

### 📋 Resumen
| Archivo | Qué es |
|---|---|
| `RESUMEN-CATALOGO.md` | Las estadísticas: cuántos por tienda, marcas, categorías, qué hay que arreglar. **Empieza por aquí.** |

### 🗺️ Planes (carpeta `planes/`)
| Archivo | Qué es |
|---|---|
| `01-Workflows-Generacion-Imagenes.md` | El sistema de "recetas" para generar imágenes (8 workflows), explicado fácil + plantillas de prompt. |
| `02-Plan-Auditoria-Web.md` | Soluciones concretas a los 3 hallazgos de tu auditoría (hero, mega menú, portadas) con datos reales. |
| `03-Mapa-Estrategico.md` | **El mapa completo:** qué tenemos, qué está roto (195 colecciones, duplicados, shops fantasma), cómo acomodarlo, y la dirección creativa nano-banana (personajes, stylist, look editorial). |
| `04-Direccion-Creativa-Banana.md` | Dirección creativa aplicando la skill **banana**: casting de 7 personajes recurrentes, modos por dominio, ratios, y Reasoning Briefs reales listos para generar. |
| `05-Investigacion-Prompting-Realista.md` | Cómo lograr realismo extremo: weighting en Gemini, anti-"plastic skin", casting atractivo real, do/don'ts fashion, códigos Banana Republic, candid reportaje, modelo NB2. |
| `06-Mapa-Web-Estilos-Imagen.md` | Mapa de cada espacio con imagen de la web → qué estilo va en cada uno. |
| `07-Workflow-Produccion-Galeria.md` | Workflow anti-errores visuales (`gallery.py`) + checklist QA + estilo por tienda. |
| `08-Casting-y-Asignacion.md` | El casting de 6 modelos (3H+3M) + asignación de productos + `shoot.py`. |
| `09-Plan-Styling-Pose.md` | **El plan final:** look Levi's MX natural pro — styling completo + librería de poses + shot list por producto. |

### 🛠️ Scripts (carpeta `scripts/`)
| Archivo | Qué es |
|---|---|
| `shoot.py` | **Motor final.** Modelo del casting + producto real → galería styleada (look completo + pose por toma + luz Levi's). Nano Banana 2 @ 2K. |
| `gallery.py` | Versión previa (Gap limpio, 4 tomas) — base del workflow anti-errores. |

> Imágenes generadas (casting, lote, pruebas) viven en `assets/` — NO versionadas (reproducibles con los scripts). El casting base está en `assets/casting/`.

### 🖼️ Vista interactiva
| Archivo | Qué es |
|---|---|
| `catalogo-dashboard.html` | **Ábrelo en tu navegador** (doble clic). Las 585 fichas con fotos reales, filtros por tienda/marca/categoría/género + flags de error. |

### 🎨 Herramienta de imágenes
Skill **banana** instalada (`~/.claude/skills/banana/`) + preset de marca `~/.banana/presets/konpreshop.json`. Falta API key de Gemini para generar (`/banana setup`).

## Lo más importante de un vistazo
- **585 productos**, 579 activos, 2,260 imágenes (promedio 3.86 c/u).
- **4 tiendas:** OutletShop (235) · UniformesShop (145) · FraganciasShop (47) · CapShop (44).
- **⚠️ 123 productos huérfanos** sin etiqueta de tienda (Victorinox, gorras, promocionales) → hay que decidir dónde van.
- **⚠️ 82 productos con 0–1 foto** → prioridad #1 cuando generemos.
- **⚠️ 29 agotados** → no usar en hero ni destacados.

## Motor de imágenes elegido
**Nano-banana (Gemini)** para escenas/lifestyle. Photoroom queda como opción solo para recortes de fondo si hace falta.

## Próximo paso (cuando des luz verde)
Generar primero el **Grupo A** (auditoría): ~17 imágenes (portadas + mega menú + hero). Es lo que hace que la web se vea pro de inmediato.
