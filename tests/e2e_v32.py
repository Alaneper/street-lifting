"""Version 32 : RPE visé par le coach (colonne « INTENSITÉ CIBLE ») affiché dans la séance, la fiche et la séance en direct."""
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
    cases = {"7": "RPE visé 7", "RPE 7": "RPE visé 7", "@8": "RPE visé 8", "7-8": "RPE visé 7 à 8", "6,5 - 7,5": "RPE visé 6,5 à 7,5",
             "≤ 7": "RPE max 7", "max 7": "RPE max 7", "ne pas dépasser RPE 7": "RPE max 7", "75%": "Intensité visée 75%", "4x4 RPE 7": "RPE visé 7", "": None}
    r = pg.evaluate("c => Object.fromEntries(Object.keys(c).map(t => { const x = rpeCible({intensite:t}); return [t, x && x.lab]; }))", cases)
    for t, want in cases.items(): check(f"lecture « {t} »", r[t] == want, r[t])
    pg.evaluate("""(() => { const s = S.find(z => z.exercices.some(e => liftOf(e.mouvement))); const k = s.exercices.findIndex(e => liftOf(e.mouvement));
      window.T = {s:s.key, k}; s.exercices[k].intensite = 'max 7'; })()""")
    r = pg.evaluate("presc(seanceByKey(T.s).exercices[T.k])")
    check("fiche de la séance : « RPE max 7 » dans la prescription", "RPE max 7" in r, r)
    pg.evaluate("(async () => { store.del(ck('sl4-live')); live = null; await startLive(T.s, T.k); })()"); pg.wait_for_timeout(600)
    r = pg.evaluate("(document.querySelector('.rpecible')||{}).textContent || ''")
    check("séance en direct : encadré « RPE max 7 » visible", "RPE max 7" in r and "ne pas dépasser" in r, r)
    pg.evaluate("live.rows[T.k].rpe1 = 8; renderLayer()"); pg.wait_for_timeout(200)
    r = pg.evaluate("[document.querySelector('.rpecible').className, document.querySelector('.rpecible').textContent]")
    check("RPE noté 8 > 7 : alerte « au-dessus de la consigne »", "over" in r[0] and "Au-dessus" in r[1], r)
    pg.evaluate("seanceByKey(T.s).exercices[T.k].intensite = ''; renderLayer()"); pg.wait_for_timeout(200)
    check("case vide : aucun encadré (rien ne change pour les progs sans RPE visé)", pg.evaluate("!document.querySelector('.rpecible')"))
    check("version 32 ou plus", float(pg.evaluate("APP_VER").split(" ")[0]) >= 32)
    check("aucune erreur console", not [e for e in errs if "Failed to load resource" not in e], errs[:4])
    br.close()
print("ÉCHECS :", fails if fails else "aucun"); import sys; sys.exit(1 if fails else 0)
