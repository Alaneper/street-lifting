"""Historique : un onglet supprimé par le coach reste visible ; une nouvelle prog avec un nouveau « BLOC 1 » coexiste avec l'ancien."""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(4000)
    n = pg.evaluate(f"(window.__sheets['{APP}'].HISTORIQUE||[]).length")
    print("lignes HISTORIQUE :", n, "| entête :", pg.evaluate(f"(window.__sheets['{APP}'].HISTORIQUE||[[]])[0].slice(0,4)"))
    rm2 = pg.evaluate("repMaxes(compSets('SQUAT')).filter(x=>x.b).map(x=>x.n+':'+x.b.c+'@'+blocShort(x.b.bloc))")
    print("squat avant :", rm2)
    # 1. le coach supprime BLOC 2
    pg.evaluate(f"delete window.__sheets['{COACH}']['BLOC 2']; syncAll(false)"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(3000)
    print("ordre après suppression :", pg.evaluate("progOrder.map(blocLabel)"))
    print("squat après :", pg.evaluate("repMaxes(compSets('SQUAT')).filter(x=>x.b).map(x=>x.n+':'+x.b.c+'@'+blocShort(x.b.bloc))"))
    # 2. nouvelle prog : un seul BLOC 1, tout neuf
    pg.evaluate(f"""(()=>{{const old=window.__sheets['{COACH}'];window.__sheets['1NEWPROGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx']={{'BLOC 1':JSON.parse(JSON.stringify(old['BLOC 7']))}};}})()""")
    pg.wait_for_timeout(3000); pg.evaluate("CHG.coachLink({},{value:'https://docs.google.com/spreadsheets/d/1NEWPROGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/edit'})"); pg.wait_for_timeout(7000); pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(3000)
    print("coach :", pg.evaluate("D.profil.coach_sheet_id"), pg.evaluate("Object.keys(window.__sheets)"), pg.evaluate("seanceErr"))
    print("ordre nouvelle prog :", pg.evaluate("progOrder.map(blocLabel)"))
    print("bloc actif :", pg.evaluate("blocLabel(activeBloc())"), "| séances archivées :", pg.evaluate("S.filter(s=>s.archived).length"))
    pg.click("[data-tab=prog]"); pg.wait_for_timeout(1500); pg.screenshot(path=str(OUT/"progres-semaine.png"), full_page=True)
    print("semaine :", pg.locator("#v-prog .hero").nth(1).inner_text().replace("\n"," | ")[:150])
    print("ERRORS:", errs[:10])
