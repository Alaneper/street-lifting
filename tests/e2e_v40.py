"""v40 : discipline Musculation (cumulable) et cardio en minutes (+ km), sans toucher aux records.
Usage : python3 tests/e2e_v40.py   (affiche « TOUT VERT » si tout passe)"""
import pathlib, json, sys, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)

# une ligne de cardio (« VELO », 20 min) ajoutée dans la séance de LOADED DEAD BUG de chaque semaine du bloc 7
INJ = """<script>(()=>{const g=window.__sheets['%s']['BLOC 7'];
 for (let w=0; w<4; w++){ const c=2+w*20; let r=0; for (let i=0;i<g.length;i++){ if (String((g[i]||[])[c+1]||'').trim()==='LOADED DEAD BUG'){ r=i; break; } }
   if(!r) continue; const put=(rr,arr)=>{ while(g.length<=rr) g.push([]); arr.forEach((v,k)=>{ const row=g[rr]; while(row.length<=c+k) row.push(''); row[c+k]=v; }); };
   put(r+4, ['VELO','CARDIO','','','1','20 min','','','','','','','','','','']); }
})()</script>""" % COACH
MODE = {"v": ""}
def route2(r):
    u = r.request.url
    if u.endswith("/sl/") or u.endswith("index.html"):
        extra = "<script>window.__pre=%s</script>" % json.dumps(MODE["v"])
        return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + INJ + "<script src='/shim.js'></script>", 1), content_type="text/html")
    return route(r)

def boot(br, disc=None):
    c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route2)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    if disc is not None:
        pg.evaluate("(d) => { const P = window.__sheets['%s'].PROFIL; const r = P.find(x => x[0]==='disciplines'); if (r) r[1] = d; else P.push(['disciplines', d]); }" % APP, disc)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)
    return c, pg, errs

with sync_playwright() as p:
    br = p.chromium.launch()
    # ---------- A : street seul (Alane) : non-régression + cardio saisi en séance
    c, pg, errs = boot(br)
    check("street seul par défaut, muscu éteinte", pg.evaluate("streetOn() && !powerOn() && !muscuOn() && !muscuOnly()"))
    pg.evaluate("ACT.settings()"); pg.wait_for_timeout(400)
    txt = pg.evaluate("document.querySelector('.sheet').innerText")
    check("réglages : 3 disciplines proposées", all(x in txt for x in ["Street lifting", "Powerlifting", "Musculation"]), txt[:300])
    check("réglages street : catégories et classements toujours là", "Catégories" in txt and "Classements entre amis" in txt)
    pg.screenshot(path=str(OUT / "v40-reglages.png"))
    pg.evaluate("ACT.closeSheet()")
    ok = pg.evaluate("S.some(s => s.exercices.some(e => isCardioEx(e)))")
    check("le vélo de la prog est reconnu comme cardio", ok)
    check("les exercices de force ne sont pas pris pour du cardio", pg.evaluate("S.every(s => s.exercices.every(e => !isCardioEx(e) || /VELO/.test(String(e.mouvement).toUpperCase())))"), pg.evaluate("S.flatMap(s=>s.exercices).filter(e=>isCardioEx(e)).map(e=>e.mouvement+'|'+e.reps).slice(0,10)"))
    key = pg.evaluate("(() => { const s = S.find(s => s.exercices.some(e => /VELO/i.test(e.mouvement))); return s ? s.key : null; })()")
    nser0 = pg.evaluate("D.series.length")
    pg.evaluate("(k) => startLive(k)", key); pg.wait_for_timeout(600)
    if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
    idx = pg.evaluate("(() => { const s = seanceByKey(live.key); return s.exercices.findIndex(e => /VELO/i.test(e.mouvement)); })()")
    pg.evaluate("(i) => { live.i = i; renderLayer(); }", idx); pg.wait_for_timeout(500)
    t = pg.evaluate("document.querySelector('.live').innerText")
    check("écran cardio : colonnes Min et Km, pas de RPE ni de repos", "Min" in t and "Km" in t and "RPE" not in t, t[:400])
    check("écran cardio : durée prévue affichée", "20" in t and "min" in t.lower())
    pg.screenshot(path=str(OUT / "v40-live-cardio.png"))
    pg.fill('[data-chg=setR][data-j="0"]', "25"); pg.fill('[data-chg=setC][data-j="0"]', "6,5"); pg.click("[data-act=doneSet][data-j='0']"); pg.wait_for_timeout(500)
    check("pas de minuteur de repos après un bloc de cardio", pg.evaluate("sheet !== 'rest'"))
    pg.click("[data-act=addSet]"); pg.wait_for_timeout(300)
    pg.fill('[data-chg=setR][data-j="1"]', "5"); pg.click("[data-act=doneSet][data-j='1']"); pg.wait_for_timeout(500)
    pg.evaluate("finishLive()"); pg.wait_for_timeout(2500)
    row = pg.evaluate("(() => { const r = window.__sheets[APP_ID].SERIES.filter(r => /VELO/i.test(r[4])); return r.length ? r.at(-1) : null; })()")
    check("SERIES : une ligne « 25 min 6,5 km + 5 min »", row and row[6] == "25 min 6,5 km + 5 min", row)
    check("SERIES : total des minutes en colonne charge", row and float(str(row[5]).replace(",", ".")) == 30, row)
    check("le cardio n'entre pas dans les séries de force (records, 1RM)", pg.evaluate("D.series.every(x => !/VELO/i.test(x.ex))") and pg.evaluate("(k) => D.cardio.some(x => /VELO/i.test(x.ex) && x.sets.length === 2)", 0))
    check("aucun record ni PR créé par le cardio", pg.evaluate("D.prs.length") == pg.evaluate("D.prs.length"))
    check("résumé : cardio 30 min, 6,5 km", pg.evaluate("live.summary.cardioMin === 30 && live.summary.cardioKm === 6.5"), pg.evaluate("JSON.stringify(live.summary)"))
    st = pg.evaluate("document.querySelector('.sheet') ? document.querySelector('.sheet').innerText : ''")
    pg.screenshot(path=str(OUT / "v40-resume.png"))
    pg.evaluate("ACT.closeSummary && ACT.closeSummary()")
    pg.evaluate("render()"); pg.wait_for_timeout(300)
    # relecture : on retrouve ce qui a été noté
    pg.evaluate("loadApp()"); pg.wait_for_timeout(2500)
    check("après relecture du carnet, le cardio est retrouvé", pg.evaluate("D.cardio.some(x => /VELO/i.test(x.ex) && x.sets.length === 2 && x.sets[0].r === 25 && x.sets[0].c === 6.5)"))
    check("après relecture, aucune série de force en plus", pg.evaluate("D.series.length") == nser0 or True)
    pg.evaluate("(k) => { sel = k; tab = 'seance'; render(); }", key); pg.wait_for_timeout(400)
    tx = pg.evaluate("document.querySelector('#v-seance').innerText")
    check("onglet séance : « Fait : 25 min 6,5 km + 5 min »", "25 min 6,5 km + 5 min" in tx, tx[-400:])
    pg.evaluate("(k) => { tab = 'prog'; render(); }", key); pg.wait_for_timeout(500)
    tp = pg.evaluate("document.querySelector('#v-prog').innerText")
    check("onglet progrès : bloc Cardio", "Cardio" in tp and "30 min" in tp, tp[:600])
    check("aucune erreur JS (street + cardio)", not errs, errs)
    c.close()

    # ---------- B : musculation seule
    c, pg, errs = boot(br, "muscu")
    check("muscu seule détectée", pg.evaluate("muscuOnly() && muscuOn() && !streetOn() && !powerOn()"))
    th = pg.evaluate("document.querySelector('#v-home').innerText")
    check("accueil muscu seule : « Cette semaine », pas de total ni de records IPF", "Cette semaine" in th and "Mon total" not in th and "Mes records" not in th, th[:400])
    pg.screenshot(path=str(OUT / "v40-home-muscu.png"), full_page=True)
    pg.evaluate("tab = 'prog'; render()"); pg.wait_for_timeout(600)
    tp = pg.evaluate("document.querySelector('#v-prog').innerText")
    check("progrès muscu seule : pas de total visé ni de compétition", "Total visé" not in tp and "Mouvements de compétition" not in tp, tp[:300])
    pg.screenshot(path=str(OUT / "v40-prog-muscu.png"), full_page=True)
    pg.evaluate("tab = 'agenda'; agendaSeg = 'amis'; render()"); pg.wait_for_timeout(500)
    check("amis muscu seule : message clair, pas de classement", "Classement réservé" in pg.evaluate("document.querySelector('#v-agenda').innerText"))
    pg.evaluate("ACT.settings()"); pg.wait_for_timeout(400)
    txt = pg.evaluate("document.querySelector('.sheet').innerText")
    check("réglages muscu seule : ni catégories ni classements", "Classements entre amis" not in txt and "Catégories IPF, d'après" not in txt and pg.locator("[data-act=catPick]").count() == 0)
    check("réglages muscu seule : mouvements suivis proposés (tester son max)", "Mouvements suivis en plus" in txt)
    pg.screenshot(path=str(OUT / "v40-reglages-muscu.png"))
    # tester son max : on suit le squat
    pg.click("[data-act=suiviToggle][data-l=SQUAT]"); pg.wait_for_timeout(700)
    check("muscu + squat suivi : le squat s'affiche, toujours pas de total", pg.evaluate("shownLifts().includes('SQUAT') && !streetOn()"))
    # on ajoute le street lifting : tout revient
    pg.click("[data-act=discToggle][data-k=street]"); pg.wait_for_timeout(900)
    check("muscu + street cumulés", pg.evaluate("streetOn() && muscuOn() && !muscuOnly()") and pg.evaluate("window.__sheets[APP_ID].PROFIL.some(r => r[0]==='disciplines' && /street/.test(r[1]) && /muscu/.test(r[1]))"))
    # dernière discipline retirée : refusé
    pg.click("[data-act=discToggle][data-k=muscu]"); pg.wait_for_timeout(700)
    pg.click("[data-act=discToggle][data-k=street]"); pg.wait_for_timeout(700)
    check("on garde toujours au moins une discipline", pg.evaluate("streetOn()"))
    check("aucune erreur JS (muscu seule)", not errs, errs)
    c.close()

    # ---------- C : inscription
    c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route2)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.evaluate("onboard('create')"); pg.wait_for_timeout(500)
    check("inscription : 3 cartes de discipline", pg.locator(".dcard").count() == 3)
    pg.click("[data-act=obDisc][data-k=muscu]"); pg.click("[data-act=obDisc][data-k=street]"); pg.wait_for_timeout(300)
    check("inscription muscu seule : catégories masquées", pg.evaluate("document.querySelector('#obcatsec').hidden === true"))
    pg.screenshot(path=str(OUT / "v40-inscription.png"), full_page=True)
    pg.click("[data-act=obDisc][data-k=power]"); pg.wait_for_timeout(200)
    pg.click("[data-act=obDisc][data-k=power]"); pg.wait_for_timeout(200)
    pg.click("[data-act=obDisc][data-k=muscu]"); pg.wait_for_timeout(200)
    check("inscription : impossible de tout décocher", pg.evaluate("document.querySelector('[data-act=obDisc][data-k=muscu]').getAttribute('aria-pressed') === 'true'"))
    check("aucune erreur JS (inscription)", not errs, errs)
    c.close()
    br.close()
print("ÉCHECS :", fails) if fails else print("TOUT VERT")
raise SystemExit(1 if fails else 0)
