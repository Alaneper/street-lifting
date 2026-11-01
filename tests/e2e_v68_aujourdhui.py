"""v67 étape C : carte du jour (Séance › Aujourd'hui). Test ciblé."""
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
    check("carte du jour présente", ev("!!document.querySelector('#v-home .tdc')"))
    check("titre de séance non vide", ev("document.querySelector('#v-home .tdc-ttl').textContent.trim().length") > 0)
    check("carte musculaire dans la carte du jour", ev("document.querySelectorAll('#v-home .tdc .mplate.tdc-plate svg').length") == 2)
    check("un seul bouton « commencer » (pas de doublon)", ev("document.querySelectorAll('#v-home [data-act=startLive]').length") == 1)
    check("liste « Au programme » avec vignettes", ev("document.querySelectorAll('#v-home .tdr').length") >= 1)
    check("pas de texte « undefined/NaN »", ev("!/undefined|NaN/.test(document.querySelector('#v-home').innerText)"))
    pg.evaluate("scrollTo(0,0)"); pg.screenshot(path="/tmp/home-v68.png")
    pg.click("#v-home [data-act=startLive]"); pg.wait_for_timeout(1500)
    check("« Commencer » ouvre bien la séance en direct", ev("!!live"))
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
