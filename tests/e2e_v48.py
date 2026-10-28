"""v48 (basé sur v41) : 2e modèle de coach (onglets « WEEK n », jours « DAY k »), lecture seule + fin du chargement infini.
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
    pg.evaluate("S.forEach(s => { s.jour = ''; s.free = true; })"); pg.evaluate("render()"); pg.wait_for_timeout(300)
    check("séance libre : pas de date inventée (lundi)", pg.evaluate("S.every(s => dateOf(s) === null)"))
    pg.evaluate("setTab('home')"); pg.wait_for_timeout(300)
    check("accueil libre : cases de la semaine et pas de liste datée", pg.locator(".fcell").count() >= 2 and "Aucune séance datée" not in pg.evaluate("document.body.innerText"), pg.locator(".fcell").count())
    check("bouton « Faire une autre séance »", "Faire une autre séance" in pg.evaluate("document.body.innerText"))
    # --- séance en direct : changer l'exercice 2 pour un exercice écrit
    key = pg.evaluate("S[0].key"); pg.evaluate("(k) => startLive(k)", key); pg.wait_for_timeout(500)
    check("boutons « Changer l'exercice » et « Modifier la séance » en séance", "Changer l'exercice" in pg.evaluate("document.body.innerText") and "Modifier la séance" in pg.evaluate("document.body.innerText"))
    n0 = pg.evaluate("S[0].exercices.length")
    pg.evaluate("window.__calls.length = 0")
    r = pg.evaluate("""(async () => { live.i = 1; ACT.swapOpen(); swapQ = 'Hack squat'; modScope = 'd'; const s = S[0]; const old = s.exercices[1].mouvement;
      await ACT.swapPick({i:'free'}); const e = s.exercices[1];
      return {old, now:e.mouvement, mod:!!e._mod, n:s.exercices.length, rows:Object.keys(live.rows).length, modifs:D.profil.modifs, sheet:sheet}; })()""")
    check("exercice 2 remplacé par « Hack squat », même nombre d'exercices", r["now"] == "Hack squat" and r["mod"] and r["n"] == n0 and r["rows"] == n0, r)
    check("changement noté dans le carnet (PROFIL › modifs), séance concernée seule", '"sc":"d"' in r["modifs"] and "Hack squat" in r["modifs"], r["modifs"])
    # valider une série sur l'exercice changé : rien ne part vers le Sheet du coach
    pg.evaluate("window.__calls.length = 0")
    r2 = pg.evaluate("""(async () => { const s = S[0]; live.i = 1; const st = live.rows[1]; st.sets.forEach(x => { x.done = true; x.r = 10; x.c = 80; }); st.dirty = true; const ok = await saveRow(1); return {ok}; })()""")
    calls = pg.evaluate("window.__calls.filter(x => !/^get|^batch_get/.test(x[0])).map(x => x.join(' '))")
    check("série du nouvel exercice enregistrée dans le carnet", any("SERIES" in c for c in calls), calls)
    check("rien écrit dans l'onglet WEEK pour l'exercice changé", not any("WEEK" in c for c in calls), calls)
    check("séries gardées sous le nom du nouvel exercice", pg.evaluate("D.series.some(x => x.ex.startsWith('HACK SQUAT'))"))
    # dernière fois proposée : un exercice déjà fait ailleurs
    pg.evaluate("D.series.push({id:999, date:'2026-10-10', bloc:3, semaine:'9', seance:'Autre', ex:'CURL HALTÈRES', charge:14, sets:[{r:12,c:14},{r:12,c:14},{r:12,c:14}], note:''})")
    r3 = pg.evaluate("""(async () => { const s = S[0]; swapMode = 'ad'; edSess = s.key; modScope = 'd'; swapQ = 'Curl haltères'; sheet = 'swap'; renderLayer();
      document.querySelector('#adse').value = '4'; document.querySelector('#adre').value = '12';
      await ACT.swapPick({i:'free'}); const e = s.exercices.at(-1); const k = s.exercices.length - 1;
      return {n:s.exercices.length, nom:e.mouvement, se:e.series, re:e.reps, c:live.rows[k].sets[0].c, r:live.rows[k].sets[0].r}; })()""")
    check("ajout « Curl haltères » 4 × 12 avec sa dernière charge (14 kg)", r3["n"] == n0 + 1 and r3["se"] == "4" and r3["re"] == "12" and r3["c"] == 14, r3)
    r4 = pg.evaluate("""(async () => { const s = S[0]; const a = s.exercices.map(e => e.mouvement); await ACT.edMove({k:'0', d:'1'}); const b = s.exercices.map(e => e.mouvement);
      return {a, b}; })()""")
    check("réordonner : les deux premiers échangent leur place", r4["b"][0] == r4["a"][1] and r4["b"][1] == r4["a"][0], r4)
    r5 = pg.evaluate("""(async () => { const s = S[0]; const n = s.exercices.length; const k = s.exercices.length - 1; live.rows[k].sets.forEach(x => x.done = false); await ACT.edRm({k:String(k)}); return {n, m:s.exercices.length}; })()""")
    check("retirer un exercice", r5["m"] == r5["n"] - 1, r5)
    # portée « pour la suite » : la semaine 2 suit
    r6 = pg.evaluate("""(async () => { live = null; store.set('sl4-live', null); const s1 = S.find(z => z.semaine === '1' && z.idx === 1), s2 = S.find(z => z.semaine === '2' && z.idx === 1);
      edSess = s1.key; modScope = 's'; swapMode = 'sw'; swapK = 0; swapQ = 'Squat barre'; sheet = 'swap'; const old2 = s2.exercices[0].mouvement;
      await ACT.swapPick({i:'free'}); return {old2, now2:s2.exercices[0].mouvement, now1:s1.exercices[0].mouvement}; })()""")
    check("« Pour la suite » : la semaine 2 prend aussi le changement", r6["now1"] == "Squat barre" and r6["now2"] == "Squat barre", r6)
    # le programme du coach n'a jamais été modifié
    wr = pg.evaluate("window.__calls.filter(x => !/^get|^batch_get/.test(x[0]) && /WEEK|BLOC 3/.test(String(x[1]||''))).length")
    check("aucune écriture sur le Sheet du coach pendant les modifications", wr == 0, wr)
    # rechargement : les changements sont relus depuis le carnet
    pg.evaluate("S.forEach(s => { s.exercices = s.base; })"); pg.evaluate("applyAllMods()")
    check("changements réappliqués depuis le carnet", pg.evaluate("S.find(z => z.semaine === '2' && z.idx === 1).exercices[0].mouvement") == "Squat barre")
    check("aucune erreur JavaScript", not errs, errs[:3])
    import os
    S_OUT = pathlib.Path(os.environ.get("SHOTS", "/tmp")); 
    pg.evaluate("live = null; sheet = null; renderLayer(); setTab('home')"); pg.wait_for_timeout(400); pg.screenshot(path=str(S_OUT / "v48-accueil.png"))
    pg.evaluate("(k) => startLive(k)", pg.evaluate("S[0].key")); pg.wait_for_timeout(300); pg.evaluate("swapMode='sw'; swapK=0; swapQ=''; edSess=live.key; swapFrom=null; openSheet('swap')"); pg.wait_for_timeout(400); pg.screenshot(path=str(S_OUT / "v48-echange.png"))
    pg.evaluate("swapFrom='edit'; openSheet('edit')"); pg.wait_for_timeout(400); pg.screenshot(path=str(S_OUT / "v48-modifier.png"))
    c.close(); br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
