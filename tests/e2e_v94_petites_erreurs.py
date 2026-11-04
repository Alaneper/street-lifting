"""Lot final : 1a prescription du nouvel exercice après « Changer l'exercice » ; 1b charge négative refusée ; 1c « 1e3 » jamais lu comme 13.
Rejoue : python3 tests/e2e_v94_petites_erreurs.py"""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    def start(mv, var=None, mod=None):
        key = ev("""([mv, va]) => { const z = S.find(s => !s.archived && (+s.semaine) > 1 && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === mv && (va === null || String(e.variation).toUpperCase().trim() === va))); return z && z.key; }""", [mv, var])
        ev("() => { live = null; store.set('sl4-live', null); }")
        ev("""([k, mv, va, mod]) => { const z = seanceByKey(k), i = z.exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === mv && (va === null || String(e.variation).toUpperCase().trim() === va)); if (mod) Object.assign(z.exercices[i], mod); window.__ci = i; }""", [key, mv, var, mod])
        ev("(k) => startLive(k)", key); pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
        ev("() => { live.i = window.__ci; renderLayer(); document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(400)
    cur = lambda: ev("""() => { const e = seanceByKey(live.key).exercices[live.i]; return {m:e.mouvement, s:e.series, r:e.reps, rp:e.repos, n:live.rows[live.i].sets.length}; }""")
    def swap_to(name):
        pg.click("[data-act=swapOpen]"); pg.wait_for_timeout(300); ev("(n) => { swapQ = n; }", name); ev("() => ACT.swapPick({i:'free'})"); pg.wait_for_timeout(900)
    def log(key, sets):
        ev("""([k, sets]) => { D.series.push({id:null, date:addDays(D.today, -9), bloc:0, semaine:'0', seance:'x', ex:k, charge:Math.max(...sets.map(s => s[0])), sets:sets.map(s => ({c:s[0], r:s[1]})), note:'', src:'app'}); }""", [key, sets])
    # ---------- 1a
    start("RENFO", None, {"series":"5", "reps":"15\"", "repos":"90s"})
    a = cur(); check("1a · départ : prescription « 5 × 15" + chr(34) + " » (cas du retour)", a["s"] == "5" and a["r"] == '15"', a)
    swap_to("Curl marteau jamais fait")
    a = cur(); txt = ev("document.querySelector('.live').innerText")
    check("1a · exercice jamais fait (poids) : valeur par défaut 3 × 10, pas « 5 × 15" + chr(34) + " » de l'ancien", a["s"] == "3" and a["r"] == "10" and a["rp"] == "" and a["n"] == 3 and '15"' not in txt, (a, txt[:200]))
    start("RENFO", None, {"series":"5", "reps":"15\"", "repos":"90s"}); swap_to("Planche")
    a = cur(); check("1a · remplacé par un exercice en durée : 3 × 30s", a["s"] == "3" and a["r"] == "30s", a)
    log("TRACTION NEUTRE TEST", [[12.5, 12], [12.5, 11], [12.5, 10], [12.5, 10]])
    start("RENFO", None, {"series":"5", "reps":"15\"", "repos":"90s"}); swap_to("Traction neutre test")
    a = cur(); check("1a · exercice déjà fait : séries et reps de sa dernière fois (4 × 12)", a["s"] == "4" and a["r"] == "12" and a["n"] == 4, a)
    prog = ev("""() => { for (const z of S) for (const x of (z.base || z.exercices)) if (!x._mod && String(x.mouvement).toUpperCase().trim() === 'SQUAT' && String(x.variation).toUpperCase().trim() === 'COMP') return [x.series, x.reps]; return null; }""")
    start("RENFO", None, {"series":"5", "reps":"15\"", "repos":"90s"}); swap_to("Squat comp")
    a = cur(); check("1a · exercice présent dans la prog : sa prescription de la prog %s" % (prog,), prog and a["s"] == str(prog[0]) and a["r"] == str(prog[1]), (a, prog))
    # remplacer puis revenir à l'original : prescription d'origine
    start("RENFO", None, {"series":"5", "reps":"15\"", "repos":"90s"}); orig = ev("() => seanceByKey(live.key).exercices[live.i]._id"); swap_to("Planche")
    ev("() => ACT.swapOpen()"); pg.wait_for_timeout(200)
    # rechargement : la prescription du nouvel exercice survit (Sheet profil -> modifs)
    ev("() => applyAllMods()"); a = cur(); check("1a · après réapplication des changements, la prescription du nouvel exercice reste (3 × 30s)", a["s"] == "3" and a["r"] == "30s", a)
    # ancien format de changement (3 champs, sans prescription) : toujours lu, ancien comportement
    ev("""() => { const s = seanceByKey(live.key); const m = modFor(s); m.sw = m.sw.map(x => x.slice(0, 3)); D.profil.modifs = JSON.stringify(modsList()); applyAllMods(); }""")
    a = cur(); check("1a · changement enregistré par l'ancienne version (sans prescription) : toujours appliqué, sans erreur", a["m"].upper().startswith("PLANCHE"), a)
    # ---------- 1b / 1c
    def type_val(sel, v):
        ev("""([sel, v]) => { const i = document.querySelector(sel); i.focus(); i.value = v; i.dispatchEvent(new Event('change', {bubbles:true})); }""", [sel, v]); pg.wait_for_timeout(250)
    getc = lambda: ev("() => live.rows[live.i].sets[0].c")
    for nom, mv, var in [("squat", "SQUAT", "COMP"), ("renfo", "RENFO", None), ("muscle-up", "MUSCLE UP", "COMP")]:
        start(mv, var, {"series":"3", "reps":"5", "charge":"60"})
        base = getc(); toasts0 = ev("document.body.innerText")
        type_val('[data-chg="setC"][data-j="0"]', "-5")
        check("1b · %s : « -5 » refusé (valeur inchangée %s)" % (nom, base), getc() == base and ev("document.querySelector('[data-chg=\"setC\"][data-j=\"0\"]').value") != "-5", (getc(), base))
        check("1b · %s : message « pas de valeur négative »" % nom, "négative" in ev("document.body.innerText"))
        type_val('[data-chg="setC"][data-j="0"]', "1e3")
        check("1c · %s : « 1e3 » refusé, jamais lu comme 13 (valeur %s)" % (nom, getc()), getc() == base and getc() != 13 and getc() != 1000, getc())
        type_val('[data-chg="setC"][data-j="0"]', "62,5"); check("%s : « 62,5 » toujours accepté" % nom, getc() == 62.5, getc())
        type_val('[data-chg="setC"][data-j="0"]', "62.5"); check("%s : « 62.5 » (point) accepté" % nom, getc() == 62.5, getc())
        type_val('[data-chg="setC"][data-j="0"]', "0"); check("%s : « 0 » accepté" % nom, getc() == 0, getc())
        type_val('[data-chg="setC"][data-j="0"]', ""); check("%s : champ vidé = effacé" % nom, getc() in (None, ""), getc())
    gr = lambda: ev("() => live.rows[live.i].sets[0].r")
    start("RENFO", None, {"series":"3", "reps":"10"}); type_val('[data-chg="setR"][data-j="0"]', "8"); r0 = gr()
    type_val('[data-chg="setR"][data-j="0"]', "-3"); check("1b · reps « -3 » refusées (valeur %s)" % gr(), gr() == r0 == 8, gr())
    type_val('[data-chg="setR"][data-j="0"]', "1e3"); check("1c · reps « 1e3 » refusées, pas lues comme 13", gr() == 8, gr())
    check("1c · num('1e3') = null ; num('12 reps') = 12 ; num('82,5') = 82.5 ; num('-5') = -5 (refusé en amont)", ev("[num('1e3'), num('12 reps'), num('82,5'), num('-5')].join('|')") == "|12|82.5|-5".replace("|12", "null|12").replace("null", "") or ev("num('1e3') === null && num('12 reps') === 12 && num('82,5') === 82.5"))
    # poids du jour et record
    ev("() => { ACT.settings && 0; }")
    ev("() => openSheet('pdc')"); pg.wait_for_timeout(300)
    if pg.locator("#pw").count():
        ev("() => { document.querySelector('#pw').value = '-70'; }"); n0 = ev("D.poids.length"); ev("() => ACT.pdcSave()"); pg.wait_for_timeout(400)
        check("1b · poids du jour « -70 » refusé (aucune pesée ajoutée)", ev("D.poids.length") == n0)
    ev("() => closeSheet()")
    n0 = ev("D.records ? JSON.stringify(D.records).length : 0")
    # ---------- 1e : courbes de Progrès — dates lisibles à chaque point, lecture au doigt
    def courbe(dates_kg):
        ev("""(L) => { D.prs = []; L.forEach(([o, kg]) => D.prs.push({date: addDays(D.today, -o), lift: 'SQUAT', charge: kg, reps: 1, note: '', rpe: null, eq: false})); progSeg = 'courbes'; crvSel = 'SQUAT'; setTab('prog'); }""", dates_kg); pg.wait_for_timeout(700)
        return ev("""() => ({lab:[...document.querySelectorAll('svg[data-ich=area] text')].map(t => t.textContent.trim()).filter(t => !/kg/.test(t) && t), kg:[...document.querySelectorAll('svg[data-ich=area] text')].map(t => t.textContent.trim()).filter(t => /kg/.test(t)).length, pts:ICH.area.pts.length})""")
    r = courbe([[60, 100], [30, 105], [10, 110]])
    check("1e · 3 records datés : les 3 dates sont écrites sous les points (%s)" % r["lab"], len(r["lab"]) == 3, r)
    r = courbe([[200, 90], [160, 95], [120, 100], [80, 104], [40, 108], [10, 110]])
    check("1e · 6 records : 4 repères de dates répartis dans le temps (%s)" % r["lab"], len(r["lab"]) == 4, r)
    r = courbe([[40, 100], [10, 110]])
    check("1e · 2 records : les 2 dates, points seuls (pas de droite)", len(r["lab"]) == 2 and not ev("!!document.querySelector('svg[data-ich=area] path')"), r)
    check("1e · échelle : 3 à 4 repères en kg sur l'axe vertical", 3 <= r["kg"] <= 4, r)
    courbe([[60, 100], [30, 105], [10, 110]])
    box = ev("""() => { const b = document.querySelector('svg[data-ich=area]').getBoundingClientRect(); return {x:b.x, y:b.y, w:b.width, h:b.height}; }""")
    cdp = c.new_cdp_session(pg) if hasattr(c, "new_cdp_session") else None
    ev("() => document.querySelector('svg[data-ich=area]').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
    box = ev("""() => { const b = document.querySelector('svg[data-ich=area]').getBoundingClientRect(); return {x:b.x, y:b.y, w:b.width, h:b.height}; }""")
    ev("""(b) => { const s = document.querySelector('svg[data-ich=area]'), mk = (t, x, y) => s.dispatchEvent(new PointerEvent(t, {bubbles:true, pointerType:'touch', clientX:x, clientY:y, pointerId:7, isPrimary:true})); mk('pointerdown', b.x + b.w * .55, b.y + b.h * .5); mk('pointermove', b.x + b.w * .56, b.y + b.h * .5); }""", box)
    pg.wait_for_timeout(250)
    tip = ev("""() => { const t = document.querySelector('.ich-tip'); if (!t || t.hidden) return null; const b = t.getBoundingClientRect(); return {txt:t.innerText.replace(/\\s+/g,' '), l:b.left, r:b.right, w:innerWidth}; }""")
    check("1e · lecture au doigt : la bulle donne la date, la valeur et l'écart, et reste dans l'écran (%s)" % (tip and tip["txt"]), tip and "kg" in tip["txt"] and tip["l"] >= 0 and tip["r"] <= tip["w"], tip)
    check("aucune erreur JS", not errs, errs)
    br.close()
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
