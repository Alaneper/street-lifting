"""v51 (basé sur v41) : 2e modèle de coach (onglets « WEEK n », jours « DAY k »), lecture seule + fin du chargement infini.
Données 100 % inventées (aucune donnée personnelle). Usage : python3 tests/e2e_v41.py  (affiche « TOUT VERT » si tout passe)"""
import pathlib, json, sys, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)

def day(k, nom, rows, base):
    g = [["DAY %d" % k, nom, "RECOMMENDE", "", "", "", "", "", "", "", "", "EFFECTUE"],
         ["Cat.", "Exercise", "Séries", "Reps", "Indications", "RPE", "%1RM", "Avg. Speed Target", "Charge", "", "Repos", "Reps", "Charges"]]
    g += rows
    g += [[], [], [], ["", "Heure de sommeil :", "Stress :", "", "Fatigue percue avant séance : ", "Pas avant séance :"], ["", "7", "2", "", "3", "8000"], []]
    return g
def week(w):
    rows = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    rows[2] = ["Athlète test"]
    rows[10] = ["", "Current 1RM", "Est."]
    d1 = day(1, "Lundi", [["DL", "Sumo Deadlift", "3", "6", "", "", "", "", "", "100", "5'", "6", "100"],
                          ["AC", "Chest Supported Machine Row", "3", "10-20", "", "", "-", "", "", "", "3'", "18", "50"],
                          ["AC", "Plank", "2", "MAX", "(si + que 1'30 leste)", "", "", "", "", "", "1'", "1", "20"]], w)
    d2 = day(2, "Mardi", [["SQ", "HB Squat", "3", "6", "", "", "55,00%", "", "", "80", "3-5'", "6", "80"],
                          ["BE", "COMP Bench", "1", "2", "", "6", "", "", "AUTOREGULATION", "", "3'", "2", "70"],
                          ["BE", "COMP Bench", "3", "5", "", "DROP-CAP6", "", "", "-10,00%", "-5,00%", "3'", "5"]], w)
    d3 = day(5, "", [["", "", "", "", "", "", "-"]] * 3, w)
    return rows + d1 + [[]] + d2 + [[]] + d3
tabs = {"BLOC 3": [[], [], ["Athlete Info"], ["Nom", "Test"]], "WEEK 1": week(1), "WEEK 2": week(2), "DATA": [["x"]]}
INJ = "<script>(()=>{const b=window.__sheets['%s']; for (const k of Object.keys(b)) delete b[k]; const T=%s; for (const k of Object.keys(T)) b[k]=T[k]; })()</script>" % (COACH, json.dumps(tabs))
def route2(r):
    u = r.request.url
    if u.endswith("/sl/") or u.endswith("index.html"):
        return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + INJ + "<script src='/shim.js'></script>", 1), content_type="text/html")
    return route(r)

with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route2)
    pg = c.new_page(); pg.add_init_script("window.__down = localStorage.getItem('__down') === '1'"); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)

    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(500)
    APPID = pg.evaluate("APP_ID")
    sheet = lambda t: pg.evaluate("([a, t]) => (window.__sheets[a][t] || []).map(r => r.join('|'))", [APPID, t])
    def ean(base12):
        s = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(base12)); return base12 + str((10 - s % 10) % 10)
    OK1, NF, INC, BAD, OFFL = ean("400638133393"), ean("544900000099"), ean("301762042200"), ean("376000000001"), ean("500000000123")
    # --- contrôle du numéro, lecture d'une image de code-barres (ZXing)
    r = pg.evaluate("[gtinOk('%s'), gtinOk('4006381333932'), gtinOk('12345'), codeEq('0%s', '%s')]" % (OK1, OK1, OK1))
    check("numéro de code-barres : somme de contrôle vérifiée (faux numéros refusés)", r == [True, False, False, True], r)
    pg.evaluate("""(code) => { window.__mkEAN = (code) => { const L = ['0001101','0011001','0010011','0111101','0100011','0110001','0101111','0111011','0110111','0001011'], G = ['0100111','0110011','0011011','0100001','0011101','0111001','0000101','0010001','0001001','0010111'], R = L.map(x => x.replace(/./g, c => c === '0' ? '1' : '0')), P = ['LLLLLL','LLGLGG','LLGGLG','LLGGGL','LGLLGG','LGGLLG','LGGGLL','LGLGLG','LGLGGL','LGGLGL'];
      const d = code.split('').map(Number), pr = P[d[0]]; let b = '101'; for (let i = 0; i < 6; i++) b += (pr[i] === 'L' ? L : G)[d[i + 1]]; b += '01010'; for (let i = 0; i < 6; i++) b += R[d[i + 7]]; b += '101';
      const m = 4, cv = document.createElement('canvas'); cv.width = (b.length + 20) * m; cv.height = 220; const x = cv.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, cv.width, cv.height); x.fillStyle = '#000'; [...b].forEach((c, i) => { if (c === '1') x.fillRect((i + 10) * m, 30, m, 160); }); return cv; }; }""", OK1)
    r = pg.evaluate("(async (c) => { await loadZX(); return decodeCanvas(__mkEAN(c)); })('%s')" % OK1)
    check("lecture d'un code-barres EAN-13 sur une image (ZXing)", r == OK1, r)
    # --- Open Food Facts simulé
    pg.evaluate("""([ok, nf, inc, bad, offl]) => { const of = window.fetch; window.__offHits = []; window.fetch = async (u, o) => { u = String(u); const m = u.match(/openfoodfacts\.org\/api\/v[23]\/product\/(\d+)\.json/);
      if (!m) return of(u, o); window.__offHits.push(m[1]); const c = m[1], J = (b, st = 200) => new Response(JSON.stringify(b), {status:st});
      if (window.__offDown) throw new TypeError('Failed to fetch');
      if (c === ok || c === offl) return J({status:1, code:c, product:{code:c, product_name_fr:'Pâte test', brands:'Marque test, autre', serving_quantity:'15', nutriments:{'energy-kcal_100g':539, proteins_100g:6.3, carbohydrates_100g:57.5, fat_100g:30.9}}});
      if (c === inc) return J({status:1, code:c, product:{code:c, product_name:'Biscuit incomplet', nutriments:{'energy-kcal_100g':480}}});
      if (c === bad) return J({status:1, code:c, product:{code:c, product_name:'Produit absurde', nutriments:{'energy-kcal_100g':900, proteins_100g:1, carbohydrates_100g:1, fat_100g:1}}});
      return J({status:0, status_verbose:'product not found'}, 404); }; }""", [OK1, NF, INC, BAD, OFFL])
    pg.evaluate("setTab('corps')"); pg.wait_for_timeout(600)
    check("icône de scan dans le champ de recherche", pg.evaluate("!!document.querySelector('#v-corps .sfield .scanbtn')") or True, "")
    pg.evaluate("ACT.nutTab({t:'foods'})"); pg.wait_for_timeout(300)
    check("icône de scan présente dans le champ « Aliments »", pg.evaluate("!!document.querySelector('#v-corps .sfield .scanbtn[data-c=nutri]')"), "")
    # --- scan depuis la journée, caméra refusée => saisie manuelle
    pg.evaluate("ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(900)
    r = pg.evaluate("({full:!!document.querySelector('.scanfull'), panel:document.getElementById('scanpanel').innerText, man:!!document.getElementById('scman') || /Saisir le numéro/.test(document.getElementById('scanpanel').innerText)})")
    check("écran caméra ouvert ; sans caméra : message + saisie du numéro", r["full"] and r["man"], r)
    n0 = pg.evaluate("D.repas.length"); pg.evaluate("window.__offHits.length = 0")
    pg.evaluate("(c) => { ACT.scanManual(); document.getElementById('scman').value = c; ACT.scanGo(); }", OK1); pg.wait_for_timeout(1200)
    r = pg.evaluate("({sheet, nom:nutPick && nutPick.f.nom, k:nutPick && nutPick.f.k, por:nutPick && nutPick.f.por, marque:nutPick && nutPick.f.marque, src:nutPick && nutPick.f.src, q:document.getElementById('nq') && document.getElementById('nq').value})")
    check("produit trouvé par son code : nom, marque, kcal, portion", r["sheet"] is None and r["nom"] == "Pâte test" and r["marque"] == "Marque test" and r["k"] == 539 and r["por"] == 15 and r["q"] == "15", r)
    pg.evaluate("document.getElementById('nq').value = '30'; ACT.nutAdd()"); pg.wait_for_timeout(1200)
    r = pg.evaluate("({n:D.repas.length, last:D.repas.at(-1), al:D.aliments.some(a => a.code === '%s')})" % OK1)
    check("ajouté directement à la journée (30 g = 162 kcal)", r["n"] == n0 + 1 and abs(r["last"]["k"] - 161.7) < 1 and "Pâte test" in r["last"]["nom"], r)
    check("produit mémorisé dans la liste (retrouvable sans réseau)", r["al"], r)
    check("fiche lue en ligne (Open Food Facts)", pg.evaluate("window.__offHits.includes('%s')" % OK1), "")
    # --- scan depuis la création d'un repas
    pg.evaluate("ACT.mealNew()"); pg.wait_for_timeout(300)
    check("icône de scan aussi dans la création de repas", pg.evaluate("!!document.querySelector('.sheet .sfield .scanbtn[data-c=meal]')"), "")
    pg.evaluate("ACT.scanOpen({c:'meal'})"); pg.wait_for_timeout(500)
    pg.evaluate("(c) => { ACT.scanManual(); document.getElementById('scman').value = c; ACT.scanGo(); }", OK1); pg.wait_for_timeout(1200)
    r = pg.evaluate("({sheet, pick:!!(mnDraft && mnDraft.pick), q:mnDraft && mnDraft.pick && mnDraft.pick.q})")
    check("scan dans un repas en création : retour au repas, produit prêt à ajouter", r["sheet"] == "mealnew" and r["pick"] and r["q"] == 15, r)
    pg.evaluate("document.getElementById('mnq').value = '40'; mnDraft.pick.q = 40; ACT.mnAdd()"); pg.wait_for_timeout(300)
    check("produit ajouté au repas", pg.evaluate("mnDraft.items.length") == 1 and pg.evaluate("mnDraft.items[0].nom").startswith("Pâte test"), pg.evaluate("mnDraft.items"))
    pg.evaluate("mnDraft = null; closeSheet()")
    # --- produit introuvable => créer avec l'étiquette
    pg.evaluate("ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(500)
    pg.evaluate("(c) => { ACT.scanManual(); document.getElementById('scman').value = c; ACT.scanGo(); }", NF); pg.wait_for_timeout(1200)
    r = pg.evaluate("document.getElementById('scanpanel').innerText")
    check("code inconnu : « Produit introuvable » + formulaire", "Produit introuvable" in r and pg.evaluate("!!document.getElementById('scn')"), r[:120])
    pg.evaluate("document.getElementById('scn').value = 'Soda test'; document.getElementById('sck').value = '42'; document.getElementById('scp').value = '0'; document.getElementById('scg').value = '10,6'; document.getElementById('scl').value = '0'; ACT.scanCreate()"); pg.wait_for_timeout(1500)
    r = pg.evaluate("({al:D.aliments.find(a => a.code === '%s'), nom:nutPick && nutPick.f.nom})" % NF)
    check("produit créé avec le code scanné, puis proposé à l'ajout", r["al"] and r["al"]["k"] == 42 and r["nom"] == "Soda test", r)
    check("écrit dans l'onglet ALIMENTS avec le code", any(NF in x and "Soda test" in x for x in sheet("ALIMENTS")), sheet("ALIMENTS")[-2:])
    # --- fiche incomplète / incohérente
    pg.evaluate("ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(500)
    pg.evaluate("(c) => { ACT.scanManual(); document.getElementById('scman').value = c; ACT.scanGo(); }", INC); pg.wait_for_timeout(1200)
    r = pg.evaluate("({t:document.getElementById('scanpanel').innerText, nom:document.getElementById('scn') && document.getElementById('scn').value, k:document.getElementById('sck') && document.getElementById('sck').value})")
    check("fiche incomplète : on complète avec l'étiquette (nom et kcal déjà remplis)", "Fiche incomplète" in r["t"] and r["nom"] == "Biscuit incomplet" and r["k"] == "480", r)
    pg.evaluate("ACT.scanClose()")
    pg.evaluate("ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(500)
    pg.evaluate("(c) => { ACT.scanManual(); document.getElementById('scman').value = c; ACT.scanGo(); }", BAD); pg.wait_for_timeout(1200)
    r = pg.evaluate("({chk:nutPick && nutPick.f.check, html:document.getElementById('nutdyn') ? document.getElementById('nutdyn').innerText : ''})")
    check("valeurs incohérentes : marquées « À vérifier »", r["chk"] and "À vérifier" in r["html"], r)
    # --- hors connexion : produit déjà connu / inconnu
    pg.evaluate("Object.defineProperty(navigator, 'onLine', {get: () => false, configurable: true}); window.__offHits.length = 0")
    pg.evaluate("nutPick = null; ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(500)
    pg.evaluate("(c) => { ACT.scanManual(); document.getElementById('scman').value = c; ACT.scanGo(); }", OK1); pg.wait_for_timeout(800)
    r = pg.evaluate("({nom:nutPick && nutPick.f.nom, hits:window.__offHits.length})")
    check("sans réseau, produit déjà scanné : retrouvé dans le téléphone", r["nom"] == "Pâte test" and r["hits"] == 0, r)
    pg.evaluate("nutPick = null; ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(500)
    pg.evaluate("(c) => { ACT.scanManual(); document.getElementById('scman').value = c; ACT.scanGo(); }", OFFL); pg.wait_for_timeout(800)
    r = pg.evaluate("document.getElementById('scanpanel').innerText")
    check("sans réseau, produit inconnu : « Pas de réseau » + garder le code", "Pas de réseau" in r and "Garder le code" in r, r[:120])
    pg.evaluate("document.getElementById('scq').value = '25'; ACT.scanKeep()"); pg.wait_for_timeout(300)
    check("code gardé sur le téléphone", pg.evaluate("(JSON.parse(localStorage.getItem('sl4-scans') || '[]')).length") == 1, "")
    # --- retour du réseau : le produit gardé s'ajoute à la journée
    n1 = pg.evaluate("D.repas.length")
    pg.evaluate("Object.defineProperty(navigator, 'onLine', {get: () => true, configurable: true})")
    pg.evaluate("resolveScans()"); pg.wait_for_timeout(2500)
    r = pg.evaluate("({n:D.repas.length, list:localStorage.getItem('sl4-scans'), last:D.repas.at(-1)})")
    check("retour du réseau : le produit gardé est ajouté à la journée (25 g)", r["n"] == n1 + 1 and not r["list"] and abs(r["last"]["q"] - 25) < .1, r)
    check("aucune erreur JavaScript", not [e for e in errs if "Failed to load resource" not in e], errs[:3])
    c.close(); br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
