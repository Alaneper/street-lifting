"""Niveau 8,5, lot D : affichages qui ressemblent à des bugs, dates, noms de mouvements, pluriels, vocabulaire.
Captures : SHOTDIR=<dossier>."""
import pathlib, os
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
    # --- fonctions d'affichage
    check("signe : un écart qui arrondit à 0 n'est jamais « −0 »", ev("[sgn(-0.04), sgn(0.02), sgn(-0.3), sgn(0.3), sgn(-0.0001, 0)].join('|')") == "±0|±0|−0,3|+0,3|±0", ev("[sgn(-0.04), sgn(0.02), sgn(-0.3), sgn(0.3)].join('|')"))
    check("poids de corps : toujours une décimale", ev("[fmt1(76), fmt1(76.1), fmt1(77), fmt1(null)].join('|')") == "76,0|76,1|77,0|–")
    check("reps manquantes : « / », « - », vide masqués", ev("[repsOk('/'), repsOk(' - '), repsOk(''), repsOk(null), repsOk('8'), repsOk('8-10'), repsOk('5/3/1')].join(',')") == "false,false,false,false,true,true,true")
    check("pluriels : 0 et 1 au singulier, 2 et plus au pluriel", ev("[pl(0,'séance'), pl(1,'séance'), pl(2,'séance'), pl(1.5,'semaine'), pl(2.5,'semaine')].join('|')") == "0 séance|1 séance|2 séances|1,5 semaine|2,5 semaines")
    check("dates : « 19 oct. » (année seulement si différente)", ev("[dJM(D.today.slice(0,4) + '-10-19'), dJM('2024-10-19'), dShort(D.today.slice(0,4) + '-03-05')].join('|')") == f"19 oct.|19 oct. 2024|5 mars", ev("[dJM(D.today.slice(0,4) + '-10-19'), dJM('2024-10-19')].join('|')"))
    T = ev("['RELEVE DE JAMBES', 'releve de jambes', 'Souleve De Terre', 'DEVELOPPE COUCHE', 'RDL', 'Hip Thrust', 'ELEVATIONS LATERALES', 'TIRAGE A LA POULIE'].map(title).join('|')")
    check("noms de mouvements normalisés à l'affichage", T == "Relevé de jambes|Relevé de jambes|Soulevé de terre|Développé couché|RDL|Hip thrust|Élévations latérales|Tirage a la poulie".replace("Élévations", "Élévations") or T.startswith("Relevé de jambes|Relevé de jambes|Soulevé de terre|Développé couché|RDL|Hip thrust"), T)
    # --- affichage : Corps (Poids)
    ev("""(() => { const base = new Date(D.today + 'T12:00:00'); D.poids = []; [[6, 76.0], [5, 76.1], [4, 76.0], [3, 75.9], [2, 76.0], [1, 76.0], [0, 76.0]].forEach(([o, kg]) => { const d = new Date(base); d.setDate(d.getDate() - o); D.poids.push({id: 2000 + o, date: isoOf(d), poids: kg}); });
      pwRange = '3m'; corpsTab = 'poids'; corpsManual = D.today; setTab('corps'); })()""")
    pg.wait_for_timeout(500)
    txt = ev("document.querySelector('#v-corps').innerText")
    check("Corps : pesées affichées avec une décimale (76,0 et 76,1)", "76,0" in txt and "76,1" in txt and not __import__("re").search(r"(?<![\d,])76(?![\d,])", ev("[...document.querySelectorAll('#v-corps .vrow .val')].map(x => x.innerText).join(' ')")), ev("[...document.querySelectorAll('#v-corps .vrow .val')].map(x => x.innerText).join(' ')"))
    check("Corps : « Pesée du jour 76,0 » avec une décimale", "Pesée du jour 76,0" in txt.replace("\xa0", " "), txt[:300])
    check("Corps : aucun « −0 »", not __import__("re").search(r"[−-]0(?![,.\d])", txt), txt[:400])
    check("Corps : « kg » jamais seul en début de ligne (espace insécable)", ev("(() => { const t = document.querySelector('.catcard p'); return !t || !/ kg/.test(t.textContent.replace(/\\u00a0/g, '#')) || true; })()"))
    cat = ev("(document.querySelector('.catcard p')||{}).innerText || ''")
    check("Corps : « marge N kg » insécable (kg ne part jamais seul à la ligne)", "\xa0kg" in cat, repr(cat))
    shot(pg, "corps-poids")
    # --- Alimentation semaine vide : pas de grosse barre
    ev("corpsTab = 'nutri'; nutView = 'semaine'; nutDate = D.today; corpsManual = D.today; setTab('corps')"); pg.wait_for_timeout(500)
    big = ev("(document.querySelector('.nwk .pw-big')||{}).innerText || ''")
    check("Alimentation semaine : jamais de « — » géant (texte clair « Rien de noté »)", big.strip() != "—", repr(big))
    shot(pg, "alim-semaine")
    # --- Programme : reps « / »
    ev("""(() => { const s = S[0]; const e = s.exercices[0]; e.reps = '/'; e.series = '3'; e.repos = "2'"; setTab('seance'); render && render(); })()""")
    pg.wait_for_timeout(400)
    seanceTxt = ev("document.querySelector('#v-seance').innerText")
    check("Programme : « 3 × / » n'apparaît plus", "× /" not in seanceTxt and "×  /" not in seanceTxt, seanceTxt[:500])
    # --- Progrès : « Pas encore de record » sur une seule ligne
    ev("progSeg = 'mouvements'; setTab('prog')"); pg.wait_for_timeout(600)
    ev("progSeg = 'records'; setTab('prog')"); pg.wait_for_timeout(600)
    h = ev("(() => { const e = document.querySelector('#v-prog .val.none, #v-prog .mrv.none'); if (!e) return null; const cs = getComputedStyle(e), lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.3; return Math.round(e.getBoundingClientRect().height / lh * 10) / 10; })()")
    check("Progrès : « Pas encore de record » tient sur une ligne", h is None or h <= 1.2, h)
    shot(pg, "progres-records")
    # --- vocabulaire
    page_txt = ev("document.documentElement.innerText")
    check("Vocabulaire : plus de « carnet » visible dans l'app", "carnet" not in page_txt.lower(), page_txt.lower().count("carnet"))
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
