# Casting KonpreShop + Asignación de Productos (Photoshoot)

> 6 modelos fijos (3H + 3M) generados como base reutilizable en `assets/casting/`.
> Motor de photoshoot: `scripts/shoot.py` (modelo del casting + producto real → galería con cara fija).
> Estética y reglas: docs 05 y 07. **CapShop y FraganciasShop NO usan este casting** (receta aparte).

---

## El casting (caras base en `assets/casting/`)

| ID | Nombre | Edad | Look | Tienda/segmento |
|---|---|---|---|---|
| M1 | **Mateo** | 20s | Joven fresco, fade moderno, vibe casual | Outlet hombre joven |
| M2 | **Emiliano** | 28 | Galán GQ, barba arreglada, clásico | Outlet/Uniformes hombre (core) |
| M3 | **Rodrigo** | 40s | Distinguido, canas, elegante rudo | Premium/maduro hombre |
| W1 | **Valentina** | 20s | Joven, pelo ondulado, fresca | Outlet mujer joven |
| W2 | **Renata** | 28 | Elegante profesional | Uniformes mujer / profesional |
| W3 | **Ximena** | 35 | Madura, cálida, elegante | Premium/maduro mujer |

Board: `assets/casting/_CASTING_BOARD.png`. Validado: `assets/lote/polo-emiliano/` (Emiliano + polo, cara consistente ✅).

---

## Asignación de productos (apparel Outlet + Uniformes)

> Reparto por arquetipo. Cantidades aprox. (se afinan tras el etiquetado de género). Total apparel ≈ las categorías de ropa; gorras/fragancias/accesorios van por otra vía.

### Hombres
| Modelo | Categorías asignadas | Aprox |
|---|---|---|
| **Mateo** (joven) | Playeras, polos básicos, jeans casuales, tank tops, sudaderas casual | ~60 |
| **Emiliano** (core) | Camisas (Dockers, Columbia, Soul&Blues, Pavini), polos vestir | ~90 |
| **Rodrigo** (maduro) | Camisas de vestir formales, Dockers premium, chamarras, sudaderas premium | ~55 |

### Mujeres
| Modelo | Categorías asignadas | Aprox |
|---|---|---|
| **Valentina** (joven) | Blusas & playeras jóvenes, crop tops, casual mujer | ~40 |
| **Renata** (profesional) | Blusas de trabajo (Uniformes mujer), playeras/polos dama | ~45 |
| **Ximena** (madura) | Chamarras dama, blusas elegantes, pantalones de vestir mujer | ~35 |

### Sin casting de ropa (receta propia)
- **CapShop** (gorras) → streetwear/colab artista.
- **FraganciasShop** → producto premium oscuro.
- **Victorinox / carteras / promocionales** → producto solo (sin modelo).

---

## Cómo se corre el photoshoot

```bash
KEY='<gemini key>'
python3 scripts/shoot.py --slug <producto-modelo> \
  --model-image assets/casting/<MODELO>.png \
  --product-image <foto real del producto> \
  --gender h|m \
  --garment "descripción corta de la prenda" \
  --key "$KEY"
```
Salida: `assets/lote/<slug>/` con 01-frente, 02-espalda, 03-maniqui, 04-closeup + manifest.

**QA obligatorio** (Claude revisa a tamaño completo): cara = la del casting · anatomía (brazos/manos) · color del producto · sin texto basura · piel real. Re-genera la toma que falle.

---

## Estado
- ✅ Casting 6 modelos generado.
- ✅ `shoot.py` validado (Emiliano + polo).
- ⏭️ Falta: correr el lote por modelo (necesita key permanente `AIza...` para no cortarse).
