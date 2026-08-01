#!/usr/bin/env python3
"""
KonpreShop — Generador de galería de producto (workflow anti-errores visuales).

Reglas que blindan la consistencia:
- COLOR LOCK: las tomas de producto (maniquí, closeup) se condicionan SIEMPRE con la
  foto real del producto -> el color/tela no se inventan.
- MODEL ANCHOR: se genera UN frente on-model y de ahí se derivan las demás tomas
  on-model (espalda) -> el MISMO modelo en todas, misma luz, misma sesión.
- TEMPLATE COMPARTIDO: mismo estudio/realismo/anti-error en cada prompt -> estética uniforme.
- ANTI-ERROR: cláusulas fijas contra manos deformes, texto/logos basura, piel plástica.
- SALIDA ORDENADA: lote/<slug>/01-frente 02-espalda 03-maniqui 04-closeup + manifest.json

Uso:
  python3 gallery.py --slug polo-esmeralda --product-image REF.webp \
      --gender h --garment "emerald-green polo, ribbed collar, two-button placket" \
      [--front EXISTING_FRONT.png] --key "$KEY"

QA: después de correr, Claude revisa cada salida vs checklist y re-genera las que fallen.
"""
import argparse, json, os, shutil, subprocess, sys

SKILL = os.path.expanduser("~/.claude/skills/banana/scripts/edit.py")
MODEL = "gemini-3.1-flash-image-preview"
OUTROOT = os.path.expanduser("~/claude-obsidian/KonpreShop/assets/lote")

# --- Bloques compartidos (NO cambiar entre tomas = consistencia) ---
STUDIO = ("Clean warm off-white seamless studio backdrop with DIRECTIONAL natural window light from "
          "one side, casting a DEFINED natural shadow on the backdrop wall and a grounding contact "
          "shadow beneath the subject, soft gradient light falloff for depth — real shadows, not flat "
          "high-key. Premium Gap-style ecommerce campaign look.")
REALISM = ("Shot on Kodak Portra 400, 50mm, fine film grain, real unretouched skin with "
           "visible pores and a natural healthy sheen, NOT plastic, NOT airbrushed, "
           "clean and well-groomed, NOT dirty.")
ANTIERR = ("CRITICAL ANATOMY: both arms and both hands must be FULLY VISIBLE, complete and "
           "anatomically correct with five fingers each — NO cropped, cut-off, missing, severed "
           "or deformed limbs, no extra limbs. Compose so the entire upper body and both full arms "
           "stay inside the frame with margin. Hands relaxed and natural. "
           "Do NOT render any text, logo, label, brand mark or watermark. "
           "True-to-life color matching the reference exactly.")

# Cuerpo: fuerte y atlético pero proporciones normales (NO fisicoculturista)
MODELS = {
 "h": ("an exceptionally good-looking young Sonoran man, mid-20s, a top international male fashion model "
       "(GQ cover / Vogue Hombre caliber) — flawless bone structure, chiseled symmetrical jawline, sharp "
       "cheekbones, straight nose, striking expressive dark eyes, thick well-groomed brows, perfectly "
       "styled light beard, modern textured haircut, magnetic head-turning charisma; lean athletic build "
       "with normal proportions (fit, NOT a bodybuilder); warm sun-kissed skin kept REAL with visible "
       "pores and natural texture — extremely handsome but never airbrushed or plastic"),
 "m": ("a strikingly beautiful young Sonoran woman, mid-20s, slim and naturally fit build with normal "
       "realistic proportions, warm sun-kissed skin with faint freckles, long dark wavy hair, defined "
       "cheekbones, effortless confident expression"),
}
# Encuadre seguro que NO corta brazos
FRAME = ("Three-quarter body framing from mid-thigh up, both full arms and hands clearly inside the "
         "frame with comfortable margin around the body, nothing cropped.")

def run_edit(image, prompt, key):
    out = subprocess.run([sys.executable, SKILL, "--api-key", key, "--model", MODEL,
                          "--image", image, "--prompt", prompt],
                         capture_output=True, text=True)
    # edit.py imprime JSON con "path"
    for line in out.stdout.splitlines():
        line = line.strip()
        if line.startswith('"path"') or '"path"' in line:
            try: return line.split('"path"')[1].split('"')[1]
            except Exception: pass
    # fallback: parsear bloque json completo
    try:
        js = json.loads(out.stdout[out.stdout.index("{"):out.stdout.rindex("}")+1])
        return js.get("path")
    except Exception:
        sys.stderr.write(out.stdout + "\n" + out.stderr + "\n"); return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--product-image", required=True)
    ap.add_argument("--gender", required=True, choices=["h","m"])
    ap.add_argument("--garment", required=True, help="short factual garment description")
    ap.add_argument("--front", default=None, help="optional existing front on-model to reuse")
    ap.add_argument("--key", required=True)
    a = ap.parse_args()

    d = os.path.join(OUTROOT, a.slug); os.makedirs(d, exist_ok=True)
    model = MODELS[a.gender]; manifest = {}

    # 01 FRENTE on-model (ancla del modelo)
    front_dst = os.path.join(d, "01-frente-onmodel.png")
    if a.front and os.path.exists(a.front):
        if os.path.abspath(a.front) != os.path.abspath(front_dst):
            shutil.copy(a.front, front_dst)
    else:
        p = (f"Take the exact {a.garment} shown in this product image and show it worn by {model}. "
             f"Keep the garment EXACTLY the same color, cut and details — the garment is the hero, "
             f"clearly displayed, worn naturally, looking slightly off-camera. {FRAME} "
             f"{STUDIO} {REALISM} {ANTIERR}")
        r = run_edit(a.product_image, p, a.key)
        if r: shutil.copy(r, front_dst)
    manifest["01-frente"] = os.path.basename(front_dst)

    # 02 ESPALDA (mismo modelo, derivado del frente)
    p = (f"Show this EXACT same person — same face, same hair, same skin, same body — now viewed "
         f"from BEHIND, wearing the same {a.garment} seen from the back. Identical studio and lighting. "
         f"{FRAME} {STUDIO} {REALISM} {ANTIERR}")
    r = run_edit(front_dst, p, a.key)
    if r: shutil.copy(r, os.path.join(d, "02-espalda-onmodel.png")); manifest["02-espalda"]="02-espalda-onmodel.png"

    # 03 MANIQUI invisible (color lock desde producto real)
    p = (f"Ghost-mannequin product shot of this EXACT {a.garment} on an invisible form holding a "
         f"natural 3D shape, identical color and fabric. {STUDIO} subtle contact shadow. {REALISM} {ANTIERR}")
    r = run_edit(a.product_image, p, a.key)
    if r: shutil.copy(r, os.path.join(d, "03-maniqui.png")); manifest["03-maniqui"]="03-maniqui.png"

    # 04 CLOSEUP detalle (color lock desde producto real)
    p = (f"Macro closeup detail of this EXACT {a.garment}: focus on the fabric texture and a key "
         f"construction detail (collar/pocket/stitching), identical color, shallow depth of field, "
         f"soft side light, clean warm off-white background, 100mm macro. {REALISM} {ANTIERR}")
    r = run_edit(a.product_image, p, a.key)
    if r: shutil.copy(r, os.path.join(d, "04-closeup.png")); manifest["04-closeup"]="04-closeup.png"

    json.dump(manifest, open(os.path.join(d,"manifest.json"),"w"), indent=2, ensure_ascii=False)
    print(json.dumps({"slug": a.slug, "dir": d, "shots": manifest}, ensure_ascii=False))

if __name__ == "__main__":
    main()
