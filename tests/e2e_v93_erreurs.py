"""Lot fiabilité et tactile : graphiques au doigt, aucun survol requis, états vides, noms très longs, valeurs extrêmes, hors connexion puis reconnexion, clavier / encoche (simulés).
Rejoue : python3 tests/e2e_v93_erreurs.py   (SAFE_TOP=47px SAFE_BOTTOM=34px pour simuler encoche et barre d'accueil)"""
import pathlib, os, json, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
def setup(p, size=(390, 844), touch=True):
    br = p.chromium.launch(); c = br.new_context(viewport={"width": size[0], "height": size[1]}, device_scale_factor=2, service_workers="block", has_touch=touch, is_mobile=touch, timezone_id="Europe/Brussels"); c.route("**/*", route)
    pg = c.new_page(); pg.errs = []; pg.fails = []
    pg.on("pageerror", lambda e: pg.errs.append(str(e))); pg.on("console", lambda m: pg.errs.append(m.text) if m.type == "error" else None)
    pg.on("requestfailed", lambda r: pg.fails.append(r.url[:90])); pg.on("response", lambda r: pg.fails.append(f"{r.status} {r.url[:90]}") if r.status >= 400 else None)
    return br, c, pg
def link(pg):
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
BAD = r"undefined|NaN|Infinity|\[object|null\b"
OVER = """() => { const vw = innerWidth, out = []; if (document.documentElement.scrollWidth > vw + 1) out.push('page ' + document.documentElement.scrollWidth); document.querySelectorAll('body *').forEach(el => { const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'fixed' && false) return; const r = el.getBoundingClientRect(); if (r.width < 1 || r.height < 1 || el.closest('svg')) return; if (r.right > vw + 1.5 || r.left < -1.5) { for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) { const c = getComputedStyle(a); if (/(auto|scroll|hidden)/.test(c.overflowX)) { const pr = a.getBoundingClientRect(); if (pr.right <= vw + 1.5 && pr.left >= -1.5) return; } } out.push(el.tagName + '.' + (el.className || '') + ' ' + Math.round(r.left) + '→' + Math.round(r.right)); } }); return out.slice(0, 5); }"""
with sync_playwright() as p:
    br, c, pg = setup(p); ev = pg.evaluate; link(pg); vw = 390
    cdp = c.new_cdp_session(pg)
    def touch_drag(x0, y0, x1, y1, hold=0, steps=6, end=True):
        cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y0}]})
        if hold: pg.wait_for_timeout(hold)
        for i in range(1, steps + 1): cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x0 + (x1 - x0) * i / steps, "y": y0 + (y1 - y0) * i / steps}]}); pg.wait_for_timeout(20)
        if end: cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    # ---------- 1. graphiques au doigt
    ev("""() => { const base = new Date(D.today + 'T12:00:00'); D.poids = []; for (let i = 119; i >= 0; i--) { if (i % 3 === 2) continue; const d = new Date(base); d.setDate(d.getDate() - i); D.poids.push({id: 1000 + i, date: d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'), poids: 82 - i * 0.02 + Math.sin(i) * 0.5}); }
      pwRange = '3m'; corpsTab = 'poids'; corpsManual = D.today; setTab('corps'); }""")
    pg.wait_for_timeout(700)
    ev("() => document.querySelector('svg[data-ich=pw]').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
    r = ev("() => { const r = document.querySelector('svg[data-ich=pw]').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
    x, y = r[0] + r[2] * .6, r[1] + r[3] * .5
    check("graphique de poids : touch-action laisse défiler la page à la verticale (pan-y)", ev("getComputedStyle(document.querySelector('svg[data-ich=pw]')).touchAction") in ("pan-y", "pan-y pinch-zoom"), ev("getComputedStyle(document.querySelector('svg[data-ich=pw]')).touchAction"))
    touch_drag(x, y, x - 90, y, hold=150, end=False); pg.wait_for_timeout(120)
    tip = ev("() => { const t = document.querySelector('.ich-tip'); if (!t || t.hidden) return null; const b = t.getBoundingClientRect(); return {l: b.left, r: b.right, t: b.top, b: b.bottom, txt: t.textContent}; }")
    check("graphique de poids : un doigt posé puis glissé (touchstart + touchmove) affiche la bulle", bool(tip), tip)
    check("graphique de poids : la bulle ne sort pas de l'écran", tip and tip["l"] >= 0 and tip["r"] <= vw and tip["t"] >= 0, tip)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}); pg.wait_for_timeout(300)
    y0 = ev("scrollY"); touch_drag(x, y, x, y - 180, steps=8); pg.wait_for_timeout(500)
    check("glisser le doigt à la verticale sur le graphique fait défiler la page (le graphique ne bloque pas)", ev("scrollY") > y0 + 40, (y0, ev("scrollY")))
    ev("() => window.scrollTo(0, 0)")
    # bords : bulle près du bord droit et du bord gauche
    for fx, nom in ((0.97, "droit"), (0.12, "gauche")):
        ev("() => document.querySelector('svg[data-ich=pw]').scrollIntoView({block:'center'})"); pg.wait_for_timeout(250)
        r = ev("() => { const r = document.querySelector('svg[data-ich=pw]').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
        touch_drag(r[0] + r[2] * fx, r[1] + r[3] * .5, r[0] + r[2] * fx, r[1] + r[3] * .5, hold=150, steps=1, end=False); pg.wait_for_timeout(100)
        tip = ev("() => { const t = document.querySelector('.ich-tip'); if (!t || t.hidden) return null; const b = t.getBoundingClientRect(); return {l: b.left, r: b.right}; }")
        check(f"graphique de poids : bulle au bord {nom} reste dans l'écran", tip and tip["l"] >= 0 and tip["r"] <= vw, tip)
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}); pg.wait_for_timeout(1800)
    ev("() => window.scrollTo(0, 0)"); pg.wait_for_timeout(200)
    # périodes au doigt
    for k in ("1m", "6m", "all", "7j"):
        ev(f"() => document.querySelector(\"[data-act=pwRange][data-k='{k}']\").scrollIntoView({{block:'center'}})"); pg.wait_for_timeout(150)
        b = ev(f"() => {{ const r = document.querySelector(\"[data-act=pwRange][data-k='{k}']\").getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, r.left, r.right, r.width, r.height]; }}")
        pg.touchscreen.tap(b[0], b[1]); pg.wait_for_timeout(450)
        check(f"période « {k} » atteignable au doigt (cible {round(b[4])}×{round(b[5])} px, dans l'écran)", ev("pwRange") == k and b[2] >= 0 and b[3] <= vw and b[4] >= 40 and b[5] >= 44, (ev("pwRange"), b))
    # courbes de Progrès : au doigt
    ev("() => { crvSel = 'total'; progSeg = 'courbes'; setTab('prog'); }"); pg.wait_for_timeout(1200)
    ev("""() => { D.prs = D.prs.filter(x => x.src === 'x'); const add = (l, d, kg) => D.prs.push({date: d, lift: l, charge: kg, reps: 1, note: '', rpe: null, eq: false});
      [['SQUAT', 90, 100, 105, 110], ['PULL', 22, 26, 29, 32], ['DIP', 28, 31, 34, 37]].forEach(([l, a, b, c, d]) => { [[-150, a], [-100, b], [-50, c], [-10, d]].forEach(([o, kg]) => add(l, addDays(D.today, o), kg)); }); rProg && rProg(); foldOpen.vol = true; rProg(); }""")
    pg.wait_for_timeout(1200)
    ichs = ev("() => [...document.querySelectorAll('svg[data-ich]')].filter(s => s.getBoundingClientRect().width > 0).map(s => s.dataset.ich)")
    check("Progrès : au moins un graphique interactif présent", len(ichs) >= 1, ichs)
    for kind in dict.fromkeys(ichs):
        ev(f"() => document.querySelector('svg[data-ich={kind}]').scrollIntoView({{block:'center'}})"); pg.wait_for_timeout(250)
        r = ev(f"() => {{ const r = document.querySelector('svg[data-ich={kind}]').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }}")
        touch_drag(r[0] + r[2] * .75, r[1] + r[3] * .45, r[0] + r[2] * .5, r[1] + r[3] * .45, hold=150, end=False); pg.wait_for_timeout(120)
        tip = ev("() => { const t = document.querySelector('.ich-tip:not([hidden])'); if (!t) return null; const b = t.getBoundingClientRect(); return {l: b.left, r: b.right}; }")
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}); pg.wait_for_timeout(250)
        ta = ev(f"getComputedStyle(document.querySelector('svg[data-ich={kind}]')).touchAction")
        check(f"Progrès · graphique « {kind} » : bulle au doigt dans l'écran, touch-action {ta}", tip is not None and tip["l"] >= 0 and tip["r"] <= vw and ta.startswith("pan-y"), (tip, ta))
    # ---------- 2. aucun survol requis
    hov = ev("""() => { const out = []; const walk = (rules, inHover) => [...rules].forEach(r => { if (r.cssRules && r.conditionText !== undefined) walk(r.cssRules, inHover || /hover:\\s*hover/.test(r.conditionText)); else if (r.cssRules && !r.selectorText) walk(r.cssRules, inHover); else if (r.selectorText && /:hover/.test(r.selectorText) && !inHover) out.push(r.selectorText + ' {' + r.style.cssText.slice(0, 60) + '}'); });
      [...document.styleSheets].forEach(s => { try { walk(s.cssRules, false); } catch (e) {} }); return out; }""")
    js_hover = len(re.findall(r"mouseover|mouseenter|onmouseover|:hover", (pathlib.Path(__file__).resolve().parent.parent / "src" / "app.html").read_text().split("<style>")[-1].split("</style>")[-1]))
    check("aucune règle :hover hors @media (hover: hover) (donc aucun effet de survol sur un écran tactile)", not hov, hov[:5])
    check("aucun écouteur mouseover / mouseenter dans le code de l'app", js_hover == 0, js_hover)
    # ---------- 3. états vides (nouveau compte / Sheet vide)
    ev("() => { window.__bak = JSON.stringify({S: 0}); }")
    ev("""() => { D.series = []; D.poids = []; D.prs = []; D.cardio = []; D.nutri = D.nutri ? {} : D.nutri; D.repas = []; D.aliments = []; try { D.nut = []; D.meals = []; } catch (e) {} S.forEach(s => { s.faite = false; }); }""")
    seen = []
    for tab, extra in (("home", ""), ("seance", ""), ("histo", ""), ("corps", "corpsTab='poids';"), ("corps", "corpsTab='nutri';"), ("prog", ""), ("agenda", "")):
        ev(f"() => {{ {extra} corpsManual = D.today; setTab('{tab}'); }}"); pg.wait_for_timeout(500)
        txt = ev("() => document.querySelector('main').innerText")
        m = re.findall(BAD, txt)
        seen.append((tab + ":" + extra, m[:3]))
    check("états vides : aucun « undefined / NaN / Infinity / null » à l'écran (7 écrans)", all(not m for _, m in seen), seen)
    ev("() => openSheet('settings')"); pg.wait_for_timeout(400); txt = ev("() => document.querySelector('.sheet').innerText"); check("états vides : Réglages sans « undefined / NaN »", not re.search(BAD, txt), re.findall(BAD, txt)[:3]); ev("() => closeSheet()")
    check("états vides : aucune erreur JS", not pg.errs, pg.errs[:3])
    br.close()
with sync_playwright() as p:
    br, c, pg = setup(p); ev = pg.evaluate; link(pg)
    # ---------- 4. noms très longs
    LONG = "Développé-couché-haltères-prise-neutre-avec-pause-de-trois-secondes-en-bas-et-explosif-en-haut-version-ultra-longue"
    NOSP = "A" * 90
    key = ev("""([L, N]) => { const z = S.find(s => !s.archived && (+s.semaine) > 1 && s.exercices.length >= 3); z.exercices[0].mouvement = 'RENFO'; z.exercices[0].variation = L; z.exercices[1].mouvement = 'RENFO'; z.exercices[1].variation = N; z.exercices[0].coach = L + ' ' + L; return z.key; }""", [LONG, NOSP])
    ev("(k) => { live = null; store.set('sl4-live', null); startLive(k); }", key); pg.wait_for_timeout(800)
    if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
    for i in (0, 1):
        ev("(i) => { live.i = i; renderLayer(); document.querySelector('.live').scrollTop = 0; }", i); pg.wait_for_timeout(400)
        o = ev(OVER); check(f"nom très long ({'avec espaces' if i == 0 else '90 lettres sans espace'}) : séance en direct sans débordement horizontal", not o, o)
    ev("() => { live = null; store.set('sl4-live', null); renderLayer(); setTab('seance'); sel = " + json.dumps(key) + "; rSeance(); }"); pg.wait_for_timeout(500)
    o = ev(OVER); check("noms très longs : Programme sans débordement horizontal", not o, o)
    ev("() => { setTab('histo'); }"); pg.wait_for_timeout(400); o = ev(OVER); check("noms très longs : Historique sans débordement", not o, o)
    ev("(k) => { startLive(k); live.i = 0; renderLayer(); }", key); pg.wait_for_timeout(600); pg.click(".live [data-act=swapOpen]"); pg.wait_for_timeout(500)
    o = ev(OVER); check("noms très longs : feuille « Changer l'exercice » sans débordement", not o, o); ev("() => closeSheet()")
    # ---------- 5. valeurs extrêmes
    ev("(k) => { live = null; store.set('sl4-live', null); startLive(k); live.i = seanceByKey(k).exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === 'SQUAT'); renderLayer(); }", key); pg.wait_for_timeout(700)
    vals = ["0", "999", "82,5", "82.5", "-5", "abc", "1e3", "  ", "12,"]; res = []
    for v in vals:
        ev("""(v) => { const i = document.querySelector('.lsr.cur input[data-chg=setC]'); i.value = v; i.dispatchEvent(new Event('change', {bubbles: true})); }""", v); pg.wait_for_timeout(120)
        c_ = ev("() => { const x = live.rows[live.i].sets[live.rows[live.i].sets.findIndex(s => !s.done)]; return x.c; }")
        res.append((v, c_))
    ok = all(c_ is None or (isinstance(c_, (int, float)) and abs(c_) < 1e6) for _, c_ in res)
    check("valeurs extrêmes (charge) : jamais NaN, tout est un nombre fini ou vide : " + str(res), ok, res)
    txt = ev("() => document.querySelector('.live').innerText"); check("valeurs extrêmes : aucun « undefined / NaN » dans l'écran de séance", not re.search(BAD, txt), re.findall(BAD, txt))
    for v in ["0", "999", "12,5", "-3", "x"]:
        ev("""(v) => { const i = document.querySelector('.lsr.cur input[data-chg=setR]'); if (i) { i.value = v; i.dispatchEvent(new Event('change', {bubbles: true})); } }""", v)
    ev("""() => { const i = document.querySelector('.lsr.cur input[data-chg=setC]'); i.value = '999'; i.dispatchEvent(new Event('change', {bubbles: true})); const r = document.querySelector('.lsr.cur input[data-chg=setR]'); if (r) { r.value = '999'; r.dispatchEvent(new Event('change', {bubbles: true})); } }"""); pg.wait_for_timeout(200)
    pg.click(".vbar [data-act=doneSet]"); pg.wait_for_timeout(800)
    o = ev(OVER); txt = ev("() => document.querySelector('.live').innerText")
    check("999 kg × 999 reps validés : pas de débordement, pas de NaN, pas d'erreur", not o and not re.search(BAD, txt) and not pg.errs, (o, re.findall(BAD, txt), pg.errs[:2]))
    ev("() => { rest = null; renderLayer(); }")
    ev("() => finishLive()"); pg.wait_for_timeout(2200); txt = ev("() => (document.querySelector('.fin') || document.body).innerText"); o = ev(OVER)
    check("fin de séance avec valeurs extrêmes : pas de NaN / Infinity / débordement", not re.search(BAD, txt) and not o, (re.findall(BAD, txt), o))
    ev("() => ACT.closeSummary()"); pg.wait_for_timeout(500)
    # ---------- 6. hors connexion puis reconnexion
    key = ev("() => { const z = S.find(s => !s.archived && (+s.semaine) > 1 && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === 'RENFO')); return z.key; }")
    ev("(k) => { live = null; store.set('sl4-live', null); startLive(k); }", key); pg.wait_for_timeout(700)
    if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
    n0 = len(pg.errs); ev("() => { window.__down = true; }")
    for _ in range(3):
        if pg.locator(".vbar [data-act=doneSet]").count(): pg.click(".vbar [data-act=doneSet]"); pg.wait_for_timeout(500)
    ev("() => { rest = null; renderLayer(); }"); ev("() => finishLive()"); pg.wait_for_timeout(2500)
    o = ev(OVER); check("hors connexion : la séance se termine sans erreur JS ni débordement (écran de fin affiché)", ev("!!document.querySelector('.fin')") and not o and len(pg.errs) == n0, (o, pg.errs[n0:][:2]))
    ev("() => ACT.closeSummary()"); pg.wait_for_timeout(400)
    ev("() => { window.__down = false; window.dispatchEvent(new Event('online')); }"); pg.wait_for_timeout(3000)
    ev("() => { setTab('home'); }"); pg.wait_for_timeout(800)
    check("reconnexion : aucune erreur JS, l'app répond (Séance affichée)", len(pg.errs) == n0 and ev("!!document.querySelector('main') && document.querySelector('main').innerText.length > 50"), pg.errs[n0:][:2])
    br.close()
# ---------- 7. clavier ouvert (simulé par une fenêtre plus basse) et paysage : le champ en cours reste visible
with sync_playwright() as p:
    for size, label in (((390, 844 - 336), "clavier ouvert (fenêtre réduite de 336 px)"), ((375, 667 - 300), "iPhone SE, clavier ouvert")):
        br, c, pg = setup(p, size); ev = pg.evaluate; link(pg)
        key = ev("() => { const z = S.find(s => !s.archived && (+s.semaine) > 1 && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === 'SQUAT')); return z.key; }")
        ev("(k) => { live = null; store.set('sl4-live', null); startLive(k); live.i = seanceByKey(k).exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === 'SQUAT'); renderLayer(); }", key); pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
        pg.click(".lsr.cur input[data-chg=setC]"); pg.wait_for_timeout(500)
        v = ev("""() => { const i = document.querySelector('.lsr.cur input[data-chg=setC]').getBoundingClientRect(), b = document.querySelector('.vbar [data-act=doneSet]').getBoundingClientRect(); return {inputTop: i.top, inputBottom: i.bottom, valTop: b.top, valBottom: b.bottom, vh: innerHeight}; }""")
        check(f"{label} : le champ kg est visible et « Valider la série » reste atteignable", v["inputTop"] >= 0 and v["inputBottom"] <= v["vh"] and v["valBottom"] <= v["vh"] + 1 and v["valTop"] >= 0, v)
        br.close()
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
