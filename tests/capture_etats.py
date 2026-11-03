"""Captures des états vide / chargement / erreur / hors connexion pour chaque écran (390x844).
Usage : python3 tests/capture_etats.py [dossier_sortie]. Mêmes prérequis que capture_ecrans.py."""
import sys, pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
OUTDIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
OUTDIR.mkdir(parents=True, exist_ok=True)
ECRANS = {
  "aujourdhui": ("setTab('home')", "v-home"), "programme": ("setTab('seance')", "v-seance"), "historique": ("setTab('histo')", "v-histo"),
  "poids": ("corpsTab='poids';corpsManual=D.today;setTab('corps')", "v-corps"), "alimentation": ("corpsTab='nutri';nutView='jour';corpsManual=D.today;setTab('corps')", "v-corps"),
  "records": ("progSeg='records';setTab('prog')", "v-prog"), "courbes": ("progSeg='courbes';setTab('prog')", "v-prog"),
  "competition": ("agendaSeg='compet';setTab('agenda')", "v-agenda"), "classement": ("agendaSeg='amis';setTab('agenda')", "v-agenda"),
}
ETATS = {
  "vide": "(()=>{ D.poids=[]; D.repas=[]; D.series=[]; D.prs=[]; D.comps=[]; D.cardio=[]; })()",
  "chargement": "",   # rempli par le squelette ci-dessous
  "erreur": "seanceErr='Impossible de lire ta prog : vérifie que le Sheet est partagé avec toi.'",
  "hors-ligne": "Object.defineProperty(navigator,'onLine',{get:()=>false,configurable:true});window.dispatchEvent(new Event('offline'))",
}
with sync_playwright() as p:
    br = p.chromium.launch()
    for etat, setup in ETATS.items():
        c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=1, service_workers="block"); c.route("**/*", route)
        pg = c.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
        pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4500)
        for nom, (js, vid) in ECRANS.items():
            if etat == "chargement":
                pg.evaluate("page=null;renderLayer()"); pg.evaluate(js); pg.evaluate("(id) => { document.getElementById(id).innerHTML = SKEL; }", vid)
            else:
                pg.evaluate("page=null;renderLayer()"); pg.evaluate(setup); pg.evaluate(js)
            pg.wait_for_timeout(700); pg.evaluate("window.scrollTo(0,0)")
            pg.screenshot(path=str(OUTDIR / f"{etat}__{nom}.png")); print("ok", etat, nom)
        print("ERREURS", etat, errs[:5]); c.close()
