"""Version 37 : date de début du programme (niveau 1) et bloc suivant par règles (niveau 2), sans toucher aux progs de coach."""
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
    RR = lambda l, rt, n, sets, big=False: pg.evaluate("([l, t, n, s, b]) => { const x = impRuleReps(l, t, n, s, b); return [x.load, x.cls, x.why]; }", [l, rt, n, [{"r": r} for r in sets], big])
    a = RR(60, "8-12", 3, [12, 12, 12]); check("3×12 sur 8–12 validé : charge monte (+2,5 % → 62,5)", a[:2] == [62.5, "up"], a)
    a = RR(60, "8-12", 3, [12, 11, 10]); check("3×(12,11,10) : inchangée, raison donnée", a[:2] == [60, "same"] and "pas encore validé" in a[2], a)
    a = RR(60, "8-12", 3, [12, 12]); check("séries manquantes : inchangée", a[:2] == [60, "same"], a)
    a = RR(100, "5", 5, [5, 5, 5, 5, 5], True); check("reps fixes 5×5 validé : +5 % → 105", a[:2] == [105, "up"], a)
    a = RR(60, "8-12", 3, []); check("rien de noté : inchangée", a[:2] == [60, "same"], a)
    a = RR(60, "AMRAP", 3, [12, 12, 12]); check("reps non chiffrées : inchangée", a[:2] == [60, "same"], a)
    a = RR(60, "8–12", 3, [14, 13, 12]); check("tiret demi-cadratin et reps au-dessus du haut : monte", a[:2] == [62.5, "up"], a)
    check("impRule inchangé : RPE 7 sur 80 kg → 82,5", pg.evaluate("impRule(80, 7, false).load") == 82.5)
    check("aucune erreur JS", not errs, errs)
    br.close()
print("ÉCHECS :", fails) if fails else print("TOUT VERT")
raise SystemExit(1 if fails else 0)
