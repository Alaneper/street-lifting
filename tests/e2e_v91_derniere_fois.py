"""Lot fiabilité : « Dernière fois » pour chaque exercice — jamais fait, fait il y a plus d'un mois, cardio / durée, exercice remplacé (« Changer l'exercice »), nom légèrement différent.
Rejoue : python3 tests/e2e_v91_derniere_fois.py   (SHOTDIR=<dossier> : une planche de captures « derniere-fois.png »)"""
import pathlib, os
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
SHOTS = []
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    def start_live():
        key = ev("""() => { const z = S.find(s => !s.archived && (+s.semaine) > 1 && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === 'RENFO')); return z && z.key; }""")
        ev("() => { live = null; store.set('sl4-live', null); }"); ev("(k) => startLive(k)", key); pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
        ev("() => { live.i = Math.max(0, seanceByKey(live.key).exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === 'RENFO')); renderLayer(); document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(400)
    def swap_to(name):
        """vrai parcours : « Changer l'exercice » → saisie libre du nom → l'écran de séance suit le nouvel exercice"""
        pg.click("[data-act=swapOpen]"); pg.wait_for_timeout(300)
        ev("(n) => { swapQ = n; }", name)
        ev("() => ACT.swapPick({i:'free'})"); pg.wait_for_timeout(900)
    def card():
        return ev("() => { const x = document.querySelector('.live .lastt'); return x ? x.innerText.replace(/\\s+/g, ' ').trim() : null; }")
    def snap(tag):
        ev("() => { document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(200)
        f = f"/tmp/dfois-{tag}.png"; pg.screenshot(path=f, clip={"x":0, "y":0, "width":390, "height":520}); SHOTS.append((tag, f))
    today = ev("D.today")
    def log(key, date_off, sets, cardio=False):
        ev("""([k, off, sets, cardio]) => { const d = addDays(D.today, -off), o = {id:null, date:d, bloc:0, semaine:'0', seance:'x', ex:k, charge:Math.max(...sets.map(s => s[0])), sets:sets.map(s => ({c:s[0], r:s[1]})), note:'', src:'app'};
          (cardio ? D.cardio : D.series).push(o); }""", [key, date_off, sets, cardio])
    # 1 · jamais fait
    start_live(); swap_to("Reverse fly jamais fait")
    t = card(); snap("1-jamais")
    check("1 · exercice jamais fait : « aucune série notée », pas de série inventée", t and "aucune série notée" in t and "kg ×" not in t, t)
    check("1 · … et l'écran de séance affiche bien le nouvel exercice", "REVERSE FLY JAMAIS FAIT" in ev("document.querySelector('.live').innerText.toUpperCase()"))
    # 2 · fait il y a plus d'un mois
    log("HAMMER CURL VIEUX", 45, [[30, 10], [30, 10], [30, 9]])
    start_live(); swap_to("Hammer curl vieux")
    t = card(); snap("2-plus-d-un-mois")
    d45 = ev("(() => dJM(addDays(D.today, -45)))()")
    check("2 · fait il y a 45 jours : la dernière fois est retrouvée avec sa date (%s) et ses séries" % d45, t and "30 kg × 10-10-9 rép." in t and d45 in t, t)
    # 3 · cardio et durée
    log("VELO 20 MIN", 9, [[8.4, 20]], True)
    start_live(); swap_to("Vélo 20 min")
    t = card(); snap("3a-cardio")
    check("3 · cardio : la dernière fois (durée, distance) est retrouvée — nom écrit « Vélo » avec accent, clé « VELO »", t and "20" in t and "min" in t.lower() and "aucune" not in t, t)
    check("3 · la date n'est pas répétée deux fois (« 26 oct. · 26 oct. »)", not __import__("re").search(r"(\d+ \w+\.?) · \1", t), t)
    log("PLANCHE", 6, [[0, 90], [0, 75]])
    start_live(); swap_to("Planche")
    t = card(); snap("3b-duree")
    check("3 · série en durée (planche) : la dernière fois est affichée en durée, pas en reps", t and ("1:30" in t or "90" in t) and "rép" not in t.replace("répétition", ""), t)
    # 4 · exercice remplacé : l'historique suit le NOUVEL exercice
    log("TRACTION NEUTRE TEST", 8, [[12.5, 12], [12.5, 12], [12.5, 11]])
    start_live(); old = ev("(() => { const s = seanceByKey(live.key); return exKey(s.exercices[live.i]); })()")
    old_card = card(); swap_to("Traction neutre test")
    t = card(); snap("4-remplace")
    check("4 · après « Changer l'exercice » : la carte montre l'historique du nouvel exercice (12,5 kg × 12-12-11), plus celui de « %s »" % old, t and "12,5 kg × 12-12-11 rép." in t and t != old_card, (old_card, t))
    # 5 · nom légèrement différent
    log("ECARTE POULIE", 12, [[15, 12], [15, 12], [15, 12]])
    start_live(); swap_to("Écarté  poulie")
    t = card(); snap("5a-accents")
    check("5 · accents et espaces doubles (« Écarté  poulie » / « ECARTE POULIE ») : retrouvée", t and "15 kg × 12-12-12 rép." in t, t)
    log("pull up comp", 20, [[20, 5], [20, 5]])
    start_live(); swap_to("Pull Up comp")
    t = card(); snap("5b-casse")
    check("5 · casse (« Pull Up comp » / « pull up comp » écrit en minuscules dans le carnet) : retrouvée", t and "20 kg × 5-5 rép." in t, t)
    log("PULL-UP LESTE", 15, [[10, 6], [10, 6]])
    start_live(); swap_to("Pull up lesté")
    t = card(); snap("5c-tiret")
    check("5 · tiret / espace et accent (« Pull up lesté » / « PULL-UP LESTE ») : retrouvée", t and "10 kg × 6-6 rép." in t, t)
    # contrôle : deux exercices vraiment différents ne sont PAS confondus
    check("5 · garde-fou : « ECARTE POULIE » et « ECARTE HALTERES » restent deux exercices", ev("!sameEx('ECARTE POULIE', 'ECARTE HALTERES') && sameEx('Écarté poulie', 'ECARTE  POULIE') && !sameEx('PULL UP', 'PULLOVER')"))
    check("liftOf : « Face pull », « Pullover », « Lat pulldown » ne sont plus pris pour des tractions ; « Pull up comp », « Weighted Pull-up » le restent", ev("JSON.stringify(['Face pull', 'Pullover', 'Lat pulldown', 'Pull up comp', 'Weighted Pull-up', 'Tractions'].map(liftOf))") == '[null,null,null,"PULL","PULL","PULL"]')
    check("aucune erreur JS", not errs, errs)
    br.close()
if os.environ.get("SHOTDIR"):
    from PIL import Image, ImageDraw
    out = pathlib.Path(os.environ["SHOTDIR"]); out.mkdir(parents=True, exist_ok=True)
    ims = [(t, Image.open(f)) for t, f in SHOTS]; w, h = ims[0][1].size; cols = 4; rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, (h + 40) * rows), (12, 11, 10)); d = ImageDraw.Draw(sheet)
    for i, (t, im) in enumerate(ims): x, y = (i % cols) * w, (i // cols) * (h + 40); d.text((x + 12, y + 12), t, fill=(255, 201, 48)); sheet.paste(im, (x, y + 40))
    sheet.resize((sheet.width // 2, sheet.height // 2)).save(out / "derniere-fois.png")
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
