"""v28 : mode powerlifting (disciplines, Bench/Deadlift, IPF GL), catégories auto/manuelles, âges IPF, classements séparés, inscription (maquette A).
Usage : python3 tests/e2e_v28.py   (affiche « ÉCHECS : [] » si tout passe)"""
import pathlib, json, sys, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)

# prog du coach : une ligne BENCH et une ligne DEADLIFT ajoutées dans la séance 1 de chaque semaine du bloc 7 (format ATS)
INJ = """<script>(()=>{const g=window.__sheets['%s']['BLOC 7'];
 for (let w=0; w<4; w++){ const c=2+w*20; let r=0; for (let i=0;i<g.length;i++){ if (String((g[i]||[])[c+1]||'').trim()==='LOADED DEAD BUG'){ r=i; break; } }
   if(!r) continue; const put=(rr,arr)=>{ while(g.length<=rr) g.push([]); arr.forEach((v,k)=>{ const row=g[rr]; while(row.length<=c+k) row.push(''); row[c+k]=v; }); };
   put(r+4, ['BENCH','COMP','','','3','3','3-5\\'','','100','','','','8','8,5','','']);
   put(r+5, ['DEADLIFT','COMP','','','2','3','3-5\\'','','180','','','','8','','','']); }
})()</script>""" % COACH
CLROWS = [
  {"nom":"Alane","pays":"BE","sexe":"M","cat":-80,"MU":None,"PULL":40,"DIP":60,"SQUAT":110,"total":210,"ris":300.1,"disc":"street,power","BENCH":100,"DEADLIFT":200,"SQUATP":110,"totalp":410,"gl":60.12,"mode":"classic","catp":-83,"age":"JR,OPEN","vs":True,"vp":True,"me":True},
  {"nom":"Bruno","pays":"FR","sexe":"M","cat":-87,"PULL":50,"DIP":70,"SQUAT":150,"total":270,"ris":350.2,"disc":"street","vs":True,"vp":False},
  {"nom":"Clara","pays":"BE","sexe":"F","cat":-63,"disc":"power","BENCH":80,"DEADLIFT":160,"SQUATP":130,"totalp":370,"gl":82.5,"mode":"classic","catp":-63,"age":"OPEN","vs":False,"vp":True},
  {"nom":"Dimitri","pays":"BE","sexe":"M","cat":-93,"disc":"power","BENCH":150,"DEADLIFT":280,"SQUATP":240,"totalp":670,"gl":91.0,"mode":"equipped","catp":-93,"age":"M1,OPEN","vs":False,"vp":True},
]
posted = []
def route2(r):
    u = r.request.url
    if u.endswith("/sl/") or u.endswith("index.html"):
        return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + INJ + "<script src='/shim.js'></script>", 1), content_type="text/html")
    if "script.google.com/macros" in u:
        if r.request.method == "POST": posted.append(r.request.post_data or "")
        return r.fulfill(body=json.dumps({"rows":CLROWS}), content_type="application/json", headers={"Access-Control-Allow-Origin":"*"})
    return route(r)

with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route2)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)

    # 1. Carnet d'avant la v28 : street lifting seul, catégorie gardée telle quelle, muscle-up affiché
    check("street seul par défaut", pg.evaluate("streetOn() && !powerOn()"))
    check("catégorie street inchangée (−80, à la main)", pg.evaluate("cat() === -80 && !catAutoOn('categorie')"))
    check("muscle-up dans les records de l'accueil", "Muscle-up" in pg.evaluate("document.querySelector('#v-home').innerText"))
    check("Bench non reconnu en street seul", pg.evaluate("liftOf('BENCH') === null && liftOf('DEADLIFT') === null"))
    pg.evaluate("ACT.settings()"); pg.wait_for_timeout(400)
    txt = pg.evaluate("document.querySelector('.sheet').innerText")
    check("réglages : disciplines, catégories, classements", all(x in txt for x in ["Tes disciplines", "Catégories", "Classements entre amis"]), txt[:200])
    check("réglages : plus de « muscle-up acquis »", "acquis" not in txt)
    pg.screenshot(path=str(OUT / "v28-reglages-street.png"))

    # 2. Ajout du powerlifting
    pg.click("[data-act=discToggle][data-k=power]"); pg.wait_for_timeout(800)
    check("PROFIL : disciplines = street,power", pg.evaluate("window.__sheets[APP_ID].PROFIL.some(r => r[0]==='disciplines' && r[1]==='street,power')"))
    check("Bench reconnu dans la prog", pg.evaluate("liftOf('BENCH') === 'BENCH' && liftOf('DEADLIFT') === 'DEADLIFT' && liftOf('ROMANIAN DEADLIFT') === null && liftOf('INCLINE DB BENCH PRESS') === null"))
    check("Bench : records de la prog (3 reps à 100 kg)", pg.evaluate("repMaxes(compSets('BENCH')).some(x => x.n === 3 && x.b && x.b.c === 100)"), pg.evaluate("JSON.stringify(repMaxes(compSets('BENCH')).filter(x=>x.b).map(x=>[x.n,x.b.c]))"))
    check("catégorie IPF auto d'après la pesée", pg.evaluate("catIpf() === catAuto(bw(), catsIpfFor('H', myAges().some(a=>a==='SJ'||a==='JR')))"), pg.evaluate("[catIpf(), bw()]"))
    pg.screenshot(path=str(OUT / "v28-reglages-power.png"), full_page=False)
    pg.evaluate("ACT.closeSheet()")

    # 3. PR Bench et Deadlift, total power et IPF GL
    pg.evaluate("addPR('BENCH', 100, 1, D.today, 'test', null)"); pg.wait_for_timeout(500)
    pg.evaluate("addPR('DEADLIFT', 190, 1, D.today, 'test', null)"); pg.wait_for_timeout(500)
    tp = pg.evaluate("totalPower()"); sq = pg.evaluate("best('SQUAT')")
    check("total power = squat + bench + deadlift", tp == sq + 290, [tp, sq])
    gl = pg.evaluate("glOf(totalPower(), bw())"); w = pg.evaluate("bw()")
    import math
    gA, gB, gC = 1199.72839, 1025.18162, 0.00921
    exp = round(round(100 / (gA - gB * math.exp(-gC * w)), 6) * tp, 6)
    check("IPF GL = formule officielle", abs(gl - exp) < 1e-6, [gl, exp])
    check("total street inchangé par le bench", pg.evaluate("total() === LIFTS.reduce((s,l)=>s+(best(l)||0),0)"))
    pg.click("[data-tab=prog]"); pg.wait_for_timeout(1000)
    check("Progrès : segment street / power", pg.locator("#v-prog [data-act=discSel]").count() == 2)
    pg.click("#v-prog [data-act=discSel][data-k=power]"); pg.wait_for_timeout(800)
    t = pg.evaluate("document.querySelector('#v-prog').innerText")
    check("Progrès power : total power et IPF GL", "Mon total power" in t and "IPF GL" in t and "Bench" in t and "Deadlift" in t, t[:300])
    pg.screenshot(path=str(OUT / "v28-progres-power.png"))
    check("accueil : total power quand power est choisi", "Mon total power" in pg.evaluate("(rHome(), document.querySelector('#v-home').innerText)"))

    # 4. Equipped : le squat equipped ne compte pas en street
    pg.evaluate("ACT.powerMode({k:'EQUIPPED'})"); pg.wait_for_timeout(500)
    t0 = pg.evaluate("total()")
    pg.evaluate("addPR('SQUAT', 300, 1, D.today, 'equipped', null)"); pg.wait_for_timeout(500)
    check("PR equipped marqué EQ (colonne G)", pg.evaluate("window.__sheets[APP_ID].PR.some(r => r[1]==='SQUAT' && r[6]==='EQ')"))
    check("squat equipped hors total street", pg.evaluate("total()") == t0)
    check("squat equipped dans le total power equipped", pg.evaluate("best('SQUAT', null) === 300 && totalPower() >= 300"))
    pg.evaluate("ACT.powerMode({k:'CLASSIC'})"); pg.wait_for_timeout(500)
    check("retour classic : squat equipped exclu", pg.evaluate("totalPower()") == tp)

    # 5. Catégories : à la main puis automatique
    pg.evaluate("ACT.catSet({k:'power', c:'-93'})"); pg.wait_for_timeout(500)
    check("catégorie IPF à la main", pg.evaluate("catIpf() === -93 && !catAutoOn('categorie_ipf')"))
    pg.evaluate("ACT.catAuto({k:'power'})"); pg.wait_for_timeout(500)
    check("catégorie IPF de nouveau auto", pg.evaluate("catAutoOn('categorie_ipf')"))
    pg.evaluate("openSheet('cat|power|settings')"); pg.wait_for_timeout(300)
    check("sélecteur de catégorie : 8 catégories IPF adulte ou 9 jeune", pg.locator(".catgrid button").count() in (8, 9))
    pg.screenshot(path=str(OUT / "v28-categorie.png")); pg.evaluate("ACT.closeSheet()")

    # 6. Date de naissance et âge
    pg.evaluate("CHG.birth({}, {value:'2004-03-14'})"); pg.wait_for_timeout(500)
    check("âge : Junior et Open (2004, en 2026)", pg.evaluate("JSON.stringify(myAges())") == '["JR","OPEN"]')

    # 7. Classements séparés, filtre d'âge, rien de privé envoyé
    pg.evaluate("clSync()"); pg.wait_for_timeout(1200)
    body = posted[-1] if posted else ""
    check("envoi : catégorie d'âge, pas de date de naissance", '"age":"JR,OPEN"' in body and "2004-03-14" not in body and "naissance" not in body, body[:200])
    check("envoi : visibilités et score GL", '"vp":true' in body and '"gl":' in body)
    pg.click("[data-tab=agenda]"); pg.wait_for_timeout(500); pg.click("[data-act=agSeg][data-k=amis]"); pg.wait_for_timeout(800)
    pg.click("#v-agenda [data-act=discSel][data-k=power]"); pg.wait_for_timeout(500)
    names = pg.evaluate("clRows('power').map(x => x.nom)")
    check("classement power : membres power, triés au GL", names == ["Dimitri", "Clara", "Alane"], names)
    check("classement street : sans les membres power seuls", pg.evaluate("clRows('street').map(x => x.nom)") == ["Bruno", "Alane"])
    pg.screenshot(path=str(OUT / "v28-amis-power.png"), full_page=True)
    pg.click("[data-act=clAge][data-k=M1]"); pg.wait_for_timeout(300)
    check("filtre d'âge Master 1", pg.evaluate("clRows('power').map(x => x.nom)") == ["Dimitri"])
    pg.click("[data-act=clAge][data-k='']"); pg.click("[data-act=clSort][data-k=total]"); pg.wait_for_timeout(300)
    check("tri au total", pg.evaluate("clRows('power').map(x => x.nom)") == ["Dimitri", "Alane", "Clara"])
    pg.evaluate("ACT.clVis({k:'power'})"); pg.wait_for_timeout(500)
    check("retrait du classement power enregistré", pg.evaluate("norm(D.profil.classement_power) === 'NON' && myStats().vp === false"))

    # 8. Compétition : catégories visibles en power
    pg.click("[data-act=agSeg][data-k=compet]"); pg.wait_for_timeout(500)
    check("Compétition : bloc « Tes catégories »", "Tes catégories" in pg.evaluate("document.querySelector('#v-agenda').innerText"))

    # 9. Retirer le street : power seul
    pg.evaluate("ACT.discToggle({k:'street'})"); pg.wait_for_timeout(600)
    check("power seul", pg.evaluate("!streetOn() && powerOn() && curDisc() === 'power'"))
    check("power seul : la limite de pesée suit la catégorie IPF", pg.evaluate("catLimit() === -catIpf() || catIpf() > 0"))
    check("on ne peut pas tout retirer", pg.evaluate("(ACT.discToggle({k:'power'}), powerOn())"))
    pg.click("[data-tab=home]"); pg.wait_for_timeout(500)
    h = pg.evaluate("document.querySelector('#v-home').innerText")
    check("accueil power seul : pas de muscle-up", "Muscle-up" not in h and "Bench" in h, h[:300])
    pg.screenshot(path=str(OUT / "v28-home-power.png"), full_page=True)
    print("ERREURS JS :", errs[:5]); errs_main = list(errs)

    # 10. Inscription (maquette A) : powerlifting equipped, catégories auto
    c2 = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block"); c2.route("**/*", route)
    q = c2.new_page(); e2 = []; q.on("pageerror", lambda e: e2.append(str(e)))
    q.goto("http://app.local/sl/"); q.wait_for_timeout(1000); q.click("[data-act=obLogin]"); q.wait_for_timeout(1500)
    q.click("[data-act=obStep][data-s=create]"); q.wait_for_timeout(500)
    q.fill("#obp", "Clara"); q.click("[data-act=obDisc][data-k=power]"); q.click("[data-act=obDisc][data-k=street]")
    q.click("[data-act=obMode][data-k=equipped]"); q.click("[data-act=obSex][data-k=F]")
    q.fill("#obn", "2001-05-02"); q.fill("#obw", "62,4"); q.wait_for_timeout(300)
    cats = q.evaluate("document.querySelector('#obcats').innerText")
    check("inscription : catégorie IPF −63 et âge Open en direct", "−63" in cats and "Open" in cats and "Street" not in cats, cats)
    check("inscription : PR street masqués en power seul", q.evaluate("document.querySelector('[data-lift=MU]').hidden && !document.querySelector('[data-lift=BENCH]').hidden"))
    q.screenshot(path=str(OUT / "v28-inscription.png"), full_page=True)
    q.fill("#obprBENCH", "70"); q.fill("#obprDEADLIFT", "150")
    q.click("[data-act=obCreate]"); q.wait_for_timeout(3500)
    prof = q.evaluate("(() => { const ids = Object.keys(window.__sheets).filter(k => k.startsWith('NEW')); const b = window.__sheets[ids.at(-1)]; return b ? {P:b.PROFIL, PR:b.PR} : null; })()")
    PF = dict((r[0], r[1]) for r in (prof or {}).get("P", [])[1:] if r)
    check("carnet créé : disciplines, mode, naissance", PF.get("disciplines") == "power" and PF.get("power_mode") == "equipped" and PF.get("naissance") == "2001-05-02", PF)
    check("carnet créé : plus de mu_acquis", "mu_acquis" not in PF)
    prs = (prof or {}).get("PR", [])
    check("carnet créé : PR Bench equipped", any(r[1] == "BENCH" and r[6] == "EQ" for r in prs[1:]), prs)
    print("ERREURS JS inscription :", e2[:5])
    if errs_main or e2: fails.append("erreurs JS")
    br.close()
print("ÉCHECS :", fails); sys.exit(1 if fails else 0)
