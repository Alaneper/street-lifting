"""Version 24 : classement automatique (service Apps Script), repas enregistrés, aliments mieux trouvés, vidéos des records."""
import pathlib, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
# --- faux service du classement (même logique que tools/classement.gs) ---
BOARD = {"noa@test.be":{"nom":"Noa","pays":"BE","sexe":"M","cat":-87,"MU":5,"PULL":46.25,"DIP":103.75,"SQUAT":200,"total":355,"ris":70.2,"maj":"2026-10-21"},
         "luc@test.fr":{"nom":"Luc","pays":"FR","sexe":"M","cat":-73,"MU":None,"PULL":20,"DIP":40,"SQUAT":120,"total":180,"ris":40,"maj":"2026-10-20"},
         "eva@test.fr":{"nom":"Éva","pays":"FR","sexe":"F","cat":-57,"MU":None,"PULL":10,"DIP":20,"SQUAT":80,"total":110,"ris":45,"maj":"2026-10-20"},
         "tom@test.be":{"nom":"Tom","pays":"BE","sexe":"M","cat":-80,"MU":None,"PULL":5,"DIP":10,"SQUAT":60,"total":75,"ris":15,"maj":"2026-10-19"}}
POSTS = []; MODE = {"err":None}
def svc(r):
    if MODE["err"]: return r.fulfill(body=json.dumps({"error":MODE["err"]}), content_type="application/json", headers={"Access-Control-Allow-Origin":"*"})
    me = None
    if r.request.method == "POST":
        b = json.loads(r.request.post_data); POSTS.append(b)
        if b.get("token") == "TOK":
            me = "alane@test.be"; d = b["data"]; BOARD[me] = dict(nom=d["prenom"], pays=d["pays"], sexe=d["sexe"], cat=d["cat"], MU=d["MU"], PULL=d["PULL"], DIP=d["DIP"], SQUAT=d["SQUAT"], total=d["total"], ris=d["ris"], maj="2026-10-22")
    rows = [dict(v, me=(k == me)) for k, v in BOARD.items()]
    r.fulfill(body=json.dumps({"rows":rows}), content_type="application/json", headers={"Access-Control-Allow-Origin":"*"})
OFF = {"hits":[{"code":"123","product_name_fr":"Skyr nature","brands":["Marque test"],"nutriments":{"energy-kcal_100g":63,"proteins_100g":11,"carbohydrates_100g":4,"fat_100g":0.2}}]}
SEEN_OFF = []
def off(r): SEEN_OFF.append(r.request.url); r.fulfill(body=json.dumps(OFF), content_type="application/json", headers={"Access-Control-Allow-Origin":"*"})
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    c.route("https://script.google.com/**", svc); c.route("https://search.openfoodfacts.org/**", off)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(2500)

    # ---------- 1. Classement automatique ----------
    pg.evaluate("setTab('agenda')"); pg.wait_for_timeout(200); pg.click("[data-act=agSeg][data-k=amis]"); pg.wait_for_timeout(200)
    pg.evaluate("CLASSEMENT_URL = \"\"; CL = null; rAgenda()"); pg.wait_for_timeout(200)
    check("sans service : message d'attente, rien à saisir", "Rien à saisir" in pg.evaluate("document.querySelector('#v-agenda').textContent") and not pg.evaluate("!!document.querySelector('#v-agenda input')"))
    pg.evaluate("CLASSEMENT_URL = 'https://script.google.com/macros/s/TEST/exec'; CL = null; rAgenda()"); pg.wait_for_timeout(1500)
    check("mes records envoyés automatiquement avec ma connexion", POSTS and POSTS[-1]["token"] == "TOK" and POSTS[-1]["data"]["total"] == pg.evaluate("total() || 0"), POSTS[-1:] )
    r = pg.evaluate("[...document.querySelectorAll('.podium .pod')].map(p => p.textContent.replace(/\\s+/g, ' ').trim())")
    check("podium automatique (Noa 1er, drapeau)", len(r) == 3 and "Noa" in r[1] and "🇧🇪" in r[1], r)
    me = pg.evaluate("document.querySelector('.mepos') && document.querySelector('.mepos').textContent.replace(/\\s+/g, ' ')")
    check("l'app sait que je suis Alane : ma position sans chercher", me and "Ta position" in me and "sur 5" in me, me)
    check("ma ligne mise en avant dans la liste ou le podium", pg.evaluate("!!document.querySelector('.pod.me, .clrow.me')"))
    pg.click(".podium .p1"); pg.wait_for_timeout(300)
    t = pg.evaluate("document.querySelector('.sheet').textContent.replace(/\\s+/g, ' ')")
    check("fiche d'un membre : total, RIS, 4 mouvements, pays", all(k in t for k in ["Noa", "355", "70,2", "Muscle-up", "Tractions", "Dips", "Squat", "Belgique"]), t[:200])
    pg.evaluate("ACT.closeSheet()")
    check("aucune adresse e-mail affichée", "@" not in pg.evaluate("document.querySelector('#v-agenda').textContent"))
    n = len(POSTS); pg.evaluate("syncAll && syncAll()"); pg.wait_for_timeout(2500)
    check("chaque synchro met le classement à jour", len(POSTS) > n, len(POSTS))
    MODE["err"] = "auth"; pg.evaluate("clSync().then(() => rAgenda())"); pg.wait_for_timeout(600); MODE["err"] = None
    t = pg.evaluate("document.querySelector('#v-agenda').textContent")
    check("erreur du service : dernier classement gardé + message", "Ta position" in t and "renouveler" in t, t[:160])
    pg.screenshot(path=str(H / "shots" / "amis-auto.png"))

    # ---------- 2. Aliments ----------
    pg.wait_for_function("FOODS !== null || true"); pg.evaluate("loadFoods()"); pg.wait_for_function("FOODS && FOODS.length > 100", timeout=20000)
    r = pg.evaluate("searchFoods('viande hachée').slice(0, 3).map(f => f.nom)")
    check("« viande hachée » trouvée (steak haché Ciqual)", r and "hach" in r[0].lower(), r)
    r = pg.evaluate("searchFoods('haricots verts').slice(0, 3).map(f => f.nom)")
    check("pluriel : « haricots verts » trouvés", r and "haricot" in r[0].lower(), r)
    r = pg.evaluate("searchFoods('blanc de poulet').slice(0, 3).map(f => f.nom)")
    check("« blanc de poulet » → filet de poulet", r and "poulet" in r[0].lower(), r)
    pg.evaluate("setTab('corps'); ACT.corpsTab({k:'nutri'})"); pg.wait_for_timeout(300)
    pg.fill("#nutin", "skyr"); pg.wait_for_timeout(2000)
    check("peu de résultats : marques cherchées toutes seules", SEEN_OFF and pg.evaluate("!!document.querySelector('[data-act=nutPickOff]')"), SEEN_OFF[-1:])

    # ---------- 3. Repas enregistrés ----------
    def add(q, qty):
        pg.fill("#nutin", ""); pg.fill("#nutin", q); pg.wait_for_timeout(300)
        pg.click("[data-act=nutPickFood][data-i='0']"); pg.wait_for_timeout(150); pg.fill("#nq", qty); pg.click("[data-act=nutAdd]"); pg.wait_for_timeout(700)
    k0 = pg.evaluate("dayRows(nutDate).length")
    add("viande hachée", "200"); add("haricots verts", "150")
    check("2 aliments notés", pg.evaluate("dayRows(nutDate).length") == k0 + 2)
    pg.click("[data-act=mealSave]"); pg.wait_for_timeout(300)
    # ne garder que les 2 derniers
    pg.evaluate("(() => { const R = dayRows(nutDate); mealSel = new Set(R.slice(-2).map(x => x._row)); renderLayer(); })()")
    pg.fill("#mname", "Haché-haricots"); pg.click("[data-act=mealSaveGo]"); pg.wait_for_timeout(900)
    rows = pg.evaluate(f"window.__sheets['{APP}'].MES_REPAS")
    check("repas enregistré dans le carnet (onglet MES_REPAS)", rows and rows[0][0] == "Repas" and sum(1 for x in rows[1:] if x[0] == "Haché-haricots") == 2, rows)
    check("bouton du repas sous « Ajouter »", pg.evaluate("!!document.querySelector('[data-act=mealAdd][data-n=\"Haché-haricots\"]')"))
    pg.click("[data-act=nutDay][data-d='-1']"); pg.wait_for_timeout(200)
    n0 = pg.evaluate("dayRows(nutDate).length"); kc = pg.evaluate("sum(D.mesRepas['Haché-haricots'].map(x => x.k))")
    pg.click("[data-act=mealAdd][data-n=\"Haché-haricots\"]"); pg.wait_for_timeout(900)
    check("un toucher = tout le repas ajouté au jour affiché", pg.evaluate("dayRows(nutDate).length") == n0 + 2 and abs(pg.evaluate("sum(dayRows(nutDate).map(x => x.k))") - kc) < 1)
    nrep = pg.evaluate(f"window.__sheets['{APP}'].REPAS.length")
    pg.evaluate("loadApp().then(() => rNutri())"); pg.wait_for_timeout(1500)
    check("après rechargement : repas et lignes REPAS conservés", pg.evaluate("(D.mesRepas['Haché-haricots'] || []).length") == 2 and pg.evaluate(f"window.__sheets['{APP}'].REPAS.length") == nrep)
    pg.click("[data-act=mealsManage]"); pg.wait_for_timeout(200); pg.click("[data-act=mealDel]"); pg.wait_for_timeout(700)
    pg.evaluate("ACT.closeSheet()"); pg.evaluate("loadApp().then(() => rNutri())"); pg.wait_for_timeout(1500)
    check("repas supprimé (aussi dans le carnet)", not pg.evaluate("Object.keys(D.mesRepas).length"))
    pg.screenshot(path=str(H / "shots" / "repas.png"))

    # ---------- 4. Vidéos des records ----------
    pg.evaluate("ACT.rmInfo({l:'SQUAT', n:'3'})"); pg.wait_for_timeout(600)
    check("fiche record : section Vidéos", "Ajouter une vidéo" in pg.evaluate("document.querySelector('.sheet').textContent"))
    def vid(name, c, rpe, date):
        pg.set_input_files("input[data-chg=vidPick]", files=[{"name":name, "mimeType":"video/mp4", "buffer":b"\x00\x00\x00\x18ftypmp42" + bytes(2000)}]); pg.wait_for_timeout(300)
        pg.fill("#vc", c); pg.select_option("#vr", rpe); pg.fill("#vd", date); pg.click("[data-act=vidAddGo]"); pg.wait_for_timeout(900)
    vid("a.mp4", "100", "6", "2026-09-01"); vid("b.mp4", "100", "8", "2026-10-20")
    r = pg.evaluate("[...document.querySelectorAll('.sheet .vid')].map(v => v.querySelector('.row').textContent.replace(/\\s+/g, ' ').trim())")
    check("2 vidéos gardées pour le même record (aucune remplacée)", len(r) == 2 and "@8" in r[0] and "@6" in r[1], r)
    pg.wait_for_timeout(500)
    check("vidéos lisibles dans l'app", pg.evaluate("[...document.querySelectorAll('.sheet video')].every(v => v.src.startsWith('blob:'))"))
    pg.evaluate("ACT.closeSheet()"); pg.evaluate("ACT.openLift({l:'SQUAT'})"); pg.wait_for_timeout(400)
    check("tuile du record marquée ▶", pg.evaluate("!!document.querySelector('.rm .vid-at')"))
    pg.evaluate("ACT.closePage(); ACT.rmInfo({l:'SQUAT', n:'3'})"); pg.wait_for_timeout(500)
    b = pg.locator("[data-act=vidDel]").first; b.click(); pg.wait_for_timeout(200)
    check("suppression : demande confirmation", "Confirmer" in pg.locator("[data-act=vidDel]").first.text_content())
    pg.locator("[data-act=vidDel]").first.click(); pg.wait_for_timeout(600)
    check("une vidéo supprimée, l'autre reste", pg.evaluate("document.querySelectorAll('.sheet .vid').length") == 1)
    pg.screenshot(path=str(H / "shots" / "videos.png"))
    pg.reload(); pg.wait_for_function("typeof D !== 'undefined' && D && lastSync > 0", timeout=20000); pg.wait_for_timeout(800)
    pg.evaluate("ACT.rmInfo({l:'SQUAT', n:'3'})"); pg.wait_for_timeout(800)
    check("après relance de l'app : la vidéo est toujours là", pg.evaluate("document.querySelectorAll('.sheet .vid').length") == 1)
    # ---------- 5. Libellés « compétition », pays sans drapeau (v25) ----------
    pg.evaluate("ACT.closeSheet && ACT.closeSheet()")
    check("onglet « Comp »", pg.evaluate("[...document.querySelectorAll('nav button')].pop().textContent.trim()") == "Comp")
    pg.evaluate("setTab('agenda')"); pg.wait_for_timeout(200)
    check("segment « Compétitions »", "Compétitions" in pg.evaluate("document.querySelector('#v-agenda .segc').textContent"))
    pg.evaluate("setTab('prog')"); pg.wait_for_timeout(300)
    check("« Mouvements de compétition »", "Mouvements de compétition" in pg.evaluate("document.body.textContent") and "de compét " not in pg.evaluate("document.body.textContent"))
    pg.evaluate("ACT.settings()"); pg.wait_for_timeout(300)
    r = pg.evaluate("(() => { const s = document.querySelector('#spays'), o = [...s.options]; return [document.querySelector('label[for=spays]').textContent, o.length, s.value, o[0].textContent, o.some(x => [...x.textContent].some(ch => ch.codePointAt(0) >= 0x1F1E6 && ch.codePointAt(0) <= 0x1F1FF)), o.some(x => x.textContent === 'Japon')]; })()")
    check("pays : liste de tous les pays, sans drapeau, libellé « Pays »", r[0] == "Pays" and r[1] >= 240 and r[2] == "BE" and r[3] == "Belgique" and not r[4] and r[5], r)
    pg.evaluate("ACT.closeSheet()")
    check("version 26 ou plus", int(pg.evaluate("APP_VER").split(" ")[0]) >= 26)
    check("aucune erreur console", not errs, errs[:5])
    br.close()
print("ÉCHECS :", fails)
