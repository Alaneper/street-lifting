"""Lot fiabilité et tactile : deux planches de captures (390 px). SHOTDIR=<dossier> python3 tests/capture_lot_fiabilite.py"""
import pathlib, os
from PIL import Image, ImageDraw
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
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    shots = []
    def snap(tag, label, full=True):
        f = f"/tmp/np/lf-{tag}.png"; pg.screenshot(path=f); shots.append((label, f))
    def open_case(find, mod, prev):
        key = ev("""([f]) => { const z = S.find(s => !s.archived && (+s.semaine) > 1 && s.exercices.some(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1])); return z && z.key; }""", [find])
        ev("() => { live = null; store.set('sl4-live', null); }")
        ev("""([k, f, mod, prev]) => { const z = seanceByKey(k), i = z.exercices.findIndex(e => String(e.mouvement).toUpperCase().trim() === f[0] && String(e.variation).toUpperCase().trim() === f[1]), e = z.exercices[i]; Object.assign(e, mod); window.__ci = i;
          const key = exKey(e), r = s => rank(s.bloc) * 100 + (num(s.semaine) || 0), z0 = S.filter(s => s.idx === z.idx && r(s) < r(z)).sort((a, b) => r(b) - r(a))[0];
          D.series = D.series.filter(x => x.ex !== key); if (z0) D.series.push({id:null, date:'2026-10-28', bloc:z0.bloc, semaine:z0.semaine, seance:z0.seance, ex:key, charge:Math.max(...prev.map(s => s[0])), sets:prev.map(s => ({c:s[0], r:s[1]})), note:'', src:'app'}); }""", [key, find, mod, prev])
        ev("(k) => startLive(k)", key); pg.wait_for_timeout(700)
        if pg.locator("[data-act=pdcSave]").count(): pg.click("[data-act=pdcSave]"); pg.wait_for_timeout(500)
        ev("() => { live.i = window.__ci; renderLayer(); document.querySelector('.live').scrollTop = 0; }"); pg.wait_for_timeout(500)
    # planche 1 : séance en direct
    open_case(["MUSCLE UP", "COMP"], {"series": "4", "reps": "1", "charge": "5"}, [[5, 1]] * 4)
    pg.click(".vbar [data-act=doneSet]"); pg.wait_for_timeout(900); snap("a", "a/b/c · +5 kg : barre opaque, minuteur 1 ligne, RPE au-dessus, lest en une ligne")
    open_case(["SQUAT", "COMP"], {"series": "3", "reps": "3", "charge": "140"}, [[140, 3]] * 3)
    pg.click(".vbar [data-act=doneSet]"); pg.wait_for_timeout(900); snap("b", "squat 140 : le bloc de disques reste pour la barre")
    open_case(["SQUAT", "COMP"], {"series": "3", "reps": "3", "charge": "85"}, [[85, 3]] * 3)
    ev("document.querySelector('.lsr.cur input[data-chg=setC]').value = '86,75'; document.querySelector('.lsr.cur input[data-chg=setC]').dispatchEvent(new Event('change', {bubbles:true}))"); pg.wait_for_timeout(400); snap("c", "g · 86,75 kg inatteignable : un tap = 85 kg")
    pg.click("#lgear .lg-fix"); pg.wait_for_timeout(500); snap("c2", "g · après le tap")
    for _ in range(8):
        if pg.locator(".vbar [data-act=doneSet]").count(): pg.click(".vbar [data-act=doneSet]"); pg.wait_for_timeout(350)
    ev("() => { rest = null; renderLayer(); finishLive(); }"); pg.wait_for_timeout(2300); snap("d", "f · fin de séance : Séries · Reps · Tonnage · Records")
    sheet(shots, "planche-seance-en-direct.png")
    ev("() => ACT.closeSummary()"); pg.wait_for_timeout(500)
    # planche 2 : Poids, courbe < 3 points, Programme, Historique
    shots = []
    ev("""() => { const base = new Date(D.today + 'T12:00:00'); D.poids = []; for (let i = 119; i >= 0; i--) { if (i % 3 === 2) continue; const d = new Date(base); d.setDate(d.getDate() - i); D.poids.push({id: 1000 + i, date: d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'), poids: 82 - i * 0.02 + Math.sin(i * 1.7) * 0.7}); } pwRange = '3m'; corpsTab = 'poids'; corpsManual = D.today; setTab('corps'); }""")
    pg.wait_for_timeout(800); snap("p", "d · Poids : « Limite » hors courbe, Min · Max")
    ev("""() => { D.prs = []; const add = (l, d, kg) => D.prs.push({date: d, lift: l, charge: kg, reps: 1, note: '', rpe: null, eq: false}); add('SQUAT', addDays(D.today, -40), 100); add('SQUAT', addDays(D.today, -10), 110); progSeg = 'courbes'; crvSel = 'SQUAT'; setTab('prog'); }"""); pg.wait_for_timeout(1200); snap("e", "e · courbe à 2 points : points seuls")
    ev("() => { sel = null; setTab('seance'); rSeance(); window.scrollTo(0, 0); }"); pg.wait_for_timeout(800); snap("h", "Programme : sous-onglets et barre des semaines à 44 px")
    ev("() => { setTab('histo'); }"); pg.wait_for_timeout(800); snap("i", "Historique : calendrier compact (justifié)")
    sheet(shots, "planche-ecrans-retouches.png")
    br.close()
