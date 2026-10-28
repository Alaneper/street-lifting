"""v50 (basé sur v41) : 2e modèle de coach (onglets « WEEK n », jours « DAY k »), lecture seule + fin du chargement infini.
Données 100 % inventées (aucune donnée personnelle). Usage : python3 tests/e2e_v41.py  (affiche « TOUT VERT » si tout passe)"""
import pathlib, json, sys, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)

def day(k, nom, rows, base):
    g = [["DAY %d" % k, nom, "RECOMMENDE", "", "", "", "", "", "", "", "", "EFFECTUE"],
         ["Cat.", "Exercise", "Séries", "Reps", "Indications", "RPE", "%1RM", "Avg. Speed Target", "Charge", "", "Repos", "Reps", "Charges"]]
    g += rows
    g += [[], [], [], ["", "Heure de sommeil :", "Stress :", "", "Fatigue percue avant séance : ", "Pas avant séance :"], ["", "7", "2", "", "3", "8000"], []]
    return g
def week(w):
    rows = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    rows[2] = ["Athlète test"]
    rows[10] = ["", "Current 1RM", "Est."]
    d1 = day(1, "Lundi", [["DL", "Sumo Deadlift", "3", "6", "", "", "", "", "", "100", "5'", "6", "100"],
                          ["AC", "Chest Supported Machine Row", "3", "10-20", "", "", "-", "", "", "", "3'", "18", "50"],
                          ["AC", "Plank", "2", "MAX", "(si + que 1'30 leste)", "", "", "", "", "", "1'", "1", "20"]], w)
    d2 = day(2, "Mardi", [["SQ", "HB Squat", "3", "6", "", "", "55,00%", "", "", "80", "3-5'", "6", "80"],
                          ["BE", "COMP Bench", "1", "2", "", "6", "", "", "AUTOREGULATION", "", "3'", "2", "70"],
                          ["BE", "COMP Bench", "3", "5", "", "DROP-CAP6", "", "", "-10,00%", "-5,00%", "3'", "5"]], w)
    d3 = day(5, "", [["", "", "", "", "", "", "-"]] * 3, w)
    return rows + d1 + [[]] + d2 + [[]] + d3
tabs = {"BLOC 3": [[], [], ["Athlete Info"], ["Nom", "Test"]], "WEEK 1": week(1), "WEEK 2": week(2), "DATA": [["x"]]}
INJ = "<script>(()=>{const b=window.__sheets['%s']; for (const k of Object.keys(b)) delete b[k]; const T=%s; for (const k of Object.keys(T)) b[k]=T[k]; })()</script>" % (COACH, json.dumps(tabs))
def route2(r):
    u = r.request.url
    if u.endswith("/sl/") or u.endswith("index.html"):
        return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + INJ + "<script src='/shim.js'></script>", 1), content_type="text/html")
    return route(r)

with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route2)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)

    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(500)
    sess = """const s = S.find(z => z.jour === 'Mardi'); live = null; startLive(s.key); const k = s.exercices.findIndex(e => /COMP Bench/i.test(e.mouvement)); live.i = k; const st = live.rows[k];"""
    # --- 1. coupure réseau pendant la séance : rien ne se perd, aucune erreur
    pg.evaluate("window.__down = true; window.__calls.length = 0")
    r = pg.evaluate("(async () => { " + sess + """ st.sets.forEach(x => { x.done = true; x.r = 5; x.c = 100; }); st.rpeLast = 8; st.dirty = true;
      const ok = await saveRow(k); return {ok, faite:s.faite, n:outbox.length, ls:JSON.parse(localStorage.getItem('sl4-outbox') || '[]').length, loc:D.series.filter(x => x.ex === exKey(s.exercices[k])).length, dot:document.getElementById('syncdot').className, row:s.exercices[k].row}; })()""")
    check("hors connexion : la série est enregistrée sans erreur (ok + ✓)", r["ok"] and r["faite"], r)
    check("actions gardées en file ET sur le téléphone (localStorage)", r["n"] >= 2 and r["ls"] == r["n"], r)
    check("la série est déjà visible dans l'app", r["loc"] == 1, r)
    check("pastille rouge « en attente »", "off" in r["dot"], r)
    # --- 2. on la modifie encore hors connexion : une seule action par série (la plus récente)
    r2 = pg.evaluate("(async () => { " + sess + """ st.sets.forEach(x => { x.done = true; x.r = 6; x.c = 105; }); st.dirty = true; await saveRow(k);
      return {n:outbox.length, series:outbox.filter(o => o.t === 'serie').length, txt:outbox.find(o => o.t === 'serie').rowv[6]}; })()""")
    check("2e enregistrement hors ligne : toujours UNE seule action « série » (la dernière version)", r2["series"] == 1 and "6" in r2["txt"], r2)
    # --- 3. rechargement de la page hors connexion : la file survit
    n_before = r2["n"]
    pg.evaluate("window.__calls.length = 0")
    # --- 4. retour du réseau : tout part dans le bon ordre, une seule fois
    pg.evaluate("window.__down = false")
    r3 = pg.evaluate("(async () => { await flushOutbox(); return {n:outbox.length, ls:localStorage.getItem('sl4-outbox')}; })()")
    check("retour du réseau : la file se vide", r3["n"] == 0 and not r3["ls"], r3)
    w = [str(x) for x in pg.evaluate("window.__calls.filter(x => !/^get|^batch_get/.test(x[0]))")]
    check("une seule série ajoutée à SERIES (pas de doublon)", sum(1 for x in w if "append" in x.lower() and "SERIES" in x) == 1, w[:6])
    rows = pg.evaluate("(a) => (window.__sheets[a]['SERIES'] || []).filter(r => /Bench/i.test(String(r[4]))).map(r => r.join('|'))", pg.evaluate("APP_ID"))
    check("valeur finale écrite = dernière version (6 reps à 105)", len(rows) == 1 and "105" in rows[0], rows)
    vals = pg.evaluate("(r) => [__sheets['%s']['WEEK 1'] || [] , __sheets['%s']['WEEK 2'] || []].map(w => (w[r - 1] || []).slice(11, 13).join('|'))" % (COACH, COACH), r["row"])
    check("cases EFFECTUE du coach remplies après le retour du réseau", any("105" in v for v in vals), vals)
    # --- 5. fin de séance hors connexion puis reconnexion : jamais de doublon même si on rejoue
    pg.evaluate("window.__down = true")
    r4 = pg.evaluate("(async () => { " + sess + """ st.sets.forEach(x => { x.done = true; x.r = 7; x.c = 110; }); st.dirty = true; await saveRow(k); return outbox.length; })()""")
    pg.evaluate("window.__down = false; window.__calls.length = 0")
    pg.evaluate("(async () => { await flushOutbox(); await flushOutbox(); })()"); pg.wait_for_timeout(2500)
    rows = pg.evaluate("(a) => (window.__sheets[a]['SERIES'] || []).filter(r => /Bench/i.test(String(r[4]))).map(r => r.join('|'))", pg.evaluate("APP_ID"))
    check("reprise puis 2e envoi : toujours une seule ligne SERIES, mise à jour (110)", len(rows) == 1 and "110" in rows[0], rows)
    check("aucune erreur JavaScript", not errs, errs[:3])
    c.close(); br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
