"""v49 (basé sur v41) : 2e modèle de coach (onglets « WEEK n », jours « DAY k »), lecture seule + fin du chargement infini.
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
    # --- catalogue d'exercices : machines jamais vues dans la prog
    r = pg.evaluate("""(() => { const s = S[0]; edSess = s.key; swapMode = 'sw'; swapK = 0; const a = candidates('', exKey(s.exercices[0])).length, b = candidates('machine', '').length, c = candidates('leg ext', '').map(x => x.m);
      return {a, b, c}; })()""")
    check("sans recherche : 8 suggestions au plus", r["a"] <= 8, r)
    check("avec recherche : machines du catalogue trouvées (jamais dans la prog)", r["b"] > 8 and any("Leg extension" in x for x in r["c"]), r)
    r = pg.evaluate("""(async () => { const s = S[0]; live = null; edSess = s.key; modScope = 'd'; swapMode = 'sw'; swapK = 0; swapQ = 'leg ext'; sheet = 'swap'; renderLayer(); swapCands = candidates(swapQ, exKey(s.exercices[0]));
      const i = swapCands.findIndex(c => c.m === 'Leg extension'); await ACT.swapPick({i:String(i)}); return {now:s.exercices[0].mouvement}; })()""")
    check("choisir « Leg extension » dans le catalogue", r["now"] == "Leg extension", r)
    # --- créer un repas sans l'ajouter au journal
    pg.evaluate("setTab('corps')"); pg.wait_for_timeout(300)
    n0 = pg.evaluate("D.repas.length"); pg.evaluate("window.__calls.length = 0")
    r = pg.evaluate("""(async () => { ACT.mealNew(); mnDraft.name = 'Repas test'; mnDraft.q = 'riz'; const sug = searchFoods(parseFoodLine('riz').txt); const ok = sug.length > 0;
      ACT.mnPick({i:'0'}); mnDraft.pick.q = 150; ACT.mnAdd(); const n1 = mnDraft.items.length; await ACT.mnSave();
      return {ok, n1, saved:Object.keys(D.mesRepas || {}), tot:(D.mesRepas['Repas test'] || []).length, rep:D.repas.length}; })()""")
    check("repas créé avec ses aliments dans « Mes repas »", r["ok"] and r["n1"] == 1 and "Repas test" in r["saved"] and r["tot"] == 1, r)
    check("le repas créé n'est PAS ajouté au journal", r["rep"] == n0, r)
    calls = pg.evaluate("window.__calls.filter(x => !/^get|^batch_get/.test(x[0])).map(x => x.join(' '))")
    check("rien écrit dans REPAS (journal), seulement MES_REPAS", any("MES_REPAS" in c for c in calls) and not any(" REPAS" in c and "MES_REPAS" not in c for c in calls), calls)
    r = pg.evaluate("""(async () => { await ACT.mealAdd({n:'Repas test'}, null); return {rep:D.repas.length}; })()""")
    check("puis « + » l'ajoute au journal", r["rep"] == n0 + 1, r)
    # --- supprimer une prog importée par l'app (jamais un autre onglet)
    APPID = pg.evaluate("APP_ID")
    pg.evaluate("(a) => { window.__sheets[a]['Mon programme'] = [['Street Lifting · programme'],['x']]; window.__sheets[a]['Autre onglet'] = [['rien']]; }", APPID)
    r = pg.evaluate("""(async () => { let e1 = null; try { await Store.prog.removeTab('Autre onglet'); } catch(e){ e1 = String(e.message || e); }
      window.__req = []; let e2 = null; try { await Store.prog.removeTab('Mon programme'); } catch(e){ e2 = String(e.message || e); }
      return {e1, e2, req:(window.__req || []).map(x => Object.keys(x)[0])}; })()""")
    check("un onglet sans marqueur de l'app n'est jamais supprimé", r["e1"] and "pas été créé par l'app" in r["e1"], r)
    check("l'onglet de prog de l'app est supprimé (deleteSheet envoyé)", r["e2"] is None and "deleteSheet" in r["req"], r)
    r = pg.evaluate("""(() => { const sv = D.profil.coach_sheet_id; D.profil.coach_sheet_id = APP_ID; const keep = S.slice(); S = [{own:true, sheet:'Mon programme', archived:false}, {own:true, sheet:'Mon programme', archived:false}];
      const h = progTabsHtml(); S = keep; D.profil.coach_sheet_id = sv; return {h}; })()""")
    check("liste « Programmes ajoutés » avec bouton Supprimer et 2 séances", "Programmes ajoutés" in r["h"] and "Supprimer" in r["h"] and "2 séances" in r["h"], r["h"][:200])
    check("aucune erreur JavaScript", not errs, errs[:3])
    c.close(); br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
