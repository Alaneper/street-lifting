"""Retours vidéo, lot F : écran de lancement à chaque ouverture (barre déterminée (v77), 0,4 s minimum) et icônes valides. Test ciblé."""
import pathlib, time, json
from PIL import Image
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
ROOT = H.parent
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
# --- icônes : plein cadre, fond sombre aux quatre coins, logo clair au centre (l'ancienne 180 était un coin d'image zoomé, coins blancs)
for f, n in [("icon-180.png", 180), ("icon-192.png", 192), ("icon-512.png", 512), ("icon-maskable.png", 512)]:
    im = Image.open(ROOT / f).convert("RGB"); w, h = im.size
    corners = [im.getpixel(p) for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]]
    bright = sum(1 for x in range(int(w * .3), int(w * .7), 3) for y in range(int(h * .3), int(h * .7), 3) if sum(im.getpixel((x, y))) > 600)
    check(f"{f} : {n}×{n}, coins sombres (pas de blanc), logo clair au centre", im.size == (n, n) and all(sum(c) < 120 for c in corners) and bright > 40, (im.size, corners, bright))
man = json.loads((ROOT / "manifest.webmanifest").read_text())
check("manifest : icônes 192, 512 et maskable présentes", {i["src"] for i in man["icons"]} == {"icon-192.png", "icon-512.png", "icon-maskable.png"})
html = (ROOT / "test-build.html").read_text(encoding="utf-8")
check("apple-touch-icon pointe vers icon-180.png (versionné)", 'rel="apple-touch-icon"' in html and "icon-180.png?v=" in html)
check("service worker : icônes dans le cache de l'app", all(x in (ROOT / "sw.js").read_text() for x in ["icon-180.png", "icon-192.png", "icon-512.png"]))
# --- lancement
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    t0 = time.time(); pg.goto("http://app.local/sl/", wait_until="commit")
    pg.wait_for_selector("#splash", state="attached", timeout=5000)
    check("écran de lancement présent à l'ouverture", pg.evaluate("!!document.getElementById('splash') && /BE TOO STRONG/.test(document.getElementById('splash').innerText)"))
    check("barre de progression déterminée (v77, suit de vraies étapes)", pg.evaluate("!!document.querySelector('#splash [role=progressbar][aria-valuenow]')"))
    check("logo B² dans l'écran de lancement", pg.evaluate("!!document.querySelector('#splash svg')"))
    pg.wait_for_selector("#splash", state="detached", timeout=15000); dt = time.time() - t0
    check("écran de lancement visible au moins 0,4 s", dt >= .39, round(dt, 2))
    check("écran de lancement retiré ensuite (plus rien ne bloque)", pg.evaluate("!document.getElementById('splash')"))
    pg.wait_for_timeout(300)
    check("aucune erreur console", not errs, errs[:3])
    # deuxième ouverture : données gardées sur le téléphone → l'écran s'affiche de nouveau, 0,4 s minimum
    pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(1500)
    t1 = time.time(); pg.reload(wait_until="commit"); pg.wait_for_selector("#splash", state="attached", timeout=5000)
    check("réouverture : l'écran de lancement revient", True)
    pg.wait_for_selector("#splash", state="detached", timeout=15000); dt2 = time.time() - t1
    check("réouverture : visible au moins 0,4 s", dt2 >= .39, round(dt2, 2))
    check("réouverture : l'app s'affiche avec ses données", pg.evaluate("typeof D !== 'undefined' && !!D && !!document.querySelector('#v-home') && document.querySelector('#v-home').innerText.length > 20"))
    br.close()
print("ÉCHECS :", fails)
