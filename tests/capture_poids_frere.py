"""Retours frère D : graphique de poids (pesées du jour en gris, tendance 7 j, graduations, 5 dates, limite, stats, périodes). SHOTDIR=<dossier> python3 tests/capture_poids_frere.py"""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOT = pathlib.Path(os.environ["SHOTDIR"]); SHOT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    # ~100 pesées quotidiennes en dents de scie autour d'une lente descente vers la limite de catégorie (jeu de test, pas des données réelles)
    ev("""(() => { const base = new Date(D.today + 'T12:00:00'); D.poids = []; for (let i = 99; i >= 0; i--) { const d = new Date(base); d.setDate(d.getDate() - i); const saw = [0.9, -0.6, 0.4, -1.0, 0.7, -0.2, 0.1][i % 7]; D.poids.push({id: 2000 + i, date: isoOf(d), poids: Math.round((81.5 - (99 - i) * 0.02 + saw) * 10) / 10}); } })()""")
    for k in ("3m", "7j", "1m"):
        ev(f"(() => {{ pwRange = '{k}'; pwAnim = false; corpsTab = 'poids'; corpsManual = D.today; setTab('corps'); rCorps(); }})()"); pg.wait_for_timeout(1500)
        pg.evaluate("window.scrollTo(0, 0)")
        pg.screenshot(path=str(SHOT / f"poids-{k}.png"))
    print(ev("[...document.querySelectorAll('svg[data-ich=pw] text')].map(t => t.textContent)"), "erreurs:", errs)
    print(ev("document.querySelector('.pw-av').innerText"), "|", ev("[...document.querySelectorAll('.rng.pwr button')].map(b => b.textContent)"))
    br.close()
