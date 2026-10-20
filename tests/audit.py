"""Audit visuel : capture chaque écran (iPhone 390×844, iPad 834×1194)."""
import pathlib, sys, time, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
A = H / "audit"; A.mkdir(exist_ok=True)
W = sys.argv[1] if len(sys.argv) > 1 else "phone"
VP = {"phone": (390, 844), "ipad": (834, 1194)}[W]
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":VP[0],"height":VP[1]}, device_scale_factor=1, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e))); pg.on("console", lambda m: errs.append(m.type + " " + m.text) if m.type in ("error", "warning") else None)
    shot = lambda n, full=True: pg.screenshot(path=str(A / f"{W}-{n}.png"), full_page=full)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1200); shot("01-login", False)
    pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500); shot("02-carnet", False)
    t0 = time.time(); pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== \"undefined\" && D && S.length > 0", timeout=20000); t1 = time.time()
    pg.wait_for_timeout(2500)
    print("chargement initial (mock) :", round(t1 - t0, 2), "s | appels API :", len(pg.evaluate("window.__api || []")))
    shot("03-home")
    for t in ["seance", "prog", "corps", "agenda"]:
        pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.click(f"[data-tab={t}]"); pg.wait_for_timeout(1800); shot(f"04-{t}")
    pg.click("[data-tab=corps]"); pg.wait_for_timeout(500); pg.click("[data-act=corpsTab][data-k=poids]"); pg.wait_for_timeout(800); shot("04-corps-poids")
    pg.click("[data-act=corpsTab][data-k=nutri]"); pg.wait_for_timeout(300)
    pg.click("[data-tab=prog]"); pg.wait_for_timeout(500)
    for l in ["PULL", "MU"]:
        pg.evaluate(f"ACT.openLift({{l:'{l}'}})"); pg.wait_for_timeout(1500)
        pg.locator(".page").evaluate("e=>e.style.position='static'"); shot(f"05-lift-{l}"); pg.evaluate("ACT.closePage()"); pg.wait_for_timeout(300)
    k = pg.evaluate("exercisePoints().find(o=>/SQUAT · COMP/.test(o.key)).key")
    pg.evaluate(f"ACT.openEx({{k:{json.dumps(k)}}})"); pg.wait_for_timeout(1200); pg.locator(".page").evaluate("e=>e.style.position='static'"); shot("06-ex"); pg.evaluate("ACT.closePage()")
    pg.click("[data-act=settings]"); pg.wait_for_timeout(700); shot("07-settings", False)
    pg.locator(".sheet").evaluate("e=>{e.style.maxHeight='none';e.style.position='static'}"); shot("07-settings-full"); pg.evaluate("ACT.closeSheet()")
    pg.evaluate("ACT.openLift({l:'SQUAT'})"); pg.wait_for_timeout(1200); pg.evaluate("ACT.rmInfo({l:'SQUAT',n:'3'})"); pg.wait_for_timeout(600); shot("08-rm", False); pg.evaluate("ACT.closeSheet(); ACT.closePage()")
    key = pg.evaluate("(nextSeance()||S.at(-1)).key"); pg.evaluate(f"startLive({json.dumps(key)}, 0)"); pg.wait_for_timeout(900); shot("09-pdc", False)
    pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(500); shot("10-live", False)
    pg.evaluate("live.i=1; renderLayer()"); pg.wait_for_timeout(400); shot("10-live-2", False)
    pg.locator(".setrow .ck").first.click(); pg.wait_for_timeout(800); shot("11-rest", False)
    pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(300)
    pg.click("[data-act=finishLive]"); pg.wait_for_timeout(1500); shot("12-finish", False)
    print("erreurs/avertissements :", errs[:20])
