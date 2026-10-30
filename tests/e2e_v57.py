"""v57 : choix reps / temps par exercice + sélection du contenu au toucher d'une case.
Usage : python3 tests/e2e_v57.py   (affiche « TOUT VERT » si tout passe)"""
import pathlib, json, sys, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)

def boot(br):
    c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)
    return c, pg, errs

with sync_playwright() as p:
    br = p.chromium.launch()
    c, pg, errs = boot(br)
    # logique pure
    r = pg.evaluate("""(() => { const e = {mouvement:'ROWING', variation:'HALTERE', reps:'12'}; const a = isTimedEx(e);
      D.profil.ex_modes = exModeStr(e, 'T'); const b = isTimedEx(e), o1 = exModeOf(e);
      D.profil.ex_modes = exModeStr(e, 'R'); const d = isTimedEx(e);
      const g = {mouvement:'GAINAGE', variation:'', reps:'45s'}; D.profil.ex_modes = exModeStr(g, 'R'); const f = isTimedEx(g);
      const sq = {mouvement:'SQUAT', variation:'', reps:'5'}; D.profil.ex_modes = exModeStr(sq, 'T'); const h = isTimedEx(sq);
      D.profil.ex_modes = ''; return [a, b, o1, d, f, h, isTimedEx(g)].join('|'); })()""")
    check("choix temps / reps prime sur la détection ; un mouvement de force reste en reps ; sans choix, auto", r == "false|true|T|false|false|false|true", r)
    # séance en direct sur un exercice non-force, non-cardio
    ok = pg.evaluate("""(() => { for (const s of S) { const i = s.exercices.findIndex(e => !liftOf(e.mouvement) && !isCardioEx(e) && !isTimedEx(e)); if (i >= 0) { window.__ts = [s.key, i]; return true; } } return false; })()""")
    check("exercice d'accessoire repéré dans la prog", ok)
    if ok:
        pg.evaluate("startLive(__ts[0], __ts[1])"); pg.wait_for_timeout(900)
        check("en-tête « Reps » au départ", "Reps" in pg.evaluate("document.querySelector('.setgrid .hd').innerText"))
        btns = pg.query_selector_all("[data-act=exMode]")
        check("deux boutons Reps / Temps présents", len(btns) == 2)
        pg.click("[data-act=exMode][data-v=T]"); pg.wait_for_timeout(700)
        check("après « Temps » : en-tête « Durée »", "Durée" in pg.evaluate("document.querySelector('.setgrid .hd').innerText"))
        check("case durée en texte libre", pg.evaluate("document.querySelector('.setrow input[data-chg=setR]').getAttribute('placeholder')") == "1:30")
        check("choix gardé dans le profil", "=T" in pg.evaluate("D.profil.ex_modes || ''"))
        pg.click("[data-act=exMode][data-v=R]"); pg.wait_for_timeout(700)
        check("retour en « Reps »", "Reps" in pg.evaluate("document.querySelector('.setgrid .hd').innerText"))
        # sélection au toucher
        pg.fill(".setrow input[data-chg=setC]", "28,5"); pg.dispatch_event(".setrow input[data-chg=setC]", "change")
        pg.evaluate("document.activeElement && document.activeElement.blur()")
        pg.focus(".setrow input[data-chg=setC]"); pg.wait_for_timeout(100)
        sel = pg.evaluate("(() => { const i = document.activeElement; return [i.selectionStart, i.selectionEnd, i.value.length].join('|'); })()")
        a, b, n = [int(x) for x in sel.split("|")]
        check("toucher la case de charge sélectionne tout (début = 0, fin = longueur)", a == 0 and b == n and n > 0, sel)
        pg.keyboard.press("Backspace"); pg.wait_for_timeout(100)
        check("une seule touche d'effacement vide la case", pg.evaluate("document.activeElement.value") == "")
        pg.keyboard.type("30"); pg.wait_for_timeout(100)
        check("taper remplace la valeur", pg.evaluate("document.activeElement.value") == "30")
        pg.focus(".setrow input[data-chg=setR]"); pg.wait_for_timeout(100)
        a2 = pg.evaluate("(() => { const i = document.activeElement; return i.selectionStart + '|' + i.selectionEnd + '|' + i.value.length; })()")
        x, y, z = [int(v) for v in a2.split("|")]
        check("même chose sur la case reps", x == 0 and y == z, a2)
    check("aucune erreur JS", not errs, str(errs[:3]))
    br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
