"""v67 étape H : Classement / Compétitions v3. Test ciblé."""
import pathlib, re
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
    pg.click("[data-tab=agenda]"); pg.wait_for_timeout(1200)
    T = lambda: ev("document.querySelector('#v-agenda').innerText").lower()
    check("carte Prochaine compétition", "prochaine compétition" in T() and ev("!!document.querySelector('#v-agenda .cc .cc-d')"))
    check("J−X dans la carte, sans débordement", ev("(() => { const r = document.querySelector('.cc-d').getBoundingClientRect(); return r.right <= innerWidth - 8 && /J.\\d+|Jour J/.test(document.querySelector('.cc-d').textContent); })()"))
    check("tuiles catégorie/poids/total", ev("document.querySelectorAll('#v-agenda .cctl .mt3').length") >= 2)
    check("étapes du jour J + checklist", "jour j, étape par étape" in T() and "checklist" in T())
    check("calendrier et formulaire conservés", ev("!!document.querySelector('#v-agenda .cal') && !!document.querySelector('#cpn')"))
    check("pas de undefined/NaN", not re.search(r"undefined|nan", T()))
    pg.click("[data-act=agSeg][data-k=amis]"); pg.wait_for_timeout(1200)
    check("onglet Amis s'affiche", ev("document.querySelector('#v-agenda').innerText.length") > 20)
    check("aucune erreur JS", not errs, errs[:3])
    br.close()
print("ÉCHECS:", fails) if fails else print("TOUT OK")
