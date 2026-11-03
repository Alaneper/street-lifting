"""Capture de la caméra du scanner (caméra simulée par Chromium : image de test, pas de vrai code-barres). 390x844 @2x."""
import sys, pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
OUTDIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUT; OUTDIR.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    br = p.chromium.launch(args=["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"])
    c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", permissions=["camera"]); c.route("**/*", route)
    pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(1500)
    pg.evaluate("ACT.scanOpen({c:'nutri'})"); pg.wait_for_timeout(1500)
    pg.evaluate("document.getElementById('scanv').style.visibility='hidden'")   # la vidéo simulée est une mire verte : on la masque pour juger l'interface
    pg.screenshot(path=str(OUTDIR / "scanner.png"))
    # état « produit trouvé » : produit FICTIF (valeurs de démonstration), seulement pour juger la mise en page
    pg.evaluate("scanFound({nom:'Skyr nature 0 %', marque:'', k:63.3, p:10.7, g:4, l:0.2, por:150, src:'perso', code:'', check:null})"); pg.wait_for_timeout(500)
    pg.screenshot(path=str(OUTDIR / "scanner-trouve.png"))
    print("ERREURS:", errs[:3]); br.close()
