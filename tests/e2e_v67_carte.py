"""v67 étape B : carte musculaire vectorielle (planche craie). Test ciblé, sans captures lourdes."""
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
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(1500)
    ev = lambda js: pg.evaluate(js)
    check("tous les mouvements ont une carte", ev("['SQUAT','BENCH','DEADLIFT','PULL','DIP','MU'].every(l => muscleFig(l).includes('mplate'))"))
    check("mouvement inconnu → rien (pas d'erreur)", ev("muscleFig('CARDIO') === ''"))
    check("squat : quadriceps en principal (face)", ev("muscleFig('SQUAT',{view:'front'}).includes('class=\"m quadriceps a1\"')"))
    check("squat : vue auto = face ; deadlift : vue auto = dos", ev("muscleFig('SQUAT').includes('vue de face') && muscleFig('DEADLIFT').includes('vue de dos')"))
    check("both : 2 figures", ev("(muscleFig('BENCH',{view:'both'}).match(/<svg/g)||[]).length") == 2)
    check("identifiants de découpe uniques entre deux cartes", ev("(() => { const d = document.createElement('div'); d.innerHTML = muscleFig('PULL') + muscleFig('PULL'); const ids = [...d.querySelectorAll('[id]')].map(e => e.id); return ids.length > 0 && new Set(ids).size === ids.length; })()"))
    check("liste muscles : squat principal contient Quadriceps", "Quadriceps" in ev("muscleList('SQUAT')")["p"] if False else "Quadriceps" in ev("muscleList('SQUAT').p"))
    # rendu réel : la couleur du muscle principal est rouge, le secondaire rose, le repos beige
    ev("(() => { const d = document.createElement('div'); d.id = 'tstmap'; d.style.cssText = 'position:fixed;top:0;left:0;z-index:99;width:390px;display:flex;gap:6px'; d.innerHTML = muscleFig('SQUAT',{view:'both'}) + muscleFig('PULL',{view:'both'}); document.body.appendChild(d); })()")
    col = lambda sel: ev(f"getComputedStyle(document.querySelector('#tstmap {sel} .b')).fill")
    check("principal = rouge", col(".m.quadriceps.a1") == "rgb(220, 58, 28)", col(".m.quadriceps.a1"))
    check("secondaire = rose", col(".m.abdos.a2") == "rgb(239, 168, 147)", col(".m.abdos.a2"))
    check("fond planche craie", ev("getComputedStyle(document.querySelector('#tstmap .mplate')).backgroundColor") == "rgb(241, 237, 228)")
    pg.locator("#tstmap").screenshot(path="/tmp/carte-v67.png")
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
