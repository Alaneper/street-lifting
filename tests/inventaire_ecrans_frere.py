"""Inventaire fonction par fonction des écrans (actions, champs, titres, boutons) — v65 / v68 / niveau 85 / retours-frère.
Usage : python3 tests/inventaire_ecrans_frere.py > ecrans.json"""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
JS = """() => { const v = [...document.querySelectorAll('.view')].find(x => x.offsetParent !== null) || document.body; const root = v;
  const U = a => [...new Set(a)].sort();
  return {acts:U([...root.querySelectorAll('[data-act]')].map(x => x.dataset.act)), chg:U([...root.querySelectorAll('[data-chg],[data-inp]')].map(x => (x.dataset.chg || x.dataset.inp))),
    titres:U([...root.querySelectorAll('h1,h2,h3,.h2,.slab')].map(x => x.innerText.replace(/\\s+/g, ' ').trim()).filter(Boolean)),
    boutons:U([...root.querySelectorAll('button,[role=button],a.btn')].map(x => x.innerText.replace(/\\s+/g, ' ').trim()).filter(t => t && t.length < 60)),
    segments:U([...root.querySelectorAll('[aria-pressed]')].map(x => (x.innerText || x.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').trim()).filter(t => t && t.length < 30))}; }"""
def merge(a, b):
    for k in b: a[k] = sorted(set(a.get(k, [])) | set(b[k]))
    return a
out = {}
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate; errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(800); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1800)
    tabs = ev("[...document.querySelectorAll('[data-tab]')].map(x => x.dataset.tab)")
    for t in dict.fromkeys(tabs):
        ev("(t) => setTab(t)", t); pg.wait_for_timeout(700)
        acc = ev(JS); n = 0
        # parcourt les segments (sous-onglets, filtres, périodes) : chaque état est relevé
        for i in range(14):
            seg = pg.locator(".view:visible [aria-pressed=false]:visible")
            if i >= seg.count(): break
            try: seg.nth(i).click(timeout=1500); pg.wait_for_timeout(350); acc = merge(acc, ev(JS)); n += 1
            except Exception: pass
            ev("(t) => { try { sheet = null; page = null; } catch(e){} setTab(t); }", t); pg.wait_for_timeout(250)
        out[t] = acc; out[t]["etats_parcourus"] = n
    # écrans ouverts par un geste : réglages, pesée, fiche mouvement, bilan
    for nm in ["settings", "weigh"]:
        try: ev("(n) => openSheet(n)", nm); pg.wait_for_timeout(600); out["feuille:" + nm] = ev("() => { const r = document.querySelector('#layer .sheet') || document.body; const U = a => [...new Set(a)].sort(); return {acts:U([...r.querySelectorAll('[data-act]')].map(x => x.dataset.act)), chg:U([...r.querySelectorAll('[data-chg],[data-inp]')].map(x => x.dataset.chg || x.dataset.inp)), titres:U([...r.querySelectorAll('h1,h2,h3,.h2,.slab,.show')].map(x => x.innerText.replace(/\\s+/g, ' ').trim()).filter(Boolean)), boutons:U([...r.querySelectorAll('button')].map(x => x.innerText.replace(/\\s+/g, ' ').trim()).filter(t => t && t.length < 70))}; }"); ev("() => { sheet = null; renderLayer(); }")
        except Exception as e: out["feuille:" + nm] = str(e)
    out["erreurs_js"] = errs; br.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
