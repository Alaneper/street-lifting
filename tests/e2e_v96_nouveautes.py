"""Lot final · « Nouveautés » et question « C'est ta prog perso ? » : compte neuf = rien ; compte existant = une fois ; choix déjà faits conservés ;
la charge dans le Sheet n'est JAMAIS activée sans réponse « Oui » ; jamais proposée sur un modèle coach WEEK.
Rejoue : python3 tests/e2e_v96_nouveautes.py"""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
ERRS = []
def boot(c, pre=None):
    pg = c.new_page(); pg.on("pageerror", lambda e: ERRS.append(str(e)))
    if pre: pg.add_init_script(pre)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(2200)
    return pg
with sync_playwright() as p:
    br = p.chromium.launch()
    new = lambda: br.new_context(viewport={"width":390, "height":844}, service_workers="block")
    # 1 · compte existant : Nouveautés une fois ; la question n'apparaît que si le Sheet est un modèle non-WEEK avec colonne Charge
    c = new(); c.route("**/*", route); pg = boot(c); ev = pg.evaluate
    info = ev("() => ({sheet, week:S.some(z => z.week), cols:S.some(z => z.sheet && z.cols && z.cols.charge), cid:coachId(), q:csQuestion(), on:chargeSyncOn(coachId())})")
    print("   état du jeu de test :", info)
    check("compte existant : « Nouveautés » ouverte", info["sheet"] == "news", info)
    check("la charge dans le Sheet n'est PAS activée par « Nouveautés » (fermée sans répondre)", not info["on"], info)
    q_txt = ev("() => (document.querySelector('.sheet')||{}).textContent||''")
    check("question « C'est ta prog perso ? » : affichée seulement si éligible (non WEEK + colonne Charge)", ("C'est ta prog perso" in q_txt) == info["q"], (info["q"], "C'est ta prog perso" in q_txt))
    ev("() => closeSheet()"); pg.wait_for_timeout(300)
    ev("() => maybeNews()"); pg.wait_for_timeout(300)
    check("fermée sans répondre : ni activée, ni reposée (une seule fois)", not ev("chargeSyncOn(coachId())") and ev("sheet") != "news")
    # 2 · simulation d'éligibilité
    def fresh_news():
        ev("() => { store.set(NEWS_K, {v:NEWS_V}); sheet = null; page = null; }")
    ev("() => { S.forEach(z => { z.week = false; z.sheet = z.sheet || 'X'; z.cols = Object.assign({}, z.cols || {}, {charge: z.cols && z.cols.charge || 5}); }); store.set(NEWS_K, {v:NEWS_V}); sheet = null; page = null; renderLayer(); }")
    check("Sheet perso (non WEEK, colonne Charge) : la question est éligible", ev("csQuestion()") is True)
    ev("() => maybeNews()"); pg.wait_for_timeout(300)
    t = ev("() => ({sheet, txt:(document.querySelector('.sheet')||{}).textContent||''})")
    check("… elle s'affiche seule (sans la liste, déjà vue)", t["sheet"] == "news" and "C'est ta prog perso" in t["txt"] and "Barre et disques" not in t["txt"], t["txt"][:120])
    check("… et ne coche rien toute seule", not ev("chargeSyncOn(coachId())"))
    pg.click("[data-act=newsQ][data-v='0']"); pg.wait_for_timeout(400)
    check("réponse « Non » : désactivée, feuille fermée", not ev("chargeSyncOn(coachId())") and ev("sheet") is None)
    ev("() => maybeNews()"); pg.wait_for_timeout(300)
    check("… et la question n'est plus reposée", ev("sheet") is None)
    ev("() => { store.set(NEWS_K, {v:NEWS_V}); ACT.newsQ({v:'1'}); }"); pg.wait_for_timeout(300)
    check("réponse « Oui » : activée pour ce Sheet", ev("chargeSyncOn(coachId())"))
    ev("() => { setChargeSync(coachId(), false); store.set(NEWS_K, {v:NEWS_V}); S[0].week = true; }")
    check("modèle coach WEEK : la question n'est JAMAIS proposée", ev("csQuestion()") is False)
    ev("() => { maybeNews(); }"); pg.wait_for_timeout(300)
    check("… même au lancement : aucune feuille", ev("sheet") is None)
    c.close()
    # 3 · choix déjà faits conservés : charge dans le Sheet déjà activée avant la mise à jour ; options absentes = défauts
    c = new(); c.route("**/*", route)
    pg = boot(c); ev = pg.evaluate
    cid = ev("coachId()")
    ev("(id) => { store.set('sl4-chargesync', {[id]: true}); store.set('sl4-news', null); sheet = null; }", cid)
    pg.reload(); pg.wait_for_timeout(3500)
    s = ev("() => ({on:chargeSyncOn(coachId()), sheet, q:csQuestion(), opts:store.get('sl4-opts'), d:OPTS.every(o => optOn(o.k) === (o.k !== 'calc'))})")
    check("testeur existant : son choix « charge dans le Sheet » activé est conservé", s["on"], s)
    check("… et la question n'est pas reposée puisqu'il a déjà choisi", s["q"] is False, s)
    check("… ses options d'affichage valent les défauts (rien n'était enregistré)", s["opts"] in (None, {}) and s["d"], s)
    # 4 · compte neuf : aucune « Nouveautés »
    ev("() => { store.set('sl4-news', null); D.series = []; D.poids = []; S.length = 0; sheet = null; }")
    ev("() => { S = []; maybeNews(); }"); pg.wait_for_timeout(300)
    check("compte neuf (aucune donnée) : pas de « Nouveautés », marqué comme vu", ev("sheet") != "news" and ev("(store.get('sl4-news')||{}).v") == "69", ev("[sheet, store.get('sl4-news')]"))
    check("aucune erreur JavaScript", not ERRS, ERRS[:3])
    br.close()
print("\nÉCHECS :", fails if fails else "aucun"); print("TOUT OK" if not fails else "ÉCHEC")
raise SystemExit(1 if fails else 0)
