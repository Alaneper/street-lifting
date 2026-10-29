"""v55 : pas de doublon à la création d'un aliment (même nom + même marque). Usage : python3 tests/e2e_v55.py"""
import pathlib, json, sys, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route)
    pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4500)
    pg.evaluate("CAT_URL = ''; setTab('corps')"); pg.wait_for_timeout(500); pg.evaluate("ACT.nutTab({t:'foods'})"); pg.wait_for_timeout(300)
    def create(nom, marque="", k="150"):
        pg.evaluate("(q) => { nutQ = q; nutRefresh(); }", nom); pg.wait_for_timeout(150)
        if not pg.evaluate("!!document.getElementById('ncn')"): pg.evaluate("ACT.nutCreate()"); pg.wait_for_timeout(200)
        pg.evaluate("([n, m, k]) => { document.getElementById('ncn').value = n; document.getElementById('ncm').value = m; document.getElementById('nck').value = k; document.getElementById('ncp').value = '20'; document.getElementById('ncg').value = '0'; document.getElementById('ncl').value = '8'; ACT.nutCreateSave(); }", [nom, marque, k]); pg.wait_for_timeout(1500)
    n0 = pg.evaluate("D.aliments.length")
    create("Bœuf du boucher test", "Boucherie")
    check("premier produit créé", pg.evaluate("D.aliments.length") == n0 + 1, pg.evaluate("D.aliments.length"))
    pg.evaluate("nutPick = null; nutCreate = false; nutRefresh()")
    create("boeuf du boucher TEST", "boucherie", "999")
    r = pg.evaluate("({n:D.aliments.length, txt:(document.getElementById('ncdup') || {}).innerText || ''})")
    check("même nom + marque (accents et majuscules ignorés) : rien créé, avertissement affiché", r["n"] == n0 + 1 and "Tu as déjà" in r["txt"], r)
    pg.evaluate("ACT.nutDupUse()"); pg.wait_for_timeout(300)
    r = pg.evaluate("({n:D.aliments.length, pick:nutPick && nutPick.f.nom, k:nutPick && nutPick.f.k, form:!!document.getElementById('ncn')})")
    check("« Utiliser celui-ci » : produit existant sélectionné (150 kcal), pas de doublon", r["n"] == n0 + 1 and r["pick"] == "Bœuf du boucher test" and r["k"] == 150 and not r["form"], r)
    pg.evaluate("nutPick = null"); create("boeuf du boucher test", "boucherie", "170")
    pg.evaluate("ACT.nutDupForce()"); pg.wait_for_timeout(1500)
    check("« Créer quand même » : second produit créé", pg.evaluate("D.aliments.length") == n0 + 2, pg.evaluate("D.aliments.length"))
    pg.evaluate("nutPick = null; nutCreate = false; nutRefresh()")
    create("Bœuf du boucher test", "Autre boucherie")
    check("même nom, autre marque : créé sans avertissement", pg.evaluate("D.aliments.length") == n0 + 3, pg.evaluate("D.aliments.length"))
    check("aucune erreur de page", not errs, errs[:2])
    br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
