"""v56 : produits proposés envoyés au catalogue partagé (file d'attente, case à décocher, produits incohérents jamais envoyés). Usage : python3 tests/e2e_v56.py"""
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
    pg.evaluate("CAT_URL = 'https://cat.test/exec'; window.__sent = []; window.__down = false; const of = window.fetch; window.fetch = (u, o) => { u = String(u); if (u.startsWith('https://cat.test')) { if (window.__down) return Promise.reject(new Error('down')); if (u.includes('a=submit')) window.__sent.push(u); return Promise.resolve({json: () => Promise.resolve({ok:true, st:'prive'})}); } return of(u, o); }; setTab('corps')"); pg.wait_for_timeout(500); pg.evaluate("ACT.nutTab({t:'foods'})"); pg.wait_for_timeout(300)
    def create(nom, marque="", k="150"):
        pg.evaluate("(q) => { nutQ = q; nutRefresh(); }", nom); pg.wait_for_timeout(150)
        if not pg.evaluate("!!document.getElementById('ncn')"): pg.evaluate("ACT.nutCreate()"); pg.wait_for_timeout(200)
        pg.evaluate("([n, m, k]) => { document.getElementById('ncn').value = n; document.getElementById('ncm').value = m; document.getElementById('nck').value = k; document.getElementById('ncp').value = '20'; document.getElementById('ncg').value = '0'; document.getElementById('ncl').value = '8'; ACT.nutCreateSave(); }", [nom, marque, k]); pg.wait_for_timeout(1500)
    def create(nom, k="150", share=True, p="20", g="0", l="8", marque="M"):
        pg.evaluate("(q) => { nutQ = q; nutRefresh(); }", nom); pg.wait_for_timeout(150)
        if not pg.evaluate("!!document.getElementById('ncn')"): pg.evaluate("ACT.nutCreate()"); pg.wait_for_timeout(200)
        pg.evaluate("([n, m, k, s, p, g, l]) => { document.getElementById('ncn').value = n; document.getElementById('ncm').value = m; document.getElementById('nck').value = k; document.getElementById('ncp').value = p; document.getElementById('ncg').value = g; document.getElementById('ncl').value = l; document.getElementById('ncs').checked = s; ACT.nutCreateSave(); }", [nom, marque, k, share, p, g, l]); pg.wait_for_timeout(1500)
        pg.evaluate("nutPick = null; nutCreate = false; nutRefresh()")
    sent = lambda: pg.evaluate("window.__sent.length")
    create("Produit partagé un")
    check("création : envoi au catalogue", sent() == 1, sent())
    u = pg.evaluate("window.__sent[0]")
    check("l'envoi contient nom/kcal/identifiant d'appareil aléatoire, rien de personnel", "nom=Produit%20partag" in u and "k=150" in u and re.search(r"dev=[a-z0-9]{20}&", u) and "alane" not in u.lower(), u)
    create("Produit privé deux", share=False)
    check("case décochée : rien envoyé", sent() == 1, sent())
    create("Produit incohérent", k="900", p="1", g="1", l="1", marque="X")
    check("valeurs incohérentes : jamais envoyées", sent() == 1, sent())
    pg.evaluate("window.__down = true"); create("Produit hors ligne", k="150", marque="Y")
    q = pg.evaluate("(JSON.parse(localStorage.getItem('sl4-subq') || '[]')).length")
    check("service indisponible : produit gardé en file d'attente", q >= 1 and sent() == 1, [q, sent()])
    pg.evaluate("window.__down = false; commFlush()"); pg.wait_for_timeout(800)
    q = pg.evaluate("(JSON.parse(localStorage.getItem('sl4-subq') || '[]')).length")
    check("retour du service : file vidée et produit envoyé", q == 0 and sent() == 2, [q, sent()])
    check("aucune erreur de page", not errs, errs[:2])
    br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
