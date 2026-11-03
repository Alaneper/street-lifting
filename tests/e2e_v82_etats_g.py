"""Niveau 8,5, lot G : états vide / chargement / erreur / hors connexion sur chaque écran, avec de vrais mécanismes :
- chargement : premier lancement sans données sur le téléphone et réseau qui ne répond pas (les appels Sheets restent en attente) ;
- erreur : l'API Sheets refuse (Failed to fetch) alors que les données du téléphone existent ;
- hors connexion : navigator.onLine = false + événement « offline » ;
- vide : Google Sheet sans aucune donnée.
Contrôles : pas de texte « undefined / NaN / null », écran jamais blanc, bandeau d'état attendu, bouton « Réessayer » qui existe. Captures : SHOTDIR=<dossier>."""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOT = pathlib.Path(os.environ["SHOTDIR"]) if os.environ.get("SHOTDIR") else None
if SHOT: SHOT.mkdir(parents=True, exist_ok=True)
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
ECR = {"aujourdhui": ("setTab('home')", "v-home"), "programme": ("setTab('seance')", "v-seance"), "historique": ("setTab('histo')", "v-histo"),
  "poids": ("corpsTab='poids';corpsManual=D&&D.today;setTab('corps')", "v-corps"), "alimentation": ("corpsTab='nutri';nutView='jour';corpsManual=D&&D.today;setTab('corps')", "v-corps"),
  "records": ("progSeg='records';setTab('prog')", "v-prog"), "courbes": ("progSeg='courbes';setTab('prog')", "v-prog"), "mouvements": ("progSeg='mouvements';setTab('prog')", "v-prog"),
  "competition": ("agendaSeg='compet';setTab('agenda')", "v-agenda"), "amis": ("agendaSeg='amis';setTab('agenda')", "v-agenda")}
INIT = """
(() => { let real = null; window.__MODE = 'ok';
  Object.defineProperty(window, 'fetch', { configurable: true, get(){ return (u, o) => { const url = String(u);
    if (url.startsWith('https://sheets.googleapis.com/')) { if (window.__MODE === 'fail') return Promise.reject(new TypeError('Failed to fetch')); if (window.__MODE === 'hang') return new Promise(() => {}); }
    return real(u, o); } }, set(f){ real = f; } }); })();
"""
BAD = r"(undefined|NaN|\[object|null\b)"
import re
def audit(pg, nom, etat, vid, expect_bar=None, minlen=8):
    t = pg.evaluate("(id) => { const v = document.getElementById(id); return v ? v.innerText : ''; }", vid)
    bar = pg.evaluate("(() => { const n = document.getElementById('netbar'); return n && !n.hidden ? n.innerText.replace(/\\s+/g, ' ') : ''; })()")
    ok = len(t.strip()) > minlen and not re.search(BAD, t)
    if expect_bar is not None: ok = ok and expect_bar in bar
    check(f"{etat} · {nom} : écran lisible, sans « undefined/NaN/null »" + (f", bandeau « {expect_bar} »" if expect_bar else ""), ok, (t[:140], bar))
    if SHOT: pg.screenshot(path=str(SHOT / f"{etat}__{nom}.png"))
    return t, bar
def login(br, **kw):
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=1, service_workers="block", **kw); c.route("**/*", route); c.add_init_script(INIT)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    return c, pg, errs
with sync_playwright() as p:
    br = p.chromium.launch()
    # ---------- erreur de synchro (données du téléphone présentes)
    c, pg, errs = login(br); ev = pg.evaluate
    ev("window.__MODE = 'fail'"); ev("seanceErr = ''; syncFail = ''"); ev("syncAll && syncAll(true)"); pg.wait_for_timeout(2500)
    for nom, (js, vid) in ECR.items():
        ev(js); pg.wait_for_timeout(500); audit(pg, nom, "erreur", vid, "Synchro impossible")
    ev(ECR["aujourdhui"][0]); pg.wait_for_timeout(300)
    g = ev("(() => { const n = document.getElementById('netbar'), b = n.querySelector('.nbt'), r = n.querySelector('[data-act=sync]'); const rb = b.getBoundingClientRect(), rr = r.getBoundingClientRect(), rn = n.getBoundingClientRect(); return {h: Math.round(rn.height), textW: Math.round(rb.width), btnLeft: rr.left >= rb.right - 1, title: b.querySelector('b').getBoundingClientRect().height}; })()")
    check("erreur : bandeau lisible (titre sur une ligne, texte sur toute la largeur, bouton à droite)", g["h"] <= 130 and g["textW"] >= 180 and g["btnLeft"] and g["title"] < 24, g)
    check("erreur : « Réessayer » présent dans le bandeau", ev("!!document.querySelector('#netbar [data-act=sync]')"))
    n0 = ev("D.series.length + D.poids.length")
    check("erreur : aucune donnée perdue", n0 > 0, n0)
    ev("window.__MODE = 'ok'"); ev("document.querySelector('#netbar [data-act=sync]').click()"); pg.wait_for_timeout(3500)
    check("erreur : « Réessayer » rétablit la synchro (bandeau disparu)", ev("(() => { const n = document.getElementById('netbar'); return !n || n.hidden || !/impossible/.test(n.innerText); })()"))
    # ---------- hors connexion (données présentes)
    c.set_offline(True); ev("Object.defineProperty(navigator, 'onLine', {get: () => false, configurable: true}); window.dispatchEvent(new Event('offline'))"); pg.wait_for_timeout(500)
    for nom, (js, vid) in ECR.items():
        ev(js); pg.wait_for_timeout(500); audit(pg, nom, "hors-ligne", vid, "Hors connexion")
    c.set_offline(False); c.close()
    # ---------- vide (Google Sheet sans données)
    c, pg, errs = login(br); ev = pg.evaluate
    ev("(() => { D.poids = []; D.repas = []; D.series = []; D.prs = []; D.comps = []; D.cardio = []; })()")
    for nom, (js, vid) in ECR.items():
        ev(js); pg.wait_for_timeout(500); audit(pg, nom, "vide", vid)
    ev("progSeg='records'; setTab('prog')"); pg.wait_for_timeout(400)
    check("vide · Progrès : « Mon total » affiche « — » (jamais « 0 kg »)", ev("(document.querySelector('#v-prog .hb')||{innerText:''}).innerText.trim()") == "—", ev("(document.querySelector('#v-prog .hb')||{innerText:''}).innerText"))
    check("aucune erreur JS (erreur / hors ligne / vide)", not errs, errs[:3]); c.close()
    # ---------- chargement : premier lancement, le réseau ne répond pas
    c0, pg0, _ = login(br); state = c0.storage_state(); c0.close()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=1, service_workers="block", storage_state=state); c.route("**/*", route)
    c.add_init_script(INIT + "window.__MODE = 'hang'; try { Object.keys(localStorage).filter(k => /cache/.test(k)).forEach(k => localStorage.removeItem(k)); } catch(e){}")
    pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); ev = pg.evaluate
    pg.goto("http://app.local/sl/", wait_until="commit"); pg.wait_for_timeout(2600)
    check("chargement : l'écran de lancement a laissé la place à l'app (≤ 2,6 s, réseau muet)", ev("!document.getElementById('splash')"))
    for nom, (js, vid) in ECR.items():
        ev(js.replace("corpsManual=D&&D.today;", "")); pg.wait_for_timeout(400)
        t, bar = audit(pg, nom, "chargement", vid, minlen=-1)
        sk = ev("(() => { const v = document.getElementById('%s'); return !!v.querySelector('.skel') || /Synchronisation|chargement|Lecture/i.test(v.innerText + ' ' + ((document.getElementById('syncline')||{}).innerText||'')); })()" % vid)
        check(f"chargement · {nom} : squelette ou message d'attente, jamais une zone vide", sk, (t[:100], bar))
    check("aucune erreur JS (chargement)", not errs, errs[:3]); c.close()
    br.close()
print("ÉCHECS :", fails)
