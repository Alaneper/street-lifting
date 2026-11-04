"""Lot « fiabilité et tactile » : courbes à moins de 3 points. (Les autres preuves du lot : e2e_v87, e2e_v88, e2e_v70, e2e_v91, e2e_v92.) Rejoue : python3 tests/e2e_v90_fiabilite.py"""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    # courbe Chart.js (fiche exercice, fiche mouvement) : 2 points = points seuls ; 3 points = ligne
    ev("() => { const h = document.createElement('div'); h.id = 'tmpc'; h.style.cssText = 'position:fixed;left:0;top:0;width:300px;height:200px;z-index:99'; h.innerHTML = '<canvas id=\"c2\"></canvas><canvas id=\"c3\"></canvas>'; document.body.appendChild(h); }")
    ev("() => { lineChart('c2', null, [{label:'e1RM', data:[100, 105], color:'#4F8DF5', area:true}], {unit:' kg', dates:['2026-10-01', '2026-10-20']}); lineChart('c3', null, [{label:'e1RM', data:[100, 105, 110], color:'#4F8DF5', area:true}], {unit:' kg', dates:['2026-10-01', '2026-10-10', '2026-10-20']}); }")
    pg.wait_for_function("charts && charts.c2 && charts.c3", timeout=10000)
    d2, d3 = ev("() => { const a = charts.c2.data.datasets[0], b = charts.c3.data.datasets[0]; return [a.showLine, a.fill, a.pointRadius, b.showLine, b.fill]; }"), None
    check("1e · 2 points : points seuls (pas de droite, pas d'aire), points visibles", d2[0] is False and d2[1] is False and d2[2] >= 5, d2)
    d3 = ev("() => { const b = charts.c3.data.datasets[0]; return [b.showLine, b.fill]; }")
    check("1e · 3 points : la courbe est tracée normalement", d3[0] is True and d3[1] == "origin", d3)
    # courbe en aire (Progrès) : 2 points = deux points, aucune ligne ni aire
    s2 = ev("() => areaSvg([{date:'2026-10-01', v:100}, {date:'2026-10-20', v:105}])"); s3 = ev("() => areaSvg([{date:'2026-10-01', v:100}, {date:'2026-10-10', v:103}, {date:'2026-10-20', v:105}])")
    cnt = lambda h, tag: h.count("<" + tag)
    check("1e · courbe de progrès à 2 points : 2 points, aucun tracé de ligne", s2.count('r="6"') == 2 and 'stroke-width="2.8"' not in s2, (s2.count('r="6"'), 'stroke-width="2.8"' in s2))
    check("1e · courbe de progrès à 3 points : la ligne est tracée", 'stroke-width="2.8"' in s3 and s3.count('r="6"') == 1)
    check("aucune erreur JS", not errs, errs)
    br.close()
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
