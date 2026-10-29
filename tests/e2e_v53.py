"""v53 : catalogue d'aliments (service Apps Script simulé) — scan d'un code absent d'Open Food Facts, recherche par nom, service en panne. Usage : python3 tests/e2e_v53.py"""
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
    pg.evaluate("setTab('corps')"); pg.wait_for_timeout(500); pg.evaluate("ACT.nutTab({t:'foods'})"); pg.wait_for_timeout(300)
    def ean(b):
        s = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(b)); return b + str((10 - s % 10) % 10)
    ONLYCAT = ean("500000000777")
    pg.evaluate("""(code) => { const of = window.fetch; window.__cat = {hits:[], down:false};
      window.fetch = async (u, o) => { u = String(u);
        if (u.includes('cat.local')) { window.__cat.hits.push(u); if (window.__cat.down) throw new TypeError('Failed to fetch');
          const q = new URL(u).searchParams, J = b => new Response(JSON.stringify(b));
          if (q.get('a') === 'code') return J({ok:true, p: q.get('c') === code ? {code, nom:'Barre test catalogue', marque:'Marque C', k:380, p:30, g:35, l:12, por:45} : null});
          if (q.get('a') === 'q') return J({ok:true, r:[{code:'111', nom:'Skyr test', marque:'Ferme', k:57, p:9.5, g:3.6, l:0.5}, {code:'222', nom:'Incohérent test', marque:'X', k:900, p:1, g:1, l:1}, {code:'333', nom:'Vide', marque:'', k:null, p:null, g:null, l:null}]}); }
        if (/openfoodfacts\\.org\\/api/.test(u)) return new Response(JSON.stringify({status:0}), {status:404});
        if (/search\\.openfoodfacts\\.org|cgi\\/search/.test(u)) return new Response(JSON.stringify({hits:[{code:'111', product_name:'Skyr test', brands:'Ferme', nutriments:{'energy-kcal_100g':57, proteins_100g:9.5, carbohydrates_100g:3.6, fat_100g:0.5}}, {code:'444', product_name:'Skyr OFF seul', brands:'Y', nutriments:{'energy-kcal_100g':60, proteins_100g:10, carbohydrates_100g:4, fat_100g:0.2}}]}));
        return of(u, o); }; }""", ONLYCAT)
    check("désactivé par défaut (CAT_URL vide)", pg.evaluate("CAT_URL") == "", "")
    pg.evaluate("ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(500)
    pg.evaluate("(c) => { ACT.scanManual(); document.getElementById('scman').value = c; ACT.scanGo(); }", ONLYCAT); pg.wait_for_timeout(1200)
    check("sans catalogue : code absent d'OFF => « Produit introuvable »", "Produit introuvable" in pg.evaluate("document.getElementById('scanpanel') ? document.getElementById('scanpanel').innerText : ''"), "")
    check("sans catalogue : aucun appel au service", pg.evaluate("window.__cat.hits.length") == 0, "")
    pg.evaluate("ACT.scanClose()"); pg.wait_for_timeout(300)
    pg.evaluate("CAT_URL = 'http://cat.local/exec'")
    pg.evaluate("ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(500)
    pg.evaluate("(c) => { ACT.scanManual(); document.getElementById('scman').value = c; ACT.scanGo(); }", ONLYCAT); pg.wait_for_timeout(1500)
    r = pg.evaluate("({sheet, nom:nutPick && nutPick.f.nom, k:nutPick && nutPick.f.k, por:nutPick && nutPick.f.por, via:nutPick && nutPick.f.via})")
    check("avec catalogue : code absent d'OFF trouvé dans le catalogue", r["sheet"] is None and r["nom"] == "Barre test catalogue" and r["k"] == 380 and r["por"] == 45 and r["via"] == "cat", r)
    pg.evaluate("nutPick = null; nutQ = 'skyr'; nutRefresh()"); pg.wait_for_timeout(200)
    pg.evaluate("ACT.nutOff({})"); pg.wait_for_timeout(1500)
    r = pg.evaluate("offRes && offRes.map(f => f.nom + (f.check ? '!' : ''))")
    check("recherche par nom : catalogue d'abord, OFF sans doublon, incohérent en dernier, vide écarté", r == ["Skyr test", "Skyr OFF seul", "Incohérent test!"], r)
    pg.evaluate("window.__cat.down = true; offRes = null; ACT.nutOff({})"); pg.wait_for_timeout(1500)
    r = pg.evaluate("offRes && offRes.map(f => f.nom)")
    check("service en panne : la recherche continue avec Open Food Facts", r == ["Skyr test", "Skyr OFF seul"], r)
    pg.evaluate("ACT.scanClose && ACT.scanClose()")
    pg.evaluate("ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(400)
    pg.evaluate("(c) => { ACT.scanManual(); document.getElementById('scman').value = c; ACT.scanGo(); }", ONLYCAT); pg.wait_for_timeout(1500)
    check("service en panne : code inconnu => « Produit introuvable » (pas de blocage)", "Produit introuvable" in pg.evaluate("document.getElementById('scanpanel') ? document.getElementById('scanpanel').innerText : ''"), "")
    check("aucune erreur de page", not errs, errs[:2])
    br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
