import pathlib, zipfile, tempfile
H = pathlib.Path(__file__).resolve().parent
# archive MyFitnessPal synthétique (le fichier d'origine vivait dans le dossier d'une ancienne session)
MFP = pathlib.Path(tempfile.mkdtemp()) / "mfp.zip"
with zipfile.ZipFile(MFP, "w") as z:
    z.writestr("measurements.csv", "Date,Weight\n" + "\n".join(f"2026-0{m}-{d:02d},{74.0 + (m + d) % 5 * 0.1:.1f}" for m in (6, 7) for d in (1, 8, 15, 22)))
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4000)
    pg.click("[data-tab=corps]"); pg.wait_for_timeout(800); pg.click("[data-act=corpsTab][data-k=poids]"); pg.wait_for_timeout(500)
    pg.evaluate("ACT.settings({})"); pg.wait_for_timeout(500); pg.evaluate("document.querySelector('#imp').closest('details').open = true"); pg.set_input_files("#imp", str(MFP)); pg.wait_for_timeout(4000)
    imp_txt = pg.locator("#impres").text_content() or ""
    print("import :", imp_txt, "| details ouvert:", pg.evaluate("document.querySelector('details.more').open"), "| rows:", pg.evaluate("typeof importRows !== 'undefined' && importRows ? importRows.length : -1"))
    pg.evaluate("ACT.openLift({l:'DIP'})"); pg.wait_for_timeout(1200)
    print("records :", pg.locator(".rec").all_inner_texts()[:3])
    print("ERRORS:", errs)
    import sys; sys.exit(1 if errs or "8 pesées trouvées" not in imp_txt else 0)
