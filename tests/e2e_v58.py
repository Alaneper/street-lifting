"""v58 : « Mon objectif » replié en une ligne (onglet Corps > Alimentation).
Usage : python3 tests/e2e_v58.py   (affiche « TOUT VERT » si tout passe)"""
import pathlib, sys
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2000)
    def goto_nutri(obj="suivi"):
        pg.evaluate("(o) => { D.profil.nut_objectif = o; corpsTab = 'nutri'; corpsManual = D.today; nutGoalOpen = false; setTab('corps'); render(); }", obj); pg.wait_for_timeout(800)
    goto_nutri("suivi")
    check("la carte objectif existe", pg.evaluate("!!document.querySelector('#nutgoal')"))
    check("repliée par défaut (suivi simple)", pg.evaluate("!document.querySelector('#nutgoal').open"))
    h = pg.evaluate("document.querySelector('#nutgoal').getBoundingClientRect().height")
    check("replié : moins de 90 px de haut (avant : environ un cinquième de l'écran)", h < 90, str(h))
    check("la ligne dit l'objectif", "Suivi simple" in pg.evaluate("document.querySelector('#nutgoal summary').innerText"))
    pg.click("#nutgoal summary"); pg.wait_for_timeout(300)
    check("un toucher déplie les réglages", pg.evaluate("document.querySelector('#nutgoal').open") and pg.is_visible("#nob"))
    pg.select_option("#nob", "maintien"); pg.wait_for_timeout(1200)
    check("après un changement de réglage, la carte reste ouverte", pg.evaluate("!!document.querySelector('#nutgoal') && document.querySelector('#nutgoal').open"))
    pg.click("#nutgoal summary"); pg.wait_for_timeout(300)
    check("on peut la replier", pg.evaluate("!document.querySelector('#nutgoal').open"))
    # infos manquantes : reste ouverte
    pg.evaluate("D.profil.taille_cm = ''; D.profil.naissance = '';"); goto_nutri("perte")
    miss = pg.evaluate("(() => { const t = nutTargets(nutDate); return !!(t.missing && t.missing.length); })()")
    if miss: check("objectif perte sans taille : ouverte d'office", pg.evaluate("document.querySelector('#nutgoal').open"))
    check("aucune erreur JS", not errs, str(errs[:3]))
    br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
