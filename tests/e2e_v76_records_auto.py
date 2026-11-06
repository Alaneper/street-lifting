"""v76 : record de 1 rép. mis à jour par les séries faites (prog ou séance), total et classement qui suivent ;
ligne « Charge la plus lourde » ; une ligne de séance gardée d'une ouverture précédente ne sert qu'au même exercice."""
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

    # 1 · record auto depuis une série de 1 rép. notée en séance
    L = pg.evaluate("""(() => { for (const l of ALL_LIFTS) { if (best(l) === null) continue; for (const s of S) for (const e of s.exercices) if (liftOf(e.mouvement) === l && isCompEx(e)) return [l, exKey(e)]; } return null; })()""")
    check("point de départ : un mouvement avec record et ligne de compétition", L is not None)
    l, EX = L
    ev2 = lambda js: pg.evaluate(js.replace("{l}", l).replace("{EX}", EX))
    base = pg.evaluate(f"({{b:best('{l}'), t:totalOf(LIFTS.includes('{l}') ? 'street' : 'power'), prs:D.prs.length}})")
    pg.evaluate(f"""(() => {{ const z = S[0], tpl = D.series[0] || {{}}; D.series.push(Object.assign({{}}, tpl, {{date:D.today, bloc:z.bloc, semaine:z.semaine, seance:z.seance, ex:{EX!r}, sets:[{{c:best('{l}') + 7.5, r:1}}], note:''}})); saveCache(); }})()""")
    r = pg.evaluate(f"({{b:best('{l}'), t:totalOf(LIFTS.includes('{l}') ? 'street' : 'power'), prs:D.prs.length, bs:bestSeries('{l}').at(-1)}})")
    check(f"1 rép. plus lourde faite en séance ({l}) : le record monte tout seul", r["b"] == base["b"] + 7.5, (base, r))
    check("le total suit (donc le classement entre amis)", r["t"] - base["t"] == 7.5, (base, r))
    check("l'onglet PR n'est pas modifié", r["prs"] == base["prs"])
    check("la courbe des records a le nouveau point, marqué automatique", r["bs"]["auto"] is True and r["bs"]["v"] == r["b"], r["bs"])
    ev2("ACT.openLift({l:'{l}'})"); pg.wait_for_timeout(500)
    hero = pg.evaluate("(document.querySelector('.rhero') || {}).innerText || ''")
    check("fiche Squat : le grand chiffre est le nouveau record, avec « en séance »", str(int(r["b"])) in hero.replace(" ", "").replace(" ", "") and "en séance" in hero, hero[:200])
    # une série de plusieurs reps plus lourde n'est pas un record
    ev2("""(() => { const z = S[0], tpl = D.series[0]; D.series.push(Object.assign({}, tpl, {date:D.today, bloc:z.bloc, semaine:z.semaine, seance:z.seance, ex:'{EX}', sets:[{c:best('{l}') + 20, r:3}], note:''})); saveCache(); renderLayer(); })()""")
    pg.wait_for_timeout(400)
    r2 = ev2("({b:best('{l}'), line:(document.querySelector('.rheavy') || {}).innerText || ''})")
    check("3 reps plus lourdes : le record de 1 rép. ne bouge pas", r2["b"] == r["b"], r2)
    check("ligne « Charge la plus lourde » (ou « Lest le plus lourd ») : charge et reps", ("Charge la plus lourde" in r2["line"] or "Lest le plus lourd" in r2["line"]) and "× 3" in r2["line"], r2)
    # une série future (date après aujourd'hui) ne compte pas
    ev2("""(() => { const z = S[0], tpl = D.series[0]; D.series.push(Object.assign({}, tpl, {date:addDays(D.today, 5), bloc:z.bloc, semaine:z.semaine, seance:z.seance, ex:'{EX}', sets:[{c:best('{l}') + 50, r:1}], note:''})); saveCache(); })()""")
    check("une série datée dans le futur ne devient pas un record", pg.evaluate(f"best('{l}') === {r['b']}"))
    # totalSeries ne casse pas les records (plus de remplacement temporaire de D.prs)
    check("courbe du total : calculée sans toucher aux records", pg.evaluate(f"(() => {{ const n = D.prs.length; const ts = totalSeries('power'); return ts.length > 0 && D.prs.length === n && best('{l}') === {r['b']}; }})()"))
    pg.evaluate("page = null; renderLayer()")

    # 2 · séance en direct : une ligne gardée d'un autre exercice est refaite
    info = pg.evaluate("""(() => { const s = S.find(z => z.exercices.some(e => !liftOf(e.mouvement) && !isCardioEx(e) && num(e.series) >= 3)); if (!s) return null;
      const k = s.exercices.findIndex(e => !liftOf(e.mouvement) && !isCardioEx(e) && num(e.series) >= 3), e = s.exercices[k];
      store.set('sl4-live', {key:s.key, start:Date.now(), i:k, rows:{[k]:{ex:'AUTRE · EXERCICE', sets:[{c:10, r:5, done:true}, {c:10, r:5, done:true}], cnt:true, dirty:false}}, pdc:true});
      return {key:s.key, k, n:num(e.series)}; })()""")
    check("il existe un exercice à 3 séries ou plus", info is not None)
    if info:
        pg.evaluate(f"startLive({info['key']!r}, {info['k']})"); pg.wait_for_timeout(700)
        n = pg.evaluate(f"live.rows[{info['k']}].sets.length")
        check(f"ligne gardée d'un autre exercice : refaite avec les {info['n']} séries prévues", n == info["n"], n)
        pg.evaluate("live = null; store.del ? store.del('sl4-live') : store.set('sl4-live', null); renderLayer()")
    errs = [e for e in errs if "favicon" not in e]
    check("aucune erreur JavaScript", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails if fails else "aucun")
