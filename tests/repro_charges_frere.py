"""Retours testeur C : séquence « curl 20 → 22 kg » et « squat 120 → 135 kg » rejouée semaine après semaine.
Marche sur n'importe quel arbre (v65, v68, niveau 85, retours-frère) : affiche la charge proposée à chaque semaine et ce qui est écrit dans le Sheet.
Usage : [SYNC=1] python3 tests/repro_charges_frere.py        (SYNC=1 : réglage « Mon Sheet est ma prog personnelle » actif, si la version le connaît)"""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SYNC = os.environ.get("SYNC") == "1"
CASES = {
  "curl biceps (renfo)": {"find": ["RENFO", "CURL BICEPS"], "presc": "20", "weeks": {"1": [[20, 13]], "2": [[22, 10], [22, 10]], "3": [[22, 10], [22, 10]]}},
  "squat compétition":   {"find": ["SQUAT", "COMP"], "presc": "120", "weeks": {"1": [[120, 3]], "2": [[125, 3]], "3": [[130, 3]], "4": [[135, 3]]}},
}
out = {}
with sync_playwright() as p:
    br = p.chromium.launch()
    for name, cs in CASES.items():
        c = br.new_context(viewport={"width":390, "height":844}, service_workers="block"); c.route("**/*", route)
        pg = c.new_page(); ev = pg.evaluate; errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://app.local/sl/"); pg.wait_for_timeout(800)
        pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
        # la prog du Sheet reste telle que le testeur l'a écrite : même charge prescrite toutes les semaines
        ev("""([coach, f, presc]) => { for (const [tab, g] of Object.entries(window.__sheets[coach])) { if (!/^BLOC/.test(tab)) continue;
            g.forEach(r => { for (let c = 2; c < r.length; c += 20) if (String(r[c]).trim() === f[0] && String(r[c + 1]).toUpperCase().trim() === f[1] && String(r[c + 5]).length) { if (f[1] === 'COMP' && String(r[c + 4]) !== '1') continue; r[c + 8] = presc; } }); } }""", [COACH, cs["find"], cs["presc"]])
        if SYNC: ev("([k, id]) => localStorage.setItem(k, JSON.stringify({[id]: true}))", ["sl4-chargesync", COACH])
        pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
        rows = []
        for w, did in cs["weeks"].items():
            r = ev("""async ([f, w, did]) => {
              const z = S.find(s => !s.archived && s.bloc === 1 && s.semaine === w && s.idx === 0 && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1])); if (!z) return {err:'séance introuvable'};
              live = null; store.set('sl4-live', null);
              const k = z.exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1] && (f[1] !== 'COMP' || String(e.series) === '1'));
              await startLive(z.key); const e = z.exercices[k], st = live.rows[k];
              const shown = st.sets.map(x => x.c), presc = e.charge, cell = () => { try { return window.__sheets['%s'][z.sheet][e.row - 1][z.cols.charge - 1]; } catch(err){ return 'n/a'; } };
              const before = cell(), n0 = window.__calls.filter(c => c[0] === 'update_values' && String(c[1]).indexOf(z.sheet) >= 0).length;
              st.sets = did.map(d => ({c:d[0], r:d[1], done:true})); st.dirty = true; await saveRow(k);
              const wl = window.__calls.filter(c => c[0] === 'update_values' && String(c[1]).indexOf(z.sheet) >= 0).slice(n0).map(c => String(c[1]).replace(/^'[^']*'!/, '')), wrote = wl.length;
              const ser = window.__sheets['%s'].SERIES.slice(-1)[0];
              live = null; store.set('sl4-live', null);
              return {semaine:w, charge_prescrite_dans_le_Sheet:presc, charge_proposee_par_l_app:shown, fait:did.map(d => d[0] + ' kg × ' + d[1]).join(' · '), case_Charge_apres:cell(), ecritures_dans_la_prog:wrote, cellules_ecrites_dans_la_prog:wl, ligne_carnet:ser}; }""" % (COACH, APP), [cs["find"], w, did])
            rows.append(r)
        out[name] = rows; out[name + " · erreurs JS"] = errs; c.close()
    br.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
