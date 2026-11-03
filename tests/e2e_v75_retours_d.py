"""Retours vidéo, lot D : Compétition (un seul nom, une action), en-tête opaque et réductible, marque B², voile du scanner. Test ciblé."""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(2500)
    ev = lambda js: pg.evaluate(js)
    check("B² visible dans l'en-tête de Séance", ev("getComputedStyle(document.querySelector('.b2m')).display") != "none")
    pg.click("[data-tab=corps]"); pg.wait_for_timeout(600)
    check("B² absente hors Séance", ev("getComputedStyle(document.querySelector('.b2m')).display") == "none")
    a = ev("(() => { const c = getComputedStyle(document.querySelector('.topbar'), '::before').backgroundColor; const m = c.match(/[\\d.]+/g); return m.length > 3 ? +m[3] : 1; })()")
    check("en-tête : fond opaque (≥ 95 %)", a >= .95, a)
    ev("window.scrollTo(0, 400)"); pg.wait_for_timeout(500)
    check("en-tête : titre réduit au défilement", ev("document.body.classList.contains('scrolled') && getComputedStyle(document.querySelector('#tabname')).transform !== 'none'"))
    pg.click("[data-tab=agenda]"); pg.wait_for_timeout(800)
    check("un seul nom : onglet = titre = Compétition", ev("document.querySelector('.tabs button[data-tab=agenda]').textContent.trim()") == "Compétition" and ev("document.querySelector('#tabname').textContent") == "Compétition")
    pg.click("[data-act=agSeg][data-k=amis]"); pg.wait_for_timeout(800)
    check("titre inchangé sur Amis", ev("document.querySelector('#tabname').textContent") == "Compétition")
    pg.click("[data-act=agSeg][data-k=compet]"); pg.wait_for_timeout(800)
    check("Compétition : J–N puis la prochaine action, avant le calendrier", ev("(() => { const q = s => document.querySelector(s); const cc = q('#v-agenda .cc'), st = q('#v-agenda .steps'), f = q('#fold-cal'); return !!cc && !!st && !!f && cc.compareDocumentPosition(st) & 4 && st.compareDocumentPosition(f) & 4; })()"))
    check("Compétition : calendrier, liste et formulaire repliés", ev("['cal','comps','add'].every(k => { const d = document.getElementById('fold-' + k); return d && !d.open; })"))
    check("Compétition : une seule action orange visible", ev("[...document.querySelectorAll('#v-agenda .btn:not(.ghost):not(.line):not(.sm)')].filter(b => b.offsetParent !== null && !b.closest('details:not([open])')).length") == 1)
    check("pas de undefined/NaN", ev("!/undefined|NaN/.test(document.querySelector('#v-agenda').innerText)"))
    pg.evaluate("sheet = 'scan'; scanCtx = 'nutri'; renderLayer()"); pg.wait_for_timeout(400)
    check("scanner : voile sombre derrière l'indication", ev("(() => { const m = getComputedStyle(document.querySelector('.scanhint')).backgroundColor.match(/[\\d.]+/g); return m.length > 3 && +m[3] >= .6; })()"))
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
