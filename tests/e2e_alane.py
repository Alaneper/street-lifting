"""Records et séance en direct sur un extrait réel de la prog d'Alane (BLOC 7, S1–S2)."""
import pathlib, json, sys
H = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(H))
from fixture_alane_b7 import grid, EXPECT
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
INJ = """<script>(()=>{const s=window.__sheets['%s'];for(const k of Object.keys(s)) if(/^BLOC/.test(k)) delete s[k];
 s['BLOC 7']=%s; const a=window.__sheets['%s']; a.PR=[a.PR[0]]; a.SERIES=[a.SERIES[0]]; a.BLOCS=[a.BLOCS[0],['7','2026-10-12','']];})()</script>""" % (COACH, json.dumps(grid()), APP)
def route2(r):
    u = r.request.url
    if u.endswith("/sl/") or u.endswith("index.html"):
        return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + INJ + "<script src='/shim.js'></script>", 1), content_type="text/html")
    return route(r)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, service_workers="block"); c.route("**/*", route2)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)
    bad = 0
    for l, exp in EXPECT.items():
        got = pg.evaluate(f"Object.fromEntries(repMaxes(compSets('{l}')).filter(x=>x.b).map(x=>[x.n,x.b.c]))")
        ok = {int(k): v for k, v in got.items()} == exp; bad += not ok
        print(("OK " if ok else "KO "), l, got, "attendu", exp)
    # séance en direct S2, séance 1
    key = pg.evaluate("S.find(s=>s.semaine==='2'&&s.seance==='Séance 1').key")
    pg.evaluate(f"startLive({json.dumps(key)}, 1)"); pg.wait_for_timeout(800)
    pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(300)
    print("top set :", pg.evaluate("live.rows[1].sets.map(x=>x.c+'x'+x.r)"), "|", pg.locator(".live .hero .hu").first.inner_text())
    print("back-off prérempli :", pg.evaluate("live.rows[2].sets.map(x=>x.c+'x'+x.r)"))
    pg.evaluate("live.rows[1].sets[0].c=107.5; live.rows[1].sets[0].done=true; live.i=2; renderLayer()"); pg.wait_for_timeout(400)
    print("back-off après top set à 107,5 :", pg.evaluate("live.rows[2].sets.map(x=>x.c)"), "|", pg.locator(".live .hero .hu").first.inner_text())
    print("héros :", pg.locator(".live .hero").first.inner_text().replace("\n"," | "))
    pg.screenshot(path=str(OUT/"alane-live.png"))
    print("ERRORS:", errs[:10]); sys.exit(1 if bad else 0)
