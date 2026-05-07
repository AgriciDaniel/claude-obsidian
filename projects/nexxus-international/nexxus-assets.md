# Nexxus International — Assets y Archivos

## Logos

| Archivo | Descripción | Ruta |
|---------|-------------|------|
| `nexxus_logo_transparent.png` | Logo dark sobre fondo transparente | `assets/nexxus_logo_transparent.png` |
| `nexxus_logo_white.png` | Logo blanco (para fondos oscuros) | `assets/nexxus_logo_white.png` |

## Imágenes de campaña (nuevas, compartidas por usuario)

Guardadas en `~/Desktop/nexxus-portfolio-assets/new-images/`

| Clave JSON | Archivo | Descripción |
|------------|---------|-------------|
| `hugo_red_room` | `new_img_00.jpg` | Jashlem — traje negro, cuarto rojo HUGO (editorial) |
| `ch212_bar` | `new_img_01.jpg` | Jashlem — bar CH 212, neon "212", muy moody |
| `f1_pista` | `new_img_02.jpg` | Jashlem — F1 Miami, auto blanco, gafas de sol |
| `f1_jersey` | `new_img_03.jpg` | Jashlem — espalda HUGO jersey F1, multitudes |
| `maybelline_bear` | `new_img_04.jpg` | Kenia OS — oso rosa gigante Maybelline NY |

## Imágenes existentes (web-images/)

Ruta base: `~/Desktop/nexxus-portfolio-assets/web-images/`

| Clave | Archivo |
|-------|---------|
| `hugo_cover` | `1_hugo_jashlem_cover_hires.jpg` |
| `hugo_global` | `2_hugo_jashlem_global_hires.jpg` |
| `hugo_f1_1/2/3` | `3_hugo_f1_miami_1/2/3.jpg` |
| `maybelline_kenia` | `4_kenia_os_maybelline.jpg` |
| `nyx_jimena` | `5_jimena_nyx_billboard.jpg` |
| `ae_domelipa` | `6_domelipa_american_eagle_hires.jpg` |
| `ch212_model` | `8_carolina_herrera_212_model.jpg` |

## Logos de marcas

Ruta: `~/Desktop/nexxus-portfolio-assets/logos/`

- `hugo_logo_header.png`
- `maybelline_header.png`
- `nyx_header.png`
- `american_eagle_header.png`
- `carolina_herrera_header.png`
- `garnier_header.png`
- `sephora_header.png`
- `shein_header.png`

## Archivos del proyecto

| Archivo | Descripción |
|---------|-------------|
| `nexxus-portfolio-v3.html` | HTML v3 completo (5.2 MB, self-contained con base64) |
| `imgs_v3.json` | 32 imágenes base64 para embeber en HTML (9.1 MB) |
| `nexxus-portfolio-v2.html` | HTML v2 (descartado — demasiado cinematográfico) |
| `NEXXUS_INTERNATIONAL_Portfolio_2025.pdf` | PDF v2 (3.9 MB, 12 páginas A4 landscape) |

## Para generar PDF v3

```bash
cd ~/Desktop/nexxus-portfolio-assets
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless=new \
  --print-to-pdf="NEXXUS_INTERNATIONAL_Portafolio_2025_v3.pdf" \
  --print-to-pdf-no-header \
  --no-margins \
  "file:///Users/ericolea/Desktop/nexxus-portfolio-assets/nexxus-portfolio-v3.html"
```
