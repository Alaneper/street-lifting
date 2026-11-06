"""Niveau 8,5, lot E : structure par écran. Simule l'encoche de l'iPhone (zone sûre du haut = 47 px). Captures : SHOTDIR=<dossier>."""
import pathlib, os
os.environ["SAFE_TOP"] = "47px"
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOT = pathlib.Path(os.environ["SHOTDIR"]) if os.environ.get("SHOTDIR") else None
if SHOT: SHOT.mkdir(parents=True, exist_ok=True)
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
def shot(pg, name):
    if SHOT: pg.screenshot(path=str(SHOT / (name + ".png")))
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    ev = pg.evaluate
    # --- zone sûre : fiche de mouvement défilée
    ev("page = {type: 'lift', l: 'SQUAT'}; liftMetric = '1rm'; renderLayer()"); pg.wait_for_timeout(800)
    ev("document.querySelector('.page').scrollTop = 500"); pg.wait_for_timeout(400)
    r = ev("(() => { const b = document.querySelector('.pagebar'), t = b.querySelector('.iconbtn'); const rb = b.getBoundingClientRect(), rt = t.getBoundingClientRect(); return {barTop: Math.round(rb.top), btnTop: Math.round(rt.top), bg: getComputedStyle(b, '::before').backgroundColor}; })()")
    check("fiche défilée : barre collée en haut et boutons sous la zone sûre (≥ 47 px)", r["barTop"] == 0 and r["btnTop"] >= 47, r)
    check("fiche défilée : fond d'en-tête opaque", "rgb" in r["bg"] and "0)" not in r["bg"].split(",")[-1][-3:], r)
    shot(pg, "fiche-defilee")
    ev("page = null; renderLayer()")
    # --- Progrès défilé : en-tête opaque + fondu
    ev("progSeg = 'records'; setTab('prog')"); pg.wait_for_timeout(600)
    ev("window.scrollTo(0, 420)"); pg.wait_for_timeout(500)
    r = ev("(() => { const s = getComputedStyle(document.querySelector('.topbar'), '::after'); return {op: s.opacity, h: s.height, scrolled: document.body.classList.contains('scrolled')}; })()")
    check("Progrès défilé : fondu sous l'en-tête", r["scrolled"] and float(r["op"]) > .9 and r["h"] != "auto" and float(r["h"][:-2]) >= 12, r)
    shot(pg, "progres-defile")
    ev("window.scrollTo(0, 0)")
    # --- Programme : « Fait » aligné comme « Prochaine »
    ev("setTab('seance')"); pg.wait_for_timeout(700)
    r = ev("""(() => { const mk = c => { const e = document.createElement('span'); e.className = 'fchip ' + c; e.textContent = 'x'; document.body.appendChild(e); const cs = getComputedStyle(e), o = [cs.fontSize, cs.paddingTop, cs.paddingLeft, cs.borderRadius, cs.fontWeight, Math.round(e.getBoundingClientRect().height)].join('|'); e.remove(); return o; }; return [mk('done'), mk('now')]; })()""")
    check("Programme : « Fait » a la même forme que « Prochaine » (taille, marges, rayon)", r[0] == r[1], r)
    check("Programme : le CSS de « Fait » existe dans les lignes de la semaine", "fchip done" in open(str(H.parent / "src" / "app.html")).read())
    shot(pg, "programme")
    # --- Mouvements : classement par nom
    g = ev("['Releve de jambes', 'Gainage planche', 'Loaded dead bug', 'Developpe incline halteres', 'Rowing barre', 'Curl marteau', 'Fentes bulgares', 'Course a pied 30 min', 'Mobilite hanches'].map(mvGroupByName).join(',')")
    check("Mouvements : classement d'après le nom (tronc, poussée, tirage, jambes, cardio, autres)", g == "tronc,tronc,tronc,pousser,tirer,tirer,jambes,cardio,", g)
    ev("progSeg = 'mouvements'; mvQ = ''; setTab('prog')"); pg.wait_for_timeout(700)
    shot(pg, "mouvements")
    # --- Courbes sans records : état vide compact, sans « Mon total »
    ev("progSeg = 'courbes'; const sv = D.prs; D.prs = []; D.series = D.series.filter(x => false); window.__sv = sv; setTab('prog'); rProg && rProg()"); pg.wait_for_timeout(600)
    t = ev("document.querySelector('#v-prog').innerText")
    check("Courbes vides : message compact, sans « Mon total » ni gros « — »", "Mon total" not in t and "—" not in t.split("Pas encore")[0], t[:300])
    ev("D.prs = window.__sv; rProg && rProg()")
    # --- Historique : calendrier compact
    ev("setTab('histo')"); pg.wait_for_timeout(600)
    h = ev("Math.round(document.querySelector('.hcal').getBoundingClientRect().height)")
    z = ev("(() => { const b = document.querySelector('button.hc'); if (!b) return [44, 44]; const a = getComputedStyle(b, '::after'); return [parseFloat(a.width), parseFloat(a.height)]; })()")
    hc = ev("Math.round(document.querySelector('button.hc').getBoundingClientRect().height)")
    check("Historique : calendrier accessible par défaut (case ≥ 44 px, règle des options)", hc >= 44, (h, hc, z))
    shot(pg, "historique")
    # --- Amis : podium dès 3 membres (v76, demande d'Alane)
    FIX = "CL = {rows: [%s]}; clErr = ''; agendaSeg = 'amis'; setTab('agenda'); rAgenda()"
    mem = lambda n: ",".join("{nom:'%s',ris:%s,total:%s,disc:'street',pays:'BE'%s}" % (x, 80 - i * 3, 190 - i * 10, ",me:true" if i == 1 else "") for i, x in enumerate(["Tom", "Alane", "Inès", "Sam", "Yanis", "Léa"][:n]))
    ev(FIX % mem(3)); pg.wait_for_timeout(600)
    check("Amis (3 membres, v76) : podium, ma position, pas de liste en dessous", ev("!!document.querySelector('.podium')") and ev("!!document.querySelector('.mepos')") and ev("document.querySelectorAll('.clrow').length") == 0, ev("document.querySelector('#v-agenda').innerText.slice(0, 300)"))
    ev(FIX % mem(2)); pg.wait_for_timeout(400)
    check("Amis (2 membres) : pas de podium, ma position et la liste", not ev("!!document.querySelector('.podium')") and ev("document.querySelectorAll('.clrow').length") == 2)
    ev(FIX % mem(4)); pg.wait_for_timeout(400)
    check("Amis (4 membres, v76) : podium puis la liste dès le 4e", ev("!!document.querySelector('.podium')") and ev("document.querySelectorAll('.clrow').length") == 1)
    ev(FIX % mem(3)); pg.wait_for_timeout(400)
    shot(pg, "amis-3")
    ev(FIX % mem(6)); pg.wait_for_timeout(600)
    check("Amis (6 membres) : podium conservé", ev("!!document.querySelector('.podium')"))
    ev("CL = {rows: [{nom:'Alane',ris:79,total:190,disc:'street',pays:'BE',me:true}]}; rAgenda()"); pg.wait_for_timeout(400)
    check("Amis (seul) : état clair, sans podium", not ev("!!document.querySelector('.podium')") and "seul membre" in ev("document.querySelector('#v-agenda').innerText"), ev("document.querySelector('#v-agenda').innerText.slice(0, 300)"))
    # --- Réglages
    ev("setTab('seance'); openSheet('settings')"); pg.wait_for_timeout(700)
    st = ev("document.querySelector('.sheet').innerText"); vals = ev("[...document.querySelectorAll('.sheet input')].map(i => i.value).join(' ')")
    check("Réglages : aucune adresse de Google Sheet visible", "docs.google.com" not in st and "docs.google.com" not in vals, vals[:120])
    check("Réglages : « Se déconnecter » au style distinct", ev("(() => { const b = document.querySelector('[data-act=logout]'); return !!b && b.classList.contains('danger'); })()"))
    check("Réglages : « Méthodes et sources » replié", ev("(() => { const d = document.querySelector('details.srcs'); return !!d && !d.open && d.querySelector('summary').innerText.includes('Méthodes'); })()"))
    shot(pg, "reglages")
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
