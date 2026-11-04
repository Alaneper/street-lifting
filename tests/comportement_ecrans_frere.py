"""Retours frère A (2e passage) : comparaison de COMPORTEMENT v65 / refonte sur Programme, Historique et fin de séance, avec le même jeu de test.
Usage : python3 tests/comportement_ecrans_frere.py > sortie.json  (à lancer dans chaque arbre : v65, refonte)"""
import pathlib, os, json, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
out = {"programme": {}, "historique": {}, "fin": {}}
LINES = """(sel) => { const e = document.querySelector(sel); return e ? e.innerText.split('\\n').map(x => x.replace(/\\s+/g, ' ').trim()).filter(Boolean) : null; }"""
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(2000)
    # ---------- PROGRAMME
    ev("setTab('seance')"); pg.wait_for_timeout(800)
    out["programme"]["defaut"] = ev(LINES, "#v-seance")
    blocs = ev("[...new Set(S.map(s => s.bloc))].sort((a, b) => a - b)")
    out["programme"]["blocs"] = blocs
    ex = {}
    for b in blocs[:7]:
        try:
            ev("(b) => ACT.pickBloc({b:String(b)})", b); pg.wait_for_timeout(700)
        except Exception as e: out["programme"]["erreur_pickBloc_%s" % b] = str(e)[:100]; continue
        ex["bloc%s" % b] = ev(LINES, "#v-seance")
    out["programme"]["par_bloc"] = ex
    # une séance précise ouverte dans le programme : tout son détail (exercices, séries × reps, charge, RPE)
    keys = ev("S.filter(s => s.bloc === 2 && s.semaine === '3').map(s => s.key)")
    det = {}
    for k in keys[:4]:
        ev("(k) => ACT.sel({k})", k); pg.wait_for_timeout(500)
        det[k] = ev(LINES, "#v-seance")
    out["programme"]["detail_seances_bloc2_s3"] = det
    # séance faite : ce que le programme montre d'une séance passée
    fk = ev("(S.find(s => s.faite && !s.archived) || {}).key")
    if fk:
        ev("(k) => ACT.sel({k})", fk); pg.wait_for_timeout(500); out["programme"]["seance_faite"] = {"key": fk, "texte": ev(LINES, "#v-seance")}
    # ---------- HISTORIQUE (n'existe pas en v65 : on compare avec ce qu'elle offrait pour une séance passée)
    has_histo = ev("typeof rHisto === 'function'")
    out["historique"]["ecran_historique_existe"] = has_histo
    if has_histo:
        ev("setTab('histo')"); pg.wait_for_timeout(800); out["historique"]["ecran"] = ev(LINES, "#v-histo")
    # séances terminées et leur détail via « openSeance » (existe dans les deux versions)
    done = ev("S.filter(s => s.faite && dateOf(s)).sort((a, b) => dateOf(a) < dateOf(b) ? 1 : -1).slice(0, 3).map(s => s.key)")
    out["historique"]["nb_seances_faites"] = ev("S.filter(s => s.faite && dateOf(s)).length")
    dd = {}
    for k in done:
        try:
            ev("setTab('home')"); ev("(k) => ACT.openSeance({k})", k); pg.wait_for_timeout(700)
            dd[k] = {"feuille": ev(LINES, "#layer .sheet, .sheet, .page"), "dates": ev("(k) => dateOf(seanceByKey(k))", k)}
            ev("try { closeSheet && closeSheet(); } catch(e){}")
        except Exception as e: dd[k] = str(e)[:100]
    out["historique"]["detail_seance_passee"] = dd
    # ---------- FIN DE SÉANCE : même séance jouée de bout en bout
    ev("setTab('home')"); ev("live = null; store.set('sl4-live', null);")
    key = ev("(S.find(s => !s.archived && !s.faite && s.exercices.length >= 3 && s.exercices.slice(0, 3).every(e => !isCardioEx(e))) || {}).key")
    out["fin"]["seance"] = key
    sers0 = ev("window.__sheets['%s'].SERIES.length" % APP); coach0 = json.dumps(ev("window.__sheets['%s']" % COACH))
    ev("(k) => startLive(k)", key); pg.wait_for_timeout(900)
    if pg.locator("[data-act=pdcSave]").count(): pg.fill("#pw", "75,4"); pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(600)
    n = ev("seanceByKey(live.key).exercices.length"); jouees = []
    for i in range(min(3, n)):
        ev("(i) => { live.i = i; renderLayer(); }", i); pg.wait_for_timeout(400)
        for _ in range(12):
            j = ev("live.rows[live.i].sets.findIndex(x => !x.done)")
            if j < 0: break
            sel = f"[data-act=doneSet][data-j='{j}']"
            try: pg.locator(sel).first.click(timeout=2500)
            except Exception: ev("(j) => ACT.doneSet({j:String(j)})", j)
            pg.wait_for_timeout(300); ev("rest = null")
        jouees.append(ev("live.rows[live.i].sets.map(x => [x.c, x.r, !!x.done, !!x.rec])"))
        ev("rest = null"); pg.click("[data-act=liveNav][data-d='1']") if i < 2 else None; pg.wait_for_timeout(700)
    out["fin"]["series_jouees"] = jouees
    ev("finishLive()"); pg.wait_for_timeout(1500)
    out["fin"]["resume"] = ev(LINES, ".sheet, .fin, #layer")
    out["fin"]["boutons_resume"] = ev("[...document.querySelectorAll('.sheet button, .fin button, #layer .sheet button')].map(b => b.innerText.replace(/\\s+/g,' ').trim()).filter(Boolean)")
    sers1 = ev("window.__sheets['%s'].SERIES" % APP)
    out["fin"]["lignes_serie_ajoutees"] = sers1[sers0:]
    coach1 = ev("window.__sheets['%s']" % COACH)
    chg = []
    for tab, g in coach1.items():
        g0 = json.loads(coach0).get(tab, [])
        for r, row in enumerate(g):
            for cc, v in enumerate(row):
                o = g0[r][cc] if r < len(g0) and cc < len(g0[r]) else None
                if o != v: chg.append([tab, r + 1, cc + 1, o, v])
    out["fin"]["cases_ecrites_chez_le_coach"] = chg
    out["fin"]["pesees_ecrites"] = ev("window.__sheets['%s'].POIDS.slice(-2)" % APP)
    out["erreurs_js"] = errs; br.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
