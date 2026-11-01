"""v67 étape F : Progrès v3 (Records | Courbes). Test ciblé."""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(2500)
    ev = lambda js: pg.evaluate(js)
    pg.click("[data-tab=prog]"); pg.wait_for_timeout(1500)
    check("2 sous-onglets Records / Courbes", ev("[...document.querySelectorAll('#v-prog .segc button')].map(b => b.textContent).join('|')") == "Records|Courbes")
    check("Records : héros du total", ev("!!document.querySelector('#v-prog .hero')"))
    check("Records : cartes de mouvement avec vignette musculaire", ev("document.querySelectorAll('#v-prog .liftrow .mplate.thumb svg').length") >= 3)
    bc = ev("getComputedStyle(document.querySelector('#v-prog .liftrow .bar i')).backgroundColor")
    check("Records : barres d'objectif en bleu acier (donnée)", bc == "rgb(111, 160, 218)", bc)
    pg.screenshot(path="/tmp/prog-records.png")
    pg.click("[data-act=progSeg][data-k=courbes]"); pg.wait_for_timeout(2500)
    check("Courbes : sous-onglet actif", ev("document.querySelector('[data-act=progSeg][data-k=courbes]').getAttribute('aria-pressed')") == "true")
    check("Courbes : courbe du total (ou message si 1 seul record)", ev("!!document.querySelector('#c-total') || /courbe apparaît/.test(document.querySelector('#v-prog').innerText)"))
    check("Courbes : tuiles par mouvement", ev("document.querySelectorAll('#v-prog .fts .ft').length") >= 1)
    check("Courbes : volume par semaine", ev("/Volume par semaine/.test(document.querySelector('#v-prog').innerText)"))
    check("pas de « undefined / NaN »", ev("!/undefined|NaN/.test(document.querySelector('#v-prog').innerText)"))
    pg.screenshot(path="/tmp/prog-courbes.png")
    pg.click("[data-act=progSeg][data-k=records]"); pg.wait_for_timeout(500)
    check("retour sur Records", ev("!!document.querySelector('#v-prog .liftrow')"))
    pg.click("#v-prog .liftrow"); pg.wait_for_timeout(800)
    check("une carte de mouvement ouvre sa fiche", ev("!!document.querySelector('#layer .page, #layer [data-act=closePage], #layer h1, #layer .hero')"))
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
