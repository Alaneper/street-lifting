import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4000)
    pg.click("[data-tab=corps]"); pg.wait_for_timeout(1500)
    for q, exp in [("250 g de pâtes sèches", 910), ("1 cordon bleu", 226), ("abricot 100g", 44.1), ("p", None)]:
        pg.fill("#nutin", q); pg.wait_for_timeout(400)
        sug = pg.locator("#nutdyn .item .ttl").all_inner_texts()[:5]
        print(q, "→", sug)
        if exp is None: continue
        pg.locator("#nutdyn .item").first.click(); pg.wait_for_timeout(300)
        if q.startswith("1 "): pg.locator("#nutdyn .chip").first.click(); pg.wait_for_timeout(200)
        print("   quantité :", pg.input_value("#nq"))
        pg.click("[data-act=nutAdd]"); pg.wait_for_timeout(800)
    print("héros :", pg.locator("#v-corps .hero").first.inner_text().replace("\n", " | "))
    print("REPAS :", pg.evaluate(f"(window.__sheets['{APP}'].REPAS||[]).slice(0,4)"))
    pg.fill("#ndep", "4398"); pg.click("[data-act=nutDep]"); pg.wait_for_timeout(800)
    print("dépense :", pg.evaluate(f"(window.__sheets['{APP}'].DEPENSE||[]).slice(0,3)"), "| héros :", pg.locator("#v-corps .hero").first.inner_text().replace("\n"," | "))
    pg.select_option("#nob", "perte"); pg.wait_for_timeout(1200)
    print("objectif :", pg.locator("#v-corps .panel").last.inner_text().replace("\n", " | ")[:400])
    pg.screenshot(path=str(OUT / "nutri.png"), full_page=True)
    print("ERRORS:", errs[:8])
