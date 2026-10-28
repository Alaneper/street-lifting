"""Recherche d'aliments (v52) : requêtes courantes → premier résultat attendu (tous les noms existent dans la table Ciqual 2025)."""
import pathlib, json, sys, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
EXPECT = {"patate douce":"Patate douce", "patates douces":"Patate douce", "patate":"Pomme de terre", "thon en boîte":"Thon, au naturel", "popcorn":"Pop-corn", "pop corn":"Pop-corn", "cornflakes":"Pétales de maïs",
 "lait d'amande":"Boisson à l'amande", "lait de soja":"Boisson au soja", "lait d'avoine":"Boisson à l'avoine", "jambon blanc":"Jambon cuit", "coca":"Cola, sucré", "coca zéro":"Cola, sans sucres", "pomme":"Pomme, chair", "banane":"Banane, chair",
 "chips":"Chips de pommes de terre", "chicon":"Endive", "oeuf":"Oeuf", "oeufs":"Oeuf", "riz basmati":"Riz basmati", "riz blanc cuit":"Riz blanc, cuit", "blanc de poulet":"Poulet, filet", "fromage blanc":"Fromage blanc", "steak haché 5%":"Boeuf, steak haché 5%"}
fails = []
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); pg.goto("http://app.local/sl/"); pg.wait_for_timeout(800); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4000)
    pg.evaluate("loadFoods()"); pg.wait_for_timeout(1500)
    for q, want in EXPECT.items():
        r = pg.evaluate("(q) => searchFoods(parseFoodLine(q).txt).slice(0,1).map(f => f.nom)[0] || ''", q)
        ok = r.lower().startswith(want.lower()); print(("OK  " if ok else "KO  ") + f"{q!r:20} -> {r}")
        if not ok: fails.append(q)
    br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
