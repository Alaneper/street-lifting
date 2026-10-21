"""Service worker (v20) : ouverture depuis le téléphone, hors ligne, et arrivée d'une nouvelle version."""
import sys, json, time, pathlib, importlib.util
sys.argv = sys.argv[:1] + ["sw"]
H = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("perf", H / "perf.py"); perf = importlib.util.module_from_spec(spec); spec.loader.exec_module(perf)
import tempfile
from playwright.sync_api import sync_playwright
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
tmp = pathlib.Path(tempfile.mkdtemp()); site, vend = perf.build_site(tmp)
s1, s2 = perf.serve(site, 8123, slow=False), perf.serve(vend, 8124, slow=False)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, service_workers="allow")
    pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://127.0.0.1:8123/"); pg.wait_for_timeout(300)
    pg.evaluate(f"localStorage.setItem('sl-cfg', JSON.stringify({{appId:'{perf.APP}'}})); localStorage.setItem('sl-tok', JSON.stringify({{t:'TOK', exp:Date.now() + 3600e3}}))")
    pg.goto("http://127.0.0.1:8123/"); pg.wait_for_function("typeof lastSync !== 'undefined' && lastSync > 0", timeout=30000); pg.wait_for_timeout(2500)
    check("service worker actif", pg.evaluate("!!navigator.serviceWorker.controller"))
    # 1. Serveur coupé : l'app s'ouvre quand même, avec les dernières données
    s1.shutdown(); s1.server_close()
    pg.reload(); pg.wait_for_timeout(1500)
    check("hors ligne : l'app s'ouvre avec les données du téléphone", pg.evaluate("!!document.querySelector('#v-home .hero')"))
    # 2. Nouvelle version en ligne : appliquée tout de suite si rien n'a été touché
    import re
    bump = lambda h, n: re.sub(r'<meta name="sl-build" content="\d+">', f'<meta name="sl-build" content="{n}">', h)
    orig = (site / "index.html").read_text()
    html = bump(orig.replace('const APP_VER = "', 'const APP_VER = "TEST-NOUVELLE · ', 1), 99990000000001)
    (site / "index.html").write_text(html)
    s1 = perf.serve(site, 8123, slow=False)
    pg.reload(); pg.wait_for_timeout(4500)
    v = pg.evaluate("APP_VER")
    check("nouvelle version installée sans rien toucher", v.startswith("TEST-NOUVELLE"), v)
    check("après l'installation automatique : pas de bandeau en trop", not pg.evaluate("!!document.querySelector('.upd')"))
    # 3. Encore une version, mais l'app est déjà utilisée : bandeau « Mettre à jour »
    #    (serveur lent : le toucher arrive avant la réponse, comme sur un vrai réseau mobile)
    pg.wait_for_timeout(500)
    (site / "index.html").write_text(bump(html.replace("TEST-NOUVELLE", "TEST-BANDEAU", 1), 99990000000002))
    s1.shutdown(); s1.server_close(); s1 = perf.serve(site, 8123, slow=True)
    pg2 = c.new_page(); pg2.goto("http://127.0.0.1:8123/", wait_until="commit"); pg2.wait_for_selector("#v-home .hero"); pg2.mouse.click(200, 400)
    pg2.wait_for_timeout(4000)
    check("version arrivée en cours d'usage : bandeau, pas de rechargement forcé", pg2.evaluate("!!document.querySelector('.upd') && APP_VER.startsWith('TEST-NOUVELLE')"), pg2.evaluate("APP_VER"))
    pg2.click(".upd button"); pg2.wait_for_timeout(1500)
    check("« Mettre à jour » charge la nouvelle version", pg2.evaluate("APP_VER").startswith("TEST-BANDEAU"), pg2.evaluate("APP_VER"))
    # 4. Version plus ancienne servie par erreur (CDN) : ignorée, pas de retour en arrière
    (site / "index.html").write_text(bump(orig.replace('const APP_VER = "', 'const APP_VER = "TEST-ANCIENNE · ', 1), 1))
    pg3 = c.new_page(); pg3.goto("http://127.0.0.1:8123/"); pg3.wait_for_timeout(4000)
    check("version plus ancienne en ligne : ignorée", pg3.evaluate("APP_VER").startswith("TEST-BANDEAU") and not pg3.evaluate("!!document.querySelector('.upd')"), pg3.evaluate("APP_VER"))
    check("aucune erreur", not errs, errs[:3])
    br.close()
s1.shutdown(); s2.shutdown()
print("ÉCHECS :", fails)
