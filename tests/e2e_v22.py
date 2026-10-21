"""Version 22 : retrait de « dernière fois » en séance et de la dépense du jour ; records par reps avec RPE et date."""
import pathlib, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(2500)
    # Séance : plus de « Séries · dernière fois (Bloc 5, S3) »
    key = pg.evaluate("(nextSeance()||S.at(-1)).key"); pg.evaluate(f"startLive({json.dumps(key)}, 1)"); pg.wait_for_timeout(500); pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(300)
    t = pg.evaluate("document.querySelector('.live').textContent")
    check("séance : plus de « dernière fois »", "dernière fois" not in t and "charge prévue" not in t)
    check("séance : le tableau des séries reste", pg.evaluate("!!document.querySelector('.live .setrow')"))
    pg.evaluate("live = null; renderLayer(); store.del(ck('sl4-live'))")
    # Alimentation : plus de dépense du jour ni de montre
    pg.evaluate("setTab('corps'); corpsTab = 'nutri'; D.profil.nut_objectif = 'suivi'; rCorps()"); pg.wait_for_timeout(400)
    t = pg.evaluate("document.querySelector('#v-corps').textContent")
    check("alimentation : plus de « Dépense du jour » ni de montre", "Dépense" not in t and "montre" not in t and pg.evaluate("!document.querySelector('#ndep')"))
    pg.evaluate("D.profil.nut_objectif = 'perte'; rCorps()"); pg.wait_for_timeout(300)
    t = pg.evaluate("document.querySelector('#v-corps').textContent")
    check("alimentation : cible calculée sans la montre", "Cible du jour" in t and "Dépense" not in t, t[t.find("Mon objectif"):t.find("Mon objectif") + 200])
    check("Méthodes : plus de montre", "montre" not in pg.evaluate("(ACT.settings(), document.querySelector('.sheet').textContent)")); pg.evaluate("ACT.closeSheet()")
    check("carnet : l'onglet DEPENSE n'est plus lu", not any("DEPENSE" in a for a in pg.evaluate("window.__api")))
    # 1RM estimé avec le RPE : 30 kg × 1 à RPE 6 ≠ 1RM de 30 kg
    r = pg.evaluate("""(() => { const w = bwAt(D.today), e = e1rmBest('SQUAT', [{c:30, r:1, rpe:6, date:D.today}]); const e2 = e1rmOf('SQUAT', {c:30, r:1, rpe:6, date:D.today}); return [Math.round(e.v * 10) / 10, Math.round(30 / 0.863 * 10) / 10, e2.xe]; })()""")
    check("1RM estimé : 30 kg × 1 à RPE 6 → ≈ 34,8 kg (RPE pris en compte jusqu'à 6)", r[0] == r[1] and r[2] == 5, r)
    # Records par reps : RPE affiché, à charge égale le RPE le plus bas l'emporte, toutes les perfs datées
    r = pg.evaluate("""(() => { const rm = repMaxes([{c:25, r:3, rpe:7, date:'2026-09-01'}, {c:25, r:3, rpe:6, date:'2026-10-01'}, {c:24, r:3, rpe:5, date:'2026-08-01'}]); return [rm[2].b.c, rm[2].b.rpe]; })()""")
    check("records : à charge égale, le RPE le plus bas est le record", r == [25, 6], r)
    pg.evaluate("ACT.openLift({l:'SQUAT'})"); pg.wait_for_timeout(1500)
    r = pg.evaluate("[...document.querySelectorAll('.rm .rpe-at')].map(e => e.textContent)")
    check("records : RPE affiché dans les cases (« @9 »)", len(r) > 0 and all(x.startswith("@") for x in r), r)
    n = pg.evaluate("[...document.querySelectorAll('.rm')].find(e => e.dataset.act === 'rmInfo').dataset.n")
    pg.evaluate(f"ACT.rmInfo({{l:'SQUAT', n:'{n}'}})"); pg.wait_for_timeout(400)
    r = pg.evaluate("[...document.querySelectorAll('.sheet .item')].map(e => e.textContent.replace(/\\s+/g, ' ').trim().slice(0, 120))")
    check("détail d'un record : chaque perf avec son RPE et sa date", len(r) > 0 and all(("RPE" in x) and any(m in x for m in ["2025", "2026", "Date inconnue"]) for x in r), r[:3])
    pg.evaluate("ACT.closeSheet()")
    # Ajouter un record avec son RPE (colonne F du carnet)
    pg.fill("#prc", "121"); pg.fill("#prr", "1"); pg.select_option("#prpe", "8"); pg.click("[data-act=addPR]"); pg.wait_for_timeout(900)
    r = pg.evaluate(f"window.__sheets['{APP}'].PR.at(-1)")
    check("ajout d'un record : RPE enregistré dans le carnet", str(r[5]) == "8" and str(r[2]) == "121", r)
    check("version 22", pg.evaluate("APP_VER").startswith("22"))
    check("aucune erreur console", not errs, errs[:5])
    br.close()
print("ÉCHECS :", fails)
