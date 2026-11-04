"""Retours testeur C : captures « curl 20 → 22 kg » (semaine 3) et Réglages. Usage : SHOTDIR=<dossier> [SYNC=1] python3 tests/capture_charges_frere.py (marche sur v65 / v68 / niveau 85 / retours-frère)"""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOT = pathlib.Path(os.environ["SHOTDIR"]); SHOT.mkdir(parents=True, exist_ok=True); SYNC = os.environ.get("SYNC") == "1"
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(800); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    ev("""([coach]) => { for (const [tab, g] of Object.entries(window.__sheets[coach])) { if (!/^BLOC/.test(tab)) continue; g.forEach(r => { for (let c = 2; c < r.length; c += 20) if (String(r[c]).trim() === 'RENFO' && String(r[c + 1]).toUpperCase().trim() === 'CURL BICEPS') r[c + 8] = '20'; }); } }""", [COACH])
    if SYNC: ev("([k, id]) => localStorage.setItem(k, JSON.stringify({[id]: true}))", ["sl4-chargesync", COACH])
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    for w, did in [("1", [[20, 13], [20, 13], [20, 13]]), ("2", [[22, 10], [22, 10]])]:
        ev("""async ([w, did]) => { const z = S.find(s => !s.archived && s.bloc === 1 && s.semaine === w && s.idx === 0); live = null; store.set('sl4-live', null); await startLive(z.key);
          const k = z.exercices.findIndex(e => /CURL BICEPS/.test(e.variation)), st = live.rows[k]; st.sets = did.map(d => ({c:d[0], r:d[1], done:true})); st.dirty = true; await saveRow(k); live = null; store.set('sl4-live', null); }""", [w, did])
    ev("""async () => { const z = S.find(s => !s.archived && s.bloc === 1 && s.semaine === '3' && s.idx === 0); live = null; store.set('sl4-live', null); await startLive(z.key); window.__k = z.exercices.findIndex(e => /CURL BICEPS/.test(e.variation)); }"""); pg.wait_for_timeout(700)
    if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
    ev("() => { live.i = window.__k; renderLayer(); const l = document.querySelector('.live'); if (l) l.scrollTop = 0; }"); pg.wait_for_timeout(500)
    pg.screenshot(path=str(SHOT / "curl-semaine3.png")); print("propose :", ev("live.rows[live.i].sets.map(x => x.c)"))
    if SYNC:
        ev("() => { live = null; store.set('sl4-live', null); renderLayer(); openSheet('settings'); }"); pg.wait_for_timeout(700)
        ev("() => { const e = document.querySelector('#csync'); if (e) e.scrollIntoView({block:'center'}); }"); pg.wait_for_timeout(400)
        pg.screenshot(path=str(SHOT / "reglage-charges.png"))
    print("erreurs :", errs); br.close()
