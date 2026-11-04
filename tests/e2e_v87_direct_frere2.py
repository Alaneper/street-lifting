"""Retours frère (2e passage), séance en direct : « Voir l'exécution » retiré, repos visible après validation, RPE 1re/dernière série,
barre de disques juste sous la série en cours, boutons toujours accessibles, dernière charge faite à côté de la prescrite, carte des muscles repliée.
Rejoue avec : python3 tests/e2e_v87_direct_frere2.py"""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
RECT = """(s) => { const x = document.querySelector(s); if (!x) return null; const b = x.getBoundingClientRect(); return {top:b.top, bottom:b.bottom, h:b.height}; }"""
def open_case(pg, ev, find, mod, prev, w2=False, prev_presc=None):
    key = ev("""([f, w2]) => { const z = S.find(s => !s.archived && (!w2 || (+s.semaine) > 1) && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1])); return z && z.key; }""", [find, w2])
    ev("() => { live = null; store.set('sl4-live', null); }")
    ev("""([k, f, mod, prev, pp]) => { const z = seanceByKey(k), i = z.exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1]), e = z.exercices[i]; Object.assign(e, mod);
      const key = exKey(e), r = s => rank(s.bloc) * 100 + (num(s.semaine) || 0), z0 = S.filter(s => s.idx === z.idx && r(s) < r(z)).sort((a, b) => r(b) - r(a))[0];
      if (pp && z0) { const ez = z0.exercices.find(x => exKey(x) === key); if (ez) ez.charge = pp; }
      D.series = D.series.filter(x => x.ex !== key); if (z0) D.series.push({id:null, date:'2026-10-28', bloc:z0.bloc, semaine:z0.semaine, seance:z0.seance, ex:key, charge:Math.max(...prev.map(s => s[0])), sets:prev.map(s => ({c:s[0], r:s[1]})), note:'', src:'app'}); window.__ci = i; }""", [key, find, mod, prev, prev_presc])
    ev("(k) => startLive(k)", key); pg.wait_for_timeout(700)
    if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
    ev("() => { live.i = window.__ci; renderLayer(); document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(500)

with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    # ---- force 4 × 1 à +5 kg
    open_case(pg, ev, ["MUSCLE UP", "COMP"], {"series": "4", "reps": "1", "charge": "5"}, [[5, 1]] * 4)
    txt = ev("document.querySelector('.live').innerText")
    check("1 · « Voir l'exécution » n'existe plus nulle part dans l'écran de séance", "Voir l'exécution" not in txt and not ev("!!document.querySelector('.live .vx')"))
    check("7 · la carte beige des muscles a disparu ; les muscles sont dans un bloc replié", not ev("!!document.querySelector('.live .lgc')") and ev("!!document.querySelector('.live details.lgm') && !document.querySelector('.live details.lgm').open"))
    check("1c · lest +5 kg : une ligne compacte (56 px au plus), pas de grand bloc", ev("!!document.querySelector('#lgear .lg-cl')") and not ev("!!document.querySelector('#lgear .lg-lest')") and ev(RECT, "#lgear")["h"] <= 56, ev(RECT, "#lgear"))
    m = ev(RECT, ".lgm"); check("7 · bloc des muscles replié : 56 px de haut au plus", m and m["h"] <= 56, m)
    check("B1 · 4 séries visibles ensemble", ev("document.querySelectorAll('.live .lsr').length") == 4)
    bar = ev(RECT, ".vbar"); nav = ev("""() => ['-1','1'].map(d => { const b = document.querySelector('.vbar [data-d="' + d + '"]'); return !!b && b.getBoundingClientRect().height >= 44; })""")
    check("5 · Précédent / Suivant sont dans la barre fixe du bas, à côté de « Valider la série 1 » (44 px au moins)", all(nav) and ev("(document.querySelector('.vbar [data-act=doneSet]')||{}).textContent") == "Valider la série 1", nav)
    ev("() => { const l = document.querySelector('.live'); l.scrollTop = l.scrollHeight; }"); pg.wait_for_timeout(300)
    sw, ed, vb = ev(RECT, "[data-act=swapOpen]"), ev(RECT, "[data-act=editOpen]"), ev(RECT, ".vbar")
    check("5 · en bas de page, « Changer l'exercice » et « Modifier la séance » sont entièrement au-dessus de la barre fixe", sw and ed and sw["bottom"] <= vb["top"] and ed["bottom"] <= vb["top"], (sw, ed, vb))
    ev("() => { document.querySelector('.live').scrollTop = 0; }")
    # ---- repos après validation de la 1re série
    pg.click(".vbar [data-act=doneSet]"); pg.wait_for_timeout(900)
    rb, vb = ev(RECT, "#restbox"), ev(RECT, ".vbar")
    check("2 · minuteur de repos affiché après validation, fixé juste au-dessus de la barre, sans la recouvrir", rb and rb["bottom"] <= vb["top"] and rb["top"] > 300, (rb, vb))
    ev("() => { const l = document.querySelector('.live'); l.scrollTop = l.scrollHeight; }"); pg.wait_for_timeout(300)
    fl = ev(RECT, "[data-act=finishLive].lfin")
    check("2 · pendant le repos, en bas de page, « Terminer la séance » reste entièrement visible (au-dessus de la carte de repos)", fl and fl["bottom"] <= ev(RECT, "#restbox")["top"], (fl, ev(RECT, "#restbox")))
    ev("() => { document.querySelector('.live').scrollTop = 0; }")
    rp = ev(RECT, ".live .lrpe"); s1 = ev(RECT, ".lsr")
    check("1b · le minuteur tient sur une ligne (64 px au plus)", rb["h"] <= 64, rb)
    check("1b · première vue après validation : la ligne RPE (boutons compris) est entièrement au-dessus du minuteur", rp and rp["bottom"] <= rb["top"], (rp, rb))
    check("1b · … et la liste des séries (S1 au moins) reste visible", s1 and s1["top"] >= 0 and s1["bottom"] <= rb["top"], (s1, rb))
    bg = ev("(() => { const c = getComputedStyle(document.querySelector('.vbar')); return [c.backgroundImage, c.backgroundColor]; })()")
    check("1a · la barre fixe du bas est opaque (aucun dégradé, couleur sans transparence) : plus de texte visible entre les boutons", bg[0] == "none" and not bg[1].startswith("rgba(") and "transparent" not in bg[1], bg)
    rt = ev("document.querySelector('#restbox').innerText.replace(/\\s+/g,' ')")
    check("2 · « Repos 0:00 / durée », pause, −15 s, +30 s, Passer", all(w in rt for w in ["Repos", "/ 3:00", "−15 s", "+30 s", "Passer"]) and ev("!!document.querySelector('#restpp')"), rt)
    ev("document.querySelector('[data-act=restPause]').click()"); pg.wait_for_timeout(300)
    check("2 · pause du repos", ev("!!rest.pauseAt"))
    ev("document.querySelector('[data-act=restEnd]').click()"); pg.wait_for_timeout(300)
    check("2 · « Passer » ferme le repos", not ev("!!document.querySelector('#restbox')"))
    # ---- RPE
    r1 = ev("[...document.querySelectorAll('.lrh span')].map(s => s.textContent)")
    check("3 · après la 1re série : « RPE de la 1re série » apparaît sous la liste des séries", len(r1) == 1 and r1[0].startswith("RPE de la 1re série"), r1)
    check("3 · le RPE vient juste après la liste des séries", ev("(() => { const a = document.querySelector('.lsets'), b = document.querySelector('.lrpe'); return !!a && !!b && !!(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING); })()"))
    for _ in range(5):
        if pg.locator(".vbar [data-act=doneSet]").count(): pg.click(".vbar [data-act=doneSet]"); pg.wait_for_timeout(450)
    ev("() => { rest = null; renderLayer(); }"); pg.wait_for_timeout(200)
    r2 = ev("[...document.querySelectorAll('.lrh span')].map(s => s.textContent)")
    check("3 · à la dernière série validée : « RPE de la dernière série » apparaît aussi", len(r2) == 2 and r2[1].startswith("RPE de la dernière série"), r2)
    # ---- squat de compétition : disques juste sous la série en cours
    open_case(pg, ev, ["SQUAT", "COMP"], {}, [[85, 3]])
    ok = ev("""() => { const cur = document.querySelector('.lsr.cur'), g = document.querySelector('#lgear'), list = document.querySelector('.lsets'); return !!cur && !!g && cur.nextElementSibling === g && list.contains(g); }""")
    check("4 · la barre de disques est juste sous la série en cours, dans la liste des séries", ok)
    # ---- renfo : pas de barre ; dernière charge faite à côté de la prescrite
    open_case(pg, ev, ["RENFO", "CURL BICEPS"], {"series": "2", "reps": "10", "charge": "20"}, [[22, 10], [22, 10]], True, "20")
    check("6 · prescription 20 kg, dernière charge faite 22 kg : les deux sont affichées côte à côte dans le titre", "20 kg" in ev("document.querySelector('.lx-p').innerText") and "dernière charge faite : 22 kg" in ev("document.querySelector('.lx-p').innerText"), ev("document.querySelector('.lx-p').innerText"))
    check("6 · la série 1 est préremplie à 22 kg", ev("document.querySelector('.lsr.cur input[data-chg=setC]').value") == "22")
    check("renfo : aucune barre de disques", not ev("!!document.querySelector('#lgear')"))
    # ---- E : disques du lest (tractions, dips, muscle-up) et de chaque série des mouvements à barre, jamais sur le renfo
    ev_ = lambda x: ev(x)
    check("E · lestCalc : 50 kg = 2 disques de 25 (rouges) ; 5 kg = un disque de 5 ; 0 = aucun", ev("JSON.stringify([lestCalc(50).out, lestCalc(5).out, lestCalc(31.25).out, lestCalc(0)])") == "[[25,25],[5],[25,5,1.25],null]")
    check("E · couleurs 25 rouge, 20 bleu, 15 jaune, 10 vert (règlement)", ev("JSON.stringify([25,20,15,10].map(p => PLATE_STYLE[p][0]))") == '["#E0412B","#2F63B5","#FFC930","#2E9E5B"]')
    open_case(pg, ev, ["MUSCLE UP", "COMP"], {"series": "3", "reps": "1", "charge": "50"}, [[50, 1], [50, 1], [47.5, 1]])
    check("E · lest 50 kg (2 disques) : une ligne compacte sous la série en cours, 2 disques rouges, pas de grand bloc", ev("document.querySelectorAll('#lgear .lg-cl .pl i').length") == 2 and not ev("!!document.querySelector('#lgear .lg-lest')") and "Lest : 25 + 25 kg" in ev("document.querySelector('#lgear .lg-t').textContent") and ev(RECT, "#lgear")["h"] <= 56, ev(RECT, "#lgear"))
    pl = ev("[...document.querySelectorAll('.lsr:not(.cur) .pl')].map(x => x.getAttribute('aria-label'))")
    check("E · chaque autre série affiche ses disques à côté (S2, S3 = 2 × 25)", pl == ["Lest : 25 + 25 kg"] * 2, pl)
    ev("document.querySelector('.lsr.cur input[data-chg=setC]').value = '20'; document.querySelector('.lsr.cur input[data-chg=setC]').dispatchEvent(new Event('change', {bubbles:true}))"); pg.wait_for_timeout(300)
    pl = ev("[...document.querySelectorAll('.lsr:not(.cur) .pl')].map(x => x.getAttribute('aria-label'))")
    check("E · changer la charge de S1 met à jour les disques des séries suivantes (20 kg = 1 disque bleu)", pl == ["Lest : 20 kg"] * 2 and "Lest : 20 kg" in ev("document.querySelector('#lgear .lg-t').textContent"), pl)
    open_case(pg, ev, ["SQUAT", "COMP"], {"series": "3", "reps": "3", "charge": "140"}, [[140, 3]] * 3)
    pl = ev("[...document.querySelectorAll('.lsr:not(.cur) .pl')].map(x => x.getAttribute('aria-label'))")
    check("E · squat 140 kg : disques par côté sur chaque série (25 + 25 + 5 + 2,5)", pl == ["Par côté : 25 + 25 + 5 + 2,5 kg"] * 2, pl)
    open_case(pg, ev, ["RENFO", "CURL BICEPS"], {"series": "3", "reps": "11", "charge": "42"}, [[42, 11]] * 3, True)
    check("E · renfo : ni carte de disques, ni disques sur les séries", not ev("!!document.querySelector('#lgear, .lsr .pl')"))
    open_case(pg, ev, ["MUSCLE UP", "COMP"], {"series": "3", "reps": "1", "charge": "52.5"}, [[52.5, 1]] * 3)
    check("1c · lest à 3 disques (52,5 kg) : le bloc visuel reste", ev("document.querySelectorAll('#lgear .lg-lest rect').length") == 3 and not ev("!!document.querySelector('#lgear .lg-cl')"), ev("document.querySelector('#lgear').innerText + ' / ' + JSON.stringify(live.rows[live.i].sets.map(x => x.c))"))
    open_case(pg, ev, ["SQUAT", "COMP"], {"series": "3", "reps": "3", "charge": "85"}, [[85, 3]] * 3)
    ev("document.querySelector('.lsr.cur input[data-chg=setC]').value = '86,75'; document.querySelector('.lsr.cur input[data-chg=setC]').dispatchEvent(new Event('change', {bubbles:true}))"); pg.wait_for_timeout(300)
    fx = ev("(document.querySelector('#lgear .lg-fix')||{}).textContent")
    check("1g · charge inatteignable (86,75 kg) : message et bouton « Mettre 85 kg »", "Mettre 85 kg" in (fx or "") and "86,75" in ev("document.querySelector('#lgear').innerText"), fx)
    pg.click("#lgear .lg-fix"); pg.wait_for_timeout(400)
    check("1g · un tap met 85 kg sur la série en cours ; les séries suivantes suivent ; plus d'avertissement", ev("document.querySelector('.lsr.cur input[data-chg=setC]').value") == "85" and not ev("!!document.querySelector('#lgear .lg-fix')") and ev("live.rows[live.i].sets.map(x => x.c).join()") == "85,85,85", ev("live.rows[live.i].sets.map(x => x.c).join()"))

    check("aucune erreur JS", not errs, errs)
    br.close()
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
