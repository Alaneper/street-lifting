"""Version 20 : un test par bug corrigé (relevé de la vidéo du 21/10/2026)."""
import pathlib, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, info if not cond else "")
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=1, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(2500)

    # 1. Séance passée non notée : « Pas notée » et non « À venir »
    r = pg.evaluate("""() => { const s = S.find(x => x.faite && dateOf(x) && dateOf(x) < D.today); s.faite = false; sel = s.key; setTab('seance');
      return document.querySelector('#v-seance .hero .hu').textContent; }""")
    check("séance passée non notée → « Pas notée »", r == "Pas notée", r)
    pg.evaluate("ACT.sync ? 0 : 0"); pg.evaluate("syncAll(true)"); pg.wait_for_timeout(2500)

    # 2. Texte de la pesée en compét : plus de « pour obtenir une projection »
    r = pg.evaluate("""() => { D.poids = D.poids.filter(p => p.date >= addDays(D.today, -21)).slice(-2); setTab('agenda'); return document.querySelector('#v-agenda').textContent; }""")
    check("compét : plus de « obtenir une projection »", "projection" not in r)
    check("compét : nombre de pesées manquantes", "2 pesées de plus" in r, r[r.find("Pesée"):r.find("Pesée") + 160])
    pg.evaluate("syncAll(true)"); pg.wait_for_timeout(2500)

    # 3. Accord : « séance faite » au singulier
    r = pg.evaluate("""() => { const w = defaultWeek(); const ss = S.filter(s => s.bloc === w.b && s.semaine === w.w); ss.forEach((s, i) => s.faite = i === 0);
      progSel = w; setTab('prog'); const h = [...document.querySelectorAll('#v-prog .hero')].find(e => /\\//.test(e.querySelector('.hb').textContent));
      return [h.querySelector('.hb').textContent, h.querySelector('.hu').textContent]; }""")
    check("progrès : « 1/4 séance faite » (accord)", r[0].startswith("1/") and r[1].startswith("séance faite"), r)
    pg.evaluate("syncAll(true)"); pg.wait_for_timeout(2500)

    # 4. Réglages : Non / Oui à l'écran, valeurs NON / OUI conservées dans le carnet
    pg.evaluate("ACT.settings()"); pg.wait_for_timeout(400)
    r = pg.evaluate("[...document.querySelectorAll('#smu option')].map(o => o.textContent + '=' + o.value)")
    check("réglages : « Non/Oui » affichés, valeurs NON/OUI", r == ["Non=NON", "Oui=OUI"], r)
    r = pg.evaluate("[...document.querySelectorAll('.sheet a.btn')].map(a => getComputedStyle(a).textDecorationLine)")
    check("réglages : « Ouvrir mon carnet » sans soulignement", r and all(x == "none" for x in r), r)
    pg.evaluate("ACT.closeSheet()")

    # 5. Bouton du calendrier sur une ligne
    pg.evaluate("setTab('agenda')"); pg.wait_for_timeout(300)
    r = pg.evaluate("(() => { const b = document.querySelector('[data-act=ics]'); return [b.textContent, b.getBoundingClientRect().height]; })()")
    check("compét : « Ajouter au Calendrier » sur une ligne", r[0] == "Ajouter au Calendrier" and r[1] <= 56, r)
    r = pg.evaluate("[...document.querySelectorAll('[data-act=editComp],[data-act=delComp]')].map(b => Math.round(b.getBoundingClientRect().height))")
    check("compét : Modifier / Supprimer ≥ 44 px", r and min(r) >= 44, r)

    # 6. Infobulle du volume : mouvements à 0 masqués, total ajouté
    pg.evaluate("setTab('prog')"); pg.wait_for_function("charts['c-vol']", timeout=10000)
    r = pg.evaluate("""(() => { const t = charts['c-vol'].options.plugins.tooltip; return [t.filter({parsed:{y:0}}), t.filter({parsed:{y:630}}), t.callbacks.footer([{parsed:{y:1710}}, {parsed:{y:630}}]), t.callbacks.label({dataset:{label:'Dips'}, parsed:{y:1710}})]; })()""")
    check("volume : lignes à 0 masquées", r[0] is False and r[1] is True, r)
    check("volume : total et séparateur de milliers", r[2].replace(" ", " ") == "Total : 2 340 kg" and r[3].replace(" ", " ") == "Dips : 1 710 kg", r)

    # 7. Chart.js chargé en différé : un graphique demandé avant son chargement est dessiné ensuite
    r = pg.evaluate("""(() => { const C = window.Chart; charts['c-vol'].destroy(); delete charts['c-vol']; window.Chart = undefined; rProg && 0;
      setTab('prog'); const before = !!charts['c-vol']; window.Chart = C; chartQ.splice(0).forEach(f => f()); return [before, !!charts['c-vol']]; })()""")
    check("graphique différé puis dessiné", r == [False, True], r)

    # 8. Synchro : la prog est relue en une requête groupée (au lieu d'une par bloc)
    pg.evaluate("window.__api = []"); pg.evaluate("syncAll(true)"); pg.wait_for_function("!syncing", timeout=20000); pg.wait_for_timeout(300)
    api = pg.evaluate("window.__api")
    blocs = [a for a in api if "BLOC" in a]
    check("synchro : blocs lus en une requête groupée", len(blocs) == 1 and "batchGet" in blocs[0], blocs)
    check("synchro : 10 appels Google au plus", len(api) <= 10, (len(api), api))

    # 9. Champ date d'iOS : ne déborde plus de sa colonne, aligné à gauche
    pg.evaluate("ACT.openLift({l:'PULL'})"); pg.wait_for_timeout(1200)
    r = pg.evaluate("(() => { const e = document.querySelector('#prd'), s = getComputedStyle(e); return [s.minWidth, s.appearance || s.webkitAppearance, s.textAlign, e.getBoundingClientRect().right <= e.parentElement.getBoundingClientRect().right + 0.5]; })()")
    check("date : min-width 0, apparence neutre, à gauche, dans son cadre", r[0] == "0px" and r[1] == "none" and r[2] == "left" and r[3], r)

    # 10. Fiche mouvement : titre lisible au lieu d'une pastille seule ; dates courtes qui tiennent dans les cases
    r = pg.evaluate("document.querySelector('.page .pagebar').textContent.trim()")
    check("fiche : titre « Tractions » dans la barre", r == "Tractions", r)
    r = pg.evaluate("[...document.querySelectorAll('.rm .tiny')].filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.textContent)")
    check("records par reps : aucune date coupée", r == [], r)
    pg.evaluate("ACT.closePage()"); pg.wait_for_timeout(300)

    # 11. Séance en direct : le toast ne recouvre plus « Terminer » ; boutons ≥ 44 px
    key = pg.evaluate("(nextSeance()||S.at(-1)).key"); pg.evaluate(f"startLive({json.dumps(key)}, 0)"); pg.wait_for_timeout(700)
    pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(300); pg.evaluate("toast('Record à 3 reps : 108,5 kg (+1)')"); pg.wait_for_timeout(500)
    r = pg.evaluate("(() => { const t = document.querySelector('#toast').getBoundingClientRect(), h = document.querySelector('[data-act=finishLive]').getBoundingClientRect(); return [t.top, h.bottom, h.height]; })()")
    check("séance : toast sous « Terminer »", r[0] >= r[1], r)
    check("séance : « Terminer » ≥ 44 px", r[2] >= 44, r)
    pg.wait_for_timeout(3500)
    r = pg.evaluate("document.querySelector('#toast').getBoundingClientRect().bottom")
    check("séance : toast caché entièrement hors de l'écran", r <= 0, r)
    r = pg.evaluate("[...document.querySelectorAll('[data-act=addSet],[data-act=delSet],[data-act=closeLive]')].map(b => Math.round(b.getBoundingClientRect().height))")
    check("séance : ajouter/retirer une série, fermer ≥ 44 px", r and min(r) >= 44, r)
    pg.evaluate("live = null; renderLayer(); store.del(ck('sl4-live'))"); pg.wait_for_timeout(300)

    # 12. Alimentation : pas de chiffre en double, méthode repliée, état vide clair
    pg.evaluate("setTab('corps'); corpsTab = 'nutri'; D.profil.nut_objectif = 'suivi'; rCorps()"); pg.wait_for_timeout(500)
    r = pg.evaluate("""(() => { const v = document.querySelector('#v-corps'); return [v.textContent.includes('Repère'), !!v.querySelector('details.more summary'), v.querySelector('.hero .hu').textContent]; })()""")
    check("alimentation : « Repère » en double retiré", r[0] is False, r)
    check("alimentation : méthode repliée", r[1] is True, r)
    check("alimentation : état vide explicite", r[2] in ("Rien de noté pour l'instant",) or "aliment" in r[2], r)

    # 13. Avatar : état de synchro annoncé
    r = pg.evaluate("document.querySelector('.avatar').getAttribute('aria-label')")
    check("avatar : état de synchro dans le libellé", r == "Réglages · données à jour", r)

    # 14. Barre d'onglets : libellés inactifs lisibles
    r = pg.evaluate("getComputedStyle(document.querySelector('.tabs button:not([aria-current=page])')).color")
    check("onglets inactifs en gris lisible (#8A9099)", r == "rgb(138, 144, 153)", r)
    check("aucune erreur console", not errs, errs[:5])
    br.close()
print("ÉCHECS :", fails)
