"""v75 : échelle adaptative de la courbe de poids (Auto, hauteur mini 1,5 kg) et sélecteur de zoom Auto / Serré / Large gardé dans le profil."""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(2500)
    # règle sur 6 profils très différents (amplitude en kg) : axe qui contient les données, hauteur mini, au plus 9 lignes, chiffres espacés
    PR = {"stable":[70, 70.2, 69.8, 70.1, 69.9], "variable":[78, 81, 79, 80.5, 77.6, 79.5], "seche":[95, 93, 91, 90, 88.5], "masse":[78, 82, 85, 88, 90], "leger":[52, 52.2, 52.1, 52.3], "trois":[105, 104.2, 104.6]}
    for mode, fl in (("auto", 1.5), ("serre", 1.0)):
        bad = pg.evaluate("""([P, mode, fl]) => { const out = []; for (const k in P) { const v = P[k], a = pwAxis(v, null, mode), n = a.t.length, lab = a.t.filter(x => x[1]).length, sp = a.t.filter(x => x[1]).map(x => x[0]);
          if (a.lo > Math.min(...v) || a.hi < Math.max(...v)) out.push(k + " : données hors axe");
          if (a.hi - a.lo < fl - 1e-9) out.push(k + " : hauteur < plancher");
          if (n > 10) out.push(k + " : " + n + " lignes");
          if (lab < 2 || lab > 9) out.push(k + " : " + lab + " chiffres");
          if (146 / (a.hi - a.lo) * Math.min(...sp.slice(1).map((x, i) => x - sp[i]).concat(99)) < 21.5) out.push(k + " : chiffres trop serrés"); } return out; }""", [PR, mode, fl])
        check(f"mode {mode} : 6 profils (stable, variable, sèche, masse, léger, 3 pesées)", not bad, bad)
    big = pg.evaluate("[pwAxis([76, 79, 90], null, 'auto'), pwAxis([75, 76.1], 80, 'large')].map(a => [a.hi - a.lo, a.t.filter(x => x[1]).length])")
    check("auto : amplitude 14 kg → chiffres espacés ; large : ±3 kg conservé", big[0][1] <= 9 and big[1][0] >= 7, big)
    check("limite de catégorie proche : l'axe l'inclut", pg.evaluate("(() => { const a = pwAxis([84, 86, 85.5], 87, 'auto'); return a.hi >= 87; })()"))
    check("limite lointaine : l'axe ne s'étire pas jusqu'à elle", pg.evaluate("(() => { const a = pwAxis([75, 76.1], 80, 'auto'); return a.hi < 78; })()"))
    # sélecteur dans l'écran Corps
    pg.evaluate("pwRange = '3m'; corpsTab = 'poids'; corpsManual = D.today; setTab('corps')"); pg.wait_for_timeout(500)
    check("sélecteur Zoom : Auto / Serré / Large, Auto par défaut", pg.evaluate("(() => { const b = [...document.querySelectorAll('[data-act=pwZoom]')]; return b.length === 3 && b[0].getAttribute('aria-pressed') === 'true'; })()"))
    check("cibles de 44 px au moins", pg.evaluate("[...document.querySelectorAll('[data-act=pwZoom]')].every(b => b.getBoundingClientRect().height >= 43.5)"))
    h = lambda: pg.evaluate("document.querySelector('svg[data-ich=pw]').outerHTML.length")
    a0 = pg.evaluate("[...document.querySelectorAll('svg[data-ich=pw] text')].map(t => t.textContent).join('|')")
    pg.click("[data-act=pwZoom][data-k=large]"); pg.wait_for_timeout(400)
    a1 = pg.evaluate("[...document.querySelectorAll('svg[data-ich=pw] text')].map(t => t.textContent).join('|')")
    check("Large : l'échelle change et le choix est mémorisé dans le profil", a0 != a1 and pg.evaluate("D.profil.pw_zoom === 'large' && document.querySelector('[data-act=pwZoom][data-k=large]').getAttribute('aria-pressed') === 'true'"), (a0, a1))
    pg.click("[data-act=pwZoom][data-k=serre]"); pg.wait_for_timeout(400)
    check("Serré : choix mémorisé", pg.evaluate("D.profil.pw_zoom === 'serre'"))
    pg.click("[data-act=pwRange][data-k='1m']"); pg.wait_for_timeout(400)
    check("le zoom reste choisi quand on change de période", pg.evaluate("document.querySelector('[data-act=pwZoom][data-k=serre]').getAttribute('aria-pressed') === 'true'"))
    check("zoom inconnu dans le profil : retombe sur Auto", pg.evaluate("(() => { D.profil.pw_zoom = 'zzz'; return pwZoom() === 'auto'; })()"))
    errs = [e for e in errs if "favicon" not in e]
    check("aucune erreur JavaScript", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails if fails else "aucun")
