"""Mesure des couches de surface (lot E) : pour chaque écran, couleur rendue de chaque couche (échantillon sur la capture) et luminosité CIE L*.
Usage : python3 tests/mesure_surfaces.py sortie.json  (même prérequis que capture_ecrans.py)"""
import sys, json, pathlib, io
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
from PIL import Image
OUT_JSON = sys.argv[1]
def lin(c):
    c /= 255; return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
def lstar(rgb):
    Y = .2126 * lin(rgb[0]) + .7152 * lin(rgb[1]) + .0722 * lin(rgb[2]); return 116 * Y ** (1 / 3) - 16 if Y > .008856 else 903.3 * Y
# (écran, js, [(couche, sélecteur, ancre)]) ; ancre : bl = bord gauche à 85 % de la hauteur, ml = bord gauche au milieu (à 8 px du bord, hors texte et hors coins arrondis)
ECR = [
 ("Séance", "setTab('home')", [("0 · fond d'écran", "body", "gutter"), ("1 · liste « Au programme »", "#v-home div:has(>.tdr)", "ml"), ("2 · carte séance du jour", "#v-home .tdc", "bl"), ("3 · onglet actif (contrôle)", "#v-home .segc [aria-pressed=true], #subseance [aria-pressed=true]", "ml"), ("barre d'onglets (opaque)", ".tabs", "in")]),
 ("Corps", "corpsTab='poids';corpsManual=D.today;setTab('corps')", [("0 · fond d'écran", "body", "gutter"), ("1 · carte (poids / liste)", "#v-corps div:has(>.vrow)", "ml"), ("2 · carte surélevée (catégorie)", "#v-corps .hero, #v-corps .catcard", "bl"), ("3 · contrôle actif", "#v-corps .segc [aria-pressed=true]", "ml")]),
 ("Progrès", "progSeg='records';setTab('prog')", [("0 · fond d'écran", "body", "gutter"), ("1 · tuile « Total visé »", "#v-prog .tiles2>*", "ml"), ("1 · liste des mouvements", "#v-prog .lcard", "ml"), ("2 · carte « Mon total »", "#v-prog .hero", "bl"), ("3 · onglet actif (contrôle)", "#v-prog .segc [aria-pressed=true]", "ml")]),
 ("Compétition", "agendaSeg='compet';setTab('agenda')", [("0 · fond d'écran", "body", "gutter"), ("1 · tuile catégorie / poids", "#v-agenda .cctl .mt3", "ml"), ("1 · bloc replié", "#v-agenda .fold", "ml"), ("2 · carte « J–N »", "#v-agenda .cc", "bl"), ("3 · onglet actif (contrôle)", "#v-agenda .segc [aria-pressed=true]", "ml")]),
 ("Feuille (toutes les pesées)", "setTab('corps');openSheet('pesees')", [("0 · fond d'écran (derrière le voile)", "body", "top"), ("3 · feuille", ".sheet", "in"), ("2 · carte dans la feuille", ".sheet .pmonth, .sheet .panel", "ml")]),
]
res = {}
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4500)
    for nom, js, cl in ECR:
        pg.evaluate("page=null;sheet=null;renderLayer()"); pg.evaluate(js); pg.wait_for_timeout(1500); pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(300)
        im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB"); rows = []
        for lab, sel, anc in cl:
            r = pg.evaluate("""([sel]) => { const e = document.querySelector(sel); if (!e) return null; const b = e.getBoundingClientRect(); return {x:b.x, y:b.y, w:b.width, h:b.height}; }""", [sel])
            if anc == "gutter": x, y = 3, 700
            elif anc == "top": x, y = 3, 60
            elif anc == "in" and r: x, y = r["x"] + 8, r["y"] + (8 if r["h"] < 120 else 40)
            elif not r: rows.append({"couche": lab, "absent": True}); continue
            else:
                x = r["x"] + 8; y = r["y"] + r["h"] * (.85 if anc == "bl" else .5)
                if r["y"] + 24 > 720: rows.append({"couche": lab, "absent": True}); continue   # hors écran (ou sous l'ombre de la barre d'onglets)
                y = max(r["y"] + 24, min(y, 720)); x = max(2, min(x, 386))
            rgb = im.getpixel((int(x * 2), int(y * 2))); rows.append({"couche": lab, "hex": "#%02X%02X%02X" % rgb, "L": round(lstar(rgb), 2)})
        res[nom] = rows; print(nom, [(r["couche"], r.get("hex")) for r in rows])
    br.close()
json.dump(res, open(OUT_JSON, "w"), ensure_ascii=False, indent=1)
