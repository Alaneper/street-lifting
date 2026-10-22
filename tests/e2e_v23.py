"""Version 23 : RPE jusqu'à 5, RPE de la 1re série pour les records, classement entre amis (podium, drapeaux, position)."""
import pathlib, json
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
    # RPE 5 : 30 kg × 1 à RPE 5 → 6 reps « à fond » (RTS 6 reps = 83,7 %)
    r = pg.evaluate("(() => { const e = e1rmOf('SQUAT', {c:30, r:1, rpe:5, date:D.today}); return [e.xe, Math.round(e.v * 10) / 10]; })()")
    check("RPE 5 pris en compte", r == [6, round(30 / 0.837, 1)], r)
    check("ajout d'un record : RPE 5 proposé", pg.evaluate("(ACT.openLift({l:'SQUAT'}), [...document.querySelectorAll('#prpe option')].some(o => o.value === '5'))")); pg.evaluate("ACT.closePage()")
    # RPE de la 1re série pour une séance notée dans l'app (4 × 4)
    r = pg.evaluate("""(() => { const s = S.find(z => z.faite && z.exercices.some(e => liftOf(e.mouvement) === 'SQUAT' && isCompEx(e) && num(e.rpe1)));
      const e = s.exercices.find(e => liftOf(e.mouvement) === 'SQUAT' && isCompEx(e) && num(e.rpe1));
      D.series.push({date:dateOf(s), bloc:s.bloc, semaine:s.semaine, seance:s.seance, ex:exKey(e), note:'L' + e.row, sets:[{c:77.7, r:4}, {c:77.7, r:4}, {c:77.7, r:4}, {c:77.7, r:4}]});
      const x = compSets('SQUAT').filter(y => y.c === 77.7); return [num(e.rpe1), x.length, x[0].rpe]; })()""")
    check("séance notée dans l'app : RPE de la 1re série repris", r[1] == 4 and r[2] == r[0], r)
    r = pg.evaluate("(() => { const b = repMaxes(compSets('SQUAT'))[3].b; return [b.c, b.rpe]; })()")
    check("record 4 reps : affiché avec le RPE de la 1re série", r[0] >= 77.7 and r[1] is not None, r)
    check("version 23 ou plus", int(pg.evaluate("APP_VER").split(" ")[0]) >= 23)
    check("aucune erreur console", not errs, errs[:5])
    br.close()
print("ÉCHECS :", fails)
