"""Inventaire de la séance en direct (données pour le tableau de non-régression v65 / v68 / niveau 85 / retours-frère).
Marche sur n'importe quel arbre. Usage : python3 tests/inventaire_live_frere.py > inventaire.json"""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
CASES = {"force (squat comp)": ["SQUAT", "COMP", 1], "renfo (curl)": ["RENFO", "CURL BICEPS", None], "lest (muscle-up)": ["MUSCLE UP", "COMP", None], "en durée (dead bug)": ["RENFO", "LOADED DEAD BUG", None]}
JS_DOM = """() => { const r = document.querySelector('.live'); if (!r) return {err:'pas de séance'};
  const T = s => r.querySelectorAll(s).length, txt = r.innerText.replace(/\\s+/g, ' ');
  return {acts:[...new Set([...r.querySelectorAll('[data-act]')].map(x => x.dataset.act))].sort(), chg:[...new Set([...r.querySelectorAll('[data-chg]')].map(x => x.dataset.chg))].sort(),
    lignes_series:T('.setrow, .lsr'), champs_charge_reps:T('input'), points_progression:T('.live-progress i, .lprog i'), carte_hero:T('.hero'), prbox:T('#prbox'),
    rpe_boutons:T('.rpe button'), commentaire:T('textarea, [data-act=comOpen]'), texte:txt.slice(0, 700)}; }"""
out = {}
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(800); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    for name, (m, v, ser) in CASES.items():
        r = ev("""async ([m, v, ser]) => { const z = S.find(s => !s.archived && s.bloc === 1 && s.semaine === '2' && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === m && String(e.variation).toUpperCase().trim() === v)); if (!z) return null;
          live = null; store.set('sl4-live', null); const k = z.exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === m && String(e.variation).toUpperCase().trim() === v && (ser === null || String(e.series) === '1' || true));
          await startLive(z.key, k); return z.key; }""", [m, v, ser])
        if not r: out[name] = "absent du jeu de test"; continue
        pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
        ev("() => { live.i = %d; renderLayer(); }" % ev("seanceByKey(live.key).exercices.findIndex(e => String(e.variation).toUpperCase().trim() === '%s' && String(e.mouvement).toUpperCase().trim() === '%s')" % (v, m))); pg.wait_for_timeout(500)
        a = ev(JS_DOM)
        if pg.locator("[data-act=doneSet]").count():
            pg.locator("[data-act=doneSet]").first.click(); pg.wait_for_timeout(900); ev("() => { rest = null; sheet = null; renderLayer(); }"); pg.wait_for_timeout(300)
        b = ev(JS_DOM); out[name] = {"avant_serie": a, "apres_serie_1": b}
        ev("() => { live = null; store.set('sl4-live', null); renderLayer(); }")
    out["erreurs_js"] = errs; br.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
