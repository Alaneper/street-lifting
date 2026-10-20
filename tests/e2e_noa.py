"""Vérifie les records par reps sur un extrait réel de la prog de Noa (B8)."""
import pathlib, json, sys
H = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(H))
from fixture_noa_b8 import grid, EXPECT
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
G = json.dumps(grid())
INJ = """<script>(()=>{const s=window.__sheets['%s'];for(const k of Object.keys(s)) if(/^BLOC/.test(k)) delete s[k];
 s['B8 force 3 semaines ']=%s; const a=window.__sheets['%s']; a.PR=[a.PR[0]]; a.POIDS=[a.POIDS[0],['2026-09-01','85','']];})()</script>""" % (COACH, G, APP)
def route2(r):
    u = r.request.url
    if u.endswith("/sl/") or u.endswith("index.html"):
        html = (P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + INJ + "<script src='/shim.js'></script>", 1)
        return r.fulfill(body=html, content_type="text/html")
    return route(r)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, service_workers="block"); c.route("**/*", route2)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(3000)
    print("semaines :", pg.evaluate("[...new Set(S.map(s=>s.semaine))]"), "| séances :", pg.evaluate("S.length"))
    bad = 0
    for l, exp in EXPECT.items():
        got = pg.evaluate(f"Object.fromEntries(repMaxes(compSets('{l}')).filter(x=>x.b).map(x=>[x.n,x.b.c]))")
        ok = all(abs(got.get(str(n), -1) - v) < 1e-6 for n, v in exp.items())
        bad += not ok
        print(("OK " if ok else "KO "), l, got, "attendu", exp)
    print("variantes exclues (pause/raw pausé) :", pg.evaluate("compSets('DIP').some(x=>x.c===70||x.c===62.5)") is False and pg.evaluate("compSets('SQUAT').every(x=>x.c!==162.5)"))
    print("vieux modèle ignoré :", pg.evaluate("compSets('SQUAT').every(x=>x.c!==300)"))
    pg.evaluate("ACT.openLift({l:'SQUAT'})"); pg.wait_for_timeout(1500); pg.evaluate("ACT.rmInfo({l:'SQUAT',n:'3'})"); pg.wait_for_timeout(600)
    print("détail 3 reps :", pg.locator(".sheet").inner_text().replace("\n"," | ")[:300])
    pg.screenshot(path=str(OUT/"noa-rm.png"))
    print("ERRORS:", errs[:10]); sys.exit(1 if bad else 0)
