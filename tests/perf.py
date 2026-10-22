"""Mesure de l'ouverture de l'app installée (service worker actif), sur un faux réseau mobile.

Hypothèses (pas des mesures de ton iPhone) :
- réseau : 150 ms d'aller-retour + 1,6 Mbit/s, tailles compressées (profil « 4G lente » de Lighthouse) ;
- API Google Sheets : 350 ms par appel ; aller-retour chez Google pour renouveler l'accès : 400 ms.
Scénarios :
  A. ouverture avec accès Google encore valide, données déjà sur le téléphone ;
  B. ouverture avec accès expiré (le cas de ta vidéo) : passage par accounts.google.com.
Mesures : premier affichage (FCP), contenu visible (données affichées), données à jour (synchro finie).
Usage : python3 tests/perf.py [étiquette]   → écrit tests/perf_<étiquette>.json
"""
import os, sys, json, time, gzip, threading, pathlib, shutil, tempfile, re
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

H = pathlib.Path(__file__).resolve().parent; P = H.parent
B = pathlib.Path(os.environ.get("BENCH_DEPS", "/tmp/claude-0/-home-claude/a112c60f-9639-549a-a0f9-bbd91e82e76a/scratchpad/bench"))
LABEL = sys.argv[1] if len(sys.argv) > 1 else "run"
RTT, BW = 0.150, 1.6e6 / 8
API_LAT, GOOGLE_LAT = 350, 0.400
APP = "10OP7QRneqxxU1ad4BbVaYulLQUBDmaj7Hcu3n3IQBtA"

def make_handler(root, slow=True):
    class Hd(SimpleHTTPRequestHandler):
        def __init__(s, *a, **k): super().__init__(*a, directory=str(root), **k)
        def log_message(s, *a): pass
        def end_headers(s):
            s.send_header("Access-Control-Allow-Origin", "*"); s.send_header("Cache-Control", "no-cache"); super().end_headers()
        def copyfile(s, src, dst):
            data = src.read()
            if slow: time.sleep(RTT + len(gzip.compress(data)) / BW)
            dst.write(data)
    return Hd

def serve(root, port, slow=True):
    srv = ThreadingHTTPServer(("127.0.0.1", port), make_handler(root, slow)); threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv

def build_site(tmp):
    site, vend = tmp / "site", tmp / "vendor"; site.mkdir(); vend.mkdir()
    for f in ["sw.js", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png", "aliments.json"]:
        if (P / f).exists(): shutil.copy(P / f, site / f)
    shutil.copy(B / "node_modules/chart.js/dist/chart.umd.js", vend / "chart.umd.min.js")
    shutil.copy(B / "node_modules/jszip/dist/jszip.min.js", vend / "jszip.min.js")
    css = ""
    for fam, slug, ws in [("Barlow", "barlow", [400, 500, 600, 700]), ("Barlow Condensed", "barlow-condensed", [600, 700, 800])]:
        for w in ws:
            fn = f"{slug}-latin-{w}-normal.woff2"; shutil.copy(B / f"node_modules/@fontsource/{slug}/files/{fn}", vend / fn)
            css += f"@font-face{{font-family:'{fam}';font-weight:{w};font-display:swap;src:url(http://127.0.0.1:8124/{fn}) format('woff2');}}\n"
    (vend / "fonts.css").write_text(css)
    html = (P / "test-build.html").read_text()
    html = re.sub(r'https://fonts\.googleapis\.com/css2\?[^"]+', "http://127.0.0.1:8124/fonts.css", html)
    html = re.sub(r'https://cdnjs\.cloudflare\.com/ajax/libs/Chart\.js/[^"]+', "http://127.0.0.1:8124/chart.umd.min.js", html)
    html = re.sub(r'https://cdnjs\.cloudflare\.com/ajax/libs/jszip/[^"\']+', "http://127.0.0.1:8124/jszip.min.js", html)
    lat = f"<script>(function(){{const f0=window.fetch;window.__apiT=[];window.fetch=async(u,o)=>{{if(String(u).includes('sheets.googleapis.com')){{const t=performance.now();await new Promise(r=>setTimeout(r,{API_LAT}));const r=await f0(u,o);window.__apiT.push([Math.round(t),Math.round(performance.now()),decodeURIComponent(String(u).slice(46,130))]);return r;}}return f0(u,o);}};}})();</script>"
    inj = "<script>" + (H / "mock.js").read_text() + "</script><script>" + (H / "shim.js").read_text() + "</script>" + lat
    html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + inj, 1) if '<meta charset="utf-8">' in html else html.replace("<head>", "<head>" + inj, 1)
    (site / "index.html").write_text(html)
    return site, vend

MARKS = """
(() => {
  const mark = n => { try { const m = JSON.parse(localStorage.getItem('__marks') || '[]'); if (!m.some(x => x[0] === n && x[2] === location.href)) { m.push([n, Date.now(), location.href]); localStorage.setItem('__marks', JSON.stringify(m)); } } catch(e){} };
  mark('doc');
  try { new PerformanceObserver(l => l.getEntries().forEach(e => { if (e.name === 'first-contentful-paint') mark('fcp'); })).observe({type:'paint', buffered:true}); } catch(e){}
  const iv = setInterval(() => {
    try {
      const h = document.querySelector('#v-home .hero, #v-home .day');
      if (h && !window.__cs) { window.__cs = 1; requestAnimationFrame(() => requestAnimationFrame(() => mark('content'))); }
      if (typeof lastSync !== 'undefined' && lastSync > 0) { mark('fresh'); clearInterval(iv); }
    } catch(e){}
  }, 16);
})();
"""

def run():
    tmp = pathlib.Path(tempfile.mkdtemp()); site, vend = build_site(tmp)
    s1, s2 = serve(site, 8123), serve(vend, 8124)
    out = {}
    with sync_playwright() as p:
        br = p.chromium.launch()
        c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="allow")
        def google(route):
            u = route.request.url; q = dict(x.split("=", 1) for x in u.split("?", 1)[1].split("&"))
            from urllib.parse import unquote
            time.sleep(GOOGLE_LAT)
            route.fulfill(status=302, headers={"Location": unquote(q["redirect_uri"]) + "#access_token=TOK&token_type=Bearer&expires_in=3599&state=" + q["state"]})
        c.route("https://accounts.google.com/**", google)
        c.add_init_script(MARKS)
        pg = c.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        # 1re visite : installation, carnet, première synchro (non mesurée)
        pg.goto("http://127.0.0.1:8123/"); pg.wait_for_timeout(300)
        pg.evaluate(f"""localStorage.setItem('sl-cfg', JSON.stringify({{appId:'{APP}', email:'alane@test.be'}}));
                       localStorage.setItem('sl-tok', JSON.stringify({{t:'TOK', exp:Date.now() + 3600e3}}));""")
        pg.goto("http://127.0.0.1:8123/"); pg.wait_for_function("typeof lastSync !== 'undefined' && lastSync > 0", timeout=60000)
        pg.wait_for_timeout(6000)  # blocs archivés, cache écrit, service worker actif
        pg.evaluate("navigator.serviceWorker.ready.then(()=>1)")
        def measure(name, expire):
            res = []
            for k in range(3):
                pg.goto("about:blank")
                pg.evaluate("1")
                pg2 = c.new_page(); pg2.on("pageerror", lambda e: errs.append(str(e)))
                pg2.goto("http://127.0.0.1:8123/sw.js")  # même origine, pour préparer le stockage
                pg2.evaluate("localStorage.setItem('__marks','[]')")
                if expire: pg2.evaluate("localStorage.setItem('sl-tok', JSON.stringify({t:'OLD', exp:Date.now() - 1000}))")
                t0 = time.time() * 1000
                pg2.goto("http://127.0.0.1:8123/", wait_until="commit")
                pg2.wait_for_function("(JSON.parse(localStorage.getItem('__marks')||'[]')).some(m => m[0]==='fresh')", timeout=60000)
                m = pg2.evaluate("JSON.parse(localStorage.getItem('__marks'))")
                first = lambda n: next((x[1] for x in m if x[0] == n), None)
                r = {n: round((first(n) - t0) / 1000, 2) if first(n) else None for n in ["fcp", "content", "fresh"]}
                r["pages"] = len({x[2] for x in m if x[0] == "doc"})
                if k == 0: out.setdefault("appels_api_" + name, pg2.evaluate("window.__apiT"))
                res.append(r); pg2.close()
            med = {n: sorted(x[n] for x in res if x[n] is not None)[len(res) // 2] for n in ["fcp", "content", "fresh"]}
            out[name] = {"essais": res, "médiane": med}
            print(name, med)
        measure("A_acces_valide", False)
        measure("B_acces_expire", True)
        out["erreurs_console"] = errs[:10]
        br.close()
    s1.shutdown(); s2.shutdown()
    out["hypotheses"] = {"aller_retour_s": RTT, "debit_octets_s": BW, "api_sheets_ms": API_LAT, "google_s": GOOGLE_LAT}
    (H / f"perf_{LABEL}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    run()
