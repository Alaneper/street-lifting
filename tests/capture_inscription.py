"""Capture des écrans de première ouverture (connexion, choix du carnet) en 390x844 @2x."""
import sys, pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
OUTDIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUT; OUTDIR.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1200); pg.screenshot(path=str(OUTDIR / "inscription-1-connexion.png"))
    pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500); pg.screenshot(path=str(OUTDIR / "inscription-2-carnet.png"))
    print("ERREURS:", errs[:5])
