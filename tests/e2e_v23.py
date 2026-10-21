"""Version 23 : RPE jusqu'à 5, RPE de la 1re série pour les records, classement entre amis (podium, drapeaux, position)."""
import pathlib, json
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
    # RPE 5 : 30 kg × 1 à RPE 5 → 6 reps « à fond » (RTS 6 reps = 83,7 %)
    r = pg.evaluate("(() => { const e = e1rmOf('SQUAT', {c:30, r:1, rpe:5, date:D.today}); return [e.xe, Math.round(e.v * 10) / 10]; })()")
    check("RPE 5 pris en compte", r == [6, round(30 / 0.837, 1)], r)
    check("ajout d'un record : RPE 5 proposé", pg.evaluate("(ACT.openLift({l:'SQUAT'}), [...document.querySelectorAll('#prpe option')].some(o => o.value === '5'))")); pg.evaluate("ACT.closePage()")
    # RPE de la 1re série pour une séance notée dans l'app (4 × 4)
    r = pg.evaluate("""(() => { const s = S.find(z => z.faite && z.exercices.some(e => liftOf(e.mouvement) === 'SQUAT' && isCompEx(e) && num(e.rpe1)));
      const e = s.exercices.find(e => liftOf(e.mouvement) === 'SQUAT' && isCompEx(e) && num(e.rpe1));
      D.series.push({date:dateOf(s), bloc:s.bloc, semaine:s.semaine, seance:s.seance, ex:exKey(e), note:'L' + e.row, sets:[{c:77.7, r:4}, {c:77.7, r:4}, {c:77.7, r:4}, {c:77.7, r:4}]});
      const x = compSets('SQUAT').filter(y => y.c === 77.7); return [num(e.rpe1), x.length, x[0].rpe]; })()""")
    check("séance notée dans l'app : RPE de la 1re série repris", r[1] == 4 and r[2] == r[0], r)
    r = pg.evaluate("(() => { const b = repMaxes(compSets('SQUAT'))[3].b; return [b.c, b.rpe]; })()")
    check("record 4 reps : affiché avec le RPE de la 1re série", r[0] >= 77.7 and r[1] is not None, r)
    # Amis : pays, création du classement, podium, position, fiche
    pg.evaluate("ACT.settings()"); pg.wait_for_timeout(300)
    check("réglages : pays avec drapeau, Belgique par défaut", pg.evaluate("document.querySelector('#spays').value") == "BE" and "🇧🇪" in pg.evaluate("document.querySelector('#spays option:checked').textContent"))
    pg.evaluate("ACT.closeSheet(); setTab('agenda')"); pg.wait_for_timeout(300)
    pg.click("[data-act=agSeg][data-k=amis]"); pg.wait_for_timeout(300)
    check("Amis : invitation à créer le classement", pg.evaluate("!!document.querySelector('[data-act=clCreate]')"))
    pg.click("[data-act=clCreate]"); pg.wait_for_timeout(2500)
    cid = pg.evaluate("clId()")
    rows = pg.evaluate(f"window.__sheets['{cid}'] && window.__sheets['{cid}'].CLASSEMENT")
    check("classement créé, ma ligne écrite", rows and rows[0][0] == "Email" and rows[1][0] == "alane@test.be", rows)
    check("classement mémorisé dans le carnet", pg.evaluate(f"window.__sheets['{APP}'].PROFIL.some(r => r[0] === 'classement_id' && r[1] === '{cid}')"))
    # d'autres membres (dont un Français), puis relecture
    pg.evaluate(f"""(() => {{ const t = window.__sheets['{cid}'].CLASSEMENT;
      t.push(['noa@test.be','Noa','BE','H','-87','5','46,25','103,75','200','355','70,2','2026-10-21']);
      t.push(['luc@test.fr','Luc','FR','H','-73','','20','40','120','180','40','2026-10-20']);
      t.push(['eva@test.fr','Éva','FR','F','-57','','10','20','80','110','45','2026-10-20']);
      t.push(['tom@test.be','Tom','BE','H','-80','','5','10','60','75','15','2026-10-19']); }})()""")
    pg.evaluate("clSync(true).then(() => rAgenda())"); pg.wait_for_timeout(1200)
    r = pg.evaluate("[...document.querySelectorAll('.podium .pod')].map(p => p.textContent.replace(/\\s+/g, ' ').trim())")
    check("podium : 2e, 1er, 3e dans l'ordre visuel, avec drapeaux", len(r) == 3 and "Noa" in r[1] and "🇧🇪" in r[1] and r[1].strip().endswith("1"), r)
    me = pg.evaluate("document.querySelector('.mepos') && document.querySelector('.mepos').textContent.replace(/\\s+/g, ' ')")
    check("ma position affichée sans chercher", me and "Ta position" in me and "sur 5" in me, me)
    r = pg.evaluate("[...document.querySelectorAll('.clrow')].map(x => x.textContent.replace(/\\s+/g, ' ').trim())")
    check("liste à partir du 4e avec drapeau et total", len(r) == 2 and r[0].startswith("4") and ("🇫🇷" in r[0] or "🇧🇪" in r[0]) and "kg" in r[0], r)
    pg.click(".podium .p1"); pg.wait_for_timeout(400)
    t = pg.evaluate("document.querySelector('.sheet').textContent.replace(/\\s+/g, ' ')")
    check("fiche d'un ami : total, RIS et les 4 mouvements", all(k in t for k in ["Noa", "355", "70,2", "Muscle-up", "Tractions", "Dips", "Squat", "Belgique"]), t[:200])
    pg.evaluate("ACT.closeSheet()")
    pg.screenshot(path=str(H / "shots" / "amis.png"))
    # mise à jour de ma ligne seulement quand mes chiffres changent
    n0 = pg.evaluate("window.__api.length"); pg.evaluate("clSync(true)"); pg.wait_for_timeout(800)
    calls = pg.evaluate(f"window.__api.slice({n0})")
    check("pas d'écriture si rien n'a changé", not any(a.startswith("PUT") or a.startswith("POST") for a in calls), calls)
    pg.evaluate("D.profil.pays = 'FR'"); pg.evaluate("clSync(true)"); pg.wait_for_timeout(800)
    r = pg.evaluate(f"window.__sheets['{cid}'].CLASSEMENT.find(x => x[0] === 'alane@test.be')")
    check("changement de pays envoyé au classement", r[2] == "FR", r)
    # accès refusé : message clair
    pg.evaluate("window.__fail = 403; CL = null; clErr = ''"); pg.evaluate("clSync(true).then(() => rAgenda())"); pg.wait_for_timeout(800); pg.evaluate("window.__fail = 0")
    t = pg.evaluate("document.querySelector('#v-agenda').textContent")
    check("accès refusé : explique quoi demander", "pas encore accès" in t and "alane@test.be" in t, t[:200])
    check("version 23 ou plus", int(pg.evaluate("APP_VER").split(" ")[0]) >= 23)
    check("aucune erreur console", not [e for e in errs if "403" not in e], errs[:5])
    br.close()
print("ÉCHECS :", fails)
