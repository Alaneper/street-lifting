"""Retour d'Alane (04/11, iPhone) : impossible de quitter la séance en direct, la flèche et « Pause » étaient sous l'heure et la batterie.
Cause : `.live .livehead{padding:4px 0 8px}` écrasait le décalage de la zone sûre. Test avec encoche (47 px) et barre d'accueil (34 px) simulées :
les boutons de l'en-tête sont sous la zone sûre, touchables (elementFromPoint), au repos et défilé ; « Pause » quitte bien la séance. Usage : python3 tests/e2e_v98_entete_encoche.py"""
import pathlib, os, sys
os.environ["SAFE_TOP"] = "47px"; os.environ["SAFE_BOTTOM"] = "34px"
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch()
    for nom, vp in (("390×844", {"width":390, "height":844}), ("375×667", {"width":375, "height":667}), ("430×932", {"width":430, "height":932})):
        c = br.new_context(viewport=vp, device_scale_factor=2, service_workers="block", has_touch=True, is_mobile=True); c.route("**/*", route)
        pg = c.new_page(); ev = pg.evaluate; errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
        pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(2000)
        ev("() => ACT.closeSheet && ACT.closeSheet()")
        ev("() => { const s = S.find(z => !z.archived && (+z.semaine) > 1 && z.exercices.length > 1); live = null; store.set('sl4-live', null); startLive(s.key); }"); pg.wait_for_timeout(800)
        ev("() => ACT.closeSheet && ACT.closeSheet()")
        m = """() => { const l = document.querySelector('.live'); const out = {};
          for (const sel of ['.livehead [data-act=closeLive]', '.endbtn']) { const r = document.querySelector(sel).getBoundingClientRect(); const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
            out[sel] = {top: Math.round(r.top), h: Math.round(r.height), hit: !!(t && t.closest('[data-act=closeLive]'))}; } return out; }"""
        for y in (0, 400):
            ev("(y) => { document.querySelector('.live').scrollTop = y; }", y); pg.wait_for_timeout(250)
            r = ev(m)
            check(f"{nom} · défilement {y} : flèche et Pause sous la zone sûre (≥ 47 px) et touchables", all(v["top"] >= 47 and v["h"] >= 44 and v["hit"] for v in r.values()), r)
        # chaque bouton quitte vraiment la séance
        for sel in ("[data-act=closeLive].endbtn", ".livehead .iconbtn[data-act=closeLive]"):
            ev("() => { const s = S.find(z => !z.archived && (+z.semaine) > 1 && z.exercices.length > 1); live = null; store.set('sl4-live', null); startLive(s.key); }"); pg.wait_for_timeout(700)
            ev("() => ACT.closeSheet && ACT.closeSheet()"); ev("() => { document.querySelector('.live').scrollTop = 300; }"); pg.wait_for_timeout(250)
            pg.tap(sel); pg.wait_for_timeout(900)
            check(f"{nom} · toucher {sel} quitte la séance", ev("() => !document.querySelector('.live') && live === null"), sel)
        check(f"{nom} · aucune erreur JavaScript", not errs, errs[:2]); c.close()
    br.close()
print("ÉCHECS :", fails if fails else "aucun"); sys.exit(1 if fails else 0)
