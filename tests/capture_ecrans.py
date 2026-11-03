"""Capture de chaque écran de l'app en 390x844 @2x, défilement en haut, avec le jeu de données du mock.
Usage : python3 tests/capture_ecrans.py [dossier_sortie] [écran ...]
Prérequis : python3 tools/build.py test.apps.googleusercontent.com test-build.html ; BENCH_DEPS=<dossier avec node_modules chart.js, jszip, @fontsource>."""
import sys, pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
OUTDIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
OUTDIR.mkdir(parents=True, exist_ok=True)
only = set(sys.argv[2:])
ECRANS = {
  "aujourdhui": "setTab('home')", "programme": "setTab('seance')", "historique": "setTab('histo')",
  "poids": "corpsTab='poids';corpsManual=D.today;setTab('corps')", "alimentation": "corpsTab='nutri';corpsManual=D.today;setTab('corps')",
  "progres": "progSeg='records';setTab('prog')", "classement": "setTab('agenda')",
  "mouvements": "progSeg='mouvements';mvQ='';setTab('prog')", "mouvements-recherche": "progSeg='mouvements';mvQ='dip';setTab('prog')",
  "courbes": "progSeg='courbes';setTab('prog')",
  "fiche-squat": "page={type:'lift',l:'SQUAT'};liftMetric='1rm';renderLayer()", "fiche-exercice": "page={type:'ex',k:exercisePoints().find(o=>o.lift).key};exMetric='e1rm';renderLayer()",
  "reglages": "ACT.settings&&ACT.settings({})",
  "serie-validee": "setTab('home');startLive((todaySeance()||nextSeance()).key, 1);ACT.closeSheet&&ACT.closeSheet();onSetDone(0)",
  "direct": "setTab('home');startLive((todaySeance()||nextSeance()).key, 1);ACT.closeSheet&&ACT.closeSheet()",
}
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4500)
    # jeu de séries réaliste (le mock n'en a aucune) : 3 exercices par séance faite et datée
    pg.evaluate("""(()=>{ let n=0; S.filter(z=>z.faite && dateOf(z)).forEach((z,i)=>{ [['SQUAT COMP',100+i*2.5,5],['DIPS COMP',30+i,4],['PULL UP COMP',20+i,3]].forEach(([ex,c,k])=>D.series.push({id:900+n++,date:dateOf(z),bloc:z.bloc,semaine:z.semaine,seance:z.seance,ex:ex,charge:c,sets:Array(k).fill(0).map(()=>({r:5,c:c})),note:'',src:'',com:''})); }); })()""")
    for nom, js in ECRANS.items():
        if only and nom not in only: continue
        pg.evaluate("page=null;renderLayer()"); pg.evaluate(js); pg.wait_for_timeout(1500); pg.evaluate("window.scrollTo(0,0)")
        pg.screenshot(path=str(OUTDIR / f"{nom}.png"))
        print("ok", nom)
    print("ERREURS:", errs[:10])
