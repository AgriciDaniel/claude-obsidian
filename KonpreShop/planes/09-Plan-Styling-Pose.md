# Plan de Styling + Pose (estilo Levi's MX — natural pro)

> Basado en las referencias de Eric (`Desktop/shoot/`): páginas de producto Levi's México.
> "Más styleado, foto natural pro, sin tanta luz, cada look con pose relajada pero fashion."
> Esto se planea ANTES de disparar (shot list de director de arte). Reemplaza el look plano/bright anterior.

---

## 1. El look objetivo (ADN de las referencias)

| Elemento | Spec |
|---|---|
| **Fondo** | Seamless neutro claro cálido (warm light-gray / greige suave). NO blanco quemado, NO oscuro. |
| **Luz** | Natural de ventana, **balanceada y suave**, con una sombra direccional sutil. "Sin tanta luz" = no high-key, no flasheado; tampoco moody-oscuro. Punto medio natural pro. |
| **Styling** | **Looks COMPLETOS**, no la prenda sola: top + bottom + calzado, a veces layered (tee bajo camisa abierta) + accesorio simple (cinto, beanie, lentes). La prenda héroe se ve clara pero en contexto. |
| **Pose** | Relajada pero fashion, **variada por toma** (no frontal tiesa). |
| **Modelo** | Peinado + makeup natural (mujeres pretty), grooming (hombres). Piel real. |
| **Galería** | 5–6 tomas: varios ángulos + 1 detalle. |

---

## 2. Reglas de STYLING por tipo de prenda

**TOPS** (camisa, playera, polo, blusa):
- Pareja: jeans Levi's o pantalón neutro + calzado limpio (botas/tenis).
- Layering opcional: tee lisa bajo camisa abierta; accesorio (cinto/beanie).
- Encuadre: cuerpo superior completo hasta medio muslo. La prenda héroe domina.

**BOTTOMS** (pantalón, jeans):
- Pareja: tee fitted o camisa fajada simple + tenis/botas.
- Encuadre: de pecho/cintura hacia abajo hasta el calzado, mostrando el fit.
- OBLIGATORIO: vista de **espalda** (clave en jeans) + detalle de bolsas/herrajes.

---

## 3. Librería de POSES (relajadas pero fashion) — se asigna 1 por toma

| Código | Pose | Para |
|---|---|---|
| **P1 Hero** | De pie relajado, peso en una pierna, una mano en bolsa, mirada a cámara, calma segura | Toma 1 (héroe) |
| **P2 ¾** | Torso girado ¾, mano ajustando cuello/manga o en bolsa, mirada ligeramente fuera | Toma 2 |
| **P3 Movimiento** | A media zancada caminando, natural, mirada fuera (candid fashion) | Toma 3 |
| **P4 Espalda** | Vista de espalda o glance sobre el hombro | Toma 4 |
| **P5 Lean/Sentado** | Recargado en pared o sentado relajado, editorial | alterno |
| **P6 Detalle** | Crop en la prenda (manos en bolsas enmarcando, cuello, bolsas traseras) | Toma 5 |

---

## 4. Plantilla de shot list por producto

```
Producto: __________   Modelo: __________   Tienda: __________
Styling (look completo): [héroe] + [bottom/top pareja] + [calzado] + [layer/accesorio]
Tomas:
  01  P1 Hero      — look completo, frente
  02  P2 ¾         — gesto natural
  03  P3 Movimiento— caminando
  04  P4 Espalda
  05  P6 Detalle / o maniquí limpio del producto solo
Fondo: warm light-gray  ·  Luz: natural balanceada + sombra sutil
```

---

## 5. Ejemplos concretos (así se planea cada uno)

**Camisa Authentic Levi's (Emiliano · OutletShop)**
- Styling: camisa azul abierta + tee blanca debajo + jeans Levi's + botas + (beanie opcional).
- Tomas: P1 hero (manos en bolsa) · P2 ¾ ajustando manga · P3 caminando · P4 espalda · P6 detalle cuello/bolsillo.

**Pantalón Chino Khaki (Rodrigo · Outlet/Uniformes)**
- Styling: chino khaki + tee blanca fajada simple + tenis blancos + cinto.
- Encuadre: pecho-abajo. Tomas: P1 frente fit · P2 ¾ · P4 **espalda (bolsas)** · P6 detalle herrajes/dobladillo.

**Blusa floral (Valentina · OutletShop mujer)**
- Styling: blusa + jeans Levi's high-rise + sandalias/botín + arracadas. Pelo ondas, makeup natural.
- Tomas: P1 hero · P2 ¾ mano en cintura · P3 movimiento · P6 detalle tela.

---

## 6. Qué cambia en el motor (`shoot.py`)
- **Fondo/luz** → neutro claro cálido + luz natural balanceada (bajar de moody-oscuro, subir de bright; punto Levi's).
- **Styling** → nuevo parámetro: el look se arma completo (prenda + pareja + calzado + layer).
- **Pose por toma** → cada una de las 5 tomas usa una pose distinta de la librería (no repetir frontal).
- **Bottoms** → encuadre cintura-abajo + espalda obligatoria.

> Pendiente: aprobar este plan → actualizo `shoot.py` con styling+poses+luz Levi's → re-disparo 1 look de validación → si pasa, corremos el lote.
