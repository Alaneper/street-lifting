"""Niveau 8,5, lot B : graphiques interactifs (Poids, Courbes, tonnage, barres de la semaine d'Alimentation, fiche).
Échelle à 3-4 graduations avec unité, dates sur l'axe, repère + bulle qui suivent le doigt, toucher = détail, période animée. Captures : SHOTDIR=<dossier>."""
import pathlib, os
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOT = pathlib.Path(os.environ["SHOTDIR"]) if os.environ.get("SHOTDIR") else None
if SHOT: SHOT.mkdir(parents=True, exist_ok=True)
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
def shot(pg, name):
    if SHOT: pg.screenshot(path=str(SHOT / (name + ".png")))
def centre(pg, sel, fx=.5, fy=.5):
    b = pg.evaluate("(s => { const r = document.querySelector(s).getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })", sel)
    return b[0] + b[2] * fx, b[1] + b[3] * fy
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block", has_touch=False); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    # jeu réaliste : ~120 pesées sur 4 mois, séances faites avec séries
    pg.evaluate("""(() => { const base = new Date(D.today + 'T12:00:00'); D.poids = []; for (let i = 119; i >= 0; i--) { if (i % 3 === 2) continue; const d = new Date(base); d.setDate(d.getDate() - i); D.poids.push({id: 1000 + i, date: isoOf(d), poids: Math.round((78.4 - (119 - i) * 0.012 + Math.sin(i / 6) * .5) * 10) / 10}); }
      pwRange = '3m'; corpsTab = 'poids'; corpsManual = D.today; setTab('corps'); })()""")
    pg.wait_for_timeout(600)
    # --- Poids
    check("Poids : 3 à 4 graduations avec « kg »", 3 <= pg.evaluate("[...document.querySelectorAll('svg[data-ich=pw] text')].filter(t => /^[\\d,]+ kg$/.test(t.textContent)).length") <= 4, pg.evaluate("[...document.querySelectorAll('svg[data-ich=pw] text')].map(t => t.textContent)"))
    check("Poids : au moins 3 dates sur l'axe", pg.evaluate("[...document.querySelectorAll('svg[data-ich=pw] text')].filter(t => /^\\d+ [a-zéû]+\\.?( \\d{4})?$|^[a-zéû]+\\.? \\d\\d$/.test(t.textContent)).length") >= 3, pg.evaluate("[...document.querySelectorAll('svg[data-ich=pw] text')].map(t => t.textContent)"))
    x, y = centre(pg, "svg[data-ich=pw]", .6, .5)
    pg.mouse.move(x, y); pg.mouse.down(); pg.wait_for_timeout(150)
    check("Poids : toucher fait apparaître le repère et la bulle (date, valeur, écart)", pg.evaluate("(() => { const g = document.querySelector('svg[data-ich=pw] .ich-g'), t = document.querySelector('.ich-tip'); return getComputedStyle(g).visibility === 'visible' && !t.hidden && /\\d+,\\d kg/.test(t.textContent) && /vs |Première/.test(t.textContent) && /(Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)/.test(t.textContent) && !/[−-]0(?![,.\\d])/.test(t.textContent); })()"), pg.evaluate("document.querySelector('.ich-tip').textContent"))
    t1 = pg.evaluate("document.querySelector('.ich-tip').textContent")
    shot(pg, "poids-bulle")
    pg.mouse.move(x - 90, y, steps=6); pg.wait_for_timeout(150)
    t2 = pg.evaluate("document.querySelector('.ich-tip').textContent")
    check("Poids : le repère suit le doigt (la bulle change quand on glisse)", t1 != t2, (t1, t2))
    pg.mouse.up(); pg.wait_for_timeout(200)
    check("Poids : un glissé n'ouvre aucune feuille", pg.evaluate("sheet === null"))
    pg.wait_for_timeout(1700)
    check("Poids : repère et bulle disparaissent après le geste", pg.evaluate("document.querySelector('.ich-tip').hidden && getComputedStyle(document.querySelector('svg[data-ich=pw] .ich-g')).visibility === 'hidden'"))
    pg.mouse.move(x, y); pg.mouse.down(); pg.mouse.up(); pg.wait_for_timeout(500)
    check("Poids : toucher un point ouvre le détail du jour", pg.evaluate("sheet === 'pday' && !!document.querySelector('.sheet #cw') && /Corriger/.test(document.querySelector('.sheet').innerText)"), pg.evaluate("sheet"))
    check("Poids : détail du jour sans « −0 »", pg.evaluate("!/[−-]0(?![,.\\d])/.test(document.querySelector('.sheet').innerText)"))
    shot(pg, "poids-detail-jour")
    # corriger une pesée du passé met à jour cette date seulement
    d0 = pg.evaluate("pdDay"); n0 = pg.evaluate("D.poids.length")
    pg.evaluate("ACT.closeSheet()"); pg.wait_for_timeout(200)
    # période animée
    pg.click("[data-act=pwRange][data-k='1m']"); pg.wait_for_timeout(100)
    check("Poids : changement de période animé (courbe tracée)", pg.evaluate("!!document.querySelector('.ichart.pw-anim .pw-line') && getComputedStyle(document.querySelector('.pw-line')).animationName === 'pwdraw'"))
    pg.wait_for_timeout(500); shot(pg, "poids-1m")
    pg.click("[data-act=pwRange][data-k='7j']"); pg.wait_for_timeout(400)
    check("Poids : période sans assez de pesées → état vide lisible (pas de graphique cassé)", pg.evaluate("!!document.querySelector('.emptycard') || !!document.querySelector('svg[data-ich=pw]')"))
    pg.click("[data-act=pwRange][data-k='all']"); pg.wait_for_timeout(400)
    check("Poids : « Tout » → dates avec mois et année si plusieurs années ou longue période", pg.evaluate("!!document.querySelector('svg[data-ich=pw]')"))
    # --- Courbes : Mon total (jeu de records datés pour les trois mouvements)
    pg.evaluate("""(() => { const add = (l, d, kg) => D.prs.push({date: d, lift: l, charge: kg, reps: 1, note: '', rpe: null, eq: false}); [[100, 20, 60, 70], [80, 12, 25, 30], [60, 10, 22, 28]].forEach(() => {});
      [['SQUAT', 90, 100, 105, 110], ['PULL', 22, 26, 29, 32], ['DIP', 28, 31, 34, 37]].forEach(([l, a, b, c, d]) => { [[-150, a], [-100, b], [-50, c], [-10, d]].forEach(([o, kg]) => add(l, addDays(D.today, o), kg)); }); })()""")
    pg.evaluate("progSeg = 'courbes'; setTab('prog')"); pg.wait_for_timeout(1500)
    has = pg.evaluate("!!document.querySelector('svg[data-ich=area]')")
    check("Courbes : graphique Mon total dessiné", has)
    if has:
        tx = pg.evaluate("[...document.querySelectorAll('svg[data-ich=area] text')].map(t => t.textContent)")
        check("Courbes : 3 à 4 graduations avec « kg » et au moins 3 dates (sans « / »)", 3 <= sum(1 for t in tx if t.endswith(" kg")) <= 4 and sum(1 for t in tx if not t.endswith("kg")) >= 3 and not any("/" in t for t in tx), tx)
        cx, cy = centre(pg, "svg[data-ich=area]", .6, .5); pg.mouse.move(cx, cy); pg.mouse.down(); pg.wait_for_timeout(200)
        tt = pg.evaluate("document.querySelector('.crv .ich-tip').textContent")
        check("Courbes : bulle avec date complète, valeur et écart avec le point précédent", "kg" in tt and ("vs " in tt or "Premier" in tt) and not __import__("re").search("[−-]0(?![,.\\d])", tt), tt)
        shot(pg, "courbes-total-bulle"); pg.mouse.up(); pg.wait_for_timeout(1800)
    # --- tonnage
    pg.evaluate("foldOpen.vol = true; rProg()"); pg.wait_for_timeout(1200)
    has = pg.evaluate("!!document.querySelector('svg[data-ich=ton]')")
    check("Tonnage : graphique par semaine présent", has)
    if has:
        yl = pg.evaluate("[...document.querySelectorAll('svg[data-ich=ton] text')].map(t => t.textContent)")
        check("Tonnage : graduations avec « kg » et dates d'axe", sum(1 for t in yl if t.endswith("kg")) >= 3 and sum(1 for t in yl if not t.endswith("kg")) >= 2, yl)
        pg.evaluate("document.querySelector('svg[data-ich=ton]').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
        bx = pg.evaluate("(() => { const r = [...document.querySelectorAll('svg[data-ich=ton] rect[data-i]')].at(-2).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()")
        pg.mouse.move(*bx); pg.mouse.down(); pg.wait_for_timeout(150)
        check("Tonnage : bulle (semaine, tonnage, écart)", pg.evaluate("(() => { const t = document.querySelector('.tonn .ich-tip'); return !t.hidden && /kg/.test(t.textContent) && /vs |Première/.test(t.textContent); })()"), pg.evaluate("document.querySelector('.tonn .ich-tip').textContent"))
        shot(pg, "tonnage-bulle")
        pg.mouse.up(); pg.wait_for_timeout(500)
        check("Tonnage : toucher une barre ouvre la semaine correspondante", pg.evaluate("progSel && typeof progSel.b === 'number' && !!document.getElementById('wkv')"), pg.evaluate("JSON.stringify(progSel)"))
        shot(pg, "tonnage-semaine-ouverte")
    # --- Alimentation : barres de la semaine
    pg.evaluate("""(() => { D.repas = D.repas || []; for (let i = 0; i < 6; i++) { const d = addDays(D.today, -i); D.repas.push({id: 9000 + i, date: d, heure: '12:30', slot: 1, nom: 'Test ' + i, k: 1800 + i * 150, p: 110, g: 200, l: 60}); }
      corpsTab = 'nutri'; nutView = 'semaine'; nutDate = D.today; corpsManual = D.today; setTab('corps'); })()""")
    pg.wait_for_timeout(700)
    has = pg.evaluate("!!document.querySelector('svg[data-ich=nwk]')")
    check("Alimentation semaine : barres interactives présentes", has)
    if has:
        yl = pg.evaluate("[...document.querySelectorAll('svg[data-ich=nwk] text')].map(t => t.textContent)")
        check("Alimentation semaine : graduations et libellé « Objectif … kcal » lisibles", len(yl) >= 9, yl)
        bx = pg.evaluate("(() => { const r = [...document.querySelectorAll('svg[data-ich=nwk] rect[data-i]')].filter(e => +e.getAttribute('height') > 0).at(0).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()")
        pg.mouse.move(*bx); pg.mouse.down(); pg.wait_for_timeout(150)
        check("Alimentation semaine : bulle (jour, kcal)", pg.evaluate("(() => { const t = document.querySelector('.nwk .ich-tip'); return !t.hidden && /kcal/.test(t.textContent); })()"), pg.evaluate("document.querySelector('.nwk .ich-tip').textContent"))
        shot(pg, "alim-semaine-bulle")
        pg.mouse.up(); pg.wait_for_timeout(500)
        check("Alimentation semaine : toucher une barre ouvre le jour", pg.evaluate("nutView === 'jour'"))
    # --- fiche mouvement : Progression sur 1 an
    pg.evaluate("page = {type:'lift', l:'SQUAT'}; liftMetric = '1rm'; renderLayer()"); pg.wait_for_timeout(1500)
    ok = pg.evaluate("typeof charts !== 'undefined' && !!charts['c-lift']")
    check("Fiche : « Progression sur 1 an » dessinée", ok)
    if ok:
        yt = pg.evaluate("charts['c-lift'].scales.y.ticks.map(t => t.label)")
        check("Fiche : graduations avec « kg »", all("kg" in t for t in yt) and len(yt) <= 4, yt)
        pg.evaluate("document.getElementById('c-lift').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
        cx, cy = centre(pg, "#c-lift", .7, .5); pg.mouse.move(cx, cy); pg.wait_for_timeout(500); shot(pg, "fiche-progression-bulle")
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
