"""Empreinte des calculs (records par reps, 1RM estimé, tonnage par exercice) sur 3 jeux de données :
la prog de test, l'extrait réel d'Alane (B7) et celui de Noa (B8), plus des séries notées dans l'app (charges
identiques, charges différentes, back-off, lest à 0). Sert à comparer deux versions de l'app : les chiffres doivent être identiques.
Usage : python3 tests/compare_records.py sortie.json"""
import pathlib, json, sys
H = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(H))
from fixture_alane_b7 import grid as gA
from fixture_noa_b8 import grid as gN
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SER = [["2026-10-20","7","1","Séance 1","SQUAT · COMP","140","5@140, 5@125, 5@125","app","L5"],
       ["2026-10-21","7","1","Séance 2","BENCH · COMP","100","3, 3, 3","app","L6"],
       ["2026-10-22","7","1","Séance 3","ROWING · HALTERE","32","12@30, 10@32, 9@32","app",""],
       ["2026-10-23","7","2","Séance 1","DIPS · LESTE","10","8@0, 6@10","app",""],
       ["2026-10-24","7","2","Séance 2","CURL · BARRE","25","12, 12, 10","app",""]]
def inj(name, grid, ser):
    g = json.dumps(grid) if grid else "null"
    return """<script>(()=>{const s=window.__sheets['%s']; const G=%s; if (G){ for(const k of Object.keys(s)) if(/^BLOC|^B8/.test(k)) delete s[k]; s['%s']=G; }
      const a=window.__sheets['%s']; a.SERIES=[a.SERIES[0]].concat(%s);})()</script>""" % (COACH, g, name, APP, json.dumps(ser))
SETS = [("defaut", None, None, SER), ("alane", "BLOC 7", gA(), SER), ("noa", "B8 force 3 semaines ", gN(), [])]
out = {}
with sync_playwright() as p:
    br = p.chromium.launch()
    for lab, name, grid, ser in SETS:
        I = inj(name or "x", grid, ser)
        def mk(I):
            def route2(r, *_):
                u = r.request.url
                if u.endswith("/sl/") or u.endswith("index.html"):
                    return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + I + "<script src='/shim.js'></script>", 1), content_type="text/html")
                return route(r)
            return route2
        route2 = mk(I)
        c = br.new_context(viewport={"width":390,"height":844}, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route2)
        pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
        pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
        pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)
        out[lab] = pg.evaluate("""(() => { const r6 = v => Math.round(v * 1e6) / 1e6;
          const ex = exercisePoints().map(o => [o.key, o.pts.map(p => [p.date, p.label, r6(p.charge), r6(p.e1rm), r6(p.e1rmBest), r6(p.tonnage), p.totalReps, p.sets.map(x => x.c + 'x' + x.r).join(' ')])]);
          const rm = Object.fromEntries(ALL_LIFTS.map(l => [l, repMaxes(compSets(l)).filter(x => x.b).map(x => [x.n, x.b.c])]));
          return {nSeries:D.series.length, series:D.series.map(x => x.ex + ' ' + x.sets.map(y => y.c + 'x' + y.r).join(' ')), ex, rm}; })()""")
        out[lab]["errs"] = errs
        c.close()
    br.close()
pathlib.Path(sys.argv[1]).write_text(json.dumps(out, ensure_ascii=False, indent=1))
print("écrit", sys.argv[1], {k: (len(v["ex"]), v["nSeries"]) for k, v in out.items()})
