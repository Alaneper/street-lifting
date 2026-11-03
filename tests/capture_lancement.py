"""Capture de l'écran de lancement (logo, devise, barre de chargement) : scripts désactivés : on voit le HTML tel qu'il est avant le démarrage. 390x844 @2x."""
import sys, pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
OUTDIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUT; OUTDIR.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", java_script_enabled=False)
    pg = c.new_page(); pg.set_content((P / "test-build.html").read_text())
    pg.wait_for_timeout(700); pg.screenshot(path=str(OUTDIR / "lancement.png")); br.close()
