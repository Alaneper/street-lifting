"""Retours frère D : graphique de poids. Rejoue avec : python3 tests/e2e_v88_poids_frere.py"""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    def jeu(n):
        ev("""(n) => { const base = new Date(D.today + 'T12:00:00'); D.poids = []; for (let i = n - 1; i >= 0; i--) { const d = new Date(base); d.setDate(d.getDate() - i); const saw = [0.9, -0.6, 0.4, -1.0, 0.7, -0.2, 0.1][i % 7]; D.poids.push({id: 2000 + i, date: isoOf(d), poids: Math.round((80.5 - (n - 1 - i) * 0.02 + saw) * 10) / 10}); } pwRange = 'all'; pwAnim = false; corpsTab = 'poids'; corpsManual = D.today; setTab('corps'); rCorps(); }""", n); pg.wait_for_timeout(700)
    jeu(100)
    check("D · ligne grise fine des pesées du jour (dents de scie) + ligne de tendance 7 j", ev("!!document.querySelector('svg[data-ich=pw] .pw-daily') && !!document.querySelector('svg[data-ich=pw] .pw-line')"))
    check("D · plus de 15 pesées : pas de points (seulement au toucher)", ev("document.querySelectorAll('svg[data-ich=pw] circle').length") <= 2)
    tx = ev("[...document.querySelectorAll('svg[data-ich=pw] text')].map(t => t.textContent)")
    dates = [t for t in tx if not t.endswith("kg")]
    check("D · échelle verticale graduée en kg", 3 <= sum(1 for t in tx if t.endswith(" kg") and not t.startswith("Limite")) <= 4, tx)
    check("D · 5 dates en bas", len(dates) == 5, dates)
    check("D · limite de catégorie : ligne rouge pointillée", ev("(() => { const l = [...document.querySelectorAll('svg[data-ich=pw] line')].find(x => x.getAttribute('stroke-dasharray')); return !!l && l.getAttribute('stroke') === 'var(--bad)'; })()") or "Limite" not in " ".join(tx), tx)
    av = ev("(document.querySelector('.pw-av')||{innerText:''}).innerText")
    check("D · ligne « Tendance · Moyenne · Min, max »", all(w in av for w in ["Tendance", "Moyenne", "Min, max"]), av)
    check("D · périodes : 7 j, 1 mois, 3 mois, 6 mois, 1 an, 2 ans, Tout", ev("[...document.querySelectorAll('.rng.pwr button')].map(b => b.textContent)") == ["7 j", "1 mois", "3 mois", "6 mois", "1 an", "2 ans", "Tout"])
    check("D · les 7 périodes tiennent sur 390 px sans défilement horizontal", ev("(() => { const r = document.querySelector('.rng.pwr'); return r.scrollWidth <= r.clientWidth + 1; })()"))
    check("D · phrase explicative sous le graphique", "ligne grise" in ev("(document.querySelector('.pw-ex')||{innerText:''}).innerText") and "7 derniers jours" in ev("(document.querySelector('.pw-ex')||{innerText:''}).innerText"))
    for k in ("6m", "2a", "1a"):
        pg.click(f"[data-act=pwRange][data-k='{k}']"); pg.wait_for_timeout(350)
        check(f"D · période « {k} » dessine le graphique", ev("!!document.querySelector('svg[data-ich=pw] .pw-daily')"))
    jeu(10)
    check("D · moins de 15 pesées : points visibles", ev("document.querySelectorAll('svg[data-ich=pw] circle').length") >= 10)
    check("aucune erreur JS", not errs, errs)
    br.close()
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
