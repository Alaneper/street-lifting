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
    pg = c.new_page(); pg.add_init_script("window.__down = localStorage.getItem('__down') === '1'"); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)

    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(500)
    APPID = pg.evaluate("APP_ID")
    sess = """const s = S.find(z => z.jour === 'Mardi'); live = null; startLive(s.key); const k = s.exercices.findIndex(e => /COMP Bench/i.test(e.mouvement)); live.i = k; const st = live.rows[k];"""
    sheet = lambda t: pg.evaluate("(a, t) => (window.__sheets[a][t] || []).map(r => r.join('|'))", [APPID, t]) if False else pg.evaluate("([a, t]) => (window.__sheets[a][t] || []).map(r => r.join('|'))", [APPID, t])
    # --- 1. coupure réseau pendant la séance
    pg.evaluate("window.__down = true; window.__calls.length = 0")
    r = pg.evaluate("(async () => { " + sess + """ st.sets.forEach(x => { x.done = true; x.r = 5; x.c = 100; }); st.rpeLast = 8; st.dirty = true;
      const ok = await saveRow(k); return {ok, faite:s.faite, n:Store.pending(), ls:JSON.parse(localStorage.getItem('sl4-outbox') || '[]').length, loc:D.series.filter(x => x.ex === exKey(s.exercices[k])).length, dot:document.getElementById('syncdot').className, row:s.exercices[k].row}; })()""")
    check("hors connexion : la série est enregistrée sans erreur (ok + ✓)", r["ok"] and r["faite"], r)
    check("actions gardées en file ET sur le téléphone", r["n"] >= 2 and r["ls"] == r["n"], r)
    check("la série est déjà visible dans l'app", r["loc"] == 1, r)
    check("pastille rouge « en attente »", "off" in r["dot"], r)
    r2 = pg.evaluate("(async () => { " + sess + """ st.sets.forEach(x => { x.done = true; x.r = 6; x.c = 105; }); st.dirty = true; await saveRow(k);
      const adds = JSON.parse(localStorage.getItem('sl4-outbox')).filter(o => o.t === 'add' && o.tab === 'SERIES'); return {n:Store.pending(), adds:adds.length, txt:adds[0] && adds[0].rows[0][6]}; })()""")
    check("2e enregistrement hors ligne : UNE seule ligne « SERIES » en attente, à jour", r2["adds"] == 1 and "6" in str(r2["txt"]), r2)
    # --- 2. les autres écritures, toutes hors connexion
    r3 = pg.evaluate("""(async () => { const d = D.today;
      await Store.poids.add([[d, 71.3, 'test']]);
      const a = await Store.repas.add([[d, '12:30', 'Riz test', 'ciqual', '1', 150, 200, 4, 40, 1]]);
      const b = await Store.repas.add([[d, '19:00', 'Pâtes test', 'ciqual', '2', 200, 300, 10, 60, 2]]);
      await Store.repas.remove(b);                                   /* ajouté puis supprimé sans réseau : jamais envoyé */
      await Store.prs.add([d, 'SQUAT', 150, 1, 'test', '', '']);
      await Store.profil.set('pays', 'FR'); await Store.objectifs.set('SQUAT', 180, 'test');
      const c = await Store.competitions.add(['2026-12-01', 'Compet test', 'Liège', '', '']);
      await Store.competitions.update(c, ['2026-12-02', 'Compet test', 'Liège', '', '']);   /* modifiée avant envoi */
      await Store.checklist.add([[d, 'Item test', 'FALSE']]);
      await Store.bilan.add([d, 3, '1', 3, 3, 3, 3, 3, 3]);
      await Store.aliments.add(['Nutella test', 'Ferrero', 'off', '3017620422003', 539, 6.3, 57.5, 30.9, '']);
      return {n:Store.pending(), a, b, c}; })()""")
    check("poids, repas, record, réglage, objectif, compétition, checklist, bilan, produit : tous acceptés sans réseau", r3["n"] >= 10, r3)
    check("numéros provisoires négatifs pour les lignes ajoutées sans réseau", r3["a"] < 0 and r3["b"] < 0 and r3["c"] < 0, r3)
    # --- 3. l'app s'ouvre hors connexion avec les actions en attente
    pg.evaluate("saveCache(); localStorage.setItem('__down', '1')"); n_pend = pg.evaluate("Store.pending()")
    pg.reload(); pg.wait_for_timeout(3500)
    r4 = pg.evaluate("({pend:Store.pending(), D:!!D, body:document.body.innerText.length, fatal:/Pas de réseau, et rien/.test(document.body.innerText)})")
    check("page rouverte SANS réseau : app affichée, actions toujours en attente", r4["pend"] == n_pend and r4["D"] and not r4["fatal"], r4)
    # --- 4. retour du réseau
    pg.evaluate("localStorage.removeItem('__down'); window.__down = false; window.__calls.length = 0")
    pg.evaluate("flushOutbox()"); pg.wait_for_timeout(5000)
    check("retour du réseau : la file se vide", pg.evaluate("Store.pending()") == 0, pg.evaluate("Store.pending()"))
    check("poids écrit", any("71" in x for x in sheet("POIDS")), sheet("POIDS")[-2:])
    rp = sheet("REPAS"); check("repas écrit une fois, et le repas supprimé avant envoi n'est jamais écrit", sum("Riz test" in x for x in rp) == 1 and not any("Pâtes test" in x for x in rp), rp[-3:])
    check("record (PR) écrit", any("150" in x and "SQUAT" in x.upper() for x in sheet("PR")), sheet("PR")[-2:])
    check("réglage et objectif écrits", any(x.startswith("pays|FR") for x in sheet("PROFIL")) and any("180" in x for x in sheet("OBJECTIFS")), [sheet("PROFIL")[-3:], sheet("OBJECTIFS")[-2:]])
    co = sheet("COMPETITIONS"); check("compétition écrite une fois, avec la date corrigée", sum("Compet test" in x for x in co) == 1 and any("2026-12-02" in x for x in co), co)
    check("checklist, bilan et produit (Nutella) écrits", any("Item test" in x for x in sheet("CHECKLIST")) and len(sheet("BILAN")) >= 2 and any("Nutella test" in x for x in sheet("ALIMENTS")), "")
    se = [x for x in sheet("SERIES") if re.search("bench", x, re.I)]
    check("série écrite UNE fois, dernière version (6 × 105)", len(se) == 1 and "105" in se[0], se)
    w = pg.evaluate("(r) => [__sheets['%s']['WEEK 1'] || [] , __sheets['%s']['WEEK 2'] || []].map(w => (w[r - 1] || []).slice(11, 13).join('|'))" % (COACH, COACH), r["row"])
    check("cases EFFECTUE du coach remplies", any("105" in v for v in w), w)
    pg.evaluate("(async () => { live = null; await loadApp(); })()"); pg.wait_for_timeout(1500)
    check("plus de numéros provisoires dans l'app après rafraîchissement", pg.evaluate("D.repas.every(x => x.id > 0) && D.series.every(x => x.id > 0) && Object.keys(JSON.parse(localStorage.getItem('sl4-idmap') || '{}')).length === 0"), "")
    # --- 5. reprise de séance : on modifie une série déjà envoyée, hors connexion, puis on renvoie
    pg.evaluate("window.__down = true")
    pg.evaluate("(async () => { " + sess + """ st.sets.forEach(x => { x.done = true; x.r = 7; x.c = 110; }); st.dirty = true; await saveRow(k); })()"""); pg.wait_for_timeout(500)
    pg.evaluate("window.__down = false"); pg.evaluate("flushOutbox()"); pg.wait_for_timeout(4000)
    se = [x for x in sheet("SERIES") if re.search("bench", x, re.I)]
    check("modification après envoi : même ligne mise à jour (110), pas de doublon", len(se) == 1 and "110" in se[0], se)
    # --- 6. réseau qui ne répond jamais : au bout de 20 s on bascule hors connexion au lieu de bloquer l'écran
    import time; t0 = time.time(); pg.evaluate("window.__hang = true")
    r6 = pg.evaluate("(async () => { await Store.poids.add([[D.today, 69.9, 'lent']]); return Store.pending(); })()")
    dt = time.time() - t0; pg.evaluate("window.__hang = false")
    check("réseau muet : après ~20 s la pesée est mise en file, sans bloquer", r6 >= 1 and 15 < dt < 40, (r6, round(dt)))
    pg.evaluate("flushOutbox()"); pg.wait_for_timeout(3000)
    check("puis envoyée au retour du réseau", pg.evaluate("Store.pending()") == 0 and any("69" in x for x in sheet("POIDS")), pg.evaluate("Store.pending()"))
    check("aucune erreur JavaScript", not errs, errs[:3])
    c.close(); br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
