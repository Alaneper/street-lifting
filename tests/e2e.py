import sys, re, pathlib, json
from playwright.sync_api import sync_playwright
import os
H = pathlib.Path(__file__).resolve().parent; P = H.parent
B = pathlib.Path(os.environ.get("BENCH_DEPS", "/tmp/claude-0/-home-claude/a112c60f-9639-549a-a0f9-bbd91e82e76a/scratchpad/bench"))  # node_modules : chart.js, @fontsource
OUT = H / "shots"; OUT.mkdir(exist_ok=True)
css = ""
for fam, slug, ws in [("Barlow","barlow",[400,500,600,700]),("Barlow Condensed","barlow-condensed",[600,700,800])]:
    for w in ws: css += f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(http://app.local/fonts/{slug}-latin-{w}-normal.woff2) format('woff2');}}\n"
def route(r):
    u = r.request.url
    if u.startswith("https://accounts.google.com/o/oauth2/v2/auth"):
        q = dict(x.split("=",1) for x in u.split("?",1)[1].split("&"))
        from urllib.parse import unquote
        return r.fulfill(content_type="text/html", body="<script>location.replace(" + json.dumps(unquote(q["redirect_uri"]) + "#access_token=TOK&token_type=Bearer&expires_in=3599&state=" + q["state"]) + ")</script>")
    m = re.match(r"http://app\.local/sl/([^?#]*)", u)
    if m:
        f = m.group(1) or "index.html"
        if f in ("index.html", "test-build.html"):
            html = (P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script><script src='/shim.js'></script>", 1)
            return r.fulfill(body=html, content_type="text/html")
        return r.fulfill(path=str(P / f))
    if "script.google.com/macros" in u: return r.fulfill(body='{"rows":[]}', content_type="application/json", headers={"Access-Control-Allow-Origin":"*"})   # service du classement (simulé)
    if u.endswith("/mock.js"): return r.fulfill(path=str(H / "mock.js"), content_type="text/javascript")
    if u.endswith("/shim.js"): return r.fulfill(path=str(H / "shim.js"), content_type="text/javascript")
    if "jszip" in u: return r.fulfill(path=str(B / "node_modules/jszip/dist/jszip.min.js"), content_type="text/javascript")
    if "chart.umd" in u: return r.fulfill(path=str(B / "node_modules/chart.js/dist/chart.umd.js"), content_type="text/javascript")
    if "fonts.googleapis.com" in u: return r.fulfill(body=css, content_type="text/css")
    m = re.search(r"/fonts/((barlow-condensed|barlow)-latin-\d+-normal\.woff2)", u)
    if m: return r.fulfill(path=str(B / f"node_modules/@fontsource/{m.group(2)}/files/{m.group(1)}"), content_type="font/woff2")
    return r.abort()
APP = "10OP7QRneqxxU1ad4BbVaYulLQUBDmaj7Hcu3n3IQBtA"; COACH = "1PLTt-6Qb7kdPXTornMlyJfiH-Pxo3V-2FPD-BkRW2LU"
with sync_playwright() as p:
    br = p.chromium.launch()
    def ctx():
        c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block")
        c.route("**/*", route); return c
    errs = []
    def watch(pg):
        pg.on("console", lambda m: errs.append(m.type + ": " + m.text) if m.type in ("error",) else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
    # --- A : carnet existant
    c = ctx(); pg = c.new_page(); watch(pg)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1200); pg.screenshot(path=str(OUT/"1-login.png"))
    pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500); pg.screenshot(path=str(OUT/"2-carnet.png"))
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4000)
    pg.screenshot(path=str(OUT/"3-home.png"), full_page=True)
    print("api calls:", len(pg.evaluate("window.__api")))
    pg.click("[data-act=settings]"); pg.wait_for_timeout(600); pg.screenshot(path=str(OUT/"4-settings.png"), full_page=False)
    pg.evaluate("ACT.closeSheet()")
    # séance en direct + expiration du jeton
    pg.click("[data-tab=home]"); pg.wait_for_timeout(300)
    pg.click("[data-act=startLive]"); pg.wait_for_timeout(500)
    if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
    pg.click("[data-act=liveNav][data-d='1']"); pg.wait_for_timeout(400)
    pg.click("[data-act=doneSet][data-j='0']"); pg.wait_for_timeout(600)
    pg.evaluate("ACT.closeSheet && ACT.closeSheet()")
    pg.evaluate("localStorage.setItem('sl-tok', JSON.stringify({t:'OLD', exp:Date.now()-1000}))")
    pg.click("[data-act=liveNav][data-d='1']"); pg.wait_for_timeout(3500)
    pg.click("[data-act=doneSet][data-j='0']"); pg.wait_for_timeout(900); pg.screenshot(path=str(OUT/"5b-rest.png"))
    print("après reconnexion : live ouvert ?", pg.locator(".live").count(), "| url:", pg.url)
    pg.screenshot(path=str(OUT/"5-resume.png"))
    pg.click("[data-act=finishLive]"); pg.wait_for_timeout(2000); pg.screenshot(path=str(OUT/"6-summary.png")); pg.click("[data-act=closeSummary]"); pg.wait_for_timeout(1500)
    print("SERIES:", pg.evaluate(f"window.__sheets['{APP}'].SERIES.slice(-3)"))
    print("coach RPE row:", pg.evaluate(f"(()=>{{const g=window.__sheets['{COACH}']['BLOC 7']; return g.map((r,i)=>[i+1,r.slice(22,38).join('|')]).filter(x=>/SQUAT/.test(x[1])).slice(0,3)}})()"))
    for t in ["prog","corps","agenda"]:
        pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.click(f"[data-tab={t}]"); pg.wait_for_timeout(1200); pg.screenshot(path=str(OUT/f"7-{t}.png"), full_page=True)
    pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.click("[data-tab=prog]"); pg.wait_for_timeout(800)
    pg.click("#v-prog [data-act=openLift][data-l=PULL]"); pg.wait_for_timeout(1500)
    pg.locator(".page").evaluate("e=>e.style.position='static'"); pg.screenshot(path=str(OUT/"8b-lift.png"), full_page=True)
    c.close()
    # --- B : nouveau carnet (le frère)
    c = ctx(); pg = c.new_page(); watch(pg)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(800); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.click("[data-act=obStep][data-s=create]"); pg.wait_for_timeout(300)
    pg.fill("#obp", "Noa"); pg.select_option("#obc", "-73"); pg.fill("#obd", "2025-09-01"); pg.fill("#obw", "70,4"); pg.fill("#obprSQUAT", "100"); pg.fill("#obprDIP", "30")
    pg.fill("#obk", f"https://docs.google.com/spreadsheets/d/{COACH}/edit"); pg.screenshot(path=str(OUT/"8-create.png"), full_page=True)
    pg.click("[data-act=obCreate]"); pg.wait_for_timeout(4500); pg.screenshot(path=str(OUT/"9-new-home.png"), full_page=True)
    print("nouveau carnet:", pg.evaluate("Object.keys(window.__sheets).filter(k=>k.startsWith('NEW')).map(k=>window.__sheets[k].PROFIL.slice(0,4))"))
    c.close()
    print("ERRORS:", errs[:15])
    br.close()
