"""Version 33 : import d'un programme (collé → aperçu A → onglet du carnet), sans changer le comportement pour une prog de coach."""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
TXT = "SEMAINE 1\\nLUNDI PUSH\\ndc 4x6 80kg\\nsquat 3x5 100kg then 2x3 110\\ndips lest 4x8 +20\\ntractions 4x5 70%\\nlegs press 3x10 @8\\n\\nMARDI PULL\\nrowing barre 4x8 85\\nsquat 5x5 120"
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(2500)
    # 1. non-régression : avec une prog de coach, aucun bouton d'import
    check("prog de coach : impCan() faux", pg.evaluate("!impCan()"))
    pg.evaluate("openSheet('settings')"); pg.wait_for_timeout(300)
    check("prog de coach : pas de bouton d'import dans les réglages", pg.evaluate("!document.querySelector('[data-act=impOpen]')"))
    pg.evaluate("closeSheet()")
    # 2. le tableau écrit est relu tel quel par l'app (aller-retour)
    r = pg.evaluate(f"""(() => {{ const res = ProgImport.parseProgram("{TXT}"); const g = ProgImport.toGrid(res); const b = parseBloc(g, "Test", 1);
      return {{n:b.seances.length, s:b.seances.map(s => [s.semaine, s.jour, s.seance, s.exercices.map(e => [e.mouvement, e.series, e.reps, e.charge, e.intensite, chargeGuess(e)])]), prog:progInfo(g).prog}}; }})()""")
    check("onglet reconnu comme une prog (progInfo)", r["prog"] is True)
    check("2 séances relues (lundi, mardi)", r["n"] == 2, r)
    lun = r["s"][0]
    check("séance 1 : semaine 1, Lundi, « Séance 1 – PUSH »", lun[0] == "1" and lun[1] == "Lundi" and lun[2].startswith("Séance 1"), lun[:3])
    ex = {e[0] + "|" + e[2]: e for e in lun[3]}
    check("Développé couché 4×6 à 80", ex["Développé couché|6"][1:4] == ["4", "6", "80"] and ex["Développé couché|6"][5] == 80, ex.get("Développé couché|6"))
    check("Dips : lest +20 lu comme 20", ex["Dips|8"][5] == 20, ex.get("Dips|8"))
    check("Tractions 70 % → intensité visée", ex["Tractions|5"][4] == "70%", ex.get("Tractions|5"))
    check("Squat : deux lignes (3×5 à 100 puis 2×3 à 110)", [e[3] for e in lun[3] if e[0] == "Squat"] == ["100", "110"], lun[3])
    check("« @8 » lu comme RPE 8 (pas comme 8 kg)", [e for e in lun[3] if e[0] == "legs press"][0][3:5] == ["", "RPE 8"], lun[3])
    # 3. parcours complet sans prog de coach
    pg.evaluate("D.profil.coach_sheet_id = ''; saveCache(); render(); openSheet('settings')"); pg.wait_for_timeout(300)
    check("sans prog : bouton « Ajouter mon programme » dans les réglages", pg.evaluate("!!document.querySelector('[data-act=impOpen]')"))
    pg.evaluate("closeSheet(); setTab('home'); S = []; render()"); pg.wait_for_timeout(300)
    check("sans prog : carte « Ajoute ton programme » sur l'accueil", pg.evaluate("!!document.querySelector('#v-home [data-act=impOpen]')"))
    pg.click("#v-home [data-act=impOpen]"); pg.wait_for_timeout(300)
    check("étape 1 affichée", pg.evaluate("!!document.querySelector('#imptxt') && document.querySelector('.impstp .on').textContent == '1'"))
    pg.screenshot(path=str(OUT / "v33-etape1.png")); pg.click("[data-act=impRun]"); pg.wait_for_timeout(200)
    check("texte vide : on reste à l'étape 1", pg.evaluate("imp.step === 1"))
    pg.fill("#imptxt", TXT.replace("\\n", "\n")); pg.click("[data-act=impRun]"); pg.wait_for_timeout(300)
    check("étape 2 : une carte par jour (2)", pg.evaluate("imp.step === 2 && document.querySelectorAll('.impday').length === 2"))
    check("étape 2 : « reconnus » affiché", pg.evaluate("document.body.textContent.includes('reconnus')"))
    pg.screenshot(path=str(OUT / "v33-etape2.png"))
    pg.click("[data-act=impEdit][data-k='0.0.0']"); pg.wait_for_timeout(200)
    pg.fill("[data-f=l][data-k='0.0.0']", "85"); pg.dispatch_event("[data-f=l][data-k='0.0.0']", "change"); pg.wait_for_timeout(200)
    check("correction de la charge prise en compte", pg.evaluate("imp.res.weeks[0].days[0].exos[0].groups[0].load.v === 85"))
    pg.click("[data-act=impEdit][data-k='0.1.1']"); pg.wait_for_timeout(200)
    pg.click("[data-act=impDel][data-k='0.1.1']"); pg.wait_for_timeout(200)
    check("exercice retiré", pg.evaluate("imp.res.weeks[0].days[1].exos.length === 1"))
    pg.evaluate("""window.W = null; addProgTab = async (id, t, rows) => { W = {id, t, rows}; }; Store.profil.set = async () => {}; syncAll = async () => {};""")
    pg.click("[data-act=impSave]"); pg.wait_for_timeout(600)
    check("enregistrement : onglet écrit dans le carnet de l'utilisateur", pg.evaluate("W && W.id === APP_ID && W.t === 'Mon programme'"), pg.evaluate("W && W.t"))
    check("prog du carnet = coach_sheet_id", pg.evaluate("D.profil.coach_sheet_id === APP_ID"))
    check("étape 3 : confirmation", pg.evaluate("imp.step === 3 && document.body.textContent.includes('Programme ajouté')"))
    check("tableau écrit : charge corrigée à 85", pg.evaluate("W.rows.some(r => r[0] === 'Développé couché' && r[4] === '85')"))
    pg.screenshot(path=str(OUT / "v33-etape3.png"))
    # 4. texte non reconnu
    pg.evaluate("imp = impNew(); page = {type:'imp'}; renderLayer()"); pg.wait_for_timeout(200)
    pg.fill("#imptxt", "bonjour, voici mon programme de la semaine, courage"); pg.click("[data-act=impRun]"); pg.wait_for_timeout(300)
    check("texte sans exercice : message, on reste à l'étape 1", pg.evaluate("imp.step === 1"))
    # 5. fichier .xlsx (lecture locale) et lien Google Sheet
    import openpyxl
    wbk = openpyxl.Workbook(); ws = wbk.active; ws.title = "Programme"
    for r in [["Jour", "Exercice", "Séries", "Reps", "Charge", "RPE"], ["Lundi", "Squat", 4, 5, 100, 7], ["Lundi", "Développé couché", 3, 8, 80, 8], ["Lundi", "Tractions lestées", 4, 6, 15, ""], ["Mercredi", "Soulevé de terre", 3, 3, 140, 8], ["Mercredi", "Dips", 4, 8, 20, ""]]: ws.append(r)
    wbk.create_sheet("Notes").append(["Penser à bien dormir"])
    xp = str(OUT / "v33-test.xlsx"); wbk.save(xp)
    pg.evaluate("imp = impNew(); page = {type:'imp'}; renderLayer()"); pg.wait_for_timeout(200)
    pg.set_input_files("input[data-chg=impFile]", xp); pg.wait_for_timeout(1500)
    check("xlsx : aperçu à l'étape 2", pg.evaluate("imp.step === 2"), pg.evaluate("imp.step"))
    r = pg.evaluate("imp.res.weeks.flatMap(w => w.days.flatMap(d => d.exos.map(e => [d.label, e.canon || e.name, e.groups[0].sets, e.groups[0].reps, e.groups[0].load && e.groups[0].load.v])))")
    check("xlsx : 5 exercices lus avec séries, reps et charges", len(r) == 5 and ["Lundi", "Squat", 4, "5", 100] in r and ["Mercredi", "Dips", 4, "8", 20] in r, r)
    LK = "1abcdefghijklmnopqrstuvwxyz0123456789"
    pg.evaluate("""k => { window.__sheets[k] = {"Semaine 1": [['Exercice','Séries','Reps','Charge'],['Squat','5','5','110'],['Bench','4','6','85'],['Rowing','4','8','70']]}; imp = impNew(); page = {type:'imp'}; renderLayer(); }""", LK)
    pg.wait_for_timeout(200)
    pg.fill("#implink", "pas un lien"); pg.click("[data-act=impLink]"); pg.wait_for_timeout(200)
    check("lien invalide : on reste à l'étape 1", pg.evaluate("imp.step === 1"))
    pg.fill("#implink", "https://docs.google.com/spreadsheets/d/1abcdefghijklmnopqrstuvwxyz0123456789/edit"); pg.click("[data-act=impLink]"); pg.wait_for_timeout(500)
    check("lien Google Sheet : Sheet lu puis aperçu à l'étape 2", pg.evaluate("imp.step === 2 && impExos().length === 3"), pg.evaluate("[imp.step, impExos().length]"))
    pg.evaluate("k => { window.__sheets[k] = {'BLOC 1': [['x']], 'PROFIL': [['y']]}; imp = impNew(); page = {type:'imp'}; renderLayer(); }", LK); pg.wait_for_timeout(200)
    pg.fill("#implink", "https://docs.google.com/spreadsheets/d/1abcdefghijklmnopqrstuvwxyz0123456789/edit"); pg.click("[data-act=impLink]"); pg.wait_for_timeout(400)
    check("Sheet de coach (onglets BLOC) : orienté vers Réglages, pas importé", pg.evaluate("imp.step === 1"))
    check("version 33 ou plus", float(pg.evaluate("APP_VER").split(" ")[0]) >= 33)
    check("aucune erreur console", not [e for e in errs if "Failed to load resource" not in e], errs[:4])
    br.close()
print("ÉCHECS :", fails if fails else "aucun"); import sys; sys.exit(1 if fails else 0)
