"""Lot F : captures « avant / après » sur n'importe quel arbre (v68 ou courant). Usage : SHOTDIR=<dossier> python3 tests/capture_lot_f.py"""
import pathlib, os, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOT = pathlib.Path(os.environ["SHOTDIR"]); SHOT.mkdir(parents=True, exist_ok=True)
res = {}
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    for t, js in (("home", "setTab('home')"), ("prog", "progSeg='records';setTab('prog')")):
        ev(js); pg.wait_for_timeout(500); pg.screenshot(path=str(SHOT / f"onglets-{t}.png"), clip={"x": 0, "y": 844 - 90, "width": 390, "height": 90})
    # Historique : hauteur du calendrier + zone de toucher d'un jour
    ev("setTab('histo')"); pg.wait_for_timeout(700)
    res["hcal_h"] = ev("Math.round(document.querySelector('.hcal').getBoundingClientRect().height)")
    r = ev("(() => { const b = document.querySelector('button.hc'); if (!b) return null; const a = getComputedStyle(b, '::after'), r = b.getBoundingClientRect(); return {cell: [Math.round(r.width), Math.round(r.height)], zone: [Math.round(parseFloat(a.width)), Math.round(parseFloat(a.height))]}; })()")
    res["hc"] = r
    pg.screenshot(path=str(SHOT / "historique.png"))
    # Programme : sélecteur de blocs
    ev("setTab('seance')"); pg.wait_for_timeout(600); pg.screenshot(path=str(SHOT / "programme.png"))
    # toucher posé sur une ligne cliquable (Programme : chip)
    pos = ev("(() => { const b = document.querySelector('#v-seance .chip, #v-seance [data-act]'); if (!b) return null; const r = b.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2, b.className]; })()")
    if pos:
        pg.mouse.move(pos[0], pos[1]); pg.mouse.down(); pg.wait_for_timeout(80)
        res["press"] = ev("(() => { const e = document.querySelector('#v-seance .chip, #v-seance [data-act]'); const cs = getComputedStyle(e); return [e.className, cs.transform, cs.opacity]; })()")
        pg.screenshot(path=str(SHOT / "toucher.png"), clip={"x": 0, "y": max(0, pos[1] - 70), "width": 390, "height": 140}); pg.mouse.up()
    br.close()
(SHOT / "mesures.json").write_text(json.dumps(res, ensure_ascii=False, indent=1)); print(res)
