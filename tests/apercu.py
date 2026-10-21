"""Aperçu de la version en cours avec barre d'état d'iPhone simulée (47 px en haut, 34 px en bas).
Usage : python3 tests/apercu.py <dossier de sortie>"""
import pathlib, sys, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "mockups.py").read_text()
exec(src[:src.index("CSS = {")])   # route2, statusbar, board
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route2)
    pg = c.new_page()
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(2500)
    def shot(name):
        f = OUT / f"{name}.png"; pg.screenshot(path=str(f)); statusbar(f); return f
    files = []
    pg.evaluate("D.poids = D.poids.filter(p => p.date !== D.today); setTab('home')"); pg.wait_for_timeout(500); files.append(shot("v21-aujourdhui"))
    pg.evaluate("scrollTo(0, 260)"); pg.wait_for_timeout(500); files.append(shot("v21-defilement"))
    pg.evaluate("setTab('seance')"); pg.wait_for_timeout(800); files.append(shot("v21-prog"))
    key = pg.evaluate("(nextSeance()||S.at(-1)).key"); pg.evaluate(f"startLive({json.dumps(key)}, 1)"); pg.wait_for_timeout(600); pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(500)
    files.append(shot("v21-seance"))
    board(files, ["Aujourd'hui : carte pesée (3A)", "Au défilement : en-tête fixe (1B)", "Prog : héros sombre (2B)", "Séance en direct (2B)"], OUT / "v21-apercu.png", "Version 21 : tes choix appliqués")
    br.close()
print("ok")
