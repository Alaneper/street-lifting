#!/usr/bin/env python3
"""v71b — contours des muscles qui SUIVENT l'illustration.
Les polygones tracés à la main (muscle_regions.py) ne servent plus que de germes : un watershed sur les traits sombres / bords de l'écorché
fait ensuite glisser chaque limite sur la vraie séparation entre deux muscles. Sortie : muscle_regions_snapped.json {vue: {muscle: [polygone, …]}}."""
import json, sys
from pathlib import Path
import numpy as np, cv2
from scipy import ndimage as ndi
from skimage.segmentation import watershed
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import muscle_regions as MR
ERODE, DILATE = 7, 13          # germe = polygone rétréci de ERODE px ; au-delà de DILATE px du polygone = « reste du corps »
REACH = {"ischios": 26, "quadriceps": 22, "triceps": 20, "biceps": 20, "mollets": 18, "mollets_d": 18, "avant_bras": 18}   # muscles longs : on laisse plus de marge pour trouver la jonction avec le tendon

def elevation(rgb):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    s = cv2.GaussianBlur(g, (0, 0), 1.1)
    gx, gy = cv2.Sobel(s, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(s, cv2.CV_32F, 0, 1, ksize=3)
    grad = np.hypot(gx, gy)
    valley = np.clip(cv2.GaussianBlur(g, (0, 0), 5) - s, 0, None)      # traits sombres = vallées de luminance
    n = lambda a: a / (np.percentile(a, 99.5) + 1e-6)
    return np.clip(n(grad), 0, 1.5) * 0.6 + np.clip(n(valley), 0, 1.5) * 1.0

def run(view, debug=None):
    im = cv2.cvtColor(cv2.imread(str(HERE / f"{view}_clean.png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
    H, W = im.shape[:2]; body = im[..., 3] > 128
    keys = list(MR.R[view]); lab = {k: i + 1 for i, k in enumerate(keys)}; REST = len(keys) + 1
    masks = {}
    for k in keys:
        m = np.zeros((H, W), np.uint8)
        for p in MR.R[view][k]: cv2.fillPoly(m, [np.round(np.array(p)).astype(np.int32)], 255)
        masks[k] = m > 0
    reach = np.zeros((H, W), bool)
    for k, m in masks.items(): reach |= ndi.distance_transform_edt(~m) <= REACH.get(k, DILATE)
    far = ~reach
    markers = np.zeros((H, W), np.int32)
    markers[(~body) | (far & body)] = REST
    for k in keys:
        d = ndi.distance_transform_edt(masks[k]); r = min(ERODE, 0.45 * d.max())
        markers[(d > r) & (markers == 0)] = lab[k]
    ws = watershed(elevation(im[..., :3]), markers)
    out = {}
    for k in keys:
        m = ((ws == lab[k]) & body).astype(np.uint8) * 255
        # nettoyage : retire les filets qui débordent (ouverture large), comble les trous, arrondit les extrémités dentelées
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
        m = cv2.GaussianBlur(m, (0, 0), 3.2); m = (m > 127).astype(np.uint8) * 255
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        polys = []
        for c in cs:
            if cv2.contourArea(c) < 120: continue
            a = cv2.approxPolyDP(c, 1.3, True)[:, 0, :]
            if len(a) >= 4: polys.append([[int(x), int(y)] for x, y in a])
        out[k] = polys
    if debug:
        ov = im[..., :3].copy(); rng = np.random.RandomState(3); cols = {k: rng.randint(40, 255, 3) for k in keys}
        for k in keys:
            for p in out[k]: cv2.polylines(ov, [np.array(p, np.int32)], True, tuple(int(c) for c in cols[k]), 2)
        cv2.imwrite(debug, cv2.cvtColor(ov, cv2.COLOR_RGB2BGR))
    return out

if __name__ == "__main__":
    res = {v: run(v, debug=(sys.argv[1] + f"_{v}.png") if len(sys.argv) > 1 else None) for v in ("front", "back")}
    (HERE / "muscle_regions_snapped.json").write_text(json.dumps(res, separators=(",", ":")))
    print({v: {k: [len(p) for p in ps] for k, ps in r.items()} for v, r in res.items()})
