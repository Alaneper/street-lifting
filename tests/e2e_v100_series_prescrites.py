"""v72 : en séance en direct, le nombre de séries suit la prescription (« 2 × 2 » → 2 séries), même si la séance a été ouverte avant (état gardé sur le téléphone),
sauf si le sportif a lui-même ajouté ou retiré une série."""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(1500)
    ev = lambda js, *a: pg.evaluate(js, *a)
    def find(kind):
        return ev("""(kind) => { for (const s of S) { if (s.archived) continue; for (let k = 0; k < s.exercices.length; k++) { const e = s.exercices[k];
            if (isCardioEx(e) || isTimedEx(e) || !(num(e.series) >= 2) || !/^\\d+$/.test(String(e.reps).trim())) continue;
            const lift = !!liftOf(e.mouvement); if ((kind === "lift") === lift) return {key: s.key, k, n: Math.min(12, num(e.series))}; } } return null; }""", kind)
    for kind, lab in (("lift", "mouvement de compétition"), ("renfo", "musculation")):
        t = find(kind)
        check("jeu de test : un exercice « %s » à 2 séries ou plus existe" % lab, t is not None)
        if not t: continue
        key, k, n = t["key"], t["k"], t["n"]
        def reset():
            ev("localStorage.removeItem('sl4-live')"); ev("(a) => { live = null; }", 0)
        reset(); ev("async (a) => { await startLive(a[0], a[1]); }", [key, k]); pg.wait_for_timeout(300)
        len0 = ev("(k) => live.rows[k].sets.length", k)
        check("[%s] ouverture normale : %d séries pour la prescription" % (lab, n), len0 == n, len0)
        # 1. état ancien : une seule série, rien de fait ni saisi
        ev("(k) => { const r = live.rows[k]; r.sets = r.sets.slice(0, 1); r.dirty = false; delete r.cnt; persistLive(); renderLayer(); }", k); pg.wait_for_timeout(200)
        now = ev("(k) => live.rows[k].sets.length", k); txt = ev("document.querySelector('.lsh span') ? document.querySelector('.lsh span').textContent : ''")
        check("[%s] séance gardée avec 1 série : revient à %d" % (lab, n), now == n, now)
        check("[%s] texte « 0 faite sur %d · il en reste %d »" % (lab, n, n), ("0 faite sur %d" % n) in txt and ("il en reste %d" % n) in txt, txt)
        # 2. une série déjà validée, prescription plus grande : on complète sans toucher à la série faite
        ev("(k) => { const r = live.rows[k]; r.sets = [Object.assign({}, r.sets[0], {done:true, c:77, r:5})]; r.dirty = true; delete r.cnt; persistLive(); renderLayer(); }", k); pg.wait_for_timeout(200)
        st = ev("(k) => live.rows[k].sets.map(x => [x.done, x.c, x.r])", k)
        check("[%s] 1 série faite + prescription de %d : complété à %d, la série faite est intacte" % (lab, n, n), len(st) == n and st[0] == [True, 77, 5] and not any(x[0] for x in st[1:]), st)
        # 3. le sportif retire une série : son choix est respecté
        reset(); ev("async (a) => { await startLive(a[0], a[1]); }", [key, k]); pg.wait_for_timeout(300)
        pg.click("[data-act=delSet]"); pg.wait_for_timeout(200); pg.evaluate("renderLayer()"); pg.wait_for_timeout(200)
        check("[%s] série retirée à la main : %d séries conservées" % (lab, n - 1), ev("(k) => live.rows[k].sets.length", k) == n - 1, ev("(k) => live.rows[k].sets.length", k))
        # 4. le sportif ajoute une série : son choix est respecté
        pg.click("[data-act=addSet]"); pg.wait_for_timeout(200); pg.click("[data-act=addSet]"); pg.wait_for_timeout(200); pg.evaluate("renderLayer()"); pg.wait_for_timeout(200)
        check("[%s] séries ajoutées à la main : %d conservées" % (lab, n + 1), ev("(k) => live.rows[k].sets.length", k) == n + 1, ev("(k) => live.rows[k].sets.length", k))
        # 5. rechargement de la page : l'état gardé est relu et reste cohérent
        pg.reload(); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0", timeout=20000); pg.wait_for_timeout(1200)
        saved = ev("() => { const v = JSON.parse(localStorage.getItem('sl4-live') || 'null'); return v ? v.rows : null; }")
    # 6. carte « Nouveau record » : seulement pour une série faite ; l'annulation de la validation la retire
    t = find("lift"); reset(); ev("async (a) => { await startLive(a[0], a[1]); }", [t["key"], t["k"]]); pg.wait_for_timeout(300)
    ev("(k) => { const r = live.rows[k]; r.sets[0] = Object.assign({}, r.sets[0], {done:false, rec:true, recD:2.5}); persistLive(); renderLayer(); }", t["k"]); pg.wait_for_timeout(200)
    check("série non faite marquée record (état ancien) : pas de carte « Nouveau record »", ev("!document.querySelector('.recc')"))
    ev("(k) => { const r = live.rows[k]; r.sets[0].done = true; r.sets[0].rec = true; r.sets[0].recD = 2.5; persistLive(); renderLayer(); }", t["k"]); pg.wait_for_timeout(200)
    check("série faite et record : la carte « Nouveau record » s'affiche", ev("!!document.querySelector('.recc')"))
    ev("(k) => { const st = live.rows[k]; st.ed = undefined; renderLayer(); }", t["k"]); pg.wait_for_timeout(150)
    pg.click(".lsr.done [data-act=doneSet]"); pg.wait_for_timeout(250)
    check("annulation de la validation : la carte disparaît et le drapeau record est retiré", ev("!document.querySelector('.recc')") and ev("(k) => !live.rows[k].sets[0].rec && !live.rows[k].sets[0].done", t["k"]))
    reset()
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
