"""Contrôle qualité automatique, écran par écran, en iPhone 390×844 et iPad 834×1194.
Pour chaque écran : capture, axe-core (contrastes et ARIA), cibles tactiles < 44 px (Apple) et < 24 px (WCAG 2.5.8),
débordement horizontal, textes coupés, champs < 16 px (zoom iOS), erreurs console.
Usage : python3 tests/qa.py <étiquette>   → tests/audit/<étiquette>/*.png et tests/qa_<étiquette>.json"""
import pathlib, sys, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
LABEL = sys.argv[1] if len(sys.argv) > 1 else "run"
AXE = (B / "node_modules/axe-core/axe.min.js").read_text()
CHECK = r"""() => {
  const W = innerWidth, vis = e => { const r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && r.bottom > 0 && r.top < innerHeight * 6; };
  const lbl = e => (e.getAttribute('aria-label') || e.textContent || e.value || e.placeholder || e.tagName).trim().replace(/\s+/g, ' ').slice(0, 40);
  const small = [], tiny = [], over = [], cut = [], zoom = [];
  const inText = e => { const p = e.parentElement; return e.tagName === 'A' && p && /^(P|LI|SPAN)$/.test(p.tagName) && p.textContent.trim().length > e.textContent.trim().length + 10; };
  document.querySelectorAll('button, a[href], input, select, [data-act], [role=button]').forEach(e => {
    if (!vis(e) || e.closest('[hidden]') || e.disabled) return;
    { const cs = getComputedStyle(e); if (cs.opacity === '0' || cs.pointerEvents === 'none') return; }
    if (e.matches('input[type=hidden]')) return;
    const r = e.getBoundingClientRect();
    if (inText(e)) return;               /* lien dans une phrase : exception WCAG 2.5.8 */
    /* Zone tactile réelle : on sonde autour de l'élément (une zone agrandie par ::after compte). */
    const hit = (x, y) => { if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) return false; const t = document.elementFromPoint(x, y); return !!t && (t === e || e.contains(t)); };
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    let hh = r.height, ww = r.width;
    if (r.top >= 0 && r.bottom <= innerHeight && hit(cx, cy)) {
      if (hh < 44 && hit(cx, cy - 21.5) && hit(cx, cy + 21.5)) hh = 44;
      if (ww < 44 && hit(cx - 21.5, cy) && hit(cx + 21.5, cy)) ww = 44;
    } else {   /* hors de l'écran (rangée qui défile) : on lit la zone agrandie dans le CSS */
      const a = getComputedStyle(e, '::after');
      if (a.content !== 'none' && a.position === 'absolute') {
        const v = k => Math.max(0, -parseFloat(a[k]) || 0);
        hh = r.height + v('top') + v('bottom'); ww = r.width + v('left') + v('right');
      }
    }
    if (hh < 24 || ww < 24) tiny.push(lbl(e) + ' ' + Math.round(ww) + '×' + Math.round(hh));
    else if (hh < 44 || ww < 44) small.push(lbl(e) + ' ' + Math.round(ww) + '×' + Math.round(hh));
    if (e.matches('input, select, textarea') && parseFloat(getComputedStyle(e).fontSize) < 16) zoom.push(lbl(e));
  });
  document.querySelectorAll('body *').forEach(e => {
    if (!vis(e) || e.closest('svg, canvas, .chips, .hscroll, [data-scroll-x]')) return;
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    if (s.position !== 'fixed' && (r.right > W + 1 || r.left < -1) && !e.closest('[style*="overflow"]')) over.push(e.tagName + '.' + e.className + ' ' + Math.round(r.left) + '→' + Math.round(r.right));
    if (s.textOverflow === 'ellipsis' && e.scrollWidth > e.clientWidth + 1) cut.push(lbl(e));
  });
  return {cibles_moins_24:tiny, cibles_moins_44:small, debordements:over.slice(0, 15), textes_coupes:cut, champs_zoom_ios:zoom,
          defilement_horizontal:document.documentElement.scrollWidth > W + 1};
}"""
def axe(pg):
    pg.evaluate(AXE)
    r = pg.evaluate("""() => axe.run(document, {runOnly:{type:'tag', values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}, resultTypes:['violations']})
      .then(r => r.violations.map(v => ({id:v.id, n:v.nodes.length, ex:v.nodes.slice(0, 4).map(n => (n.any[0] && n.any[0].message || n.failureSummary || '').slice(0, 160) + ' ← ' + n.html.slice(0, 90))})))""")
    return r
VPS = {"iphone": (390, 844), "ipad": (834, 1194)}
OUTD = H / "audit" / LABEL; OUTD.mkdir(parents=True, exist_ok=True)
report = {}
with sync_playwright() as p:
    br = p.chromium.launch()
    for vp, (w, h) in VPS.items():
        c = br.new_context(viewport={"width":w, "height":h}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
        pg = c.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e))); pg.on("console", lambda m: errs.append(m.type + " " + m.text) if m.type == "error" else None)
        def snap(name, full=True):
            pg.wait_for_timeout(350)
            pg.screenshot(path=str(OUTD / f"{vp}-{name}.png"), full_page=full)
            report[f"{vp}/{name}"] = dict(pg.evaluate(CHECK), axe=axe(pg))
        pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1200); snap("01-connexion", False)
        pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500); snap("02-carnet", False)
        pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
        pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0", timeout=20000); pg.wait_for_timeout(3000)
        snap("03-aujourdhui")
        for t, n in [("seance", "04-prog"), ("prog", "05-progres"), ("corps", "06-corps-alimentation"), ("agenda", "08-compet")]:
            pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.click(f"[data-tab={t}]"); pg.wait_for_timeout(1500); snap(n)
            if t == "corps":
                pg.click("[data-act=corpsTab][data-k=poids]"); pg.wait_for_timeout(900); snap("07-corps-poids")
                pg.click("[data-act=corpsTab][data-k=nutri]"); pg.wait_for_timeout(300)
        pg.click("[data-tab=prog]"); pg.wait_for_timeout(500)
        pg.evaluate("ACT.openLift({l:'PULL'})"); pg.wait_for_timeout(1500); pg.locator(".page").evaluate("e=>e.style.position='static'"); snap("09-fiche-tractions")
        pg.evaluate("ACT.closePage()"); pg.wait_for_timeout(300)
        pg.click("[data-act=settings]"); pg.wait_for_timeout(700); snap("10-reglages", False); pg.evaluate("ACT.closeSheet()"); pg.wait_for_timeout(300)
        key = pg.evaluate("(nextSeance()||S.at(-1)).key"); pg.evaluate(f"startLive({json.dumps(key)}, 0)"); pg.wait_for_timeout(900); snap("11-seance-pesee", False)
        pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(500)
        pg.evaluate("live.i=1; renderLayer()"); pg.wait_for_timeout(400); snap("12-seance-serie", False)
        pg.locator(".setrow .ck").first.click(); pg.wait_for_timeout(900); snap("13-seance-apres-validation", False)
        pg.evaluate("live.i=2; renderLayer()"); pg.wait_for_timeout(400)
        if pg.locator(".setrow .ck").count(): pg.locator(".setrow .ck").first.click(); pg.wait_for_timeout(900); snap("14-seance-repos", False)
        pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(300)
        pg.click("[data-act=finishLive]"); pg.wait_for_timeout(1500); snap("15-seance-bilan", False)
        report[f"{vp}/console"] = errs[:20]
        c.close()
    br.close()
tot = {"cibles<24": 0, "cibles<44": 0, "debordements": 0, "textes_coupes": 0, "champs_zoom_ios": 0, "axe": 0}
for k, v in report.items():
    if not isinstance(v, dict): continue
    tot["cibles<24"] += len(v["cibles_moins_24"]); tot["cibles<44"] += len(v["cibles_moins_44"]); tot["debordements"] += len(v["debordements"])
    tot["textes_coupes"] += len(v["textes_coupes"]); tot["champs_zoom_ios"] += len(v["champs_zoom_ios"]); tot["axe"] += sum(x["n"] for x in v["axe"])
report["_totaux"] = tot
(H / f"qa_{LABEL}.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
print(json.dumps(tot, ensure_ascii=False))
print("console:", report.get("iphone/console"), report.get("ipad/console"))
