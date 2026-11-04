"""Retours frère, lot B : séance en direct. Toutes les séries visibles, format « 5 kg × 1 rép. », propagation de la charge, RPE 1re et dernière série,
prescription en grand, « Dernière fois » série par série, série en cours agrandie. Captures : SHOTDIR=<dossier>."""
import pathlib, os, json, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOT = pathlib.Path(os.environ["SHOTDIR"]) if os.environ.get("SHOTDIR") else None
if SHOT: SHOT.mkdir(parents=True, exist_ok=True)
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
def shot(pg, name):
    if SHOT: pg.screenshot(path=str(SHOT / (name + ".png")))
CASES = {
  "force":  {"find": ["MUSCLE UP", "COMP"],      "mod": {"series": "4", "reps": "1", "charge": "5"},  "prev": [[5, 1], [5, 1], [5, 1], [5, 1]]},
  "renfo":  {"find": ["RENFO", "CURL BICEPS"],   "mod": {"series": "3", "reps": "11", "charge": "42"}, "prev": [[42, 11], [42, 11], [42, 12]]},
  "compet": {"find": ["SQUAT", "COMP"],          "mod": {},                                          "prev": [[85, 3]]},
  "neuf":   {"find": ["RENFO", "CURL BICEPS"],   "mod": {"variation": "EXERCICE JAMAIS FAIT", "series": "3", "reps": "10", "charge": "20"}, "prev": None},
}
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    def open_case(name):
        cs = CASES[name]
        key = ev("""(f) => { const z = S.find(s => !s.archived && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1])); return z && z.key; }""", cs["find"])
        ev("() => { live = null; store.set('sl4-live', null); }")
        ev("""([k, f, mod, prev]) => { const z = seanceByKey(k), i = z.exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1]), e = z.exercices[i]; Object.assign(e, mod);
          const key = exKey(e), z0 = S.filter(s => s.idx === z.idx && s !== z).sort((a, b) => (b.bloc - a.bloc) || ((+b.semaine) - (+a.semaine)))[0];
          D.series = D.series.filter(x => x.ex !== key); if (prev) D.series.push({id:null, date:'2026-10-28', bloc:z0.bloc, semaine:z0.semaine, seance:z0.seance, ex:key, charge:Math.max(...prev.map(s => s[0])), sets:prev.map(s => ({c:s[0], r:s[1]})), note:'', src:'app'}); window.__ci = i; }""", [key, cs["find"], cs["mod"], cs["prev"]])
        ev("(k) => startLive(k)", key); pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
        ev("() => { live.i = window.__ci; renderLayer(); document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(500)
    def txt(sel): return ev("(s) => { const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g, ' ').trim() : null; }", sel)
    def rows_txt(): return ev("() => [...document.querySelectorAll('.live .lsr')].map(r => r.className + ' | ' + (r.querySelector('.w') ? r.querySelector('.w').innerText : [...r.querySelectorAll('input')].map(i => i.value).join('/')))")
    def sets(): return ev("() => live.rows[live.i].sets.map(s => [s.c, s.r, s.done])")
    def set_input(j, val, which=0):
        loc = pg.locator(f".live .lsr[data-j='{j}'] input").nth(which); loc.fill(val); loc.dispatch_event("change"); pg.wait_for_timeout(150)

    # ============ B1, B2, B5, B6, B7 sur les trois cas
    for name in ("force", "renfo", "compet"):
        open_case(name); n = ev("live.rows[live.i].sets.length")
        shot(pg, f"{name}-1")
        check(f"{name} · B1 toutes les séries visibles ({n})", ev("document.querySelectorAll('.live .lsr').length") == n, rows_txt())
        check(f"{name} · B1 une seule série mise en avant (en cours)", ev("document.querySelectorAll('.live .lsr.cur').length") == 1)
        check(f"{name} · B1 « il en reste » visible", re.search(r"il en reste %d" % n, txt(".live .lsh") or "") is not None or n == 1, txt(".live .lsh"))
        check(f"{name} · B1 case à cocher sur chaque série", ev("[...document.querySelectorAll('.live .lsr')].every(r => r.querySelector('.ck'))"))
        bad = ev("""() => { const t = [...document.querySelectorAll('.live .lsr, .live .lastt')].map(e => e.innerText.replace(/\\s+/g, ' ')).join(' | '); return t.match(/(?<![\\d,])\\d+(?:,\\d+)?\\s×\\s\\d+(?!\\d|\\s*rép)/g); }""")
        check(f"{name} · B2 jamais « 5 × 1 » (toujours « kg × N rép. »)", not bad, bad)
        check(f"{name} · B2 chaque ligne se lit « … kg × N rép. »", all(re.search(r"(kg|Poids du corps) × \d+ rép\.|kg\s*×", r) for r in rows_txt() if r.startswith("lsr |") or r.startswith("lsr done |")), rows_txt())
        m = ev("""() => { const n = document.querySelector('.live .lx-n'), p = document.querySelector('.live .lx-p'), d = document.querySelector('.live .lx-d');
          return {n: n && n.innerText, p: p && p.innerText, d: d && d.innerText, fn: n && parseFloat(getComputedStyle(n).fontSize), fp: p && parseFloat(getComputedStyle(p).fontSize), fd: d && parseFloat(getComputedStyle(d).fontSize)}; }""")
        check(f"{name} · B5 nom et prescription en grand, détails en petit", m["n"] and m["p"] and m["fn"] >= 30 and m["fp"] >= 24 and (m["fd"] is None or m["fd"] <= 14), m)
        h = ev("""() => { const r = [...document.querySelectorAll('.live .lsr')]; const c = document.querySelector('.live .lsr.cur'); return {cur: Math.round(c.getBoundingClientRect().height), autres: r.filter(x => x !== c).map(x => Math.round(x.getBoundingClientRect().height)), f: parseFloat(getComputedStyle(c.querySelector('input')).fontSize)}; }""")
        check(f"{name} · B7 série en cours agrandie dans la liste complète", h["cur"] >= 76 and all(x <= 64 for x in h["autres"]) and h["f"] >= 28, h)
        check(f"{name} · B6 « Dernière fois » visible", "DERNIÈRE FOIS" in (txt(".live .lastt") or "").upper(), txt(".live .lastt"))
        m_ = m
        if name == "force": check("force · B5 « 4 × 1 à +5 kg »", m_["p"] == "4 × 1 à +5 kg", m_)
        if name == "force": check("force · B6 dernière fois série par série", "+5 kg × 1-1-1-1 rép." in txt(".live .lastt"), txt(".live .lastt"))
        if name == "renfo":
            check("renfo · B5 « 3 × 11 à 42 kg »", m_["p"] == "3 × 11 à 42 kg", m_)
            check("renfo · B6 « 42 kg × 11-11-12 rép. » (série par série)", "42 kg × 11-11-12 rép." in txt(".live .lastt"), txt(".live .lastt"))
            check("renfo · B4 aucun RPE demandé en renfo", ev("document.querySelectorAll('.live .lrpe').length") == 0)
    # ============ B6 : aucun historique
    open_case("neuf")
    check("neuf · B6 sans historique : le dit clairement", "aucune série notée" in (txt(".live .lastt") or ""), txt(".live .lastt"))

    # ============ B3 : propagation de la charge (comportement v65) et séries modifiables
    open_case("force")
    set_input(0, "7,5")
    check("B3 changer la charge de la 1re série la propage aux suivantes (données)", [s[0] for s in sets()] == [7.5, 7.5, 7.5, 7.5], sets())
    check("B3 … et l'affichage des séries suivantes suit", all("+7,5 kg × 1 rép." in r for r in rows_txt()[1:]), rows_txt())
    pg.click(".live .lsr[data-j='2'] .lt"); pg.wait_for_timeout(300)
    set_input(2, "10")   # une série modifiée à la main
    set_input(0, "8")
    check("B3 comme en v65 : une charge modifiée à la main reste, les séries suivantes qui avaient l'ancienne charge suivent", [s[0] for s in sets()] == [8, 8, 10, 10], sets())
    check("B3 chaque série reste modifiable (champ de saisie ouvert au toucher)", ev("document.querySelectorAll('.live .lsr.ed input, .live .lsr.cur input').length") >= 4)
    # ============ B4 : RPE sur la 1re et la dernière série, comme en v65
    check("B4 pas de RPE tant que la 1re série n'est pas faite", ev("document.querySelectorAll('.live .lrpe').length") == 0)
    pg.click(".live .lsr.cur .ck"); pg.wait_for_timeout(700); ev("() => { rest = null; renderLayer(); }"); pg.wait_for_timeout(300)
    check("B4 après la 1re série : « RPE de la 1re série »", "RPE de la 1re série" in (txt(".live .lrpe") or ""), txt(".live .lrpe"))
    check("B4 … et pas encore celui de la dernière", "dernière" not in " ".join(ev("[...document.querySelectorAll('.live .lrpe .lrh span')].map(x => x.innerText)")))
    pg.click(".live .lrpe [data-act=rpe][data-v='8']"); pg.wait_for_timeout(200)
    for j in (1, 2, 3):
        pg.click(f".live .lsr[data-j='{j}'] .ck"); pg.wait_for_timeout(500); ev("() => { rest = null; renderLayer(); }"); pg.wait_for_timeout(150)
    labs = ev("[...document.querySelectorAll('.live .lrpe .lrh span')].map(x => x.innerText)")
    check("B4 toutes les séries faites : RPE de la 1re ET de la dernière série", any("1re" in l for l in labs) and any("dernière" in l for l in labs), labs)
    pg.locator(".live .lrpe").last.locator("[data-act=rpe][data-v='9']").click(); pg.wait_for_timeout(200)
    shot(pg, "force-4-toutes-faites")
    check("B1 série faite : lumières allumées sur les 4 lignes", ev("document.querySelectorAll('.live .lights.on, .live .lights.rec').length") == 4)
    ex = ev("({r1: live.rows[live.i].rpe1, rL: live.rows[live.i].rpeLast})")
    check("B4 RPE 8 sur la 1re et 9 sur la dernière", ex == {"r1": 8, "rL": 9}, ex)
    cell = ev("""() => { const s = seanceByKey(live.key), e = s.exercices[live.i]; return [s.cols.rpe1, s.cols.rpeLast, e.row, s.sheet]; }""")
    pg.click("[data-act=liveNav][data-d='1']"); pg.wait_for_timeout(1200)
    got = ev("(a) => { const g = window.__sheets['%s'][a[3]]; return [(g[a[2] - 1] || [])[a[0] - 1], (g[a[2] - 1] || [])[a[1] - 1]]; }" % COACH, cell)
    check("B4 les deux RPE partent dans les colonnes du coach (RPE S1 et dernière série)", got == ["8", "9"] or got == [8, 9] or got == ["8", "9"], got)
    srow = ev("window.__sheets['%s'].SERIES.slice(-1)[0]" % APP)
    check("B3/B4 le carnet garde la charge de chaque série faite (8, 8, 10, 10)", srow and srow[6] == "1@8, 1@8, 1@10, 1@10", srow)
    check("aucune erreur JS", not errs, errs)
    br.close()
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
