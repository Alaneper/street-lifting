"""v71 : silhouettes d'écorché (illustration + zones tracées) et dictionnaire exercices → muscles (source Liftosaur). Test ciblé."""
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
    # 1. chaque muscle cité par une famille a une zone dessinée sur au moins une vue
    miss = ev("(() => { const ks = new Set(); Object.values(MUSCLE_MAP).forEach(m => Object.keys(m).forEach(k => ks.add(k))); return [...ks].filter(k => !MUSCLE_ART.front.reg[k] && !MUSCLE_ART.back.reg[k]); })()")
    check("tous les muscles du dictionnaire ont une zone dessinée", not miss, miss)
    # 2. les zones restent dans l'image
    out = ev("(() => { const o = []; for (const v of ['front','back']) { const a = MUSCLE_ART[v]; for (const k in a.box) { const b = a.box[k]; if (b[0] < 0 || b[1] < 0 || b[2] > a.w || b[3] > a.h) o.push(v + ':' + k); } } return o; })()")
    check("toutes les zones sont dans l'image", not out, out)
    # 3. images partagées, figure légère
    html = ev("muscleFig('SQUAT',{view:'both'}).length")
    check("une figure double fait moins de 6 Ko (les images ne sont pas répétées)", html < 6000, html)
    check("les images d'écorché sont fournies (data:image/webp)", ev("MUSCLE_IMG.front.startsWith('data:image/webp;base64,') && MUSCLE_IMG.back.startsWith('data:image/webp;base64,')"))
    # 4. un exemple par famille : le principal de la source est bien en principal
    cases = {"Face pull":["deltoide_d"], "Hip thrust":["fessiers"], "Leg curl":["ischios"], "Presse à cuisses":["quadriceps"], "Russian twist":["obliques"], "Rowing barre":["dorsaux","trapeze_d"], "Curl marteau":["biceps"], "Skullcrusher":["triceps"], "Shrugs haltères":["trapeze","trapeze_d"], "Mollets debout":["mollets","mollets_d"], "Adducteurs machine":["adducteurs"], "Élévations latérales":["deltoide"], "Développé couché prise serrée":["triceps"], "Roue abdominale":["abdos"], "Pullover":["dorsaux"]}
    bad = {}
    for n, ps in cases.items():
        got = ev("(n) => { const k = exMuscleKey(n); const m = k && MUSCLE_MAP[k] || {}; return Object.keys(m).filter(x => m[x] === 1).sort(); }".replace("(n) =>", "((n) =>") + ")(%r)" % n) if False else ev("((n) => { const k = exMuscleKey(n); const m = k && MUSCLE_MAP[k] || {}; return Object.keys(m).filter(x => m[x] === 1).sort(); })(%r)" % n)
        if sorted(ps) != got: bad[n] = got
    check("%d exercices : muscles principaux conformes à la source" % len(cases), not bad, bad)
    # 5. vignette : cadrage carré sur les muscles principaux
    vb = ev("muscleFig('X_CURL',{cls:'thumb'}).match(/viewBox=\"([^\"]+)\"/)[1].split(' ').map(Number)")
    check("vignette : cadre carré", abs(vb[2] - vb[3]) < 1 and vb[2] < 900, vb)
    # 6. rendu réel : rouge principal, rose secondaire, aucune erreur
    ev("(() => { const d = document.createElement('div'); d.id = 'tstmap'; d.style.cssText = 'position:fixed;top:0;left:0;z-index:99;width:390px'; d.innerHTML = muscleFig('BENCH',{view:'front'}); document.body.appendChild(d); })()")
    st = lambda sel, c="t": ev(f"(() => {{ const e = document.querySelector('#tstmap {sel} .{c}'); const c = getComputedStyle(e); return [c.display, c.opacity]; }})()")
    check("pectoraux (principal) rouge plein, épaules (secondaire) rose", st(".m.pectoral.a1") == ["inline", "1"] and st(".m.deltoide.a2", "s") == ["inline", "1"], (st(".m.pectoral.a1"), st(".m.deltoide.a2", "s")))
    check("muscle non travaillé : pas recoloré (le crème de l'illustration reste visible)", st(".m.quadriceps") == ["none", "1"])
    ok = ev("(() => { const u = document.querySelector('#tstmap .m.pectoral.a1 .t'); const m = u.getAttribute('mask').slice(4, -1); return !!document.querySelector(u.getAttribute('href')) && !!document.querySelector(m); })()")
    check("chaque zone référence bien l'image recolorée et son masque", ok)
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
