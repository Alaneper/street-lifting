"""Lot final : une planche de captures des écrans nouveaux ou retouchés (options). SHOTDIR=<dossier> python3 tests/capture_lot_options.py"""
import pathlib, os
from PIL import Image, ImageDraw
os.environ["SL_NEWS"] = "1"
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
OUT = pathlib.Path(os.environ["SHOTDIR"]); OUT.mkdir(parents=True, exist_ok=True)
def sheet(items, name, cols=4):
    ims = [(t, Image.open(f)) for t, f in items]; w, h = ims[0][1].size; rows = (len(ims) + cols - 1) // cols
    s = Image.new("RGB", (w * cols, (h + 44) * rows), (12, 11, 10)); d = ImageDraw.Draw(s)
    for i, (t, im) in enumerate(ims): x, y = (i % cols) * w, (i // cols) * (h + 44); d.text((x + 14, y + 14), t, fill=(255, 201, 48)); s.paste(im, (x, y + 44))
    s.resize((s.width // 2, s.height // 2)).save(OUT / name)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block", has_touch=True, is_mobile=True); c.route("**/*", route)
    pg = c.new_page(); ev = pg.evaluate
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(2500)
    shots = []
    def snap(tag, label):
        f = f"/tmp/np/lo-{tag}.png"; pg.screenshot(path=f); shots.append((label, f))
    snap("n", "Nouveautés (une seule fois) + question du Sheet" if ev("sheet") == "news" else "Nouveautés : non affichée !")
    ev("() => closeSheet()"); pg.wait_for_timeout(400)
    ev("() => { openSheet('settings'); }"); pg.wait_for_timeout(600)
    ev("() => { const h = [...document.querySelectorAll('.sheet h2')].find(x => /Affichage de la séance/.test(x.textContent)); h.scrollIntoView({block:'start'}); }"); pg.wait_for_timeout(300)
    snap("r", "Réglages › Affichage de la séance (9 interrupteurs)")
    ev("() => closeSheet()"); pg.wait_for_timeout(400)
    ev("() => { sel = null; setTab('seance'); rSeance(); }"); pg.wait_for_timeout(500)
    ev("() => { const c = document.querySelector('#subseance [data-sub=seance]'); c && c.click(); window.scrollTo(0, 0); }"); pg.wait_for_timeout(600)
    ev("() => { const h = [...document.querySelectorAll('h2')].find(x => /Tout le bloc/.test(x.textContent)); h && h.scrollIntoView({block:'start'}); window.scrollBy(0, -70); }"); pg.wait_for_timeout(300)
    snap("p", "Programme : vue du bloc entier (cases 46 px)")
    ev("() => { setTab('histo'); rHisto(); window.scrollTo(0, 0); }"); pg.wait_for_timeout(600)
    snap("h", "Historique : calendrier accessible (44 px) + silhouettes")
    ev("""() => { const z = S.find(s => !s.archived && s.exercices.length > 3 && !s.faite) || S.find(s => !s.archived && s.exercices.length > 3); z.exercices.slice(0, 5).forEach((e, i) => { Object.assign(e, {mouvement:'RENFO', variation:['Curl biceps haltères', 'Face pull', 'Leg extension', 'Scapular pull up', 'Tirage horizontal machine'][i], series:'3', reps:'12'}); }); window.__z = z.key; }""")
    ev("() => { sel = window.__z; setTab('seance'); rSeance(); const c = document.querySelector('#subseance [data-sub=seance]'); c && c.click(); window.scrollTo(0, 0); }"); pg.wait_for_timeout(600)
    ev("() => { const h = [...document.querySelectorAll('h2')].find(x => /Détail de la séance/.test(x.textContent)); h && h.scrollIntoView({block:'start'}); window.scrollBy(0, -60); }"); pg.wait_for_timeout(300)
    snap("s", "Silhouettes : sûres (curl, leg ext., tirage) ; douteuses = initiale (face pull, scapular)")
    sheet(shots, "planche-options.png", cols=5)
    br.close()
