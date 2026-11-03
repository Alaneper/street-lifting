"""Capture des écrans de première ouverture : accueil, carnet, puis l'inscription une question par écran (390x844 @2x).
Valeurs saisies = données de test fictives, rien n'est envoyé : on ne clique pas sur « Créer mon Google Sheet »."""
import sys, pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
OUTDIR = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUT; OUTDIR.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    snap = lambda n: (pg.evaluate("window.scrollTo(0,0)"), pg.screenshot(path=str(OUTDIR / f"inscription-{n}.png")))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1200); snap("1-accueil")
    pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500); snap("2-carnet")
    pg.click("[data-act=obStep][data-s=create]"); pg.wait_for_timeout(400)
    pg.fill("#obp", "Noa"); snap("3-prenom"); pg.click("[data-act=obNext]"); pg.wait_for_timeout(300)
    pg.click("[data-act=obDisc][data-k=power]"); pg.wait_for_timeout(200); snap("4-disciplines"); pg.click("[data-act=obNext]"); pg.wait_for_timeout(300)
    pg.fill("#obn", "2001-05-02"); pg.fill("#obw", "81,4"); pg.wait_for_timeout(300); snap("5-toi"); pg.click("[data-act=obNext]"); pg.wait_for_timeout(300)
    for l, v in (("SQUAT", "150"), ("BENCH", "110"), ("DEADLIFT", "142,5"), ("DIP", "40")): pg.fill(f"#obpr{l}", v)
    pg.wait_for_timeout(300); snap("6-barres"); pg.click("[data-act=obNext]"); pg.wait_for_timeout(300); snap("7-coach")
    print("ERREURS:", errs[:5])
