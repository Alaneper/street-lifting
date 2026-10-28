"""v41 : 2e modèle de coach (onglets « WEEK n », jours « DAY k »), lecture seule + fin du chargement infini.
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
    n = pg.evaluate("S.length"); check("4 séances lues (2 jours remplis × 2 semaines, jour vide ignoré)", n == 4, n)
    check("semaines 1 et 2", pg.evaluate("[...new Set(S.map(s => s.semaine))].join()") == "1,2")
    check("jours Lundi / Mardi", pg.evaluate("[...new Set(S.map(s => s.jour))].join()") == "Lundi,Mardi", pg.evaluate("S.map(s=>s.jour).join()"))
    check("bloc 3 (numéro de l'onglet BLOC 3)", pg.evaluate("S.every(s => s.bloc === 3)"))
    ex = pg.evaluate("S[0].exercices.map(e => [e.mouvement, e.series, e.reps, e.charge, e.coach].join('|'))")
    check("exercices du lundi : noms, séries, reps, charge prescrite", ex[0] == "Sumo Deadlift|3|6|100|" and ex[2].startswith("Plank|2|MAX||"), ex)
    check("indication du coach lue", "1'30" in ex[2], ex)
    mar = pg.evaluate("S.find(s => s.jour === 'Mardi').exercices.map(e => [e.mouvement, e.charge, e.intensite].join('|'))")
    check("autorégulation et décharge lues (colonnes Charge et RPE)", mar[1] == "COMP Bench|AUTOREGULATION|6" and mar[2].startswith("COMP Bench|-5,00%|DROP-CAP6"), mar)
    check("lignes de sommeil et de stress pas prises pour des exercices", pg.evaluate("S.every(s => s.exercices.every(e => !/SOMMEIL|^\\d+$/i.test(e.mouvement)))"))
    check("les numéros de ligne sont ceux de l'onglet", pg.evaluate("S[0].exercices[0].row") > 30)
    check("seules les colonnes « faites » sont inscriptibles (jamais RPE cible, charge prescrite, commentaire, recap)", pg.evaluate("S.every(s => !s.cols.rpe1 && !s.cols.rpeLast && !s.cols.commentaire && !s.cols.charge && !s.recapRow && s.cols.repsDone === 12 && s.cols.chargesDone === 13)"), pg.evaluate("JSON.stringify(S[0].cols)"))
    wr = pg.evaluate("window.__calls.filter(x => !/^get|^batch_get/.test(x[0]) && /WEEK|BLOC 3/.test(String(x[1]||''))).length")
    check("aucun appel d'écriture avant la validation d'une séance", wr == 0, wr)
    pg.evaluate("ACT && 0"); pg.evaluate("render()"); pg.wait_for_timeout(500)
    txt = pg.evaluate("document.body.innerText")
    check("plus de « Chargement de ta prog » qui tourne", "Chargement de ta prog" not in txt)
    check("aucune erreur JavaScript", not errs, errs[:3])
    pg.screenshot(path=str(OUT / "v41-accueil.png"))
    # séance en direct sur la 1re séance : pas d'erreur
    key = pg.evaluate("S[0].key"); pg.evaluate("(k) => startLive(k)", key); pg.wait_for_timeout(700)
    check("séance en direct ouverte sans erreur", not errs and pg.locator(".live").count() > 0, errs[:3])
    # v47 : valider un exercice de compétition -> reps/charges dans EFFECTUE, RPE proposé, ✓ affiché
    pg.evaluate("window.__calls.length = 0")
    r = pg.evaluate("""(async () => { const s = S.find(z => z.jour === 'Mardi'); live = null; startLive(s.key); const k = s.exercices.findIndex(e => /COMP Bench/i.test(e.mouvement)); live.i = k; const st = live.rows[k];
      st.sets.forEach(x => { x.done = true; x.r = 6; x.c = 105; }); st.rpeLast = 8; st.dirty = true; render();
      const showRpe = /RPE de la dernière série/.test(document.body.innerText);
      const ok = await saveRow(k); return {ok, showRpe, faite:s.faite, rpe:rpeSaved(s, s.exercices[k]), row:s.exercices[k].row}; })()""")
    check("RPE proposé sur un mouvement de compétition (modèle WEEK)", r["showRpe"], r)
    check("séance marquée faite (✓)", r["ok"] and r["faite"], r)
    check("RPE gardé dans le carnet", r["rpe"] == 8, r)
    w = pg.evaluate("window.__calls.filter(x => !/^get|^batch_get/.test(x[0]))")
    cells = [str(x) for x in w]
    check("reps et charges écrites dans les colonnes L et M de la bonne ligne", any("!L%d" % r["row"] in x for x in cells) and any("!M%d" % r["row"] in x for x in cells), cells[:6])
    vals = pg.evaluate("(r) => [__sheets['%s']['WEEK 1'] || [] , __sheets['%s']['WEEK 2'] || []].map(w => (w[r - 1] || []).slice(11, 13).join('|'))" % (COACH, COACH), r["row"])
    check("valeurs écrites : reps « 2, 2, 2 »-style et charge « 105 » dans EFFECTUE", any(re.search(r"\d(, \d)*\|105", v) for v in vals), vals)
    check("rien d'écrit dans les colonnes cibles (Reps, RPE, Charge prescrite) ni ailleurs", all(re.search(r"!(L|M)\d+", x) or "SERIES" in x for x in cells), cells[:8])
    pg.evaluate("render()"); pg.wait_for_timeout(300)
    c.close()
    # --- B : prog illisible (aucune séance reconnue) → message clair, pas de chargement infini
    INJ2 = "<script>(()=>{const b=window.__sheets['%s']; for (const k of Object.keys(b)) delete b[k]; b['BLOC 3']=[['Athlete Info']]; b['DATA']=[['x']]; })()</script>" % COACH
    def route3(r):
        u = r.request.url
        if u.endswith("/sl/") or u.endswith("index.html"):
            return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + INJ2 + "<script src='/shim.js'></script>", 1), content_type="text/html")
        return route(r)
    c = br.new_context(viewport={"width":390,"height":844}, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route3)
    pg = c.new_page(); pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    txt = pg.evaluate("document.body.innerText")
    check("prog non reconnue : message clair à la place du chargement infini", "aucune séance n'y a été reconnue" in txt and "Chargement de ta prog" not in txt, txt[:300])
    c.close(); br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
