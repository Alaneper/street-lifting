"""Version 21 : choix d'Alane du 21/10/2026 (maquettes 1B, 2B, 3A + trois changements de comportement)."""
import pathlib, json, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
def lum(rgb):
    v = [int(x) / 255 for x in re.findall(r"\d+", rgb)[:3]]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(v[0]) + 0.7152 * f(v[1]) + 0.0722 * f(v[2])
def cr(a, b):
    la, lb = lum(a), lum(b); return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=1, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(2500)

    # 1B. En-tête fixe : reste en haut au défilement, fond derrière, nom de l'onglet affiché
    pg.evaluate("scrollTo(0, 400)"); pg.wait_for_timeout(400)
    r = pg.evaluate("""(() => { const t = document.querySelector('.topbar').getBoundingClientRect(), b = getComputedStyle(document.querySelector('.topbar'), '::before');
      return [Math.round(t.top), document.body.classList.contains('scrolled'), getComputedStyle(document.querySelector('#tabname')).opacity, b.backgroundColor, b.left]; })()""")
    check("en-tête : reste en haut au défilement", r[0] == 0 and r[1], r)
    check("en-tête : nom de l'onglet visible au défilement", r[2] == "1", r)
    check("en-tête : fond opaque derrière (barre d'état)", "0.86" in r[3] or "rgba" not in r[3], r)
    r = pg.evaluate("(() => { const t = document.querySelector('.topbar').getBoundingClientRect(); const e = document.elementFromPoint(195, t.top + 10); return e && !!e.closest('.topbar'); })()")
    check("en-tête : le contenu passe dessous, pas dessus", r is True, r)
    pg.evaluate("scrollTo(0, 0)"); pg.wait_for_timeout(300)
    check("en-tête : nom de l'onglet masqué en haut de page", pg.evaluate("getComputedStyle(document.querySelector('#tabname')).opacity") == "0")
    pg.evaluate("setTab('prog')"); check("en-tête : nom de l'onglet suit l'onglet", pg.evaluate("document.querySelector('#tabname').textContent") == "Progrès")

    # 2B. Héros des mouvements : carte sombre, chiffre en couleur, contrastes AA
    pg.evaluate("""(() => { setTab('seance'); const el = document.querySelector('#v-seance');
      el.insertAdjacentHTML('afterbegin', ['MU','PULL','DIP','SQUAT'].map(l => heroCard({color:LCOL[l], small:'Mercredi 21 octobre · bloc 7, semaine 2', big:'Séance 2', sub:'À venir'})).join('')); })()""")
    r = pg.evaluate("""[...document.querySelectorAll('#v-seance .hero.mv')].slice(0, 4).map(h => [getComputedStyle(h).backgroundColor, getComputedStyle(h.querySelector('.hb')).color, getComputedStyle(h.querySelector('.hs')).color, getComputedStyle(h.querySelector('.hu')).color])""")
    deck = "rgb(22, 24, 28)"
    worst = min(min(cr(x[1], deck), cr(x[2], deck) / 1.5 * 1.5, cr(x[3], deck)) for x in r) if r else 0
    check("héros : 4 mouvements en carte sombre", len(r) == 4 and all(x[0] == deck for x in r), r)
    check("héros : chiffre ≥ 3:1, petits textes ≥ 4,5:1", all(cr(x[1], deck) >= 3 and cr(x[2], deck) >= 4.5 and cr(x[3], deck) >= 4.5 for x in r), [[round(cr(x[i], deck), 2) for i in (1, 2, 3)] for x in r])
    check("héros : le bleu plein reste pour le total / J-X", pg.evaluate("(() => { setTab('home'); const h = document.querySelector('#v-home .hero'); return !h.classList.contains('mv') && getComputedStyle(h).backgroundColor === 'rgb(31, 95, 208)'; })()"))
    # Couleurs d'état neutres
    pg.evaluate("setTab('prog')"); pg.wait_for_timeout(600)
    r = pg.evaluate("[...document.querySelectorAll('.tag.ok')].map(t => getComputedStyle(t).backgroundColor)")
    check("renfo : « Monte la charge » sans le vert des dips", all(x == "rgb(255, 255, 255)" for x in r), r)
    r = pg.evaluate("[...document.querySelectorAll('#v-prog span.small[style*=color]')].map(e => getComputedStyle(e).color).filter(c => c === 'rgb(43, 182, 115)' || c === 'rgb(255, 111, 97)')")
    check("progrès : écarts sans vert ni rouge", r == [], r)
    pg.wait_for_function("charts['c-vol']", timeout=10000)
    check("infobulle sombre", pg.evaluate("charts['c-vol'].options.plugins.tooltip.backgroundColor") == "#2A2E34")

    # 3A. Pesée du matin : carte sous le héros, bouton et marge mis à jour en direct, disparaît une fois pesé
    pg.evaluate("D.poids = D.poids.filter(p => p.date !== D.today); setTab('home')"); pg.wait_for_timeout(300)
    r = pg.evaluate("""(() => { const h = document.querySelector('#v-home .hero'), w = document.querySelector('#v-home .weigh'); return [!!w, w && h.nextElementSibling === w, document.querySelector('#hwbtn').textContent, (document.querySelector('#hwlim') || {}).textContent]; })()""")
    check("pesée : carte juste sous le héros", r[0] and r[1], r)
    pg.click(".weigh [data-act=stepW][data-d='0.1']"); pg.wait_for_timeout(150)
    r2 = pg.evaluate("[document.querySelector('#hw').value, document.querySelector('#hwbtn').textContent, (document.querySelector('#hwlim') || {}).textContent]")
    check("pesée : « + » met à jour le bouton et la marge", r2[1] != r[2] and r2[0] in r2[1] and (r2[2] or "") != (r[3] or ""), [r, r2])
    check("pesée : boutons de 56 px", pg.evaluate("[...document.querySelectorAll('.weigh .stepper button')].every(b => b.getBoundingClientRect().height >= 56)"))
    n0 = pg.evaluate(f"window.__sheets['{APP}'].POIDS.length")
    pg.click("#hwbtn"); pg.wait_for_timeout(1200)
    r = pg.evaluate(f"[window.__sheets['{APP}'].POIDS.length, !!document.querySelector('#v-home .weigh'), document.querySelector('#toast').textContent]")
    check("pesée : enregistrée en un toucher, la carte disparaît", r[0] == n0 + 1 and r[1] is False, r)
    check("pesée : le toast donne la marge sur la catégorie", "limite" in r[2], r)
    check("pesée : l'ancien bloc en bas de page a disparu", "Enregistrer ma pesée" not in pg.evaluate("document.querySelector('#v-home').textContent"))

    # Comportement 1 : 1RM estimé depuis la série la plus lourde
    r = pg.evaluate("""(() => { const sets = [{c:15, r:10, rpe:null, date:D.today}, {c:32.5, r:3, rpe:10, date:D.today}, {c:22.5, r:5, rpe:9, date:D.today}, {c:32.5, r:1, rpe:null, date:D.today}];
      const e = e1rmBest('PULL', sets), w = bwAt(D.today); return [e.c, e.r, Math.round(e.v * 100) / 100, Math.round(((32.5 + w) / 0.922 - w) * 100) / 100]; })()""")
    check("1RM estimé : part de la charge la plus lourde (32,5 × 3), pas de 15 × 10", r[0] == 32.5 and r[1] == 3 and abs(r[2] - r[3]) < 0.01, r)
    r = pg.evaluate("""(() => { const o = exercisePoints().find(z => z.lift === 'SQUAT' && /COMP/.test(z.key)); const p = o.pts.at(-1); const top = Math.max(...p.sets.map(x => x.c));
      const w = bwAt(p.date || D.today); return [p.e1rmBest, Math.max(...p.sets.filter(x => x.c === top).map(x => e1rm(x.c, x.r, 'SQUAT', w)))]; })()""")
    check("1RM estimé d'une séance : depuis sa série la plus lourde", abs(r[0] - r[1]) < 1e-6, r)

    # Comportement 2 : reprise automatique de la séance (< 3 h), pas si on l'a fermée avec ×
    key = pg.evaluate("(() => { const ts = todaySeance(); return ((ts && !ts.faite ? ts : nextSeance()) || S.at(-1)).key; })()")
    pg.evaluate(f"startLive({json.dumps(key)}, 1)"); pg.wait_for_timeout(500); pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(300)
    pg.reload(); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0", timeout=20000); pg.wait_for_timeout(1500)
    check("reprise : l'app rouvre la séance en cours", pg.evaluate("!!live && !!document.querySelector('.live') && live.i === 1"), pg.evaluate("[!!live, live && live.i]"))
    pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(300)
    pg.click("[data-act=closeLive]"); pg.wait_for_timeout(800)
    pg.reload(); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0", timeout=20000); pg.wait_for_timeout(1500)
    check("reprise : pas de réouverture d'une séance fermée avec ×", pg.evaluate("!live && !document.querySelector('.live')"))
    check("reprise : « Reprendre la séance » reste proposé", "Reprendre la séance" in pg.evaluate("document.querySelector('#v-home').textContent"))
    pg.evaluate(f"""(() => {{ const k = ck('sl4-live'), v = store.get(k); v.paused = false; v.at = Date.now() - 4 * 3600e3; v.start = v.at; store.set(k, v); }})()""")
    pg.reload(); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0", timeout=20000); pg.wait_for_timeout(1500)
    check("reprise : pas après 3 h", pg.evaluate("!live"))
    pg.evaluate("store.del(ck('sl4-live'))")

    # Comportement 3 : Corps s'ouvre sur Poids avant midi si pas pesé ; sinon Alimentation ; choix manuel respecté
    r = pg.evaluate("""(() => { const H = Date.prototype.getHours, out = [];
      Date.prototype.getHours = () => 8; D.poids = D.poids.filter(p => p.date !== D.today); setTab('home'); setTab('corps'); out.push(corpsTab);
      setTab('home'); D.poids.push({date:D.today, poids:74.9}); setTab('corps'); out.push(corpsTab);
      Date.prototype.getHours = () => 15; D.poids = D.poids.filter(p => p.date !== D.today); setTab('home'); setTab('corps'); out.push(corpsTab);
      Date.prototype.getHours = () => 8; ACT.corpsTab({k:'nutri'}); setTab('home'); setTab('corps'); out.push(corpsTab);
      Date.prototype.getHours = H; return out; })()""")
    check("Corps : Poids le matin si pas pesé, sinon Alimentation, choix manuel gardé", r == ["poids", "nutri", "nutri", "nutri"], r)
    # Relecture v21
    pg.evaluate("hwDraft = null; D.poids = D.poids.filter(p => p.date !== D.today); setTab('home')"); pg.wait_for_timeout(300)
    for _ in range(3): pg.click(".weigh [data-act=stepW][data-d='0.1']")
    v0 = pg.evaluate("document.querySelector('#hw').value"); pg.evaluate("render()"); pg.wait_for_timeout(200)
    check("pesée : la saisie survit à une synchro", pg.evaluate("document.querySelector('#hw').value") == v0, v0)
    check("RPE S1 rattaché à la série lourde", pg.evaluate("compSets('SQUAT').some(x => x.r === 3 && x.rpe)"))
    r = pg.evaluate("""(() => { const e = e1rmBest('PULL', [{c:32.5, r:1, date:D.today}, {c:30, r:3, rpe:9, date:D.today}]); return [e.c, e.r]; })()""")
    check("1RM estimé : un 1 rep (déjà le PR) n'est pas la base de l'estimation", r == [30, 3], r)
    pg.evaluate("D.poids.push({date:D.today, poids:74.9})")
    key = pg.evaluate("(nextSeance()||S.at(-1)).key"); pg.evaluate(f"startLive({json.dumps(key)}, 0)"); pg.wait_for_timeout(500)
    check("séance : pas de feuille « poids » si déjà pesé aujourd'hui", pg.evaluate("sheet") != "pdc", pg.evaluate("sheet"))
    pg.evaluate(f"startLive({json.dumps(key)}, 0)"); pg.wait_for_timeout(300)
    check("séance : pas de double ouverture", pg.evaluate("document.querySelectorAll('.live').length") == 1)
    pg.evaluate("live = null; renderLayer(); store.del(ck('sl4-live'))")
    check("version 21 ou plus", int(pg.evaluate("APP_VER").split(" ")[0]) >= 21)
    check("aucune erreur console", not errs, errs[:5])
    br.close()
print("ÉCHECS :", fails)
