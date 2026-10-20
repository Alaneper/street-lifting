import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4000)
    pg.click("[data-tab=corps]"); pg.wait_for_timeout(800)
    pg.set_input_files("#imp", "/tmp/claude-0/-home-claude/a112c60f-9639-549a-a0f9-bbd91e82e76a/scratchpad/mfp.zip"); pg.wait_for_timeout(1500)
    print("import :", pg.locator("#impres").inner_text())
    pg.evaluate("ACT.openLift({l:'DIP'})"); pg.wait_for_timeout(1200)
    print("records :", pg.locator(".rec").all_inner_texts()[:3])
    print("ERRORS:", errs)
