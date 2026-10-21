"""Maquettes A/B rendues avec la vraie app (données de test), barre d'état d'iPhone simulée (47 px en haut, 34 px en bas).
Usage : python3 tests/mockups.py <dossier de sortie>"""
import pathlib, sys, json
from PIL import Image, ImageDraw, ImageFont
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
base_route = route
def route2(r):
    u = r.request.url
    if re.match(r"http://app\.local/sl/(index\.html)?(\?|#|$)", u):
        html = (P / "test-build.html").read_text().replace("env(safe-area-inset-top,0px)", "47px").replace("env(safe-area-inset-bottom,0px)", "34px")
        html = html.replace("<head>", "<head><script src='/mock.js'></script><script src='/shim.js'></script>", 1)
        return r.fulfill(body=html, content_type="text/html")
    return base_route(r)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def statusbar(path):
    im = Image.open(path).convert("RGB"); d = ImageDraw.Draw(im); s = 2
    f = ImageFont.truetype(FONT, 17 * s)
    d.text((52 * s, 14 * s), "9:41", fill="white", font=f)
    d.rounded_rectangle((140 * s, 11 * s, 250 * s, 43 * s), radius=16 * s, fill="black")
    for i, hgt in enumerate([5, 8, 11, 14]): d.rectangle(((294 + i * 5) * s, (29 - hgt) * s, (297 + i * 5) * s, 29 * s), fill="white")
    d.rounded_rectangle((324 * s, 17 * s, 349 * s, 29 * s), radius=3 * s, outline="white", width=2); d.rectangle((326 * s, 19 * s, 343 * s, 27 * s), fill="white")
    d.rounded_rectangle((128 * s, (844 - 9) * s, 262 * s, (844 - 4) * s), radius=3 * s, fill="white")
    im.save(path)
def board(files, labels, out, title=None):
    ims = [Image.open(f) for f in files]; w, h = ims[0].size; pad = 40; top = 120 if title else 90
    B_ = Image.new("RGB", (len(ims) * w + (len(ims) + 1) * pad, h + top + pad), "#1a1b1e"); d = ImageDraw.Draw(B_)
    ft, fl = ImageFont.truetype(FONT, 34), ImageFont.truetype(FONT, 30)
    if title: d.text((pad, 24), title, fill="white", font=ft)
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x = pad + i * (w + pad); d.text((x, top - 46), lab, fill="#cfd3d9", font=fl); B_.paste(im, (x, top))
    B_.save(out)

CSS = {
 "1A": """body::before{content:"";position:fixed;left:0;right:0;top:0;height:47px;z-index:25;background:rgba(10,11,13,.86);-webkit-backdrop-filter:blur(18px) saturate(1.6);backdrop-filter:blur(18px) saturate(1.6);border-bottom:1px solid rgba(255,255,255,.04)}""",
 "1B": """body{padding-top:0!important}
.topbar{position:sticky;top:0;z-index:25;margin:0 -16px;padding:47px 16px 0;height:auto;min-height:91px;background:rgba(10,11,13,.86);-webkit-backdrop-filter:blur(18px) saturate(1.6);backdrop-filter:blur(18px) saturate(1.6);border-bottom:1px solid var(--seam)}
.topbar .brandmark::after{content:" · Aujourd'hui";color:var(--dust);font-weight:600}""",
 "2A": """.hero[style*="var(--mu)"]{--hc:#896714!important}.hero[style*="var(--pull)"]{--hc:#0C62EC!important}.hero[style*="var(--dip)"]{--hc:#1D7A4D!important}.hero[style*="var(--squat)"]{--hc:#C4231B!important}
.hero[style*="var(--"] .hs,.hero[style*="var(--"] .hu{color:#fff}""",
 "2B": """.hero[style*="var(--mu)"],.hero[style*="var(--pull)"],.hero[style*="var(--dip)"],.hero[style*="var(--squat)"]{
  background:radial-gradient(120% 100% at 100% 0%,color-mix(in srgb,var(--hc) 26%,transparent),transparent 62%),var(--deck);box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--hc) 28%,transparent)}
.hero[style*="var(--"] .hb{color:var(--hc)} .hero[style*="var(--"] .hs{color:var(--steel-hi)} .hero[style*="var(--"] .hu{color:var(--dust)}
.hero[style*="var(--"] .deco circle{stroke:var(--hc)} .hero[style*="var(--"] .deco{opacity:.35}""",
}
WEIGH_A = """(() => {
  D.poids = D.poids.filter(p => p.date !== D.today); render();
  const pw = D.poids.at(-1), lim = catLimit(), v = pw ? pw.poids : 74.9;
  document.querySelectorAll('#v-home .h2').forEach(h => { if (/Pesée du jour/.test(h.textContent)) { let n = h.nextElementSibling; n.nextElementSibling.remove(); n.remove(); h.remove(); } });
  const card = `<section class="card" style="margin-top:12px"><div class="row"><b style="font-size:16px">Pesée du matin</b><span class="muted small">hier ${fmt(v, 1)} kg</span></div>
    <div class="stepper" style="grid-template-columns:52px 1fr 52px;margin-top:12px"><button style="height:52px">−</button><input value="${fmt(v, 1)}" style="height:52px;font-size:30px"><button style="height:52px">+</button></div>
    <button class="btn" style="margin-top:10px">Noter ${fmt(v, 1)} kg</button>
    <p class="muted small" style="margin-top:10px;text-align:center">Limite des −${lim} : ${fmt(lim - v, 1)} kg de marge</p></section>`;
  document.querySelector('#v-home .hero').insertAdjacentHTML('afterend', card);
})()"""
WEIGH_B = """(() => {
  D.poids = D.poids.filter(p => p.date !== D.today); render();
  const pw = D.poids.at(-1), lim = catLimit(), v = pw ? pw.poids : 74.9;
  document.querySelector('#v-home .hero').insertAdjacentHTML('afterend', `<button class="vrow" style="margin-top:12px;background:var(--deck);border-radius:16px;padding:14px;border:0"><span class="d10" style="--c:var(--chalk)"></span><span class="grow"><b>Me peser</b><span>hier ${fmt(v, 1)} kg · limite des −${lim}</span></span><span class="val" style="color:var(--dust)">›</span></button>`);
  document.querySelector('#layer').innerHTML = `<div class="scrim"></div><div class="sheet" style="animation:none"><div class="wrap"><div class="grab"></div>
    <p class="muted">Pesée du matin · mercredi 21 octobre</p><p class="show" style="font-size:76px;font-weight:800;margin-top:6px">${fmt(v, 1)}<small style="font-size:.42em"> kg</small></p>
    <p class="muted" style="margin-top:6px">${fmt(lim - v, 1)} kg sous la limite des −${lim}</p>
    <div class="stepper" style="grid-template-columns:56px 1fr 56px;margin-top:16px"><button style="height:56px">−</button><input value="${fmt(v, 1)}" style="height:56px;font-size:30px"><button style="height:56px">+</button></div>
    <button class="btn" style="margin-top:12px">Noter</button></div></div>`;
})()"""
HEROES = """(() => { setTab('seance'); const el = document.querySelector('#v-seance');
  el.innerHTML = [['PULL','Mercredi 21 octobre · bloc 7, semaine 2','Séance 2','Prochaine séance'],['MU','Samedi 24 octobre · bloc 7, semaine 2','Séance 4','À venir'],
    ['DIP','Lundi 19 octobre · bloc 7, semaine 2','Séance 1','Faite'],['SQUAT','Jeudi 22 octobre · bloc 7, semaine 2','Séance 3','À venir']]
    .map(([l, a, b, c]) => heroCard({color:LCOL[l], small:a, big:b, sub:c})).join(''); scrollTo(0, 0); })()"""

with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route2)
    pg = c.new_page()
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0", timeout=20000); pg.wait_for_timeout(2500)
    def fresh():
        pg.reload(); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && typeof lastSync !== 'undefined' && lastSync > 0", timeout=20000); pg.wait_for_timeout(1200)
    def shot(name):
        f = OUT / f"{name}.png"; pg.screenshot(path=str(f)); statusbar(f); return f
    # 1. Barre d'état
    files = []
    for k in ["actuel", "1A", "1B"]:
        fresh()
        if k != "actuel": pg.add_style_tag(content=CSS[k])
        pg.evaluate("scrollTo(0, 170)"); pg.wait_for_timeout(400); files.append(shot("q1-" + k))
    board(files, ["Actuel", "A · bande floutée", "B · en-tête qui reste en haut"], OUT / "Q1-barre-etat.png", "1. Quand tu fais défiler (Aujourd'hui, défilé de 170 px)")
    # 2. Héros des mouvements
    files = []
    for k in ["actuel", "2A", "2B"]:
        fresh()
        if k != "actuel": pg.add_style_tag(content=CSS[k])
        pg.evaluate(HEROES); pg.wait_for_timeout(500); files.append(shot("q2-" + k))
    board(files, ["Actuel (texte 1,9 à 3,5:1)", "A · teintes foncées", "B · carte sombre, chiffre en couleur"], OUT / "Q2-heros.png", "2. Héros des mouvements (tractions, MU, dips, squat)")
    # 3. Pesée du matin
    files = []
    fresh(); pg.evaluate(WEIGH_A); pg.wait_for_timeout(400); files.append(shot("q3-A"))
    fresh(); pg.evaluate(WEIGH_B); pg.wait_for_timeout(400); files.append(shot("q3-B-ecran"))
    pg.evaluate("document.querySelector('#layer').innerHTML=''"); pg.wait_for_timeout(200); files.insert(1, shot("q3-B"))
    board(files, ["A · carte en haut d'Aujourd'hui", "B · raccourci « Me peser »", "B · après le toucher"], OUT / "Q3-pesee.png", "3. Pesée du matin (pas encore pesé aujourd'hui)")
    br.close()
print("ok", OUT)
