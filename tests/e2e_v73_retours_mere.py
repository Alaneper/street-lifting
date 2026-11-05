"""v73 : retours du 4 nov. — modifier/supprimer une perf, bloc suivant (jours cochés + nombre de semaines), axe du poids ±3 kg et toucher en deux temps."""
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

    # 1 · perfs modifiables
    check("chaque PR a un identifiant de ligne", pg.evaluate("D.prs.length > 0 && D.prs.every(p => p.id > 1)"), pg.evaluate("D.prs.slice(0, 3)"))
    ln = pg.evaluate("(() => { const p = D.prs.find(p => p.reps >= 1 && p.reps <= 12); return [p.lift, p.reps]; })()")
    pg.evaluate(f"openSheet('rm|{ln[0]}|{ln[1]}')"); pg.wait_for_timeout(300)
    check("« Toutes tes perfs » : chaque ligne se touche", pg.evaluate("document.querySelectorAll('.sheet [data-act=perfOpen]').length > 0"))
    i = pg.evaluate("perfL.findIndex(x => x.pr)")
    pg.click(f".sheet [data-act=perfOpen][data-i='{i}']"); pg.wait_for_timeout(300)
    check("fenêtre de modification : charge, reps, RPE, date", pg.evaluate("sheet === 'perf' && ['#pfc', '#pfr', '#pfrpe', '#pfd'].every(s => document.querySelector(s))"))
    before = pg.evaluate("perfSel.x.pr.charge")
    pg.fill("#pfc", str(before + 2.5).replace(".", ",")); pg.fill("#pfrpe", "7,5"); pg.click("[data-act=perfSave]"); pg.wait_for_timeout(600)
    check("enregistrer : la perf est corrigée et on revient à la liste", pg.evaluate(f"D.prs.some(p => p.charge === {before + 2.5} && p.rpe === 7.5) && sheet.startsWith('rm|')"), pg.evaluate("sheet"))
    n0 = pg.evaluate("D.prs.length"); i = pg.evaluate("perfL.findIndex(x => x.pr)")
    pg.click(f".sheet [data-act=perfOpen][data-i='{i}']"); pg.wait_for_timeout(300)
    pg.click("[data-act=perfDel]"); pg.wait_for_timeout(200)
    check("supprimer : demande une confirmation (sans boîte du navigateur)", pg.evaluate(f"D.prs.length === {n0} && document.body.textContent.includes('Confirmer : supprimer')"))
    pg.click("[data-act=perfDel]"); pg.wait_for_timeout(600)
    check("supprimer : la perf disparaît", pg.evaluate(f"D.prs.length === {n0 - 1}"))
    pg.evaluate("closeSheet()")
    # v74 · perf lue dans une prog (Sheet, Excel) : corrigeable à la main sans toucher à la prog
    ln = pg.evaluate("(() => { for (const l of ALL_LIFTS) { const x = compSets(l).find(y => !y.pr && y.ck); if (x) return [l, x.r]; } return null; })()")
    check("il existe une perf lue dans une prog", ln is not None)
    if ln:
        pg.evaluate(f"openSheet('rm|{ln[0]}|{ln[1]}')"); pg.wait_for_timeout(300)
        i = pg.evaluate("perfL.findIndex(x => !x.pr && x.ck)"); pg.click(f".sheet [data-act=perfOpen][data-i='{i}']"); pg.wait_for_timeout(300)
        check("perf de prog : champs modifiables (plus seulement un renvoi vers la prog)", pg.evaluate("['#pfc', '#pfr', '#pfrpe', '#pfd'].every(s => document.querySelector(s)) && document.body.textContent.includes('pas modifiée')"))
        ck = pg.evaluate("perfSel.x.ck"); c0 = pg.evaluate("perfSel.x.c")
        pg.fill("#pfc", "333"); pg.fill("#pfrpe", "8"); pg.click("[data-act=perfSave]"); pg.wait_for_timeout(600)
        r = pg.evaluate(f"(() => {{ const x = compSets('{ln[0]}').find(y => y.ck === {ck!r}); return x && [x.c, x.rpe, x.corr]; }})()")
        check("correction appliquée aux records (333 kg, RPE 8, marquée corrigée)", r == [333, 8, True], r)
        check("correction gardée dans le profil (synchronisée)", pg.evaluate("D.profil.perf_corr.includes('333')"))
        check("liste : « Corrigée à la main »", pg.evaluate("document.querySelector('.sheet').textContent.includes('Corrigée à la main')"))
        i = pg.evaluate(f"perfL.findIndex(x => x.ck === {ck!r})"); pg.click(f".sheet [data-act=perfOpen][data-i='{i}']"); pg.wait_for_timeout(300)
        pg.click("[data-act=perfReset]"); pg.wait_for_timeout(600)
        check("revenir à la valeur lue", pg.evaluate(f"(() => {{ const x = compSets('{ln[0]}').find(y => y.ck === {ck!r}); return !!x && x.c === {c0} && !x.corr; }})()"))
        i = pg.evaluate(f"perfL.findIndex(x => x.ck === {ck!r})"); pg.click(f".sheet [data-act=perfOpen][data-i='{i}']"); pg.wait_for_timeout(300)
        pg.click("[data-act=perfDel]"); pg.wait_for_timeout(150); pg.click("[data-act=perfDel]"); pg.wait_for_timeout(600)
        check("retirer une perf de prog de ses records", pg.evaluate(f"!compSets('{ln[0]}').some(y => y.ck === {ck!r})"))
        pg.evaluate("closeSheet()")

    # 3 · axe du poids (maquette 3A) et toucher
    r = pg.evaluate("""(() => { D.profil.pw_zoom = 'large'; const V = [75, 74.4, 75.6, 76.1].map((v, i) => ({date:addDays(D.today, i - 3), poids:v})); const h = pwSvg(V, V.map(p => p.poids), null);
      const labs = [...h.matchAll(/>([\\d,]+) kg</g)].map(m => +m[1].replace(',', '.')); return {labs, lines:(h.match(/<line /g) || []).length, tap2:ICH.pw.tap2}; })()""")
    check("axe (mode Large, v75) : de 3 kg sous la plus basse (74,4) à 3 kg au-dessus de la plus haute (76,1)", r["labs"] and min(r["labs"]) <= 72 and max(r["labs"]) >= 79, r)
    check("axe : chiffres tous les 1 kg, au plus 9 (pas de chevauchement)", len(r["labs"]) <= 9 and all(b - a == 1 for a, b in zip(r["labs"], r["labs"][1:])), r)
    check("axe : lignes tous les 0,5 kg", r["lines"] >= 15, r)
    check("grand écart (70 → 90 kg) : repères espacés", pg.evaluate("pwTicks(67, 93).filter(t => t[1]).length <= 9"))
    check("courbe de poids : premier toucher = bulle, second = détail", r["tap2"] is True)

    # 2 · bloc suivant : jours cochés et semaines
    pg.evaluate("D.profil.coach_sheet_id = APP_ID; render()"); pg.wait_for_timeout(300)
    pg.evaluate("openSheet('settings')"); pg.wait_for_timeout(300); pg.click("[data-act=impNext]"); pg.wait_for_timeout(400)
    check("aperçu du bloc suivant : jours à cocher et nombre de semaines", pg.evaluate("!!document.querySelector('.impdw') && !!document.querySelector('[data-act=impNw]')"))
    pg.evaluate("imp.days = []; impDaysApply(); renderLayer()")
    for j in (0, 2, 4): pg.click(f".impdw [data-j='{j}']"); pg.wait_for_timeout(100)
    labs = pg.evaluate("imp.res.weeks[0].days.map(d => d.label)")
    check("jours cochés L, M, V : séances placées dans l'ordre", labs[:3] == ["Lundi", "Mercredi", "Vendredi"][:len(labs)] if len(labs) <= 3 else labs[:3] == ["Lundi", "Mercredi", "Vendredi"], labs)
    pg.click("[data-act=impNw][data-n='3']"); pg.wait_for_timeout(200)
    check("3 semaines : 3 semaines identiques avec les mêmes jours", pg.evaluate("imp.res.weeks.length === 3 && imp.res.weeks.every(w => JSON.stringify(w.days.map(d => d.label)) === JSON.stringify(imp.res.weeks[0].days.map(d => d.label)))"))
    check("la règle de charge est conservée", pg.evaluate("document.body.textContent.includes('Règle par défaut') && !!document.querySelector('.impwhy')"))
    errs = [e for e in errs if "favicon" not in e]
    check("aucune erreur JavaScript", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails if fails else "aucun")
