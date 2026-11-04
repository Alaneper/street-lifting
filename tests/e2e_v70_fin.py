"""v67 étape E : fin de séance (« Mieux qu'hier »). Test ciblé."""
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
    ev = lambda js: pg.evaluate(js)
    pg.click("#v-home [data-act=startLive]"); pg.wait_for_timeout(1200)
    done = 0
    for _ in range(6):                       # valide la 1re série de chaque exercice rencontré (jusqu'à 4)
        if ev("!!document.querySelector('.live .vbar [data-act=doneSet]')"):
            pg.click(".live .vbar [data-act=doneSet]"); pg.wait_for_timeout(700); done += 1
            if ev("!!document.querySelector('.restpill')"): pg.click(".restpill [data-act=closeSheet]"); pg.wait_for_timeout(300)
        if done >= 4: break
        if ev("!!document.querySelector('.live .vbar [data-act=liveNav][data-d=\"1\"]:not([disabled])')"):
            pg.click(".live .vbar [data-act=liveNav][data-d='1']"); pg.wait_for_timeout(500)
        elif ev("!!document.querySelector('.live [data-act=liveNav][data-d=\"1\"]:not([disabled])')"):
            pg.click(".live [data-act=liveNav][data-d='1']"); pg.wait_for_timeout(500)
    check("au moins une série validée", done >= 1, done)
    pg.click("[data-act=finishLive]"); pg.wait_for_timeout(2200)
    check("écran de fin affiché", ev("!!document.querySelector('.fin')"))
    t = ev("(document.querySelector('.fin-t')||{}).textContent")
    check("titre honnête : « Mieux qu'hier » ou « Bien joué »", t.startswith("Mieux qu'hier") or t.startswith("Bien joué"), t)
    check("3 tuiles (séries, tonnage, record)", ev("document.querySelectorAll('.fin .ft').length") == 3)
    check("carte musculaire « Ce que tu as travaillé »", ev("document.querySelectorAll('.fin .lgc svg').length") == 2)
    check("une ligne par exercice fait (avec vignette)", ev("document.querySelectorAll('.fin .fin-r .tdr').length") >= 1)
    check("pas de « undefined / NaN »", ev("!/undefined|NaN/.test(document.querySelector('.fin').innerText)"))
    pg.screenshot(path="/tmp/fin-v70.png")
    pg.click("[data-act=closeSummary]"); pg.wait_for_timeout(1200)
    check("« Fermer » ramène à l'accueil sans séance en cours", ev("!live && !document.querySelector('.fin')"))
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
