"""Niveau 8,5, lot F : finition (onglet actif, fermeture animée des feuilles, chiffres animés, retour au toucher,
sensation d'app, réduction des animations, taille de texte agrandie). Captures : SHOTDIR=<dossier>."""
import pathlib, os
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOT = pathlib.Path(os.environ["SHOTDIR"]) if os.environ.get("SHOTDIR") else None
if SHOT: SHOT.mkdir(parents=True, exist_ok=True)
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
def shot(pg, name, clip=None):
    if SHOT: pg.screenshot(path=str(SHOT / (name + ".png")), clip=clip)
def boot(br, **kw):
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block", **kw); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    return c, pg, errs
with sync_playwright() as p:
    br = p.chromium.launch()
    c, pg, errs = boot(br); ev = pg.evaluate
    # --- sensation d'app
    r = ev("(() => { const i = document.createElement('input'); document.body.appendChild(i); const a = getComputedStyle(document.body), b = getComputedStyle(i), h = getComputedStyle(document.documentElement); const o = {body: a.userSelect || a.webkitUserSelect, input: b.userSelect || b.webkitUserSelect, callout: a.webkitTouchCallout, adjust: h.webkitTextSizeAdjust || h.textSizeAdjust, bounce: getComputedStyle(document.body).overscrollBehaviorY}; i.remove(); return o; })()")
    check("sensation d'app : pas de sélection de texte sur l'interface, champs de saisie éditables", r["body"] == "none" and r["input"] == "text", r)
    check("sensation d'app : pas de rebond parasite, taille de texte iOS non gonflée", r["bounce"] == "none" and r["adjust"] == "100%", r)
    # --- barre d'onglets : onglet actif distinct
    tabs = ["home", "corps", "prog", "agenda"]
    for t in tabs:
        ev(f"setTab('{t}')"); pg.wait_for_timeout(450)
        r = ev("(() => [...document.querySelectorAll('.tabs button')].map(b => { const s = getComputedStyle(b, '::before'); return [b.dataset.tab, b.getAttribute('aria-current'), +s.opacity, +getComputedStyle(b).fontWeight]; }))()")
        act = [x for x in r if x[1] == "page"]
        check(f"onglet « {t} » : un seul actif, pastille visible, libellé plus gras", len(act) == 1 and act[0][0] == t and act[0][2] == 1 and act[0][3] >= 700 and all(x[2] == 0 and x[3] == 600 for x in r if x[1] != "page"), r)
        shot(pg, f"onglet-{t}", clip={"x": 0, "y": 844 - 90, "width": 390, "height": 90})
    ev("setTab('home')"); pg.wait_for_timeout(500)
    # --- retour immédiat au toucher
    btn = ev("(() => { const b = document.querySelector('#v-home .btn, #v-home button.btn'); if (!b) return null; const r = b.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2, r.top > 0 && r.bottom < innerHeight]; })()")
    if btn and btn[2]:
        pg.mouse.move(btn[0], btn[1]); pg.mouse.down(); pg.wait_for_timeout(60)
        a = ev("(() => { const b = document.querySelector('#v-home .btn'); const cs = getComputedStyle(b); return [cs.transform, cs.opacity]; })()")
        shot(pg, "toucher-bouton", clip={"x": 0, "y": max(0, btn[1] - 60), "width": 390, "height": 120})
        pg.mouse.move(5, 5); pg.mouse.up(); pg.wait_for_timeout(150)
        check("toucher : le bouton réagit tout de suite (réduit et assombri) tant que le doigt est posé", a[0] != "none" and float(a[1]) < 1, a)
    else:
        ev("document.body.insertAdjacentHTML('beforeend', '<button class=\"btn\" id=\"tbtn\" style=\"position:fixed;top:100px;left:20px;width:200px\">Test</button>')")
        pg.mouse.move(100, 127); pg.mouse.down(); pg.wait_for_timeout(60)
        a = ev("(() => { const cs = getComputedStyle(document.getElementById('tbtn')); return [cs.transform, cs.opacity]; })()")
        pg.mouse.up(); ev("document.getElementById('tbtn').remove()")
        check("toucher : le bouton réagit tout de suite (réduit et assombri) tant que le doigt est posé", a[0] != "none" and float(a[1]) < 1, a)
    # --- fermeture animée d'une feuille
    ev("openSheet('settings')"); pg.wait_for_timeout(500)
    ev("closeSheet()")
    st = ev("({sheet: sheet, layer: !!document.querySelector('#layer .sheet'), ghost: document.querySelectorAll('body > .outg').length, ids: document.querySelectorAll('body > .outg [id]').length, dis: !!document.querySelector('body > .outg[aria-hidden=true]')})")
    check("fermeture : l'état est fermé tout de suite, une copie sans effet glisse vers le bas", st["sheet"] is None and not st["layer"] and st["ghost"] == 2 and st["ids"] == 0 and st["dis"], st)
    ev("document.getAnimations().forEach(a => { a.pause(); a.currentTime = 110; })"); pg.wait_for_timeout(50); shot(pg, "fermeture-feuille")   # image figée à mi-course (110 ms sur 220)
    ev("document.getAnimations().forEach(a => { a.currentTime = 220; a.play(); })")
    pg.wait_for_timeout(450)
    check("fermeture : la copie disparaît après l'animation", ev("document.querySelectorAll('body > .outg').length") == 0)
    ev("openSheet('settings')"); pg.wait_for_timeout(300)
    sh = ev("(() => { const s = document.querySelector('#layer .sheet'); return [s.getAttribute('role'), s.getAttribute('aria-modal'), s.getAttribute('aria-labelledby') || s.getAttribute('aria-label'), document.querySelector('#layer .scrim').getAttribute('aria-hidden')]; })()")
    check("VoiceOver : la feuille est une boîte de dialogue nommée, le fond est ignoré", sh[0] == "dialog" and sh[1] == "true" and bool(sh[2]) and sh[2] != 'Fenêtre' and sh[3] == "true", sh)
    ev("closeSheet()"); pg.wait_for_timeout(450)
    # --- chiffres qui s'animent (en test automatique : seulement si on le demande)
    ev("window.__animForce = true; for (const k in numMem) delete numMem[k]; corpsTab = 'poids'; corpsManual = D.today; setTab('corps')")
    pg.wait_for_timeout(130)
    mid = ev("(document.querySelector('#v-corps .pw-big')||{}).textContent")
    shot(pg, "chiffre-en-cours", clip={"x": 0, "y": 80, "width": 390, "height": 330})
    pg.wait_for_timeout(900)
    fin = ev("(document.querySelector('#v-corps .pw-big')||{}).textContent")
    check("chiffre clé : valeur intermédiaire pendant l'animation, valeur exacte à la fin", mid and fin and mid != fin and ev("(document.querySelector('#v-corps .pw-big')||{}).classList.contains('cu')") is False, (mid, fin))
    ev("window.__animForce = false")
    # --- barres qui se remplissent
    an = []
    for js in ("setTab('home')", "progSeg='records';setTab('prog')", "corpsTab='nutri';nutView='jour';setTab('corps')", "agendaSeg='compet';setTab('agenda')"):
        ev(js); pg.wait_for_timeout(300)
        an += ev("[...document.querySelectorAll('.view:not([hidden]) .bar > i, .view:not([hidden]) .nh-bar i')].map(i => getComputedStyle(i).animationName)")
    check("barres de progression : animation de remplissage définie (au moins une barre testée)", an and all(x == "barIn" for x in an), an)
    check("aucune erreur console (session normale)", not errs, errs[:3])
    # --- taille de texte agrandie : pas de débordement horizontal
    ECR = {"Séance": "setTab('home')", "Programme": "setTab('seance')", "Historique": "setTab('histo')", "Poids": "corpsTab='poids';corpsManual=D.today;setTab('corps')", "Alimentation": "corpsTab='nutri';nutView='jour';corpsManual=D.today;setTab('corps')", "Progrès": "progSeg='records';setTab('prog')", "Courbes": "progSeg='courbes';setTab('prog')", "Compétition": "agendaSeg='compet';setTab('agenda')", "Réglages": "openSheet('settings')"}
    for zoom in (1.3,):
        ev(f"document.documentElement.style.zoom = {zoom}")
        for nom, js in ECR.items():
            ev("page = null; sheet = null; renderLayer()"); ev(js); pg.wait_for_timeout(500)
            w = ev("(() => { const sh = document.querySelector('.sheet'); const el = sh || document.documentElement; return [el.scrollWidth, el.clientWidth]; })()")
            check(f"texte à {int(zoom*100)} % · {nom} : pas de débordement horizontal", w[0] <= w[1] + 1, w)
            if nom in ("Séance", "Progrès", "Réglages"): shot(pg, f"zoom130-{nom}")
        ev("document.documentElement.style.zoom = ''; page = null; sheet = null; renderLayer()")
    c.close()
    # --- réduire les animations : rien ne bouge
    c, pg, errs = boot(br, reduced_motion="reduce"); ev = pg.evaluate
    ev("window.__animForce = true; for (const k in numMem) delete numMem[k]; corpsTab = 'poids'; corpsManual = D.today; setTab('corps')"); pg.wait_for_timeout(60)
    a = ev("(document.querySelector('#v-corps .pw-big')||{}).textContent"); pg.wait_for_timeout(700); b = ev("(document.querySelector('#v-corps .pw-big')||{}).textContent")
    check("réduire les animations : les chiffres s'affichent directement à leur valeur", a == b, (a, b))
    ev("openSheet('settings')"); pg.wait_for_timeout(200); ev("closeSheet()")
    check("réduire les animations : la feuille se ferme sans copie animée", ev("document.querySelectorAll('body > .outg').length") == 0)
    check("réduire les animations : aucune animation CSS sur les barres ni sur la feuille", ev("(() => { openSheet('settings'); const s = getComputedStyle(document.querySelector('.sheet')); const r = s.animationName === 'none' || parseFloat(s.animationDuration) === 0; closeSheet(); return r; })()"))
    c.close()
    br.close()
print("ÉCHECS :", fails)
