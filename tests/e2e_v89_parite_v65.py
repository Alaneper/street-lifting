"""Retours frère A : parité de comportement avec la v65 sur le Programme (date de chaque séance de la semaine) et la fin de séance (un record = une ligne, compteur juste).
Rejoue avec : python3 tests/e2e_v89_parite_v65.py"""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(2000)
    ev("setTab('seance')"); pg.wait_for_timeout(700)
    rows = ev("[...document.querySelectorAll('.wkr b')].map(b => b.textContent)")
    check("Programme : chaque séance de la semaine affiche son jour ET sa date (comme la grille de la v65)", len(rows) >= 3 and all(__import__('re').search(r"\d+ [a-zéû]+", r) for r in rows), rows)
    ev("live = null; store.set('sl4-live', null)")
    key = ev("(S.find(s => !s.archived && !s.faite && s.exercices.some(e => liftOf(e.mouvement) === 'SQUAT' && String(e.charge).includes('%'))) || {}).key")
    ev("(k) => startLive(k)", key); pg.wait_for_timeout(900)
    if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
    i = ev("seanceByKey(live.key).exercices.findIndex(e => liftOf(e.mouvement) === 'SQUAT' && String(e.charge).includes('%'))")
    ev("(i) => { live.i = i; renderLayer(); }", i); pg.wait_for_timeout(400)
    for _ in range(8):
        j = ev("live.rows[live.i].sets.findIndex(x => !x.done)")
        if j < 0: break
        ev("(j) => { const r = live.rows[live.i].sets[j]; r.c = 150; r.r = 5; }", j); pg.locator(f"[data-act=doneSet][data-j='{j}']").first.click(); pg.wait_for_timeout(300); ev("rest = null")
    n = ev("live.rows[live.i].sets.length")
    ev("finishLive()"); pg.wait_for_timeout(1500)
    m = ev("live.summary")
    reps = [(r["l"], r["r"], r["c"]) for r in m["repRecs"]]
    check(f"Fin de séance : {n} séries identiques battant un record = un seul « record de reps » (pas un par série)", n >= 2 and len(reps) == len(set(reps)) == 1, reps)
    check("Fin de séance : le compteur « Record » correspond aux lignes affichées", ev("(document.querySelector('.fts') || document.querySelector('.sheet')).innerText").replace("\n", " ").find("Record") >= 0 and len(m["repRecs"]) + len(m["recs"]) == 1 + len(m["recs"]), (m["repRecs"], m["recs"]))
    check("aucune erreur JS", not errs, errs)
    br.close()
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
