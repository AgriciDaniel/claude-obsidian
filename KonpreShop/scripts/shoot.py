#!/usr/bin/env python3
"""
KonpreShop — Photoshoot styleado (estilo Levi's MX natural pro).
Modelo fijo del casting + producto real -> galería de looks COMPLETOS con pose por toma.

TOPS:    01 hero · 02 ¾ · 03 movimiento · 04 espalda · 05 detalle
BOTTOMS: 01 frente-fit · 02 ¾ · 03 espalda · 04 detalle  (encuadre cintura-abajo)

Uso:
  python3 shoot.py --slug camisa-emiliano --model-image casting/M2.png \
     --product-image ref.webp --gender h --kind top \
     --garment "light-blue Levi's button shirt" \
     --styling "worn open over a plain white tee, with blue Levi's jeans and brown boots" \
     --key "$KEY" [--only-front]
"""
import argparse, base64, json, shutil, sys, urllib.request
from datetime import datetime
from pathlib import Path

MODEL_ID="gemini-3.1-flash-image-preview"
API="https://generativelanguage.googleapis.com/v1beta/models"
OUT=Path.home()/"Documents"/"nanobanana_generated"
LOTE=Path.home()/"claude-obsidian"/"KonpreShop"/"assets"/"lote"

# Fondo/luz estilo Levi's MX: neutro claro cálido, natural balanceada (ni bright ni oscuro)
BG=("Soft warm neutral light-gray seamless studio backdrop (Levi's ecommerce style), natural balanced "
    "window light with a subtle directional shadow on the floor and wall — clean, natural and filmic; "
    "NOT bright high-key, NOT washed out, NOT dark moody.")
REALISM=("Shot on Kodak Portra 400, 50mm, fine film grain, real unretouched skin with visible pores and "
         "natural texture, NOT plastic, NOT airbrushed.")
ANTIERR=("Both arms and hands fully visible, complete, five fingers each, NO cropped/missing/deformed limbs. "
         "No text, logo or watermark invented. True-to-life garment color matching the product reference.")
COHESION=("ONE cohesive real person: head and neck naturally connected to the body, same skin tone and "
          "consistent lighting across face and body, natural realistic proportions, relaxed natural posture "
          "— NOT a stiff frontal pose, NOT a cut-out head on a different body.")
STYLING={"h":"Modern well-styled hair, clean grooming, handsome.",
         "m":("Professionally styled hair (soft waves or sleek blowout) and natural glam makeup — glowing "
              "skin, defined brows, subtle mascara, rosy-nude lip — pretty and polished.")}
FRAME={"top":"Vertical 3:4, full upper body down to mid-thigh, both arms and hands visible, nothing cropped.",
       "bottom":"Vertical 3:4, framed from the chest/waist down to the shoes, featuring the trousers fit and length."}
POSE={
 "p1":"standing relaxed with weight on one leg, one hand resting in a pocket, calm confident gaze to camera",
 "p2":"torso turned three-quarters to the side, one hand adjusting a sleeve or cuff, looking slightly off-camera",
 "p3":"captured mid-stride walking toward the camera, natural candid movement, looking away to the side",
 "p4":"viewed from behind with a relaxed over-the-shoulder glance, showing the back of the full outfit",
 "p1b":"standing relaxed, slight three-quarter stance, hands easy, showing the trousers fit head-on",
}

def b64(p):
    p=Path(p); mt={".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp"}.get(p.suffix.lower(),"image/png")
    return mt, base64.b64encode(open(p,"rb").read()).decode()
def txt(t): return {"text":t}
def img(p): mt,d=b64(p); return {"inlineData":{"mimeType":mt,"data":d}}

def call(parts,key):
    body={"contents":[{"parts":parts}],"generationConfig":{"responseModalities":["TEXT","IMAGE"],
          "imageConfig":{"aspectRatio":"3:4","imageSize":"2K"}}}
    req=urllib.request.Request(f"{API}/{MODEL_ID}:generateContent?key={key}",
        data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
    for attempt in range(3):
        try: r=json.loads(urllib.request.urlopen(req,timeout=180).read().decode()); break
        except Exception as e:
            if attempt==2: return None,f"err:{e}"
    c=r.get("candidates",[])
    if not c: return None,"no candidates"
    for part in c[0].get("content",{}).get("parts",[]):
        if "inlineData" in part:
            OUT.mkdir(parents=True,exist_ok=True)
            fp=OUT/f"shoot_{datetime.now():%Y%m%d_%H%M%S_%f}.png"
            open(fp,"wb").write(base64.b64decode(part["inlineData"]["data"])); return str(fp),"ok"
    return None,f"no image ({c[0].get('finishReason')})"

def main():
    ap=argparse.ArgumentParser()
    for x in ["slug","model-image","product-image","garment","key"]: ap.add_argument(f"--{x}",required=True)
    ap.add_argument("--gender",choices=["h","m"],required=True)
    ap.add_argument("--kind",choices=["top","bottom"],default="top")
    ap.add_argument("--styling",default="styled as a complete natural outfit with complementary jeans and clean shoes")
    ap.add_argument("--only-front",action="store_true")
    a=ap.parse_args()
    d=LOTE/a.slug; d.mkdir(parents=True,exist_ok=True)
    who="this exact man" if a.gender=="h" else "this exact woman"
    fr=FRAME[a.kind]; man={}

    p1=POSE["p1"] if a.kind=="top" else POSE["p1b"]
    p=(f"IMAGE 1 shows a model — keep {who}'s EXACT face and identity. IMAGE 2 shows the HERO product: a "
       f"{a.garment}. Dress {who} in a complete styled outfit: the EXACT product from image 2 (keep its "
       f"exact color, cut and details), {a.styling}. The hero garment is clearly featured. POSE: {p1}. "
       f"{COHESION} {STYLING[a.gender]} {fr} {BG} {REALISM} {ANTIERR}")
    fp,st=call([txt(p),img(a.model_image),img(a.product_image)],a.key)
    if fp: shutil.copy(fp,d/"01-hero.png"); man["01"]=st
    else: print(json.dumps({"slug":a.slug,"fail":"01","st":st})); sys.exit(1)
    if a.only_front:
        json.dump(man,open(d/"manifest.json","w"),indent=2,ensure_ascii=False); print(json.dumps({"slug":a.slug,"shots":man})); return

    # tomas derivadas del hero (misma persona, mismo outfit, nueva pose)
    seq = ([("02-trescuartos",POSE["p2"]),("03-movimiento",POSE["p3"]),("04-espalda",POSE["p4"])]
           if a.kind=="top" else [("02-trescuartos",POSE["p2"]),("03-espalda",POSE["p4"])])
    for name,pose in seq:
        p=(f"Same person from this image — same face, hair, skin, body and the SAME complete outfit — "
           f"repositioned. POSE: {pose}. Identical backdrop and lighting. {fr} {BG} {REALISM} {ANTIERR}")
        fp,st=call([txt(p),img(d/"01-hero.png")],a.key)
        if fp: shutil.copy(fp,d/f"{name}.png"); man[name]=st

    # detalle del producto (closeup, color lock desde la foto real)
    p=(f"Macro closeup detail of this EXACT {a.garment}: fabric texture and a key construction detail "
       f"(collar/pocket/stitching/hardware), identical color, shallow depth of field, soft natural light, "
       f"warm neutral light-gray background. {REALISM} {ANTIERR}")
    fp,st=call([txt(p),img(a.product_image)],a.key)
    if fp: shutil.copy(fp,d/"05-detalle.png"); man["05"]=st

    json.dump(man,open(d/"manifest.json","w"),indent=2,ensure_ascii=False)
    print(json.dumps({"slug":a.slug,"dir":str(d),"shots":man},ensure_ascii=False))

if __name__=="__main__": main()
