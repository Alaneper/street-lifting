"""Lot F : mesure d'accessibilité sur les écrans principaux (390 px) : zones de toucher < 44 px et contraste du texte < 4,5:1 (3:1 pour le gros texte).
Zone de toucher = la plus grande du bouton et de son ::after invisible (technique de zone étendue).
Usage : python3 tests/mesure_acces.py [sortie.json]   (SAFE_TOP=47px pour simuler l'encoche)
Contraste : couleur du texte composée sur la chaîne de fonds opaques ; fonds en dégradé : couleur de fond de l'élément le plus proche, résultat marqué « approx »."""
import sys, json, pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
OUT_JSON = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else H / "mesure_acces.json"
ECRANS = {
  "aujourdhui": "setTab('home')", "programme": "setTab('seance')", "historique": "setTab('histo')",
  "poids": "corpsTab='poids';corpsManual=D.today;setTab('corps')", "alimentation": "corpsTab='nutri';corpsManual=D.today;setTab('corps')",
  "progres": "progSeg='records';setTab('prog')", "courbes": "progSeg='courbes';setTab('prog')", "mouvements": "progSeg='mouvements';mvQ='';setTab('prog')",
  "competition": "agendaSeg='compet';setTab('agenda')", "amis": "agendaSeg='amis';setTab('agenda')",
  "reglages": "openSheet('settings')", "fiche-record": "page={type:'lift',l:'SQUAT'};liftMetric='1rm';renderLayer()", "fiche-mouvement": "page={type:'move',l:'SQUAT'};renderLayer()",
}
JS = r"""
(() => {
  const cv = document.createElement('canvas'); cv.width = cv.height = 1; const cx = cv.getContext('2d', {willReadFrequently: true});
  const rgba = s => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = s; cx.fillRect(0, 0, 1, 1); const d = cx.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2], d[3] / 255]; };
  const over = (f, b) => [0, 1, 2].map(i => f[i] * f[3] + b[i] * (1 - f[3]));
  const lum = c => { const a = c.map(v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }); return .2126 * a[0] + .7152 * a[1] + .0722 * a[2]; };
  const ratio = (a, b) => { const l1 = lum(a), l2 = lum(b); return (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05); };
  const bgOf = el => { const chain = []; let approx = false, n = el;
    while (n && n.nodeType === 1) { const cs = getComputedStyle(n), c = rgba(cs.backgroundColor); if (cs.backgroundImage !== 'none') approx = true; if (c[3] > 0) chain.push(c); if (c[3] >= .999) break; n = n.parentElement; }
    let base = [12, 11, 10]; for (let i = chain.length - 1; i >= 0; i--) base = chain[i][3] >= .999 ? chain[i].slice(0, 3) : over(chain[i], base); return {c: base, approx}; };
  const vis = el => { const r = el.getBoundingClientRect(); if (r.width < 1 || r.height < 1) return false; const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) return false; let n = el; while (n && n.nodeType === 1) { if (n.hidden || getComputedStyle(n).display === 'none') return false; n = n.parentElement; } return true; };
  const root = document.querySelector('.sheet') || document.querySelector('.page') || document.querySelector('.view:not([hidden])') || document.body;
  const res = {small: [], contrast: [], low: [], nolabel: [], fake: []}, seenS = new Set(), seenC = new Set();
  /* VoiceOver : nom accessible (aria-label, aria-labelledby, texte visible, title, label associé) et rôle des zones cliquables qui ne sont pas des boutons */
  const name = el => { const t = x => (x || '').replace(/\s+/g, ' ').trim(); if (t(el.getAttribute('aria-label')) || t(el.getAttribute('title'))) return true; const lb = el.getAttribute('aria-labelledby'); if (lb && t(document.getElementById(lb) && document.getElementById(lb).textContent)) return true;
    if (el.id && document.querySelector('label[for="' + el.id + '"]')) return true; if (el.closest('label') && t(el.closest('label').textContent)) return true; const c = el.cloneNode(true); c.querySelectorAll('[aria-hidden="true"]').forEach(n => n.remove()); return /[\p{L}\p{N}]/u.test(t(c.textContent)) || (el.tagName === 'INPUT' && !!t(el.getAttribute('placeholder'))); };
  document.body.querySelectorAll('button,a[href],input:not([type=hidden]),select,textarea,[role=button],[role=switch],[role=tab],[data-act]').forEach(el => {
    if (!vis(el) || el.closest('[aria-hidden="true"]') || (el.parentElement && el.parentElement.closest('button,a[href]') && !/INPUT|SELECT|TEXTAREA/.test(el.tagName))) return;
    const tag = el.tagName.toLowerCase(), k = tag + '.' + String(el.className).split(' ')[0];
    if (!name(el)) res.nolabel.push(k + '|' + (el.dataset.act || ''));
    if (el.hasAttribute('data-act') && !/^(button|a|input|select|textarea|summary|label)$/.test(tag) && !el.getAttribute('role')) res.fake.push(k + '|' + (el.dataset.act || ''));
  });
  res.nolabel = [...new Set(res.nolabel)]; res.fake = [...new Set(res.fake)];
  root.querySelectorAll('button,a[href],[data-act],input:not([type=hidden]),select,summary,[role=button]').forEach(el => {
    if (!vis(el)) return; if (el.parentElement && el.parentElement.closest('button,a[href],[data-act]') && el.tagName !== 'INPUT') return;
    const r = el.getBoundingClientRect(); if (r.top > innerHeight || r.bottom < 0) return;
    const pa = getComputedStyle(el, '::after'), ex = pa.content !== 'none' && pa.position === 'absolute' ? [parseFloat(pa.width) || 0, parseFloat(pa.height) || 0] : [0, 0];   /* zone de toucher étendue par ::after (invisible) */
    if (Math.max(r.width, ex[0]) < 43.5 || Math.max(r.height, ex[1]) < 43.5) { const k = el.tagName + '.' + el.className + '|' + (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 18); if (seenS.has(k)) return; seenS.add(k); res.small.push({el: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''), txt: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 24), w: Math.round(r.width), h: Math.round(r.height)}); }
  });
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let t; while ((t = walker.nextNode())) {
    const tx = t.textContent.trim(); if (!tx) continue; const el = t.parentElement; if (!el || ['SCRIPT', 'STYLE', 'OPTION'].includes(el.tagName) || !vis(el)) continue;
    const r = el.getBoundingClientRect(); if (r.top > innerHeight || r.bottom < 0) continue;
    const cs = getComputedStyle(el), fg = rgba(cs.color), bg = bgOf(el), c = fg[3] < 1 ? over(fg, bg.c) : fg.slice(0, 3), cr = ratio(c, bg.c), fs = parseFloat(cs.fontSize), bold = +cs.fontWeight >= 700, big = fs >= 24 || (fs >= 18.66 && bold), need = big ? 3 : 4.5;
    res.low.push([Math.round(cr * 100) / 100, tx.slice(0, 22), el.className && String(el.className).split(' ')[0], need]); if (cr < need) { const k = tx.slice(0, 24) + '|' + el.className; if (seenC.has(k)) continue; seenC.add(k); res.contrast.push({txt: tx.slice(0, 32), cls: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''), ratio: Math.round(cr * 100) / 100, need, fs: Math.round(fs), approx: bg.approx}); }
  }
  res.low.sort((a, b) => a[0] - b[0]); res.low = res.low.slice(0, 5); return res;
})()
"""
res = {}
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=1, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(1500)
    pg.evaluate("""(()=>{ let n=0; S.filter(z=>z.faite && dateOf(z)).forEach((z,i)=>{ [['SQUAT COMP',100+i*2.5,5],['DIPS COMP',30+i,4],['PULL UP COMP',20+i,3]].forEach(([ex,c,k])=>D.series.push({id:900+n++,date:dateOf(z),bloc:z.bloc,semaine:z.semaine,seance:z.seance,ex:ex,charge:c,reps:k,sets:[{r:k,c:c}],src:'app'})); }); })()""")
    for nom, js in ECRANS.items():
        pg.evaluate("page=null;sheet=null;renderLayer()"); pg.evaluate(js); pg.wait_for_timeout(1200)
        try: res[nom] = pg.evaluate(JS)
        except Exception as e: res[nom] = {"erreur": str(e)[:200]}
        r = res[nom]; print(f"{nom:16s} cibles<44 : {len(r.get('small', [])):3d} · contrastes<seuil : {len(r.get('contrast', [])):3d} · sans nom : {len(r.get('nolabel', [])):2d} · sans rôle : {len(r.get('fake', [])):2d} · plus bas : {[x[0] for x in r.get('low', [])][:2]}")
    br.close()
OUT_JSON.write_text(json.dumps(res, ensure_ascii=False, indent=1))
print("total cibles<44 :", sum(len(v.get("small", [])) for v in res.values()), "· total contrastes :", sum(len(v.get("contrast", [])) for v in res.values()), "· sans nom :", sum(len(v.get("nolabel", [])) for v in res.values()), "· sans rôle :", sum(len(v.get("fake", [])) for v in res.values()), "·", OUT_JSON)
for nom, v in res.items():
    if v.get("nolabel") or v.get("fake"): print(" ", nom, "SANS NOM:", v.get("nolabel"), "SANS RÔLE:", v.get("fake"))
