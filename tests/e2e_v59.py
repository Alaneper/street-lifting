"""v59 : charge par série fiable de bout en bout.
- relecture du carnet : durées de 200 s et plus, charges négatives différentes (« 8@-20, 8@-15 ») ;
- anciens formats relus à l'identique ; commentaires de prog toujours lus avec les limites strictes ;
- garde-fou : jamais une ligne écrite que l'app ne saurait pas relire ;
- exercice passé en « Temps » sans ligne de prog : jamais un 1RM ni un tonnage ;
- fiche exercice : « Dernière fois » montre la charge de chaque série quand elles diffèrent.
Usage : python3 tests/e2e_v59.py   (affiche « TOUT VERT » si tout passe)"""
import pathlib, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)
SER = [["2026-10-20","9","1","Libre","GAINAGE","0","240, 240, 300","app",""],
       ["2026-10-21","9","1","Libre","TRACTIONS · ASSISTEES","-15","8@-20, 8@-15","app",""],
       ["2026-10-22","9","1","Libre","FARMER WALK","40","90@40, 120@40","app",""],
       ["2026-10-23","9","1","Libre","ROWING · HALTERE","32","12@30, 10@32, 9@32","app",""],
       ["2026-10-24","9","1","Libre","CURL · BARRE","25","12, 12, 10","app",""]]
INJ = "<script>(()=>{const a=window.__sheets['%s']; a.SERIES=[a.SERIES[0]].concat(%s); const P=a.PROFIL; P.push(['ex_modes','FARMER WALK=T']);})()</script>" % (APP, json.dumps(SER))
def route2(r, *_):
    u = r.request.url
    if u.endswith("/sl/") or u.endswith("index.html"):
        return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + INJ + "<script src='/shim.js'></script>", 1), content_type="text/html")
    return route(r)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390,"height":844}, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route2)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    got = pg.evaluate("Object.fromEntries(D.series.map(x => [x.ex, x.sets.map(y => y.c + 'x' + y.r).join(' ')]))")
    check("gainage 4 et 5 min relu (avant : ligne perdue)", got.get("GAINAGE") == "0x240 0x240 0x300", str(got))
    check("charges négatives différentes relues (avant : ligne perdue)", got.get("TRACTIONS · ASSISTEES") == "-20x8 -15x8", str(got))
    check("charges différentes relues série par série", got.get("ROWING · HALTERE") == "30x12 32x10 32x9", str(got))
    check("ancien format sans @ inchangé", got.get("CURL · BARRE") == "25x12 25x12 25x10", str(got))
    # anciens formats : la lecture du carnet donne exactement la même chose qu'avant
    old = pg.evaluate("""['8,8,9','12,10,9,','8@42, 9@44','3*5','8 8 9','5@102.5, 3@107.5','10;10;8','12/10'].map(t => JSON.stringify(parseSets(t, 20)) === JSON.stringify(parseSets(t, 20, true)))""")
    check("formats existants : lecture du carnet identique à avant", all(old), str(old))
    strict = pg.evaluate("[parseSets('250, 250', 20), parseSets('8@-20', 20)]")
    check("commentaires de prog : limites strictes conservées (250 = une charge, pas des reps)", strict == [None, None], str(strict))
    # garde-fou d'écriture : aller-retour sur des cas variés
    rt = pg.evaluate("""(() => { const W = d => { const sc = d.every(x => x.c === d[0].c); return sc ? d.map(x => x.r).join(', ') : d.map(x => x.r + '@' + String(x.c)).join(', '); };
      const cases = [[{r:5,c:100},{r:5,c:90}], [{r:8,c:-20},{r:8,c:-15}], [{r:240,c:0},{r:300,c:0}], [{r:5,c:102.5},{r:3,c:107.25}], [{r:12,c:20},{r:10,c:22.5}], [{r:8,c:0},{r:6,c:10}], [{r:3,c:0.5}]];
      return cases.map(d => { const b = parseSets(W(d), Math.max(...d.map(x => x.c)), true); return !!b && b.length === d.length && b.every((y, i) => y.r === d[i].r && y.c === d[i].c); }); })()""")
    check("écrire puis relire : identique série par série (7 cas)", all(rt), str(rt))
    # exercice en « Temps » sans ligne de prog : ni 1RM ni tonnage
    ep = pg.evaluate("exercisePoints().map(o => o.key)")
    check("farmer walk en « Temps » : absent des 1RM et tonnages", "FARMER WALK" not in ep, str(ep))
    check("gainage absent des 1RM et tonnages", "GAINAGE" not in ep, str(ep))
    check("rowing présent, tonnage série par série = 968", pg.evaluate("(exercisePoints().find(o => o.key === 'ROWING · HALTERE') || {last:{}}).last.tonnage") == 968)
    # fiche exercice : charges de chaque série
    pg.evaluate("ACT.openEx({k:'ROWING · HALTERE'})"); pg.wait_for_timeout(600)
    txt = pg.evaluate("(document.querySelector('.page') || {innerText:''}).innerText")
    check("fiche : « 30 × 12 · 32 × 10 · 32 × 9 »", "30 × 12 · 32 × 10 · 32 × 9" in txt, txt[:300])
    # bout en bout : séance en direct, charges différentes, écriture dans le carnet, relecture
    ok = pg.evaluate("""(() => { for (const s of S) { const i = s.exercices.findIndex(e => !liftOf(e.mouvement) && !isCardioEx(e) && !isTimedEx(e)); if (i >= 0) { window.__ts = [s.key, i]; return true; } } return false; })()""")
    if ok:
        pg.evaluate("ACT.closePage && ACT.closePage()"); pg.evaluate("startLive(__ts[0], __ts[1])"); pg.wait_for_timeout(900)
        pg.evaluate("(() => { const st = live.rows[live.i]; while (st.sets.length < 3) st.sets.push({c:null, r:null, done:false}); st.sets.length = 3; st.dirty = true; renderLayer(); })()"); pg.wait_for_timeout(300)
        for j, (cv, rv) in enumerate([("30", "12"), ("32,5", "10"), ("32,5", "9")]):
            row = pg.locator(".setrow").nth(j)
            row.locator("input[data-chg=setC]").fill(cv); row.locator("input[data-chg=setC]").dispatch_event("change")
            row.locator("input[data-chg=setR]").fill(rv); row.locator("input[data-chg=setR]").dispatch_event("change")
            pg.wait_for_timeout(150); pg.locator(".setrow").nth(j).locator(".ck").click(); pg.wait_for_timeout(400)
            pg.evaluate("ACT.closeSheet && sheet === 'rest' && ACT.closeSheet()"); pg.wait_for_timeout(150)
        pg.evaluate("(async () => { window.__saved = await saveRow(live.i); })()"); pg.wait_for_timeout(1500)
        row = pg.evaluate("(window.__sheets['%s'].SERIES || []).slice(-1)[0]" % APP)
        check("écrit dans le carnet : « 12@30, 10@32.5, 9@32.5 », charge max 32,5", row and row[6] == "12@30, 10@32.5, 9@32.5" and float(str(row[5]).replace(",", ".")) == 32.5, str(row))
        pg.evaluate("(async () => { await loadApp(); window.__re = D.series.slice(-1)[0].sets.map(y => y.c + 'x' + y.r).join(' '); })()"); pg.wait_for_timeout(2500)
        check("relu après rechargement : identique série par série", pg.evaluate("window.__re") == "30x12 32.5x10 32.5x9", str(pg.evaluate("window.__re")))
    else: check("exercice d'accessoire trouvé pour la séance", False)
    check("aucune erreur JS", not errs, str(errs[:3]))
    br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
