"""v60 : RPE de 3 à 10 (3, 4, 5, 6, 6,5 … 10).
Usage : python3 tests/e2e_v60.py   (affiche « TOUT VERT » si tout passe)"""
import pathlib, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390,"height":844}, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2000)
    check("échelle : 3, 4, 5, 6, 6,5, 7, 7,5, 8, 8,5, 9, 9,5, 10", pg.evaluate("RPE_OPTS.join('|')") == "3|4|5|6|6.5|7|7.5|8|8.5|9|9.5|10")
    # 1RM estimé : RPE 3 jamais plus optimiste qu'un RPE 5 ; plus jamais compté comme « à fond »
    v = pg.evaluate("[e1rmOf('SQUAT', {c:100, r:5, rpe:3}).v, e1rmOf('SQUAT', {c:100, r:5, rpe:5}).v, e1rmOf('SQUAT', {c:100, r:5}).v]")
    check("1RM estimé : RPE 3 compté comme RPE 5 (prudent)", abs(v[0] - v[1]) < 1e-9 and v[0] > v[2], str(v))
    # en séance : un mouvement de force avec RPE proposé ; les 12 boutons sont là, le 3 se choisit
    ok = pg.evaluate("""(() => { for (const s of S) { const i = s.exercices.findIndex(e => liftOf(e.mouvement) && !BW_LIFTS.includes(liftOf(e.mouvement))); if (i >= 0 && s.cols.rpe1) { window.__ts = [s.key, i]; return true; } } return false; })()""")
    check("séance avec colonne RPE trouvée", ok)
    if ok:
        pg.evaluate("startLive(__ts[0], __ts[1])"); pg.wait_for_timeout(900)
        pg.locator(".setrow").first.locator(".ck").click(); pg.wait_for_timeout(500)
        pg.evaluate("sheet === 'rest' && ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(300)
        n = pg.evaluate("document.querySelectorAll('.rpe')[0] ? document.querySelectorAll('.rpe')[0].querySelectorAll('button').length : 0")
        check("12 boutons RPE en séance", n == 12, str(n))
        first = pg.evaluate("document.querySelector('.rpe button') && document.querySelector('.rpe button').innerText")
        check("le premier bouton est 3", first == "3", str(first))
        pg.locator(".rpe").first.locator("button").first.click(); pg.wait_for_timeout(400)
        check("RPE 3 enregistré", pg.evaluate("live.rows[live.i].rpe1") == 3, str(pg.evaluate("live.rows[live.i].rpe1")))
        x = pg.evaluate("document.querySelector('.rpe').scrollWidth > document.querySelector('.rpe').clientWidth")
        print("   (info) rangée RPE défilante sur 390 px :", x)
    # fiche d'explication
    pg.evaluate("ACT.rpeInfo()"); pg.wait_for_timeout(400)
    t = pg.evaluate("document.querySelector('.sheet') ? document.querySelector('.sheet').innerText : document.body.innerText")
    check("explication : ligne « 3–4 Effort léger »", "3–4" in t and "Effort léger" in t)
    check("aucune erreur JS", not errs, str(errs[:3]))
    br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
