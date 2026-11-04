"""Retours testeur C — charges : (a) réglage actif, séquence curl 20→22 kg et squat 120→135 kg ; (b) réglage désactivé ; (c) Sheet de coach (modèle « WEEK ») : cibles intactes ;
(d) case modifiée entre-temps : rien d'écrasé ; (e) hors connexion puis reconnexion : écrit une seule fois. Rejoue avec : python3 tests/e2e_v86_charges_frere.py"""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)

PRESC = {"curl": ["RENFO", "CURL BICEPS", "20", None], "squat": ["SQUAT", "COMP", "120", "1"]}
DONE = {"curl": {"1": [[20, 13]], "2": [[22, 10], [22, 10]], "3": [[22, 10], [22, 10]]}, "squat": {"1": [[120, 3]], "2": [[125, 3]], "3": [[130, 3]], "4": [[135, 3]]}}
SET_PRESC = """([coach, defs]) => { for (const [tab, g] of Object.entries(window.__sheets[coach])) { if (!/^BLOC/.test(tab)) continue;
  g.forEach(r => { for (let c = 2; c < r.length; c += 20) for (const [m, v, p, ser] of defs) if (String(r[c]).trim() === m && String(r[c + 1]).toUpperCase().trim() === v && String(r[c + 5]).length && (ser === null || String(r[c + 4]) === ser)) r[c + 8] = p; }); } }"""
PLAY = """async ([w, plan, sync]) => {   // plan = {curl:[[c,r],…], squat:[…]} ; ouvre la séance 1 de la semaine w, relève ce que l'app propose, puis note ce qui a été fait
  const z = S.find(s => !s.archived && s.bloc === 1 && s.semaine === w && s.idx === 0); live = null; store.set('sl4-live', null);
  const idx = {curl: z.exercices.findIndex(e => String(e.variation).toUpperCase().trim() === 'CURL BICEPS'), squat: z.exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === 'SQUAT' && String(e.variation).toUpperCase().trim() === 'COMP' && String(e.series) === '1')};
  await startLive(z.key); const out = {};
  for (const n of Object.keys(plan)) { const k = idx[n], st = live.rows[k], e = z.exercices[k]; out[n] = {propose: st.sets.map(x => x.c), prescrit: e.charge, k};
    window.__k = window.__k || {}; window.__k[n] = k; }
  window.__z = z.key; window.__live = true;
  for (const n of Object.keys(plan)) { const k = idx[n], st = live.rows[k]; st.sets = plan[n].map(d => ({c:d[0], r:d[1], done:true})); st.dirty = true; await saveRow(k); }
  live = null; store.set('sl4-live', null); return out; }"""
SNAP = "() => JSON.stringify(window.__sheets['%s'])" % COACH
DIFF = """([before]) => { const a = JSON.parse(before), b = window.__sheets['%s'], out = [];
  for (const tab of Object.keys(b)) { const ga = a[tab] || [], gb = b[tab]; const R = Math.max(ga.length, gb.length);
    for (let r = 0; r < R; r++) { const ra = ga[r] || [], rb = gb[r] || [], C = Math.max(ra.length, rb.length);
      for (let c = 0; c < C; c++) if (String(ra[c] ?? '') !== String(rb[c] ?? '')) out.push([tab, r, c, String(ra[c] ?? ''), String(rb[c] ?? '')]); } } return out; }""" % COACH

def start(br, sync, tabs_js=None, week_model=False):
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels")
    c.route("**/*", route); pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("window.__down = localStorage.getItem('__down') === '1'")
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(800); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.evaluate(SET_PRESC, [COACH, [[m, v, p, s] for m, v, p, s in PRESC.values()]])
    if sync: pg.evaluate("([k, id]) => localStorage.setItem(k, JSON.stringify({[id]: true}))", ["sl4-chargesync", COACH])
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    return c, pg, errs

def sequence(pg):
    """4 semaines : renvoie ce que l'app propose chaque semaine."""
    res = {}
    for w in ["1", "2", "3", "4"]:
        plan = {n: DONE[n][w] for n in DONE if w in DONE[n]}
        res[w] = pg.evaluate(PLAY, [w, plan, True])
    return res

def charge_cols(diff):   # colonne « Charge » d'un bloc de semaine : c = 10, 30, 50, 70
    return [d for d in diff if (d[2] - 10) % 20 == 0]

with sync_playwright() as p:
    br = p.chromium.launch()
    # ---------------------------------------------------------------- (a) réglage actif
    c, pg, errs = start(br, True); ev = pg.evaluate
    snap = ev(SNAP); res = sequence(pg)
    prop = lambda n, w: res[w][n]["propose"]
    check("(a) curl : propose 20 (sem. 1), 20 (sem. 2, dernière faite = 20), 22 (sem. 3)", prop("curl", "1") == [20]*3 and prop("curl", "2") == [20]*3 and prop("curl", "3") == [22]*3, [prop("curl", w) for w in "123"])
    check("(a) squat : propose 120, 120, 125, 130 (la dernière charge faite, plus la prescription 120)", [prop("squat", w) for w in "1234"] == [[120], [120], [125], [130]], [prop("squat", w) for w in "1234"])
    check("(a) la prescription lue dans le Sheet est toujours 20 / 120 avant la séance (jamais modifiée d'avance)", res["3"]["curl"]["prescrit"] == "20" and res["4"]["squat"]["prescrit"] == "120", (res["3"]["curl"]["prescrit"], res["4"]["squat"]["prescrit"]))
    d = ev(DIFF, [snap]); cc = charge_cols(d)
    got = sorted((x[1], x[2], x[4]) for x in cc)
    # curl : ligne 34 (index 33) ; squat comp : ligne 30 (index 29) ; colonnes de charge : semaine w → 10 + 20 (w-1)
    exp = sorted([(33, 30, "22"), (33, 50, "22"), (29, 30, "125"), (29, 50, "130"), (29, 70, "135")])
    check("(a) colonne « Charge » : seules les cases des semaines faites ont changé (curl S2 S3, squat S2 S3 S4), avec la charge faite", got == exp, got)
    check("(a) jamais dans les semaines suivantes ni les autres blocs (aucune case Charge hors des 5 attendues)", len(cc) == 5, len(cc))
    check("(a) la case de la semaine 1 (charge faite = prescrite) n'est pas réécrite", not any(x[1] in (33, 29) and x[2] == 10 for x in cc), cc)
    src_rows = ev("window.__sheets['%s'].SERIES.slice(1).map(r => [r[2], r[4], r[5], r[7]])" % APP)
    cm = [r for r in src_rows if "Charge du Sheet" in r[3]]
    check("(a) le carnet garde la valeur remplacée (« Charge du Sheet 20 → 22 », « 120 → 135 »)", any(r[1].endswith("CURL BICEPS") and "20 → 22" in r[3] for r in cm) and any(r[1].startswith("SQUAT") and "120 → 135" in r[3] for r in cm), cm)
    check("(a) la semaine 1 n'a pas de mention (rien remplacé)", not any(r[0] == "1" and "Charge du Sheet" in r[3] for r in src_rows), src_rows[:3])
    # annuler
    ev("openSheet('settings')"); pg.wait_for_timeout(500)
    check("(a) Réglages : réglage affiché activé", pg.locator("#csync[aria-checked=true]").count() == 1)
    n_undo = pg.locator("[data-act=chargeUndo]").count(); check("(a) Réglages : un bouton Annuler par charge mise à jour (5)", n_undo == 4 or n_undo == 5, n_undo)
    pg.locator("[data-act=chargeUndo]").first.click(); pg.wait_for_timeout(1200)
    cell = ev("window.__sheets['%s']['BLOC 1  '][29][70]" % COACH)
    check("(a) Annuler remet la charge d'avant (squat S4 : 135 → 120)", cell == "120", cell)
    check("(a) aucune erreur JS", not errs, errs); c.close()

    # ---------------------------------------------------------------- (b) réglage désactivé
    c, pg, errs = start(br, False); ev = pg.evaluate
    snap = ev(SNAP); res = sequence(pg)
    d = ev(DIFF, [snap]); cc = charge_cols(d)
    check("(b) réglage désactivé : rien n'est écrit dans la colonne « Charge »", not cc, cc)
    check("(b) la dernière charge faite reste proposée (curl sem. 3 = 22, squat sem. 4 = 130)", res["3"]["curl"]["propose"] == [22]*3 and res["4"]["squat"]["propose"] == [130], (res["3"]["curl"]["propose"], res["4"]["squat"]["propose"]))
    src_rows = ev("window.__sheets['%s'].SERIES.slice(1).map(r => r[7])" % APP)
    check("(b) le carnet ne mentionne aucune charge du Sheet", not any("Charge du Sheet" in str(r) for r in src_rows), src_rows)
    ev("openSheet('settings')"); pg.wait_for_timeout(500)
    check("(b) Réglages : réglage désactivé par défaut", pg.locator("#csync[aria-checked=false]").count() == 1)
    check("(b) le libellé demandé est affiché", "Mon Sheet est ma prog personnelle : mettre à jour la charge avec ce que j'ai fait" in pg.inner_text("#csync"), pg.inner_text("#csync")[:120])
    pg.click("#csync"); pg.wait_for_timeout(300)
    check("(b) le réglage s'active d'un toucher", ev("JSON.parse(localStorage.getItem('sl4-chargesync') || '{}')['%s']" % COACH) is True)
    check("(b) aucune erreur JS", not errs, errs); c.close()

    # ---------------------------------------------------------------- (d) case modifiée entre-temps
    c, pg, errs = start(br, True); ev = pg.evaluate
    snap = ev(SNAP)
    ev("""async () => { const z = S.find(s => !s.archived && s.bloc === 1 && s.semaine === '2' && s.idx === 0); live = null; store.set('sl4-live', null); await startLive(z.key); window.__zk = z.key; }""")
    ev("window.__sheets['%s']['BLOC 1  '][33][30] = '18'" % COACH)   # quelqu'un (ou le testeur à la main) change la case depuis la lecture
    ev("""async () => { const z = seanceByKey(window.__zk), k = z.exercices.findIndex(e => String(e.variation).toUpperCase().trim() === 'CURL BICEPS'), st = live.rows[k]; st.sets = [[22,10],[22,10]].map(d => ({c:d[0], r:d[1], done:true})); st.dirty = true; await saveRow(k); }""")
    cell = ev("window.__sheets['%s']['BLOC 1  '][33][30]" % COACH)
    check("(d) case modifiée entre-temps : rien d'écrasé (reste 18)", cell == "18", cell)
    check("(d) le testeur est prévenu", "a changé" in ev("document.querySelector('#toast').textContent") or ev("chargeLog()[0].st") == "conflict", ev("document.querySelector('#toast').textContent"))
    check("(d) le journal garde le conflit", ev("chargeLog()[0].st") == "conflict" and ev("chargeLog()[0].now") == "18", ev("JSON.stringify(chargeLog()[0])"))
    row = ev("window.__sheets['%s'].SERIES.slice(-1)[0]" % APP)
    check("(d) la série faite est quand même dans le carnet, sans mention de charge remplacée", row[5] == "22" and "Charge du Sheet" not in row[7], row)
    # variante : formule
    ev("window.__sheets['%s']['BLOC 1  '][33][50] = '=AE34'" % COACH)
    ev("""async () => { const z = S.find(s => !s.archived && s.bloc === 1 && s.semaine === '3' && s.idx === 0); live = null; store.set('sl4-live', null); await startLive(z.key); const k = z.exercices.findIndex(e => String(e.variation).toUpperCase().trim() === 'CURL BICEPS'), st = live.rows[k]; st.sets = [[22,10],[22,10]].map(d => ({c:d[0], r:d[1], done:true})); st.dirty = true; await saveRow(k); }""")
    cell = ev("window.__sheets['%s']['BLOC 1  '][33][50]" % COACH)
    check("(d) une formule dans la case n'est jamais remplacée", cell == "=AE34", cell)
    check("(d) aucune erreur JS", not errs, errs); c.close()

    # ---------------------------------------------------------------- (e) hors connexion puis reconnexion
    c, pg, errs = start(br, True); ev = pg.evaluate
    ev("""async () => { const z = S.find(s => !s.archived && s.bloc === 1 && s.semaine === '2' && s.idx === 0); live = null; store.set('sl4-live', null); await startLive(z.key); window.__zk = z.key; }""")
    ev("window.__down = true; window.__calls.length = 0")
    ev("""async () => { const z = seanceByKey(window.__zk), k = z.exercices.findIndex(e => String(e.variation).toUpperCase().trim() === 'CURL BICEPS'), st = live.rows[k]; st.sets = [[22,10],[22,10]].map(d => ({c:d[0], r:d[1], done:true})); st.dirty = true; await saveRow(k); }""")
    pend = ev("Store.pending()"); cell = ev("window.__sheets['%s']['BLOC 1  '][33][30]" % COACH)
    check("(e) hors connexion : la charge attend dans la file, la case n'a pas bougé", pend >= 1 and cell == "20", (pend, cell))
    check("(e) hors connexion : le journal marque « en attente »", ev("chargeLog()[0].st") == "queued", ev("JSON.stringify(chargeLog()[0])"))
    ev("window.__down = false; window.__calls.length = 0")
    ev("flushOutbox()"); pg.wait_for_timeout(5000)
    ev("flushOutbox()"); pg.wait_for_timeout(1500)
    cell = ev("window.__sheets['%s']['BLOC 1  '][33][30]" % COACH)
    writes = ev("window.__calls.filter(c => c[0] === 'update_values' && String(c[1]).indexOf('AE34') >= 0).length")
    check("(e) reconnexion : la charge est écrite (22) dans la case de la semaine 2", cell == "22", cell)
    check("(e) reconnexion : écrite une seule fois, même après un second envoi", writes == 1, writes)
    check("(e) le journal passe à « ok » avec la valeur remplacée", ev("chargeLog()[0].st") == "ok" and ev("chargeLog()[0].old") == "20", ev("JSON.stringify(chargeLog()[0])"))
    check("(e) plus rien en attente", ev("Store.pending()") == 0)
    check("(e) aucune erreur JS", not errs, errs); c.close()
    br.close()

# ---------------------------------------------------------------- (c) Sheet de coach au modèle « WEEK » : les cibles ne bougent jamais, même réglage actif
import re
src41 = (H / "e2e_v41.py").read_text()
i0 = src41.index("def day("); pre = src41[i0:src41.index("with sync_playwright()", i0)]
exec(pre)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route2)
    pg = c.new_page(); errs = []; ev = pg.evaluate
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    ev("([k, id]) => localStorage.setItem(k, JSON.stringify({[id]: true}))", ["sl4-chargesync", COACH])
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    ev("ensureAllBlocs()"); pg.wait_for_timeout(2500)
    snap = ev(SNAP)
    ev("""async () => { const z = S.find(s => s.week && !s.archived && s.semaine === '1' && s.idx === 0 || s.week); live = null; store.set('sl4-live', null); await startLive(z.key);
      const k = z.exercices.findIndex(e => /SUMO/i.test(e.mouvement)), st = live.rows[k]; st.sets = [[110,6],[110,6],[110,6]].map(d => ({c:d[0], r:d[1], done:true})); st.dirty = true; await saveRow(k); window.__w = z.week + '|' + (z.cols.charge === undefined); }""")
    d = ev(DIFF, [snap])
    check("(c) Sheet de coach : une charge faite a bien été notée (cases « faites »)", len(d) >= 1, d)
    chargesDone = ev("S.find(s => s.week).cols.chargesDone"); repsDone = ev("S.find(s => s.week).cols.repsDone"); comm = ev("S.find(s => s.week).cols.commentaire")
    allowed = {x - 1 for x in (chargesDone, repsDone, comm) if x}
    check("(c) Sheet de coach : seules les colonnes « faites » (reps, charges, commentaire) ont changé", all(x[2] in allowed for x in d), [x for x in d if x[2] not in allowed])
    check("(c) Sheet de coach : le modèle n'expose aucune colonne « Charge » à écrire, même réglage actif", ev("window.__w") == "true|true", ev("window.__w"))
    check("(c) aucune erreur JS", not errs, errs); c.close(); br.close()

print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
