#!/usr/bin/env python3
"""Génère src/muscle_front.webp, src/muscle_back.webp et src/muscles_art.js à partir de tools/art/ (v71).
Les deux illustrations de base (écorché crème, face et dos) viennent de Canva (génération d'image, session du 04/11/2026) ;
les zones de chaque muscle sont tracées à la main (tools/art/muscle_regions.py, coordonnées en pixels de source_front.jpg / source_back.jpg)."""
import json, sys
import numpy as np, cv2
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent; sys.path.insert(0, str(HERE / "art"))
import muscle_regions as MR
SNAP = HERE / "art" / "muscle_regions_snapped.json"   # contours calés sur l'illustration (tools/art/segment.py) ; à défaut, polygones tracés à la main
REG = json.loads(SNAP.read_text()) if SNAP.exists() else MR.R
OUT_W = 640
def unsharp(L, s, k): return L + k * (L - cv2.GaussianBlur(L, (0, 0), s))
def tone(im, kind="red", k1=1.6, k2=1.2, lo=0.30, hi=0.95, gamma=1.3):
    """Recolore l'illustration d'écorché en gardant son relief : la luminance est accentuée (fibres à petite échelle, volumes à grande échelle)
    puis passée dans un dégradé rouge (muscle principal) ou rose (secondaire). Le crème d'origine reste pour les muscles non travaillés."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32) / 255
    L = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    L = unsharp(unsharp(L, 2.0, k1), 7.0, k2)
    t = np.clip((L - lo) / (hi - lo), 0, 1) ** gamma
    if kind == "red":
        stops = [0, .22, .5, .78, 1]; cols = np.array([(64, 6, 9), (118, 12, 14), (186, 30, 22), (222, 62, 40), (240, 128, 100)], np.float32)
    else:
        stops = [0, .25, .55, .8, 1]; cols = np.array([(128, 46, 44), (190, 84, 78), (226, 128, 114), (240, 168, 152), (246, 204, 192)], np.float32)
    out = np.stack([np.interp(t, stops, cols[:, i]) for i in range(3)], -1) / 255
    return Image.fromarray((np.dstack([out, a[..., 3]]) * 255).astype(np.uint8), "RGBA")
def smooth(poly, t=0.2):
    n = len(poly); d = f"M{poly[0][0]:.1f} {poly[0][1]:.1f}"
    for i in range(n):
        p0, p1, p2, p3 = poly[(i - 1) % n], poly[i], poly[(i + 1) % n], poly[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) * t, p1[1] + (p2[1] - p0[1]) * t); c2 = (p2[0] - (p3[0] - p1[0]) * t, p2[1] - (p3[1] - p1[1]) * t)
        d += f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + "Z"
art = {}
for v in ("front", "back"):
    im = Image.open(HERE / "art" / f"{v}_clean.png").convert("RGBA"); W, H = im.size
    small = im.resize((OUT_W, round(H * OUT_W / W)), Image.LANCZOS)
    small.save(ROOT / "src" / f"muscle_{v}.webp", "WEBP", quality=82, method=6)
    tone(small, "red").save(ROOT / "src" / f"muscle_{v}_r.webp", "WEBP", quality=74, method=6)
    tone(small, "pink").save(ROOT / "src" / f"muscle_{v}_p.webp", "WEBP", quality=74, method=6)
    reg, box = {}, {}
    for k, polys in REG[v].items():
        reg[k] = "".join(smooth(p) for p in polys)
        xs = [x for p in polys for x, _ in p]; ys = [y for p in polys for _, y in p]
        box[k] = [round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))]
    art[v] = {"w": W, "h": H, "vb": [16, 16, W - 32, H - 32], "reg": reg, "box": box}
(ROOT / "src" / "muscles_art.js").write_text("/* GÉNÉRÉ par tools/gen_muscle_art.py : ne pas modifier à la main. Zones musculaires tracées sur l'illustration d'écorché (voir tools/art). */\nconst MUSCLE_ART = " + json.dumps(art, separators=(",", ":")) + ";\nconst MUSCLE_IMG = {front:\"__IMG_FRONT__\", back:\"__IMG_BACK__\", frontR:\"__IMG_FRONT_R__\", backR:\"__IMG_BACK_R__\", frontP:\"__IMG_FRONT_P__\", backP:\"__IMG_BACK_P__\"};\n")
print({v: len(art[v]["reg"]) for v in art}, [(ROOT / "src" / f"muscle_{v}.webp").stat().st_size for v in art] + [(ROOT / "src" / f"muscle_{v}_{c}.webp").stat().st_size for c in "rp" for v in art])
