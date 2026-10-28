"""(Nécessite la vidéo simulée ean.y4m : image EAN-13 convertie avec ffmpeg, voir historique v51.) v51 (basé sur v41) : 2e modèle de coach (onglets « WEEK n », jours « DAY k »), lecture seule + fin du chargement infini.
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
    mm = re.match(r"http://localhost/sl/([^?#]+)", u)
    if mm and not u.endswith('index.html') and (P / mm.group(1)).exists(): return r.fulfill(path=str(P / mm.group(1)))
    if u.endswith("/sl/") or u.endswith("index.html"):
        return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + INJ + "<script src='/shim.js'></script>", 1), content_type="text/html")
    return route(r)

with sync_playwright() as p:
    br = p.chromium.launch(args=['--unsafely-treat-insecure-origin-as-secure=http://app.local','--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream','--use-file-for-fake-video-capture=/tmp/claude-0/-home-claude/4d20e5b2-cdf2-5820-afc5-8b9ae438f4e2/scratchpad/ean.y4m'])
    c = br.new_context(permissions=["camera"], viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route2)
    pg = c.new_page(); pg.add_init_script("window.__down = localStorage.getItem('__down') === '1'"); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://localhost/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)

    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(500)
    pg.evaluate("""() => { const of = window.fetch; window.fetch = async (u, o) => { u = String(u); if (!/openfoodfacts/.test(u)) return of(u, o);
      return new Response(JSON.stringify({status:1, product:{code:'4006381333931', product_name_fr:'Surligneur test', nutriments:{'energy-kcal_100g':100, proteins_100g:5, carbohydrates_100g:10, fat_100g:5}}}), {status:200}); }; }""")
    pg.evaluate("setTab('corps')"); pg.wait_for_timeout(500); pg.evaluate("ACT.nutTab({t:'foods'})"); pg.wait_for_timeout(300)
    pg.evaluate("ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(9000)
    r = pg.evaluate("({det:typeof BarcodeDetector !== 'undefined', stream:!!scanStream, sheet, nom:nutPick && nutPick.f.nom, st:scanSt})")
    check("caméra simulée : le code-barres est lu automatiquement et le produit trouvé", r["nom"] == "Surligneur test" and r["sheet"] is None, r)
    check("caméra éteinte après la lecture", not r["stream"], r)
    c.close(); br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
