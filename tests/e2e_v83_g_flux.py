"""Niveau 8,5, lot G : les trois feux de validation, Partager (résumé et carte de record), Envoyer à mon coach (réussite et échec).
Captures : SHOTDIR=<dossier>."""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOT = pathlib.Path(os.environ["SHOTDIR"]) if os.environ.get("SHOTDIR") else None
if SHOT: SHOT.mkdir(parents=True, exist_ok=True)
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
INIT = """
(() => { let real = null; window.__MODE = 'ok'; window.__shared = []; window.__clip = [];
  Object.defineProperty(window, 'fetch', { configurable: true, get(){ return (u, o) => { const url = String(u);
    if (url.startsWith('https://sheets.googleapis.com/') && window.__MODE === 'fail') return Promise.reject(new TypeError('Failed to fetch'));
    return real(u, o); } }, set(f){ real = f; } });
  window.__shareOn = () => { navigator.share = d => { window.__shared.push(d); return Promise.resolve(); }; navigator.canShare = () => true; };
  window.__shareOff = () => { try { delete navigator.share; } catch(e){} Object.defineProperty(navigator, 'share', {value: undefined, configurable: true}); Object.defineProperty(navigator, 'clipboard', {value: {writeText: t => { window.__clip.push(t); return Promise.resolve(); }}, configurable: true}); };
})();
"""
def shot(pg, name, clip=None):
    if SHOT: pg.screenshot(path=str(SHOT / (name + ".png")), clip=clip)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route); c.add_init_script(INIT)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    ev = pg.evaluate
    # ---------- séance en direct : les trois feux
    ev("setTab('home')"); pg.wait_for_timeout(300)
    key = ev("(() => { const s = S.find(x => !x.archived && x.exercices.some(e => liftOf(e.mouvement) === 'SQUAT')); return s && s.key; })()")   # la séance du jour change avec le jour : on ouvre une séance avec du squat
    ev(f"startLive({key!r})"); pg.wait_for_timeout(700)
    if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
    # aller au premier exercice de force (liftOf) : « Squat »
    for _ in range(6):
        if ev("(() => { const s = seanceByKey(live.key), e = s.exercices[live.i]; return liftOf(e.mouvement) === 'SQUAT' && !isCardioEx(e); })()"): break
        pg.click("[data-act=liveNav][data-d='1']"); pg.wait_for_timeout(500)
    ev("document.querySelector('.live').scrollTop = 0"); pg.wait_for_timeout(200)
    avant = ev("({lights: document.querySelectorAll('.live .lights').length, on: document.querySelectorAll('.live .lights.on').length, rec: document.querySelectorAll('.live .lights.rec').length, spans: [...document.querySelectorAll('.live .lights')].map(l => l.querySelectorAll('i').length)})")
    shot(pg, "feux-0-avant")
    check("feux : 3 voyants par série (aucune série validée = voyants éteints)", avant["lights"] >= 1 and avant["on"] == 0 and avant["rec"] == 0 and all(n == 3 for n in avant["spans"]), avant)
    pg.click("[data-act=doneSet][data-j='0']"); pg.wait_for_timeout(900)
    ev("document.querySelector('.live').scrollTop = 0")
    on = ev("({on: document.querySelectorAll('.live .lights.on').length, rec: document.querySelectorAll('.live .lights.rec').length, anim: getComputedStyle(document.querySelector('.live .lights.on i, .live .lights.rec i')).animationName})")
    check("feux : série validée → les trois voyants s'allument (blanc, ou orange si record)", on["on"] + on["rec"] >= 1 and on["anim"] == "lamp", on)
    shot(pg, "feux-1-validee")
    # série suivante : charge très lourde pour provoquer un record (la série 2 est rouverte et modifiée comme à la main)
    ev("rest = null; renderLayer()"); pg.wait_for_timeout(200)
    if not pg.locator(".live .setrow[data-j='1']").count() and pg.locator(".live .lsr[data-j='1']").count(): pg.click(".live .lsr[data-j='1']"); pg.wait_for_timeout(300)
    ev("ACT.addSet()"); pg.wait_for_timeout(300)
    print("DEBUG séries :", ev("[...document.querySelectorAll('.live .lsr')].map(e => e.className + '|' + (e.dataset.j) + '|' + e.querySelectorAll('input').length)"), ev("live.rows[live.i].sets.map(s => [s.c, s.r, s.done])"))
    if pg.locator(".live .setrow[data-j='1'] input").count() >= 2:
        pg.fill(".live .setrow[data-j='1'] input >> nth=0", "400"); pg.fill(".live .setrow[data-j='1'] input >> nth=1", "5"); pg.click("[data-act=doneSet][data-j='1']"); pg.wait_for_timeout(1000)
        ev("document.querySelector('.live').scrollTop = 0")
        r = ev("({on: document.querySelectorAll('.live .lights.on').length, rec: document.querySelectorAll('.live .lights.rec').length})")
        check("feux : une série record allume les trois voyants en orange", r["rec"] >= 1, r)
        shot(pg, "feux-2-record")
    else:
        check("feux : une série record allume les trois voyants en orange", False, "série 2 introuvable")
    # série légère : voyants blancs (validée sans record)
    ev("rest = null; ACT.addSet()"); pg.wait_for_timeout(300)
    if pg.locator(".live .setrow[data-j='2'] input").count() >= 2:
        pg.fill(".live .setrow[data-j='2'] input >> nth=0", "60"); pg.fill(".live .setrow[data-j='2'] input >> nth=1", "5"); pg.click("[data-act=doneSet][data-j='2']"); pg.wait_for_timeout(900)
        ev("document.querySelector('.live').scrollTop = 0")
        w = ev("({on: document.querySelectorAll('.live .lights.on').length, rec: document.querySelectorAll('.live .lights.rec').length})")
        check("feux : une série validée sans record allume les trois voyants en blanc", w["on"] >= 1, w)
        shot(pg, "feux-3-blanc")
    else: check("feux : une série validée sans record allume les trois voyants en blanc", False, "série 3 introuvable")
    pg.evaluate("rest = null; renderLayer()")
    # ---------- fin de séance : Partager + Envoyer au coach
    ev("window.__shareOn()")
    pg.click("[data-act=finishLive]"); pg.wait_for_timeout(2500)
    check("fin de séance : le résumé propose « Partager » et le bilan", ev("!!document.querySelector('[data-act=shareSession]')"), ev("document.querySelector('.sheet') && document.querySelector('.sheet').innerText.slice(0, 300)"))
    shot(pg, "resume-fin")
    pg.click("[data-act=shareSession]"); pg.wait_for_timeout(500)
    sh = ev("window.__shared")
    check("Partager (feuille de partage iOS disponible) : le texte du résumé est transmis", len(sh) == 1 and sh[0].get("text") and "série" in sh[0]["text"], sh)
    ev("window.__shared.length = 0; window.__shareOff()")
    pg.click("[data-act=shareSession]"); pg.wait_for_timeout(500)
    cl = ev("window.__clip"); toast = ev("document.getElementById('toast').innerText")
    check("Partager (sans feuille de partage) : résumé copié et message « Résumé copié. »", len(cl) == 1 and "Résumé copié" in toast, (cl, toast))
    shot(pg, "partager-copie", clip={"x": 0, "y": 0, "width": 390, "height": 140})
    # ---------- Envoyer à mon coach : échec puis réussite
    has = ev("!!document.querySelector('.sheet [data-act=bilan]')")
    check("fin de séance : bouton du bilan pour le coach présent", has)
    def notes(v):
        for k in ev("BILAN_CRIT"): pg.click(f".sheet [data-act=score][data-k='{k}'][data-v='{v}']"); pg.wait_for_timeout(100)
        pg.wait_for_timeout(250)
    if has:
        pg.click(".sheet [data-act=bilan]"); pg.wait_for_timeout(500); notes(7); shot(pg, "coach-0-notes")
        pg.click("[data-act=saveBilan]"); pg.wait_for_timeout(2000)
        t1 = ev("document.getElementById('toast').innerText"); rows = ev(f"window.__sheets['{APP}'].BILAN.length")
        check("Envoyer au coach, réseau OK : « Bilan envoyé à ton coach » et ligne ajoutée au Google Sheet", "Bilan envoyé" in t1 and rows >= 2, (t1, rows))
        shot(pg, "coach-1-envoye", clip={"x": 0, "y": 0, "width": 390, "height": 140})
        # deuxième envoi (depuis la ligne « Bilan » de l'écran Séance), réseau coupé
        ev("live = null; renderLayer(); setTab('home')"); pg.wait_for_timeout(500)
        ev("document.querySelector('[data-act=bilan]').click()"); pg.wait_for_timeout(500); notes(8)
        ev("window.__MODE = 'fail'"); n0 = ev("Store.pending()")
        pg.click("[data-act=saveBilan]"); pg.wait_for_timeout(1800)
        t = ev("document.getElementById('toast').innerText"); pend = ev("Store.pending()"); nb = ev("document.getElementById('netbar').innerText.replace(/\\s+/g, ' ')")
        check("Envoyer au coach, réseau coupé : le message dit la vérité (« enregistré », pas « envoyé ») et le bandeau compte l'envoi en attente", "enregistré" in t and "Bilan envoyé" not in t and pend > n0 and "en attente" in nb, (t, pend, nb))
        shot(pg, "coach-2-en-attente", clip={"x": 0, "y": 0, "width": 390, "height": 200})
        rows0 = ev(f"window.__sheets['{APP}'].BILAN.length")
        ev("window.__MODE = 'ok'"); ev("syncAll && syncAll(true)"); ev("flushOutbox()"); pg.wait_for_timeout(4000)
        rows = ev(f"window.__sheets['{APP}'].BILAN.length")
        check("Envoyer au coach : au retour du réseau, l'envoi en attente part (ligne ajoutée, file vidée)", rows > rows0 and ev("Store.pending()") == 0, (rows0, rows, ev("Store.pending()")))
    ev("ACT.closeSummary()"); pg.wait_for_timeout(600)
    # ---------- Partager la carte d'un record
    ev("ACT.share({l: 'SQUAT'})"); pg.wait_for_timeout(1200)
    cv = ev("(() => { const c = document.getElementById('sharecv'); if (!c) return null; const x = c.getContext('2d'); const d = x.getImageData(0, 0, c.width, c.height).data; let nz = 0; for (let i = 0; i < d.length; i += 4000) if (d[i] + d[i+1] + d[i+2] > 30) nz++; return {w: c.width, h: c.height, nz}; })()")
    check("carte de record : l'image est bien dessinée (1080 × 1350, pas vide)", cv and cv["w"] == 1080 and cv["nz"] > 20, cv)
    shot(pg, "partager-carte")
    check("aucune erreur JS", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
