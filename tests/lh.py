"""Lighthouse (mobile, réseau et processeur bridés par Lighthouse) sur l'app avec un carnet déjà ouvert.
Les appels Google sont simulés dans la page (mock), les polices et Chart.js servis en local.
Usage : python3 tests/lh.py [étiquette]   → tests/lh_<étiquette>.json (scores + métriques)"""
import sys, json, subprocess, tempfile, pathlib, os
from playwright.sync_api import sync_playwright
sys.argv = sys.argv[:2]
H = pathlib.Path(__file__).resolve().parent
import importlib.util
spec = importlib.util.spec_from_file_location("perf", H / "perf.py"); perf = importlib.util.module_from_spec(spec); spec.loader.exec_module(perf)
LABEL = sys.argv[1] if len(sys.argv) > 1 else "run"
CHROME = "/opt/pw-browsers/chromium"
tmp = pathlib.Path(tempfile.mkdtemp()); site, vend = perf.build_site(tmp)
s1, s2 = perf.serve(site, 8123, slow=False), perf.serve(vend, 8124, slow=False)
prof = tmp / "profile"
with sync_playwright() as p:
    c = p.chromium.launch_persistent_context(str(prof), executable_path=CHROME, viewport={"width":390, "height":844})
    pg = c.new_page(); pg.goto("http://127.0.0.1:8123/"); pg.wait_for_timeout(300)
    pg.evaluate(f"""localStorage.setItem('sl-cfg', JSON.stringify({{appId:'{perf.APP}', email:'alane@test.be'}}));
                   localStorage.setItem('sl-tok', JSON.stringify({{t:'TOK', exp:Date.now() + 3600e3}}));""")
    pg.goto("http://127.0.0.1:8123/"); pg.wait_for_function("typeof lastSync !== 'undefined' && lastSync > 0", timeout=60000); pg.wait_for_timeout(4000)
    c.close()
out = {}
for mode in ["froid", "chaud"]:
    rep = tmp / f"lh_{mode}.json"
    cmd = [str(perf.B / "node_modules/.bin/lighthouse"), "http://127.0.0.1:8123/", "--quiet", "--output=json", f"--output-path={rep}",
           "--only-categories=performance,accessibility,best-practices", "--disable-storage-reset",
           f"--chrome-flags=--headless=new --no-sandbox --user-data-dir={prof}"]
    if mode == "froid": cmd.remove("--disable-storage-reset")
    env = dict(os.environ, CHROME_PATH=CHROME)
    subprocess.run(cmd, env=env, timeout=300)
    j = json.loads(rep.read_text())
    a = j["audits"]
    out[mode] = {"scores": {k: round(v["score"] * 100) for k, v in j["categories"].items()},
                 "FCP_s": round(a["first-contentful-paint"]["numericValue"] / 1000, 2), "LCP_s": round(a["largest-contentful-paint"]["numericValue"] / 1000, 2),
                 "TBT_ms": round(a["total-blocking-time"]["numericValue"]), "CLS": round(a["cumulative-layout-shift"]["numericValue"], 3),
                 "poids_ko": round(a["total-byte-weight"]["numericValue"] / 1024),
                 "echecs": [k for k, v in a.items() if v.get("score") is not None and v["score"] < 0.9 and v.get("scoreDisplayMode") in ("binary", "numeric", "metricSavings")][:25]}
    print(mode, json.dumps(out[mode], ensure_ascii=False))
s1.shutdown(); s2.shutdown()
(H / f"lh_{LABEL}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
