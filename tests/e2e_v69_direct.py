"""v67 étape D : séance en direct, barre chargée disque par disque + carte musculaire. Test ciblé."""
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
    # calcul pur
    calc = lambda t: ev(f"JSON.stringify(plateCalc({t}))")
    import json
    g = lambda t: json.loads(calc(t))
    check("100 kg = barre + colliers + 25 + 10 + 2,5 par côté", g(100)["out"] == [25, 10, 2.5] and g(100)["left"] == 0)
    check("140 kg = 25 + 25 + 5 + 2,5 par côté", g(140)["out"] == [25, 25, 5, 2.5])
    check("102,5 kg = 25 + 10 + 2,5 + 1,25", g(102.5)["out"] == [25, 10, 2.5, 1.25])
    check("barre + colliers (25 kg) = aucun disque", g(25)["out"] == [] and g(25)["left"] == 0)
    check("moins que la barre → pas de calcul", ev("plateCalc(22) === null && plateCalc(null) === null"))
    check("charge impossible : reste signalé", g(108.5)["left"] > 0 and abs(g(108.5)["reached"] - 107.5) < 1e-9 or g(108.5)["left"] > 0)
    # écran réel : aller jusqu'à un exercice avec barre
    # la séance du jour change avec le jour de la semaine : on ouvre explicitement une séance qui contient du squat (barre chargée)
    key = ev("(() => { const s = S.find(x => !x.archived && x.exercices.some(e => liftOf(e.mouvement) === 'SQUAT')); return s && s.key; })()")
    check("une séance avec du squat existe dans la prog de test", bool(key), key)
    ev(f"startLive({key!r})"); pg.wait_for_timeout(1200)
    found = False
    for _ in range(7):
        if ev("!!document.querySelector('#lgear .lg-svg')"): found = True; break
        pg.click("[data-act=liveNav][data-d='1']"); pg.wait_for_timeout(500)
    check("barre chargée affichée sur un mouvement à barre", found)
    check("carte musculaire repliée dans l'écran de séance (plus la carte beige)", ev("document.querySelectorAll('.live details.lgm .mplate.lg-plate svg').length") == 2 and ev("!document.querySelector('.live details.lgm').open") and not ev("!!document.querySelector('.live .lgc')"))
    if found:
        sel = "[data-chg=setC][data-j='0']"
        pg.fill(sel, "140"); pg.locator(sel).blur(); pg.wait_for_timeout(300)
        check("la barre suit la charge saisie (140 → 4 disques par côté, colliers en plus)", ev("document.querySelectorAll('#lgear .lg-svg rect').length") >= 8 and "25 + 25 + 5 + 2,5" in ev("document.querySelector('#lgear .lg-t').textContent"), ev("document.querySelector('#lgear .lg-t').textContent"))
        check("bouton fixe « Valider la série 1 »", ev("(document.querySelector('.live .vbar [data-act=doneSet]')||{}).textContent") == "Valider la série 1")
        check("en-tête : nom de l'exercice", ev("document.querySelector('.live .lh-n').textContent.trim().length") > 0)
        check("prescription en grand : séries × reps", "×" in ev("(document.querySelector('.live .lx-p')||{textContent:''}).textContent"))
        pg.evaluate("window.scrollTo(0,0)"); pg.screenshot(path="/tmp/live-v69.png")
        pg.click(".live .vbar [data-act=doneSet]"); pg.wait_for_timeout(900)
        check("valider la dernière série → bouton « Exercice suivant »", ev("!!document.querySelector('.live .lsr.done')") and ev("(document.querySelector('.live .vbar .btn')||{}).textContent") == "Exercice suivant")
        pg.click(".live .vbar .btn"); pg.wait_for_timeout(700)
        n = ev("live.rows[live.i].sets.length")
        check("exercice suivant : plusieurs séries", n >= 2, n)
        pg.click(".live .vbar [data-act=doneSet]"); pg.wait_for_timeout(900)
        check("valider une série (pas la dernière) → le repos démarre", ev("!!document.querySelector('.lrest')"))
        check("repos : bouton pause/lecture", ev("!!document.querySelector('.lrest #restpp')"))
        pg.click(".lrest #restpp"); pg.wait_for_timeout(400)
        check("repos : pause active (▶)", ev("document.querySelector('#restpp').textContent") == "▶")
        pg.screenshot(path="/tmp/rest-v69.png")
    check("pas de texte « undefined/NaN »", ev("!/undefined|NaN/.test(document.querySelector('.live').innerText)"))
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
