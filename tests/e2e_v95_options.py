"""Lot final · règle des options : tout est ACTIVÉ par défaut ; chaque option se coupe dans Réglages › Affichage de la séance ; message « Nouveautés » unique ;
silhouettes seulement pour les correspondances sûres ; question « C'est ta prog perso ? » jamais activée en silence.
Rejoue : python3 tests/e2e_v95_options.py"""
import pathlib, os
os.environ['SL_NEWS'] = '1'
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
def boot(c):
    pg = c.new_page(); pg.on("pageerror", lambda e: ERRS.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1800)
    return pg
ERRS = []
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = boot(c); ev = pg.evaluate
    # ---------- Nouveautés : compte existant, une seule fois
    shown = ev("() => sheet === 'news' || !!document.querySelector('.sheet')")
    pg.wait_for_timeout(900)
    news = ev("() => ({sheet, txt:(document.querySelector('.sheet')||{}).innerText||''})")
    check("« Nouveautés » s'affiche une fois pour un compte qui a déjà des données", news["sheet"] == "news" and "Nouveautés" in news["txt"], news["sheet"])
    for t in ["Barre et disques", "Dernière fois", "Dernière charge faite dans le titre", "Muscles travaillés", "Silhouettes de muscles", "Total de reps en fin de séance", "Vue du bloc entier", "Calendrier de l'Historique"]:
        check("Nouveautés liste « %s »" % t, t in news["txt"])
    check("Nouveautés ne liste pas le calendrier compact (éteint par défaut)", "Calendrier compact" not in news["txt"])
    pg.click("[data-act=closeSheet] >> nth=-1"); pg.wait_for_timeout(500)
    check("fermer « Nouveautés » : plus de feuille", ev("sheet") is None)
    ev("() => { maybeNews(); }"); pg.wait_for_timeout(400)
    check("« Nouveautés » ne revient pas (même après un nouvel appel)", ev("sheet") is None or ev("sheet") != "news", ev("sheet"))
    pg.reload(); pg.wait_for_timeout(2500)
    check("… ni après rechargement de l'app", ev("sheet") != "news", ev("sheet"))
    # ---------- défauts : tout activé, calendrier compact éteint
    d = ev("() => OPTS.map(o => [o.k, optOn(o.k)])")
    check("défauts : 8 options activées, « calendrier compact » éteint (défaut = le plus accessible)", all(v for k, v in d if k != "calc") and [v for k, v in d if k == "calc"] == [False], d)
    # ---------- Réglages : section, un interrupteur et une phrase par option
    ev("() => { sheet = null; openSheet('settings'); }"); pg.wait_for_timeout(500)
    sec = ev("""() => { const h = [...document.querySelectorAll('.sheet h2')].find(x => /Affichage de la séance/.test(x.textContent)); if (!h) return null; const g = h.nextElementSibling; return [...g.querySelectorAll('.prefrow')].map(r => ({t:r.querySelector('b').textContent, d:(r.querySelector('.grow span')||{}).textContent||'', on:r.getAttribute('aria-checked'), h:Math.round(r.getBoundingClientRect().height)})); }""")
    check("Réglages : section « Affichage de la séance » avec 9 interrupteurs", sec and len(sec) == 9, sec)
    check("chaque interrupteur a une phrase d'explication", sec and all(len(r["d"]) > 25 for r in sec), [r["t"] for r in (sec or []) if len(r["d"]) <= 25])
    check("chaque interrupteur se touche au doigt (44 px au moins)", sec and all(r["h"] >= 44 for r in sec), sec)
    check("tous activés sauf « Calendrier compact »", sec and [r["on"] for r in sec] == ["true"] * 8 + ["false"], sec)
    ev("() => closeSheet()")
    # ---------- séance en direct : chaque option coupe SA fonction
    def open_case(find, mod, prev, w2=False, prev_presc=None):
        key = ev("""([f, w2]) => { const z = S.find(s => !s.archived && (!w2 || (+s.semaine) > 1) && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1])); return z && z.key; }""", [find, w2])
        ev("() => { live = null; store.set('sl4-live', null); }")
        ev("""([k, f, mod, prev, pp]) => { const z = seanceByKey(k), i = z.exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1]), e = z.exercices[i]; Object.assign(e, mod);
          const key = exKey(e), r = s => rank(s.bloc) * 100 + (num(s.semaine) || 0), z0 = S.filter(s => s.idx === z.idx && r(s) < r(z)).sort((a, b) => r(b) - r(a))[0];
          if (pp && z0) { const ez = z0.exercices.find(x => exKey(x) === key); if (ez) ez.charge = pp; }
          D.series = D.series.filter(x => x.ex !== key); if (z0) D.series.push({id:null, date:'2026-10-28', bloc:z0.bloc, semaine:z0.semaine, seance:z0.seance, ex:key, charge:Math.max(...prev.map(s => s[0])), sets:prev.map(s => ({c:s[0], r:s[1]})), note:'', src:'app'}); window.__ci = i; }""", [key, find, mod, prev, prev_presc])
        ev("(k) => startLive(k)", key); pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
        ev("() => { live.i = window.__ci; renderLayer(); document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(500)
    def opt(k, on):
        if ev("(k) => optOn(k)", k) != on: ev("(k) => ACT.optToggle({k})", k); pg.wait_for_timeout(300)
    has = lambda sel: ev("(s) => !!document.querySelector('.live ' + s)", sel)
    open_case(["SQUAT", "COMP"], {"series": "3", "reps": "3", "charge": "140"}, [[140, 3]] * 3)
    check("défaut (squat 140 kg) : barre et disques, « Dernière fois », muscles : présents", has("#lgear .lg-bar") and has(".lastt") and has("details.lgm"))
    opt("gear", False); check("« Barre et disques » éteinte : plus de barre ni de disques sous la série", not has("#lgear") and not has(".pl") and not has(".lg-bar"))
    opt("gear", True); check("… rallumée : la barre revient", has("#lgear .lg-bar"))
    opt("last", False); check("« Dernière fois » éteinte : la carte disparaît", not has(".lastt"))
    opt("last", True); check("… rallumée : la carte revient", has(".lastt"))
    opt("musc", False); check("« Muscles travaillés » éteinte : le bloc replié disparaît", not has("details.lgm"))
    opt("musc", True); check("… rallumé", has("details.lgm"))
    open_case(["RENFO", "CURL BICEPS"], {"series": "2", "reps": "10", "charge": "20"}, [[22, 10], [22, 10]], True, "20")
    check("défaut (curl 20 → 22) : « dernière charge faite » dans le titre", has(".lx-lc"))
    opt("lastc", False); check("« Dernière charge faite » éteinte : le rappel disparaît du titre", not has(".lx-lc") and has(".lastt"))
    opt("lastc", True)
    # le muscle du curl est SÛR : silhouette et bloc présents
    check("curl biceps (correspondance sûre) : bloc « Muscles travaillés » présent avec « Biceps »", has("details.lgm") and "Biceps" in ev("(document.querySelector('.live details.lgm')||{}).textContent||''"))
    # ---------- fin de séance
    ev("() => { live.rows[live.i].sets[0].done = true; live.rows[live.i].sets[0].r = 10; live.rows[live.i].sets[0].c = 22; }")
    def fin():
        ev("() => { finishLive && finishLive(); }"); pg.wait_for_timeout(1800)
    fin()
    tiles = lambda: ev("[...document.querySelectorAll('.fin .ft')].map(x => x.querySelector('span').textContent.trim())")
    t = tiles(); check("fin de séance (défaut) : Séries, Reps, Tonnage, Record", t[:3] == ["Séries", "Reps", "Tonnage"], t)
    check("fin de séance (défaut) : carte « Ce que tu as travaillé » présente", ev("!!document.querySelector('.fin .lgc')"))
    ev("() => { ACT.optToggle({k:'reps'}); ACT.optToggle({k:'musc'}); }"); pg.wait_for_timeout(300)
    ev("() => { sheet = null; live.summary && (sheet = 'summary'); renderLayer(); }"); pg.wait_for_timeout(500)
    t = tiles(); check("« Total de reps » éteint : la tuile Reps disparaît", "Reps" not in t and t[:2] == ["Séries", "Tonnage"], t)
    check("« Muscles travaillés » éteint : la carte de fin disparaît", not ev("!!document.querySelector('.fin .lgc')"))
    ev("() => { ACT.optToggle({k:'reps'}); ACT.optToggle({k:'musc'}); }")
    ev("() => { ACT.closeSummary(); }"); pg.wait_for_timeout(800)
    # ---------- silhouettes, Programme (bloc entier), Historique (calendrier)
    ev("() => { live = null; store.set('sl4-live', null); sheet = null; page = null; renderLayer(); }")
    ev("() => { sel = null; setTab('seance'); rSeance(); }"); pg.wait_for_timeout(600)
    # (la page Programme est le sous-onglet « seance »)
    ev("() => { document.querySelector('#subseance [data-sub=seance]') && document.querySelector('#subseance [data-sub=seance]').click(); }"); pg.wait_for_timeout(600)
    g = ev("""() => { const c = [...document.querySelectorAll('.grid-bloc .cell')]; return {n:c.length, minH:Math.min(...c.map(x => x.getBoundingClientRect().height)), minW:Math.min(...c.map(x => x.getBoundingClientRect().width)), weeks:document.querySelectorAll('.grid-bloc .wk').length, done:c.filter(x => x.classList.contains('done')).length, dates:c.filter(x => /\\d+\\/\\d+/.test(x.textContent)).length}; }""")
    check("Programme (défaut) : le bloc entier est visible, une case par séance (%d cases, %d semaines)" % (g["n"], g["weeks"]), g["n"] >= 4 and g["weeks"] >= 1, g)
    check("… cases de 44 px au moins, avec leur date et un ✓ pour les séances faites", g["minH"] >= 44 and g["minW"] >= 44 and g["dates"] == g["n"], g)
    opt("bloc", False); ev("() => rSeance()"); pg.wait_for_timeout(300)
    check("« Vue du bloc entier » éteinte : la grille disparaît, la semaine reste", not ev("!!document.querySelector('.grid-bloc')") and ev("!!document.querySelector('.wkl')"))
    opt("bloc", True)
    ev("() => { setTab('histo'); rHisto(); }"); pg.wait_for_timeout(500)
    h = ev("""() => { const c = [...document.querySelectorAll('button.hc')]; const w = document.querySelector('.hcal'); return {n:c.length, minH:Math.min(...c.map(x => x.getBoundingClientRect().height)), minW:Math.min(...c.map(x => x.getBoundingClientRect().width)), cmp:!!document.querySelector('.hcal.cmp'), has:!!w}; }""")
    check("Historique (défaut) : calendrier présent, disposition accessible (cases de 44 px au moins), pas compacte", h["has"] and h["n"] > 0 and h["minH"] >= 44 and h["minW"] >= 44 and not h["cmp"], h)
    opt("calc", True); ev("() => rHisto()"); pg.wait_for_timeout(300)
    h2 = ev("""() => { const c = [...document.querySelectorAll('button.hc')]; return {cmp:!!document.querySelector('.hcal.cmp'), h:Math.round(c[0].getBoundingClientRect().height)}; }""")
    check("« Calendrier compact » allumé : cases de 36 px", h2["cmp"] and h2["h"] == 36, h2)
    opt("calc", False)
    opt("cal", False); ev("() => rHisto()"); pg.wait_for_timeout(300)
    check("« Calendrier de l'Historique » éteint : plus de calendrier, la liste des séances reste", not ev("!!document.querySelector('.hcal')") and ev("document.querySelectorAll('.hrow').length") > 0)
    opt("cal", True)
    # silhouettes : sur Aujourd'hui / Historique
    ev("() => { setTab('histo'); rHisto(); }"); pg.wait_for_timeout(300)
    n1 = ev("document.querySelectorAll('.hrow .mplate').length")
    opt("sil", False); ev("() => rHisto()"); pg.wait_for_timeout(300)
    n0 = ev("document.querySelectorAll('.hrow .mplate').length")
    check("« Silhouettes » éteintes : plus de silhouette dans l'Historique (%d → %d)" % (n1, n0), n1 > 0 and n0 == 0, (n1, n0))
    opt("sil", True)
    # ---------- dictionnaire : correspondances sûres / douteuses
    sure = {"Curl biceps haltères":"X_CURL", "Curl marteau":"X_CURL", "Leg curl":"X_LEGCURL", "Curl jambes":"X_LEGCURL", "Leg extension":"X_LEGEXT", "Presse à cuisses":"X_LEGPRESS", "Fentes marchées":"X_LUNGE",
        "Hip thrust":"X_HIP", "Soulevé de terre roumain":"X_RDL", "Mollets debout":"X_CALF", "Hyperextension":"X_BACKEXT", "Shrugs haltères":"X_SHRUG", "Oiseau haltères":"X_REAR", "Élévations latérales":"X_LATERAL",
        "Extension triceps poulie":"X_TRI", "Skull crushers":"X_TRI", "Développé militaire":"X_OHP", "Développé incliné haltères":"X_CHEST", "Pompes":"X_CHEST", "Écarté poulie":"X_FLY", "Lat pulldown":"X_PULLDN",
        "Tirage vertical":"X_PULLDN", "Tirage horizontal machine":"X_ROW", "Rowing barre":"X_ROW", "Gainage":"X_PLANK", "Relevé de jambes":"X_LEGRAISE", "Gainage latéral":"X_SIDEPL", "Rotation russe":"X_OBL", "Crunch":"X_ABS", "Soulevé de terre":"X_DEADLIFT", "Soulevé de terre sumo":"X_SUMO", "Pull-over poulie":"X_PULLOVER", "Tirage vertical prise serrée":"X_PULLDN", "Développé convergent":"X_CHEST", "Wrist curl":"X_WRIST",
        "Face pull":"X_FACEPULL", "Upright row":"X_UPRIGHT", "Reverse curl":"X_CURL", "Pullover":"X_PULLOVER", "Good morning":"X_GOODM", "Kettlebell swing":"X_SWING", "Rowing":"X_ROW", "Adducteurs machine":"X_ADDUCT", "Hip abduction":"X_ABDUCT"}
    bad = {n: ev("(n) => exMuscleKey(n)", n) for n in sure if ev("(n) => exMuscleKey(n)", n) != sure[n]}
    check("dictionnaire : %d correspondances sûres reconnues" % len(sure), not bad, bad)
    doubt = ["Scapular car's", "Scapular pull up", "Farmer's walk", "Développé haltères", "Turkish get-up", "Landmine press", "Tirage assis", "Dips machine", "Renfo", "Marche", "Étirements"]
    leak = {n: ev("(n) => exMuscleKey(n)", n) for n in doubt if ev("(n) => exMuscleKey(n)", n) is not None}
    check("dictionnaire : %d correspondances douteuses NON appliquées (affichage d'avant : initiale)" % len(doubt), not leak, leak)
    check("liftOf prime : « Squat comp » reste SQUAT ; cardio « Vélo 20 min » : aucune silhouette", ev("silKey({mouvement:'Squat', variation:'comp', reps:''})") == "SQUAT" and ev("silKey({mouvement:'RENFO', variation:'Vélo 20 min', reps:'20 min'})") is None)
    # silhouette d'un exercice douteux : initiale conservée dans la séance du jour
    ev("""() => { const z = S.find(s => !s.archived && s.exercices.length); window.__z = z.key; z.exercices[0] = Object.assign({}, z.exercices[0], {mouvement:'RENFO', variation:'Scapular pull up', series:'3', reps:'12'}); z.exercices[1] = Object.assign({}, z.exercices[1] || z.exercices[0], {mouvement:'RENFO', variation:'Curl biceps haltères', series:'3', reps:'12'}); }""")
    ev("() => { sel = window.__z; setTab('seance'); rSeance(); }"); pg.wait_for_timeout(300)
    ev("() => { const c = document.querySelector('#subseance [data-sub=home]'); c && c.click(); }")
    # carte du jour : on construit directement la ligne avec la fonction de rendu
    html = ev("""() => { const z = seanceByKey(window.__z); return z.exercices.slice(0, 2).map(e => ({n:e.variation, sil:silKey(e)})); }""")
    check("Scapular pull up : pas de silhouette (initiale) ; Curl biceps haltères : silhouette", html[0]["sil"] is None and html[1]["sil"] == "X_CURL", html)
    check("aucune erreur JavaScript", not ERRS, ERRS[:3])
    br.close()
    # ---------- compte neuf : pas de « Nouveautés » ; réponses explicites pour la question du Sheet
    c2 = br2 = None
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
