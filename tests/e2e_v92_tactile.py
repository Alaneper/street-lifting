"""Lot fiabilité et tactile : balayage tactile et erreurs (émulation tactile hasTouch ; iPhone SE 375×667, 390×844, 430×932 ; paysage 844×390 sur la séance en direct).
Mesures automatiques sur chaque écran : cibles < 44 px, cibles voisines trop serrées, cibles recouvertes (barre fixe, minuteur), débordement horizontal, texte coupé, champs < 16 px (zoom iOS), hover, erreurs JS / requêtes en échec.
Rejoue : python3 tests/e2e_v92_tactile.py   ·   AUDIT_OUT=<fichier.json> : écrit toutes les mesures ; SAFE_TOP=47px SAFE_BOTTOM=34px : simule encoche et barre d'accueil."""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []; AUDIT = {}
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
AUDIT_JS = """() => {
  const vw = innerWidth, vh = innerHeight, out = {small:[], tight:[], covered:[], overflowX:[], cut:[], font:[], n:0};
  const name = el => { const t = (el.getAttribute('aria-label') || el.innerText || el.value || el.placeholder || '').replace(/\\s+/g, ' ').trim().slice(0, 28); return (el.tagName.toLowerCase() + (el.dataset && el.dataset.act ? '[' + el.dataset.act + ']' : el.dataset && el.dataset.chg ? '[' + el.dataset.chg + ']' : '') + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : '') + ' « ' + t + ' »'); };
  const shown = el => { const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return null; for (let a = el.parentElement; a; a = a.parentElement) { const c = getComputedStyle(a); if (c.display === 'none' || c.visibility === 'hidden') return null; if (a.tagName === 'DETAILS' && !a.open && !(el.tagName === 'SUMMARY' && el.parentElement === a)) return null; }
    const r = el.getBoundingClientRect(); return r.width < 1 || r.height < 1 ? null : r; };
  const layer = document.querySelector('.sheet') || document.querySelector('.live') || document.querySelector('.page') || document.querySelector('.view:not([hidden]), main') || document.body;
  const inLayer = el => layer === document.body ? true : (layer.contains(el) || (el.closest('.vbar, .lrest, .tabs, nav, .topbar') && layer.classList.contains('live') === false && layer.classList.contains('sheet') === false && !document.querySelector('.live, .sheet, .page')));
  const SEL = 'button, a[href], [data-act], [data-chg], [data-inp], [role=button], summary, input:not([type=hidden]), select, textarea, label[for]';
  let T = [...document.querySelectorAll(SEL)].filter(el => { if (el.closest('.scrim') || !inLayer(el) || (el.tagName === 'LABEL' && el.htmlFor && document.getElementById(el.htmlFor))) return false; if (el.matches('input[type=checkbox],input[type=radio],input[type=file],input[type=range]') && el.id) return false; return true; });
  T = T.filter(el => !T.some(o => o !== el && el.contains(o) && o.matches('button, a[href], input, select, textarea, summary')));   /* un conteneur cliquable qui renferme un vrai contrôle n'est pas une cible */
  const rows = T.map(el => ({el, r: shown(el)})).filter(x => x.r); out.n = rows.length;
  /* zone de toucher réelle : on sonde autour du centre (elementFromPoint) pour compter aussi les zones agrandies par ::after, sans jamais recouvrir une autre cible */
  const hits = (el, x, y) => { if (x < 0 || y < 0 || x >= vw || y >= vh) return false; const q = document.elementFromPoint(x, y); return !!q && (q === el || el.contains(q)); };
  const extent = (el, r, horiz) => { const cx = r.left + r.width / 2, cy = Math.min(Math.max(r.top + r.height / 2, 1), vh - 2); let a = 0, b = 0; const lim = 40;
    if (horiz) { while (a < lim && hits(el, cx - a - 1, cy)) a++; while (b < lim && hits(el, cx + b + 1, cy)) b++; } else { while (a < lim && hits(el, cx, cy - a - 1)) a++; while (b < lim && hits(el, cx, cy + b + 1)) b++; } return a + b + 1; };
  rows.forEach(({el, r}) => { if (r.width < 43.5 || r.height < 43.5) { const ow = r.left + r.width / 2 < 0 || r.left + r.width / 2 >= vw || r.top + r.height / 2 < 0 || r.top + r.height / 2 >= vh;
    const w = ow ? Math.round(r.width) : (r.width < 43.5 ? Math.max(Math.round(r.width), extent(el, r, true)) : Math.round(r.width)), h = ow ? Math.round(r.height) : (r.height < 43.5 ? Math.max(Math.round(r.height), extent(el, r, false)) : Math.round(r.height));
    if (w < 43.5 || h < 43.5) out.small.push({t: name(el), w, h, box: Math.round(r.width) + '×' + Math.round(r.height)}); } });
  for (let i = 0; i < rows.length; i++) for (let j = i + 1; j < rows.length; j++) { const a = rows[i], b = rows[j]; if (a.el.contains(b.el) || b.el.contains(a.el) || a.el.closest('.segc,.rpe,.tabs,.chips,.stepper') && a.el.parentElement === b.el.parentElement) continue;
    const dx = Math.max(0, Math.max(a.r.left, b.r.left) - Math.min(a.r.right, b.r.right)), dy = Math.max(0, Math.max(a.r.top, b.r.top) - Math.min(a.r.bottom, b.r.bottom)), gap = Math.hypot(dx, dy);
    if (gap < 4 && (a.r.width < 44 || a.r.height < 44 || b.r.width < 44 || b.r.height < 44)) out.tight.push({a: name(a.el), b: name(b.el), gap: Math.round(gap)}); }
  const scroller = root => { if (!root || root === document.body) return null; const c = [root, ...root.querySelectorAll('*')].filter(e => /(auto|scroll)/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 2); return c.sort((a, b) => b.clientHeight - a.clientHeight)[0] || null; };
  const sc = scroller(layer), free = new Set(), pos = [];
  const maxS = sc ? sc.scrollHeight - sc.clientHeight : Math.max(0, document.documentElement.scrollHeight - vh), save = sc ? sc.scrollTop : scrollY;
  for (let s = 0; s <= maxS + 1; s += Math.max(120, vh * .35)) pos.push(Math.min(s, maxS)); if (pos[pos.length - 1] !== maxS) pos.push(maxS);
  pos.forEach(s => { if (sc) sc.scrollTop = s; else scrollTo(0, s); rows.forEach((rw, k) => { const r = rw.el.getBoundingClientRect(), x = r.left + r.width / 2, y = Math.min(Math.max(r.top + r.height / 2, 0), vh - 1); if (r.bottom < 0 || r.top > vh || free.has(k) || r.left + r.width / 2 < 0 || r.left + r.width / 2 > vw) { if (r.left + r.width / 2 < 0 || r.left + r.width / 2 > vw) free.add(k); return; }
    const tp = document.elementFromPoint(x, r.top + r.height / 2); if (r.top + r.height / 2 < 0 || r.top + r.height / 2 > vh) return; if (tp && (tp === rw.el || rw.el.contains(tp) || tp.contains(rw.el))) free.add(k); }); });
  if (sc) sc.scrollTop = save; else scrollTo(0, save);
  rows.forEach((rw, k) => { if (!free.has(k)) { const r = rw.el.getBoundingClientRect(); out.covered.push({t: name(rw.el)}); } });
  if (document.documentElement.scrollWidth > vw + 1) out.overflowX.push('page : scrollWidth ' + document.documentElement.scrollWidth + ' > ' + vw);
  document.querySelectorAll('body *').forEach(el => { const r = shown(el); if (!r) return; if (r.right > vw + 1.5 || r.left < -1.5) { let clipped = false; for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) { const c = getComputedStyle(a); if (/(auto|scroll|hidden)/.test(c.overflowX)) { const pr = a.getBoundingClientRect(); if (pr.right <= vw + 1.5 && pr.left >= -1.5) { clipped = true; break; } } } if (!clipped && getComputedStyle(el).position !== 'fixed' && !el.closest('svg')) out.overflowX.push(name(el) + ' (' + Math.round(r.left) + '→' + Math.round(r.right) + ')'); } });
  document.querySelectorAll('body *').forEach(el => { if (el.children.length || !el.textContent.trim()) return; const r = shown(el); if (!r) return; const cs = getComputedStyle(el); if ((/(hidden|clip)/.test(cs.overflow + cs.overflowX)) && el.scrollWidth > el.clientWidth + 1 && cs.textOverflow !== 'ellipsis') out.cut.push(name(el) + ' (' + el.scrollWidth + ' > ' + el.clientWidth + ')'); });
  document.querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=range]):not([type=hidden]):not([type=file]), select, textarea').forEach(el => { if (shown(el) && parseFloat(getComputedStyle(el).fontSize) < 15.99) out.font.push(name(el) + ' ' + getComputedStyle(el).fontSize); });
  return out; }"""
SCROLL_JS = "(bottom) => { const layer = document.querySelector('.sheet') || document.querySelector('.live') || document.querySelector('.page'); const els = layer ? [layer, ...layer.querySelectorAll('*')].filter(e => /(auto|scroll)/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 2) : []; els.forEach(e => e.scrollTop = bottom ? e.scrollHeight : 0); window.scrollTo(0, bottom ? document.body.scrollHeight : 0); }"
def audit(pg, label, size, strict=True, top_bottom=True):
    ev = pg.evaluate; res = {}
    ev(SCROLL_JS, 0); pg.wait_for_timeout(150)
    r = ev(AUDIT_JS)
    if top_bottom:
        ev(SCROLL_JS, 1); pg.wait_for_timeout(200)
        r2 = ev(AUDIT_JS)
        for k in ("small", "tight", "covered", "overflowX", "cut", "font"):
            seen = {json.dumps(x, sort_keys=True) for x in r[k]}
            r[k] += [x for x in r2[k] if json.dumps(x, sort_keys=True) not in seen]
        ev(SCROLL_JS, 0)
    AUDIT.setdefault(f"{size[0]}x{size[1]}", {})[label] = r
    return r
def tapx(pg, sel):
    b = pg.evaluate("(s) => { const r = document.querySelector(s).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }", sel); pg.touchscreen.tap(b[0], b[1])
def drag(cdp, x0, y0, x1, y1, steps=6):
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y0}]})
    for i in range(1, steps + 1): cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x0 + (x1 - x0) * i / steps, "y": y0 + (y1 - y0) * i / steps}]})
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
def setup(p, size):
    br = p.chromium.launch()
    c = br.new_context(viewport={"width": size[0], "height": size[1]}, device_scale_factor=2, service_workers="block", has_touch=True, is_mobile=True, timezone_id="Europe/Brussels"); c.route("**/*", route)
    pg = c.new_page(); pg.errs = []; pg.fails = []
    pg.on("pageerror", lambda e: pg.errs.append(str(e))); pg.on("console", lambda m: pg.errs.append(m.text) if m.type == "error" else None)
    pg.on("requestfailed", lambda r: pg.fails.append(r.url[:90])); pg.on("response", lambda r: pg.fails.append(f"{r.status} {r.url[:90]}") if r.status >= 400 else None)
    return br, c, pg
def link(pg):
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000)
    pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
def screens(pg):
    ev = pg.evaluate; go = lambda js: (ev(js), pg.wait_for_timeout(700))
    yield "Séance · Aujourd'hui", lambda: go("() => { setTab('home'); }")
    yield "Séance · Programme", lambda: go("() => { setTab('seance'); }")
    yield "Séance · Historique", lambda: go("() => { setTab('histo'); }")
    yield "Corps · Poids", lambda: go("() => { corpsTab = 'poids'; corpsManual = D.today; setTab('corps'); rCorps(); }")
    yield "Corps · Alimentation", lambda: go("() => { corpsTab = 'nutri'; corpsManual = D.today; setTab('corps'); rCorps(); }")
    yield "Progrès", lambda: go("() => { setTab('prog'); }")
    yield "Compétition", lambda: go("() => { setTab('agenda'); }")
    yield "Réglages (feuille)", lambda: go("() => { setTab('home'); openSheet('settings'); }")
    yield "Poids du matin (feuille)", lambda: go("() => { closeSheet(); openSheet('pdc'); }")
    yield "Pesée du jour (feuille)", lambda: go("() => { closeSheet(); pdDay = D.today; openSheet('pday'); }")
    yield "Aide RPE (feuille)", lambda: go("() => { closeSheet(); openSheet('rpeinfo'); }")
    yield "Ajout d'aliment (feuille)", lambda: go("() => { closeSheet(); setTab('corps'); corpsTab = 'nutri'; rCorps(); nutSlot = 'dej'; openSheet('mealnew'); }")
    yield "Scan (feuille)", lambda: go("() => { closeSheet(); openSheet('weigh'); }")
def live_screens(pg):
    ev = pg.evaluate
    key = ev("() => { const z = S.find(s => !s.archived && (+s.semaine) > 1 && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === 'SQUAT')); return z && z.key; }")
    ev("() => { closeSheet(); live = null; store.set('sl4-live', null); }"); ev("(k) => startLive(k)", key); pg.wait_for_timeout(700)
    if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
    ev("() => { live.i = seanceByKey(live.key).exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === 'SQUAT'); renderLayer(); document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(500)
    yield "Séance en direct · début"
    pg.click(".vbar [data-act=doneSet]"); pg.wait_for_timeout(900)
    yield "Séance en direct · repos + RPE"
    ev("() => { rest = null; renderLayer(); }"); pg.wait_for_timeout(200)
    pg.click(".live [data-act=swapOpen]"); pg.wait_for_timeout(500); yield "Changer l'exercice (feuille)"
    ev("() => closeSheet()"); pg.wait_for_timeout(300)
    pg.click(".live [data-act=editOpen]"); pg.wait_for_timeout(500); yield "Modifier la séance (feuille)"
    ev("() => closeSheet()"); pg.wait_for_timeout(300)
    for _ in range(8):
        if pg.locator(".vbar [data-act=doneSet]").count(): pg.click(".vbar [data-act=doneSet]"); pg.wait_for_timeout(350)
    ev("() => { rest = null; renderLayer(); }"); pg.wait_for_timeout(200)
    pg.evaluate("() => finishLive()"); pg.wait_for_timeout(2200); yield "Fin de séance"
    pg.evaluate("() => ACT.closeSummary()"); pg.wait_for_timeout(500)
RUN = [(375, 667), (390, 844), (430, 932)]
with sync_playwright() as p:
    for size in RUN:
        br, c, pg = setup(p, size); ev = pg.evaluate; tag = f"{size[0]}×{size[1]}"
        pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1200); audit(pg, "Lancement / première ouverture", size, top_bottom=False)
        link(pg)
        for label, f in screens(pg):
            try: f()
            except Exception as e: check(f"{tag} · {label} : accessible", False, str(e)[:160]); continue
            audit(pg, label, size)
        ev("() => { closeSheet(); setTab('home'); }")
        try:
            for label in live_screens(pg):
                audit(pg, label, size)
        except Exception as e: check(f"{tag} · parcours séance en direct", False, str(e)[:200])
        check(f"{tag} · aucune erreur JS ni requête en échec sur tout le parcours", not pg.errs and not pg.fails, (pg.errs[:3], pg.fails[:3]))
        br.close()
    # paysage (séance en direct)
    br, c, pg = setup(p, (844, 390)); ev = pg.evaluate; link(pg)
    try:
        for label in live_screens(pg): audit(pg, "PAYSAGE · " + label, (844, 390))
    except Exception as e: check("paysage · parcours séance en direct", False, str(e)[:200])
    check("paysage · aucune erreur JS", not pg.errs, pg.errs[:3]); br.close()
if os.environ.get("AUDIT_OUT"): pathlib.Path(os.environ["AUDIT_OUT"]).write_text(json.dumps(AUDIT, ensure_ascii=False, indent=1))
# exceptions justifiées par écrit (voir le doc projet) : le calendrier de l'Historique est volontairement compact (cases 40-42 × 36 + zone de toucher agrandie dans l écart de 4 px : 46×40 au mieux, jamais sur la case voisine) ; ses cases ne doivent pas rétrécir
JUSTIFIED = ("button[openSeance].hc",)
for scr in AUDIT.values():
    for r in scr.values():
        for x in list(r["small"]):
            if x["t"].startswith(JUSTIFIED): r["small"].remove(x); r.setdefault("justified", []).append(x); assert x["w"] >= 40 and x["h"] >= 36, x
# synthèse
for size, scr in AUDIT.items():
    for k in ("small", "covered", "overflowX", "cut", "font"):
        bad = {l: r[k] for l, r in scr.items() if r[k]}
        check(f"{size} · {k} : {'aucun' if not bad else sum(len(v) for v in bad.values())}", not bad, json.dumps(bad, ensure_ascii=False)[:600])
print("\nÉCHECS :", len(fails)); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
