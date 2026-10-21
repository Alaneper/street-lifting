"""Version 20 : un test par bug corrigé (relevé de la vidéo du 21/10/2026)."""
import pathlib, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []; odd = []; NCHK = [0]
_route = route
def route(r):
    m = re.match(r"http://app\.local/sl/([^?#]*)", r.request.url)
    if m and m.group(1) not in ("", "index.html", "test-build.html") and not (P / m.group(1)).exists():
        odd.append((r.request.url, NCHK[0])); return r.fulfill(status=404, body="")
    return _route(r)
def check(name, cond, info=""):
    NCHK[0] += 1
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
    check("compét : bouton du calendrier sur une ligne (390 px)", r[0] == "Mes compét dans le Calendrier" and r[1] <= 56, r)
    pg.set_viewport_size({"width":320, "height":700}); pg.wait_for_timeout(300)
    r = pg.evaluate("document.querySelector('[data-act=ics]').getBoundingClientRect().height")
    check("compét : bouton du calendrier sur une ligne (320 px)", r <= 56, r)
    pg.set_viewport_size({"width":390, "height":844}); pg.wait_for_timeout(300)
    r = pg.evaluate("[...document.querySelectorAll('[data-act=editComp],[data-act=delComp]')].map(b => Math.round(b.getBoundingClientRect().height))")
    check("compét : Modifier / Supprimer ≥ 44 px", r and min(r) >= 44, r)

    # 6. Infobulle du volume : mouvements à 0 masqués, total ajouté
    pg.evaluate("setTab('prog')"); pg.wait_for_function("charts['c-vol']", timeout=10000)
    r = pg.evaluate("""(() => { const t = charts['c-vol'].options.plugins.tooltip; return [t.filter({parsed:{y:0}}), t.filter({parsed:{y:630}}), t.callbacks.footer([{parsed:{y:1710}}, {parsed:{y:630}}]), t.callbacks.label({dataset:{label:'Dips'}, parsed:{y:1710}})]; })()""")
    check("volume : lignes à 0 masquées", r[0] is False and r[1] is True, r)
    check("volume : total et séparateur de milliers", r[2].replace(" ", " ") == "Total : 2 340 kg" and r[3].replace(" ", " ") == "Dips : 1 710 kg", r)

    # 7. Chart.js chargé en différé : un graphique demandé avant son chargement est dessiné ensuite
    r = pg.evaluate("""(() => { const C = window.Chart; charts['c-vol'].destroy(); delete charts['c-vol']; window.Chart = undefined; chartReady = false;
      setTab('prog'); setTab('home'); setTab('prog'); const before = !!charts['c-vol'], queued = chartQ.size; window.Chart = C; chartReady = true; chartQ.forEach(f => f()); chartQ.clear(); return [before, queued, !!charts['c-vol']]; })()""")
    check("graphique différé puis dessiné, une seule attente par graphique", r[0] is False and r[2] is True and r[1] <= 2, r)
    r = pg.evaluate("""(() => { const C = window.Chart; window.Chart = undefined; setTab('home'); setTab('prog'); const n = chartQ.size; window.Chart = C; setTab('prog'); return n; })()""")
    check("Chart.js absent après le chargement : rien ne s'accumule", r == 0, r)

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

    # 15. Relecture « regard neuf » : bandeau de mise à jour jamais au-dessus d'une séance
    pg.evaluate("setTab('home'); updShown = false; touched = true; newVersion()"); pg.wait_for_timeout(300)
    check("mise à jour : bandeau affiché hors séance", pg.evaluate("!!document.querySelector('.upd') && getComputedStyle(document.querySelector('.upd')).display !== 'none'"))
    key = pg.evaluate("(nextSeance()||S.at(-1)).key"); pg.evaluate(f"startLive({json.dumps(key)}, 0)"); pg.wait_for_timeout(700); pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(300)
    r = pg.evaluate("""(() => { const u = document.querySelector('.upd'), b = document.querySelector('[data-act=finishLive]').getBoundingClientRect();
      const t = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2); return [getComputedStyle(u).display, t && t.dataset.act]; })()""")
    check("mise à jour : bandeau caché pendant une séance, « Terminer » touchable", r == ["none", "finishLive"], r)
    pg.evaluate("live = null; renderLayer(); store.del(ck('sl4-live')); document.querySelector('.upd').remove(); updShown = false")
    # 16. Passage chez Google en cours : une mise à jour ne l'interrompt pas
    r = pg.evaluate("(() => { auth.leaving = true; touched = false; const n = newVersion(); const shown = !!document.querySelector('.upd'); auth.leaving = false; touched = true; return shown; })()")
    check("mise à jour : rien pendant le passage chez Google", r is False, r)
    # 17. Lecture groupée refusée (onglet renommé) : repli bloc par bloc, la prog reste là
    n0 = pg.evaluate("S.length")
    pg.evaluate("""(() => { const f0 = window.fetch; window.__f0 = f0; window.fetch = (u, o) => /batchGet/.test(String(u)) && /BLOC/.test(decodeURIComponent(String(u))) ? Promise.resolve(new Response('{"error":{"message":"Unable to parse range"}}', {status:400})) : f0(u, o); })()""")
    pg.evaluate("syncAll(true)"); pg.wait_for_function("!syncing", timeout=30000)
    r = pg.evaluate("[S.length, seanceErr, document.querySelector('.avatar').getAttribute('aria-label')]")
    check("prog : lecture groupée refusée → repli bloc par bloc", r[0] == n0 and r[1] == "", r)
    # 18. Réseau perdu pendant la lecture des blocs : la prog affichée et le cache restent intacts
    pg.evaluate("window.COACH = " + json.dumps(COACH))
    pg.evaluate("""(() => { window.fetch = (u, o) => String(u).includes(COACH) && /BLOC/.test(decodeURIComponent(String(u))) ? Promise.reject(new TypeError('Failed to fetch')) : window.__f0(u, o); })()""")
    pg.evaluate("syncAll(true)"); pg.wait_for_function("!syncing", timeout=30000)
    r = pg.evaluate("[S.length, (store.get(ck('sl4-cache')) || {}).S.length, document.querySelector('.avatar').getAttribute('aria-label'), !!seanceErr]")
    check("prog : échec de lecture → séances et cache conservés, état « pas synchronisé »", r[0] == n0 and r[1] == n0 and r[2] == "Réglages · pas synchronisé" and r[3], r)
    pg.evaluate("() => { window.fetch = window.__f0; }"); pg.evaluate("syncAll(true)"); pg.wait_for_function("!syncing", timeout=30000)
    # 19. « Pas notée » réservé aux séances avant la prochaine séance ; dates d'une autre année lisibles
    r = pg.evaluate("""(() => { const ns = nextSeance(), after = S[S.indexOf(ns) + 1]; if (!after || after.bloc !== ns.bloc) return 'skip';
      const t = D.today; D.today = '2099-01-01'; sel = after.key; setTab('seance'); const v = document.querySelector('#v-seance .hero .hu').textContent; D.today = t; return v; })()""")
    check("séance après la prochaine, en retard sur les dates estimées → « À venir »", r in ("À venir", "skip"), r)
    r = pg.evaluate("[dShort('2025-10-14'), dShort(D.today.slice(0, 4) + '-10-14')]")
    check("dates courtes : « oct. 25 » pour une autre année, jj/mm cette année", r == ["oct. 25", "14/10"], r)
    pg.evaluate("setTab('home')")

    # 14. Barre d'onglets : libellés inactifs lisibles
    pg.wait_for_timeout(500)   # la couleur des onglets a une transition de 0,2 s
    r = pg.evaluate("getComputedStyle(document.querySelector('.tabs button:not([aria-current=page])')).color")
    check("onglets inactifs en gris lisible (#8A9099)", r == "rgb(138, 144, 153)", r)
    check("aucune erreur console", not errs, errs[:5])
    br.close()
print("requêtes inattendues :", odd)
print("ÉCHECS :", fails)
