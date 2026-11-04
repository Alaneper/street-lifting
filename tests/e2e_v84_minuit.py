"""Retours frère, point 0 : une pesée et une séance faites juste après minuit (heure de Bruxelles, hiver et été) sont datées du jour même,
jamais de la veille, y compris quand l'app était déjà ouverte avant minuit. Rejoue avec : python3 tests/e2e_v84_minuit.py"""
import pathlib, os, datetime, zoneinfo
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
BX = zoneinfo.ZoneInfo("Europe/Brussels")
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)

def scenario(label, depart, apres_minuit, croise, live_avant=False):
    """depart : heure d'ouverture de l'app ; croise : l'app reste ouverte et on avance jusqu'à apres_minuit ; sinon ouverture directe à apres_minuit."""
    t0 = datetime.datetime.fromisoformat(depart if croise else apres_minuit).replace(tzinfo=BX)
    t1 = datetime.datetime.fromisoformat(apres_minuit).replace(tzinfo=BX)
    attendu = t1.strftime("%Y-%m-%d"); veille = (t1 - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels")
    c.route("**/*", route); c.clock.install(time=t0)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    ev = pg.evaluate
    ev("setTab('corps'); corpsTab = 'poids'; rCorps()"); pg.wait_for_timeout(300)   # l'onglet Poids reste affiché pendant le passage de minuit
    key = ev("(() => { const s = S.find(x => !x.archived && x.exercices.some(e => !isCardioEx(e))); return s && s.key; })()")
    jour_seance = attendu
    if live_avant:   # séance commencée avant minuit : toutes ses séries portent le jour où elle a commencé
        ev(f"startLive({key!r})"); pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
        jour_seance = t0.strftime("%Y-%m-%d")
    if croise:
        check(f"{label} · avant minuit : date de l'app = {t0.strftime('%Y-%m-%d')}", ev("D.today") == t0.strftime("%Y-%m-%d"), ev("D.today"))
        pg.clock.fast_forward(int((t1 - t0).total_seconds() * 1000)); pg.wait_for_timeout(600)
    check(f"{label} · l'app connaît la date du jour ({attendu})", ev("D.today") == attendu, f"D.today = {ev('D.today')}")
    # --- pesée depuis l'onglet Poids : feuille « Ajouter une pesée »
    ev("openSheet('weigh')"); pg.wait_for_timeout(400)
    pg.fill("#cw", "75,3"); pg.click("[data-act=saveW][data-src=cw]"); pg.wait_for_timeout(700)
    last = ev("window.__sheets['%s'].POIDS.slice(-1)[0]" % APP)
    check(f"{label} · pesée écrite avec la date du jour", last[0] == attendu, last)
    check(f"{label} · aucune pesée datée de la veille", last[0] != veille, last)
    # --- séance : ouverture, pesée du récap, une série validée
    if not live_avant:
        ev("setTab('home')"); pg.wait_for_timeout(300)
        ev(f"startLive({key!r})"); pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.fill("#pw", "75,4"); pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(600)
        p2 = ev("window.__sheets['%s'].POIDS.slice(-1)[0]" % APP)
        check(f"{label} · pesée du récap de séance datée du jour", p2[0] == attendu, p2)
    ex = ev("(() => { const s = seanceByKey(live.key); return s.exercices.findIndex(e => !isCardioEx(e)); })()")
    ev(f"live.i = {ex}; renderLayer()"); pg.wait_for_timeout(400)
    pg.click("[data-act=doneSet][data-j='0']"); pg.wait_for_timeout(700)
    pg.click("[data-act=liveNav][data-d='1']"); pg.wait_for_timeout(900)
    row = ev("window.__sheets['%s'].SERIES.slice(-1)[0]" % APP)
    check(f"{label} · série écrite avec la date de la séance ({jour_seance})", row and row[0] == jour_seance, row)
    check(f"{label} · aucune erreur JS", not errs, errs)
    c.close()

with sync_playwright() as p:
    br = p.chromium.launch()
    # app ouverte juste avant minuit, pas encore resynchronisée (la synchro automatique n'a lieu que toutes les 10 min)
    scenario("hiver 23h58 → 00h03, app ouverte", "2026-11-04T23:58:00", "2026-11-05T00:03:00", True)
    scenario("été 23h58 → 00h03, app ouverte", "2027-06-15T23:58:00", "2027-06-16T00:03:00", True)
    # séance commencée avant minuit (pas de synchro pendant une séance)
    scenario("hiver séance commencée 23h40, série à 00h30", "2026-11-04T23:40:00", "2026-11-05T00:30:00", True, True)
    scenario("été séance commencée 23h40, série à 00h30", "2027-06-15T23:40:00", "2027-06-16T00:30:00", True, True)
    # ouverture directe à 00h30
    scenario("hiver 00h30 (ouverture directe)", "", "2026-11-05T00:30:00", False)
    scenario("été 00h30 (ouverture directe)", "", "2027-06-16T00:30:00", False)
    # nuits des changements d'heure
    scenario("passage à l'heure d'été (28 mars) 00h30", "", "2027-03-28T00:30:00", False)
    scenario("passage à l'heure d'hiver (31 oct.) 00h30", "", "2027-10-31T00:30:00", False)
    br.close()
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
