"""Retours frère (2e passage) : preuves par capture des 7 points de la séance en direct. SHOTDIR=<dossier> python3 tests/capture_live_frere2.py"""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOT = pathlib.Path(os.environ["SHOTDIR"]); SHOT.mkdir(parents=True, exist_ok=True)
res = {}
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    cases = {
      "force": {"find": ["MUSCLE UP", "COMP"], "mod": {"series": "4", "reps": "1", "charge": "5"}, "prev": [[5, 1], [5, 1], [5, 1], [5, 1]], "w2": True},
      "renfo": {"find": ["RENFO", "CURL BICEPS"], "mod": {"series": "3", "reps": "11", "charge": "42"}, "prev": [[42, 11], [42, 11], [42, 12]], "w2": True},
      "compet": {"find": ["SQUAT", "COMP"], "mod": {}, "prev": [[85, 3]], "w2": True},
      "lest50": {"find": ["MUSCLE UP", "COMP"], "mod": {"series": "3", "reps": "1", "charge": "50"}, "prev": [[50, 1], [50, 1], [47.5, 1]], "w2": True},
      "squat140": {"find": ["SQUAT", "COMP"], "mod": {"series": "3", "reps": "3", "charge": "140"}, "prev": [[140, 3], [140, 3], [140, 3]], "w2": True},
      "curl22": {"find": ["RENFO", "CURL BICEPS"], "mod": {"series": "2", "reps": "10", "charge": "20"}, "prev": [[22, 10], [22, 10]], "prevPresc": "20", "w2": True},
    }
    for name, cs in cases.items():
        if os.environ.get('CASES') and name not in os.environ['CASES'].split(','): continue
        key = ev("""([f, w2]) => { const z = S.find(s => !s.archived && (!w2 || (+s.semaine) > 1) && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1])); return z && z.key; }""", [cs["find"], cs.get("w2")])
        ev("(k) => { live = null; store.set('sl4-live', null); }", key)
        ev("""([k, f, mod, prev, pp]) => { const z = seanceByKey(k), i = z.exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1]), e = z.exercices[i]; Object.assign(e, mod);
          const key = exKey(e), z0 = S.filter(s => s.idx === z.idx && rank(s.bloc) * 100 + (num(s.semaine) || 0) < rank(z.bloc) * 100 + (num(z.semaine) || 0)).sort((a, b) => (rank(b.bloc) * 100 + (num(b.semaine) || 0)) - (rank(a.bloc) * 100 + (num(a.semaine) || 0)))[0];
          if (pp) { const ez = z0.exercices.find(x => exKey(x) === key); if (ez) ez.charge = pp; }
          D.series = D.series.filter(x => x.ex !== key); D.series.push({id:null, date:'2026-10-28', bloc:z0.bloc, semaine:z0.semaine, seance:z0.seance, ex:key, charge:Math.max(...prev.map(s => s[0])), sets:prev.map(s => ({c:s[0], r:s[1]})), note:'', src:'app'}); window.__ci = i; }""", [key, cs["find"], cs["mod"], cs["prev"], cs.get("prevPresc")])
        ev("(k) => startLive(k)", key); pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
        ev("() => { live.i = window.__ci; renderLayer(); document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(600)
        pg.screenshot(path=str(SHOT / f"{name}-1-debut.png"))
        # fin de page : « Changer l'exercice / Modifier la séance » doivent sortir de sous la barre fixe
        ev("() => { const l = document.querySelector('.live'); l.scrollTop = l.scrollHeight; }"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(SHOT / f"{name}-2-bas-de-page.png"))
        res[name] = ev("""() => { const r = (s) => { const x = document.querySelector(s); if (!x) return null; const b = x.getBoundingClientRect(); return {top:Math.round(b.top), bottom:Math.round(b.bottom)}; };
          return {barre: r('.vbar'), changer: r('[data-act=swapOpen]'), modifier: r('[data-act=editOpen]'), prec: r('.vbar [data-d="-1"]'), suiv: r('.vbar [data-d="1"]'), valider: r('.vbar [data-act=doneSet]'), vh: innerHeight}; }""")
        ev("() => { document.querySelector('.live').scrollTop = 0; }")
        # valide la 1re série : minuteur de repos + RPE 1re série
        pg.click("[data-act=doneSet].btn") if pg.locator(".vbar [data-act=doneSet]").count() else None
        pg.wait_for_timeout(900)
        ev("() => { document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(SHOT / f"{name}-3-apres-serie1-repos.png"))
        res[name]["repos"] = ev("""() => { const x = document.querySelector('#restbox'); if (!x) return null; const b = x.getBoundingClientRect(), v = document.querySelector('.vbar').getBoundingClientRect(); return {haut:Math.round(b.top), bas:Math.round(b.bottom), barre_haut:Math.round(v.top), texte:x.innerText.replace(/\\s+/g,' ')}; }""")
        res[name]["rpe_apres_s1"] = ev("() => { const x = [...document.querySelectorAll('.lrh span')].map(s => s.textContent); return x; }")
        if pg.locator(".lrpe").count():
            ev("() => { document.querySelector('.lrpe').scrollIntoView({block:'center'}); }"); pg.wait_for_timeout(300)
            pg.screenshot(path=str(SHOT / f"{name}-4-rpe-serie1.png"))
        # valide toutes les séries : RPE dernière série
        for _ in range(8):
            if pg.locator(".vbar [data-act=doneSet]").count(): pg.click(".vbar [data-act=doneSet]"); pg.wait_for_timeout(500)
            else: break
        ev("() => { rest = null; renderLayer(); }"); pg.wait_for_timeout(300)
        res[name]["rpe_fin"] = ev("() => [...document.querySelectorAll('.lrh span')].map(s => s.textContent)")
        if pg.locator(".lrpe").count():
            ev("() => { const a = [...document.querySelectorAll('.lrpe')]; a[a.length - 1].scrollIntoView({block:'center'}); }"); pg.wait_for_timeout(300)
            pg.screenshot(path=str(SHOT / f"{name}-5-rpe-derniere.png"))
        ev("() => { live = null; store.set('sl4-live', null); renderLayer(); }"); pg.wait_for_timeout(200)
    # ce que le bouton « Voir l'exécution » ouvrait (retiré) : la fiche du mouvement, sans aucune consigne d'exécution
    if not os.environ.get('CASES') or 'compet' in os.environ['CASES']:
        ev("() => { page = {type:'lift', l:'SQUAT'}; renderLayer(); }"); pg.wait_for_timeout(1200)
        pg.screenshot(path=str(SHOT / "fiche-mouvement-squat.png")); res["fiche"] = ev("() => document.querySelector('.page').innerText.replace(/\\s+/g, ' ')")
    (SHOT / "mesures.json").write_text(json.dumps(res, ensure_ascii=False, indent=1)); print(json.dumps(res, ensure_ascii=False, indent=1)); print("erreurs :", errs)
    br.close()
