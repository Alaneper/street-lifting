"""v30-31 : couche de données isolée (Store, Account, Ranking), identifiants opaques « id », lecture en objets métier.
Vérifie que les écritures visent exactement les mêmes cellules qu'avant et que l'ancien cache (« _row », « row ») est migré.
Usage : python3 tests/e2e_v31.py   (affiche « ÉCHECS : [] » si tout passe)"""
import pathlib, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)

with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)

    # 1. Lecture : objets métier avec « id », plus aucun « _row » / « row »
    r = pg.evaluate("""(() => ({comps:D.comps.map(c => c.id), noOld:!JSON.stringify(D).includes('"_row"') && !D.comps.some(c => 'row' in c),
      api:['readAll','profil','prs','poids','series','competitions','checklist','repas','mesRepas','history','coach'].every(k => k in Store), acc:typeof Account.token, rk:typeof Ranking.exchange}))()""")
    check("compétitions lues avec leur id (lignes 2 et 3)", r["comps"] == [2, 3], r)
    check("plus de _row / row dans les données", r["noOld"])
    check("Store, Account et Ranking exposés", r["api"] and r["acc"] == "function" and r["rk"] == "function", r)

    # 2. Écritures : mêmes cellules qu'avant la v30
    w = pg.evaluate(f"""(async () => {{ __calls.length = 0; const B = __sheets['{APP}'];
      const ck = await Store.checklist.add([['2026-12-06', 'Ceinture', 'FALSE']]); await Store.checklist.setDone(ck, true);
      await Store.profil.set('pays', 'FR'); await Store.profil.set('pays', 'BE');
      const rp = await Store.repas.add([['2026-10-23', '08:00', 'Test', 'perso', '', 100, 50, 1, 2, 3]]); await Store.repas.remove(rp);
      await Store.competitions.update(3, ['2026-12-07', 'Rookie', 'Liège', '', 'Confirmée']);
      return {{calls:__calls.filter(c => c[0] !== 'get_values').map(c => c.join(' ')), ck, rp, chk:B.CHECKLIST[ck - 1], comp:B.COMPETITIONS[2].slice(0, 3),
        pays:B.PROFIL.filter(x => x[0] === 'pays').map(x => x[1]), repas:(B.REPAS[rp - 1] || []).join('')}}; }})()""")
    calls = w["calls"]
    check("checklist : ajout puis case C de la même ligne", calls[:2] == ["append_values CHECKLIST!A1:C1", f"update_values CHECKLIST!C{w['ck']}"] and w["chk"][2] == "TRUE", w)
    check("profil : clé absente ajoutée une fois, puis modifiée en colonne B", calls[2].startswith("append_values PROFIL!A1:C1") and calls[3].startswith("update_values PROFIL!B") and w["pays"] == ["BE"], w)
    check("repas : suppression = ligne A:J vidée", calls[5] == f"update_values REPAS!A{w['rp']}:J{w['rp']}" and w["repas"] == "", w)
    check("compétition : ligne A:E modifiée", calls[6] == "update_values COMPETITIONS!A3:E3" and w["comp"] == ["2026-12-07", "Rookie", "Liège"], w)

    # 3. Interface : supprimer une compétition (bouton à confirmer) utilise bien l'id
    pg.evaluate("loadApp().then(() => setTab('agenda'))"); pg.wait_for_timeout(1500)
    n0 = pg.evaluate("D.comps.length")
    b = pg.locator("[data-act=delComp]").first; b.click(); pg.wait_for_timeout(300); pg.locator("[data-act=delComp]").first.click(); pg.wait_for_timeout(2000)
    check("suppression d'une compétition depuis l'écran", pg.evaluate("D.comps.length") == n0 - 1, pg.evaluate("D.comps.map(c => c.nom)"))

    # 4. Ancien cache (≤ v30) : « _row » et « row » deviennent « id »
    m = pg.evaluate("""(() => { D.repas = [{_row:7, date:D.today, nom:'x'}]; D.comps = [{row:2, date:'2026-12-01', nom:'y'}]; D.checks = [{row:4, item:'z'}];
      D.mesRepas = {Matin:[{_row:9, nom:'a'}]}; ARCH = [{_row:11, r:[]}]; migrateIds();
      return [D.repas[0].id, D.comps[0].id, D.checks[0].id, D.mesRepas.Matin[0].id, ARCH[0].id, '_row' in D.repas[0], 'row' in D.comps[0]]; })()""")
    check("migration du cache des versions précédentes", m == [7, 2, 4, 9, 11, False, False], m)

    check("aucune erreur JS", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
