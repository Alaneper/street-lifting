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
  "aujourdhui": "setTab('home')", "aujourdhui-sans-pesee": "D.poids=D.poids.filter(p=>p.date!==D.today);hwDraft=null;setTab('home')", "programme": "setTab('seance')", "historique": "setTab('histo')",
  "poids": "corpsTab='poids';corpsManual=D.today;setTab('corps')", "alimentation": "corpsTab='nutri';corpsManual=D.today;setTab('corps')",
  "progres": "progSeg='records';setTab('prog')", "classement": "agendaSeg='amis';setTab('agenda')", "competition": "agendaSeg='compet';setTab('agenda')",
  "mouvements": "progSeg='mouvements';mvQ='';setTab('prog')", "mouvements-recherche": "progSeg='mouvements';mvQ='dip';setTab('prog')",
  "courbes": "progSeg='courbes';setTab('prog')",
  "progres-2disc": "D.profil.disciplines='street,powerlifting';progSeg='records';setTab('prog');D.profil.disciplines='street'",
  "courbes-ouvert": "foldOpen.vol=true;foldOpen.renfo=true;progSeg='courbes';setTab('prog')",
  "mouvements-tout": "mvOpen.jambes=true;mvOpen.pousser=true;mvOpen.tirer=true;mvOpen['']=true;progSeg='mouvements';mvQ='';setTab('prog')",
  "fiche-mouvement": "page={type:'move',l:'SQUAT'};renderLayer()", "fiche-squat": "page={type:'lift',l:'SQUAT'};liftMetric='1rm';renderLayer()", "fiche-exercice": "page={type:'ex',k:exercisePoints().find(o=>o.lift).key};exMetric='e1rm';renderLayer()",
  "reglages": "ACT.settings&&ACT.settings({})",
  "serie-validee": "setTab('home');startLive((todaySeance()||nextSeance()).key, 1);ACT.closeSheet&&ACT.closeSheet();onSetDone(0)",
  "fin-seance": "setTab('home');startLive((todaySeance()||nextSeance()).key, 1);ACT.closeSheet&&ACT.closeSheet();onSetDone(0);finishLive()",
  "alim-semaine": "corpsTab='nutri';nutView='semaine';corpsManual=D.today;setTab('corps');rCorps()",
  "classement-fixture": "agendaSeg='amis';CL={rows:[{nom:'Alane',ris:79.4,total:187.5,disc:'street',me:true,pays:'BE'},{nom:'Tom',ris:82.1,total:201,disc:'street',pays:'BE'},{nom:'Inès',ris:76.9,total:170,disc:'street',pays:'FR'},{nom:'Sam',ris:74.2,total:165,disc:'street',pays:'BE'},{nom:'Yanis',ris:71.8,total:160,disc:'street',pays:'FR'},{nom:'Léa',ris:70.3,total:140,disc:'street',pays:'BE'}]};clErr='';setTab('agenda');rAgenda()",   # membres fictifs : jeu de test pour la capture uniquement
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
        pg.evaluate("page=null;renderLayer()"); pg.evaluate(js); pg.wait_for_timeout(1500); pg.evaluate("window.scrollTo(0,%d)" % int(__import__("os").environ.get("SCROLL_Y", "0") or 0)); pg.wait_for_timeout(500)
        H = int(__import__("os").environ.get("CAP_H", "0") or 0)   # CAP_H=2600 : fenêtre plus haute pour voir toute une fiche en page pleine
        if H: pg.set_viewport_size({"width":390, "height":H}); pg.wait_for_timeout(400)
        pg.screenshot(path=str(OUTDIR / f"{nom}.png"))
        if H: pg.set_viewport_size({"width":390, "height":844})
        print("ok", nom)
    print("ERREURS:", errs[:10])
