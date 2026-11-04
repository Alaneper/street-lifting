"""Retours frère B : captures de la séance en direct sur 3 cas (force 4 × 1 à charge ajoutée, renfo 3 × 11 à 42 kg, compétition avec disques).
Usage : SHOTDIR=<dossier> python3 tests/capture_live_frere.py   (marche sur n'importe quel arbre : v65/v68 avec le même jeu de test)"""
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
    # historique de la semaine précédente (carnet de l'app) pour « Dernière fois » : mêmes exercices, séries notées
    cases = {
      "force": {"find": ["MUSCLE UP", "COMP"], "mod": {"series": "4", "reps": "1", "charge": "5"}, "prev": [[5, 1], [5, 1], [5, 1], [5, 1]]},
      "renfo": {"find": ["RENFO", "CURL BICEPS"], "mod": {"series": "3", "reps": "11", "charge": "42"}, "prev": [[42, 11], [42, 11], [42, 12]]},
      "compet": {"find": ["SQUAT", "COMP"], "mod": {}, "prev": [[85, 3]]},
    }
    for name, cs in cases.items():
        key = ev("""(f) => { const z = S.find(s => !s.archived && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1])); return z && z.key; }""", cs["find"])
        ev("(k) => { live = null; store.set('sl4-live', null); }", key)
        ev("""([k, f, mod, prev]) => { const z = seanceByKey(k), i = z.exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1]), e = z.exercices[i]; Object.assign(e, mod);
          const key = exKey(e), z0 = S.filter(s => s.idx === z.idx && s !== z).sort((a, b) => (b.bloc - a.bloc) || ((+b.semaine) - (+a.semaine)))[0];
          D.series = D.series.filter(x => x.ex !== key); D.series.push({id:null, date:'2026-10-28', bloc:z0.bloc, semaine:z0.semaine, seance:z0.seance, ex:key, charge:Math.max(...prev.map(s => s[0])), sets:prev.map(s => ({c:s[0], r:s[1]})), note:'', src:'app'}); window.__ci = i; }""", [key, cs["find"], cs["mod"], cs["prev"]])
        ev("(k) => startLive(k)", key); pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
        ev("() => { live.i = window.__ci; renderLayer(); document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(600)
        pg.screenshot(path=str(SHOT / f"{name}-1-debut.png"))
        res[name] = ev("""() => { const r = document.querySelector('.live'); return {sets_visibles: r.querySelectorAll('.lsr, .setrow').length, lignes: [...r.querySelectorAll('.lsr, .setrow')].map(x => x.innerText.replace(/\\s+/g, ' ').trim()), texte: r.innerText.replace(/\\s+/g, ' ').slice(0, 420)}; }""")
        # valide la 1re série puis capture
        pg.click("[data-act=doneSet]"); pg.wait_for_timeout(900)
        ev("() => { rest = null; renderLayer(); }"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(SHOT / f"{name}-2-apres-serie1.png"))
        ev("() => { closeLive && closeLive(); }") if False else None
        ev("() => { live = null; store.set('sl4-live', null); renderLayer(); }"); pg.wait_for_timeout(200)
    (SHOT / "mesures.json").write_text(json.dumps(res, ensure_ascii=False, indent=1)); print(json.dumps(res, ensure_ascii=False, indent=1)[:2500]); print("erreurs :", errs)
    br.close()
