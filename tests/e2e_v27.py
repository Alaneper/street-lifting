"""Version 27 : valeurs pré-remplies d'une séance (une seule source d'historique, fourchette de reps, propagation de la charge, prog à jour)."""
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
    # une séance (s2) et son exercice de renfo (k) qui existe aussi la semaine d'avant (s1, même séance)
    r = pg.evaluate("""(() => { for (const s2 of S) for (let k = 0; k < s2.exercices.length; k++) { const e = s2.exercices[k]; if (norm(e.mouvement) !== 'RENFO' || !num(e.series)) continue;
        const key = exKey(e); if (s2.exercices.filter(x => exKey(x) === key).length !== 1) continue;
        const rk = z => rank(z.bloc) * 100 + (num(z.semaine) || 0);
        const s1 = S.filter(z => rk(z) < rk(s2) && z.idx === s2.idx && z.exercices.filter(x => exKey(x) === key).length === 1).sort((a, b) => rk(b) - rk(a))[0];
        if (s1) { const e1 = s1.exercices.find(x => exKey(x) === key); window.T = {s1:s1.key, s2:s2.key, k, key, row1:e1.row, n:Math.min(3, num(e.series))}; return window.T; } } return null; })()""")
    check("exercice de test trouvé", r is not None, r)
    # la semaine d'avant : noté 50 kg × 20, 20, 20 ; cette semaine : la prog dit 86, reps 8-12
    pg.evaluate("""(() => { const T = window.T, s1 = seanceByKey(T.s1), s2 = seanceByKey(T.s2), e = s2.exercices[T.k];
      D.series = D.series.filter(x => !(x.bloc === s1.bloc && x.semaine === s1.semaine && x.seance === s1.seance && x.ex === T.key));
      D.series.push({date:'2026-10-14', bloc:s1.bloc, semaine:s1.semaine, seance:s1.seance, ex:T.key, note:'L' + T.row1, sets:[{c:50, r:20}, {c:50, r:20}, {c:50, r:20}]});
      window.E = e; e.charge = '86'; e.reps = '8-12'; e.series = '3'; })()""")
    r = pg.evaluate("(() => { const s2 = seanceByKey(T.s2); return initSets(s2, s2.exercices[T.k], T.k).map(x => x.c + 'x' + x.r); })()")
    check("la prog dit 86 : TOUTES les séries à 86 (pas la semaine d'avant)", all(x.startswith("86x") for x in r) and len(r) == 3, r)
    check("reps d'avant (20) hors fourchette 8-12 : bas de la fourchette", all(x.endswith("x8") for x in r), r)
    pg.evaluate("window.E.charge = ''")
    r = pg.evaluate("(() => { const s2 = seanceByKey(T.s2); const a = initSets(s2, s2.exercices[T.k], T.k).map(x => x.c + 'x' + x.r), p = prevRowSets(s2, T.k); return [a, p && p.sets.map(x => x.c + 'x' + x.r)]; })()")
    check("sans charge dans la prog : charges = colonne « Précédent » (même source)", r[1] and [x.split("x")[0] for x in r[0]] == [x.split("x")[0] for x in r[1][:3]], r)
    pg.evaluate("window.E.charge = '86'; window.E.reps = '10-20'")
    r = pg.evaluate("(() => { const s2 = seanceByKey(T.s2); return initSets(s2, s2.exercices[T.k], T.k).map(x => x.r); })()")
    check("reps d'avant (20) dans la fourchette 10-20 : gardées", r == [20, 20, 20], r)
    # séance en direct : on change la charge de la série 1, les suivantes suivent
    pg.evaluate("window.E.charge = ''; window.E.reps = '10-20'")
    pg.evaluate("(async () => { store.del(ck('sl4-live')); live = null; await startLive(T.s2, T.k); })()"); pg.wait_for_timeout(600)
    r = pg.evaluate("live.rows[T.k].sets.map(x => x.c)")
    check("départ : séries à 50 (comme « Précédent »)", r == [50, 50, 50], r)
    pg.fill('[data-chg=setC][data-j="0"]', "86"); pg.press('[data-chg=setC][data-j="0"]', "Tab"); pg.wait_for_timeout(300)
    r = pg.evaluate("[live.rows[T.k].sets.map(x => x.c), [...document.querySelectorAll('[data-chg=setC]')].map(i => i.value)]")
    check("charge 86 en série 1 : séries 2 et 3 suivent (valeurs et écran)", r[0] == [86, 86, 86] and r[1][:3] == ["86", "86", "86"], r)
    pg.fill('[data-chg=setC][data-j="1"]', "60"); pg.press('[data-chg=setC][data-j="1"]', "Tab"); pg.wait_for_timeout(200)
    pg.fill('[data-chg=setC][data-j="0"]', "90"); pg.press('[data-chg=setC][data-j="0"]', "Tab"); pg.wait_for_timeout(200)
    r = pg.evaluate("live.rows[T.k].sets.map(x => x.c)")
    check("série 2 mise à 60 : la série 3 (qui la suivait) suit ; une charge à la main n'est plus écrasée par la série 1", r == [90, 60, 60], r)
    # prog mise à jour après l'ouverture : valeurs intactes → elles suivent la prog
    pg.evaluate("window.E.charge = '70'; (async () => { store.del(ck('sl4-live')); live = null; await startLive(T.s2, T.k); })()"); pg.wait_for_timeout(500)
    pg.evaluate("window.E.charge = '86'; renderLayer()"); pg.wait_for_timeout(300)
    r = pg.evaluate("live.rows[T.k].sets.map(x => x.c)")
    check("prog changée après l'ouverture (70 → 86) : séries non touchées mises à jour", r == [86, 86, 86], r)
    pg.evaluate("window.E.charge = '99'; renderLayer()"); pg.fill('[data-chg=setC][data-j="0"]', "88"); pg.press('[data-chg=setC][data-j="0"]', "Tab"); pg.wait_for_timeout(200)
    pg.evaluate("renderLayer()"); r = pg.evaluate("live.rows[T.k].sets.map(x => x.c)")
    check("séries déjà modifiées : jamais remplacées par la prog (99)", r == [88, 88, 88], r)
    check("version 27", pg.evaluate("APP_VER").startswith("27"))
    check("aucune erreur console", not [e for e in errs if "Failed to load resource" not in e], errs[:4])
    br.close()
print("ÉCHECS :", fails)
