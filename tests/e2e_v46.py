"""v46 : exercices en temps (gainage) : durée 1:30 / 90 / 1min30, jamais arrondie, jamais un record.
Usage : python3 tests/e2e_v46.py   (affiche « TOUT VERT » si tout passe)"""
import pathlib, json, sys, re
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)

# une ligne de cardio (« VELO », 20 min) ajoutée dans la séance de LOADED DEAD BUG de chaque semaine du bloc 7
INJ = """<script>(()=>{const g=window.__sheets['%s']['BLOC 7'];
 for (let w=0; w<4; w++){ const c=2+w*20; let r=0; for (let i=0;i<g.length;i++){ if (String((g[i]||[])[c+1]||'').trim()==='LOADED DEAD BUG'){ r=i; break; } }
   if(!r) continue; const put=(rr,arr)=>{ while(g.length<=rr) g.push([]); arr.forEach((v,k)=>{ const row=g[rr]; while(row.length<=c+k) row.push(''); row[c+k]=v; }); };
   put(r+4, ['PLANCHE GAINAGE','GAINAGE','','','3','45s','','','','','','','','','','']); }
})()</script>""" % COACH
MODE = {"v": ""}
def route2(r):
    u = r.request.url
    if u.endswith("/sl/") or u.endswith("index.html"):
        extra = "<script>window.__pre=%s</script>" % json.dumps(MODE["v"])
        return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + INJ + "<script src='/shim.js'></script>", 1), content_type="text/html")
    return route(r)

def boot(br, disc=None):
    c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route2)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    if disc is not None:
        pg.evaluate("(d) => { const P = window.__sheets['%s'].PROFIL; const r = P.find(x => x[0]==='disciplines'); if (r) r[1] = d; else P.push(['disciplines', d]); }" % APP, disc)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)
    return c, pg, errs

with sync_playwright() as p:
    br = p.chromium.launch()
    c, pg, errs = boot(br)
    cases = {"1:30":90, "90":90, "1min30":90, "1'30":90, "45s":45, "1,5":90, "2min":120, "":None, "abc":None}
    got = {k: pg.evaluate("(v) => parseDur(v)", k) for k in cases}
    check("parseDur : 1:30, 90, 1min30, 1'30, 45s, 1,5, 2min", all(got[k] == v for k, v in cases.items()), str(got))
    check("fmtDur : 90 → 1:30, 45 → 45 s, 120 → 2:00", pg.evaluate("[fmtDur(90), fmtDur(45), fmtDur(120)].join('|')") == "1:30|45 s|2:00")
    check("isTimedEx : gainage et 45s oui, squat non", pg.evaluate("[isTimedEx({mouvement:'GAINAGE',variation:'',reps:'3'}), isTimedEx({mouvement:'XYZ',variation:'',reps:'45s'}), isTimedEx({mouvement:'SQUAT',variation:'',reps:'45s'}), isTimedEx({mouvement:'CURL',variation:'',reps:'10'})].join()") == "true,true,false,false")
    # séance en direct sur l'exercice injecté
    ok = pg.evaluate("""(() => { for (const s of S) { const i = s.exercices.findIndex(e => isTimedEx(e)); if (i >= 0) { window.__ts = [s.key, i]; return true; } } return false; })()""")
    check("exercice en temps repéré dans la prog", ok)
    if ok:
        pg.evaluate("startLive(__ts[0], __ts[1])"); pg.wait_for_timeout(900)
        check("en-tête « Durée » à la place de « Reps »", "Durée" in pg.evaluate("document.querySelector('.setgrid .hd').innerText"))
        ri = pg.query_selector_all(".setrow input[data-chg=setR]")
        check("case durée présente (texte libre)", len(ri) >= 1 and ri[0].get_attribute("placeholder") == "1:30")
        if ri:
            ri[0].fill("1:30"); pg.dispatch_event(".setrow input[data-chg=setR]", "change"); pg.wait_for_timeout(200)
            pg.click(".setrow .ck"); pg.wait_for_timeout(500)
            r = pg.evaluate("live.rows[live.i].sets[0].r")
            check("1:30 enregistré = 90 s (pas arrondi à 1)", r == 90, str(r))
            check("affiché en 1:30 après validation", pg.evaluate("document.querySelector('.setrow input[data-chg=setR]').value") == "1:30")
            check("aucun bloc « nouveau max » pour un temps", pg.evaluate("!document.querySelector('#prbox').innerText.includes('max')"))
    check("aucune erreur JS", not errs, str(errs[:3]))
    br.close()
print("TOUT VERT" if not fails else "ÉCHECS : " + str(fails))
