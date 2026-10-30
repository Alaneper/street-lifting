"""v61 : commentaire du sportif par exercice (carnet + Sheet du coach).
Données inventées. Usage : python3 tests/e2e_v61.py   (affiche « TOUT VERT » si tout passe)"""
import pathlib, json, sys
H = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(H))
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)

def day(k, nom, rows, extra_hdr=None, extra_col=None):
    h = ["Cat.", "Exercise", "Séries", "Reps", "Indications", "RPE", "%1RM", "Avg. Speed Target", "Charge", "", "Repos", "Reps", "Charges"]
    if extra_hdr: h = h + [extra_hdr]
    rr = [r + ([extra_col] if extra_col is not None else []) for r in rows]
    return [["DAY %d" % k, nom, "RECOMMENDE", "", "", "", "", "", "", "", "", "EFFECTUE"], h] + rr + [[], []]
def week(extra_hdr=None, extra_col=None):
    return [[], [], ["Athlète test"], []] + day(1, "Lundi", [["AC", "Chest Supported Machine Row", "3", "10", "", "", "", "", "", "50", "3'", "", ""],
                                                           ["AC", "Leg Extension", "3", "12", "", "", "", "", "", "40", "2'", "", ""]], extra_hdr, extra_col)
def boot(br, tabs=None):
    inj = "" if tabs is None else "<script>(()=>{const b=window.__sheets['%s']; for (const k of Object.keys(b)) delete b[k]; const T=%s; for (const k of Object.keys(T)) b[k]=T[k]; })()</script>" % (COACH, json.dumps(tabs))
    def route2(r, *_):
        u = r.request.url
        if u.endswith("/sl/") or u.endswith("index.html"):
            return r.fulfill(body=(P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + inj + "<script src='/shim.js'></script>", 1), content_type="text/html")
        return route(r)
    c = br.new_context(viewport={"width":390,"height":844}, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route2)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(5000)
    pg.evaluate("ensureAllBlocs()"); pg.wait_for_timeout(2500)
    return c, pg, errs
def do_sets(pg, n=2, reps="8", charge="20"):
    for j in range(n):
        row = pg.locator(".setrow").nth(j)
        row.locator("input[data-chg=setC]").fill(charge); row.locator("input[data-chg=setC]").dispatch_event("change")
        row.locator("input[data-chg=setR]").fill(reps); row.locator("input[data-chg=setR]").dispatch_event("change")
        row.locator(".ck").click(); pg.wait_for_timeout(350)
        pg.evaluate("sheet === 'rest' && ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(120)
def comment(pg, txt):
    if pg.locator("[data-act=comOpen]").count(): pg.click("[data-act=comOpen]"); pg.wait_for_timeout(200)
    pg.fill("#lcom", txt); pg.wait_for_timeout(100)
def save(pg):
    pg.evaluate("(async () => { window.__ok = await saveRow(live.i); })()"); pg.wait_for_timeout(1500)
def series_last(pg): return pg.evaluate("window.__sheets['%s'].SERIES.slice(-1)[0]" % APP)
def cell(pg, tab, col, row): return pg.evaluate("(() => { const g = window.__sheets['%s'][%s]; return ((g[%d - 1] || [])[%d - 1]) ?? ''; })()" % (COACH, json.dumps(tab), row, col))

with sync_playwright() as p:
    br = p.chromium.launch()
    # ---------- A. modèle d'Alane et Noa : colonne « COMMENTAIRE ATHLÈTE » ----------
    c, pg, errs = boot(br)
    ok = pg.evaluate("""(() => { for (const s of S) { if (!s.cols.commentaire || s.week) continue; const i = s.exercices.findIndex(e => norm(e.mouvement) === 'RENFO' && !isTimedEx(e) && !isCardioEx(e) && !String(e.commentaire || '').trim()); if (i >= 0) { window.__ts = [s.key, i]; return true; } } return false; })()""")
    check("A · exercice de renfo avec case commentaire vide", ok)
    if ok:
        pg.evaluate("startLive(__ts[0], __ts[1])"); pg.wait_for_timeout(900)
        check("A · lien « + Commentaire pour ton coach » visible", pg.locator("[data-act=comOpen]").count() == 1 and "pour ton coach" in pg.locator("[data-act=comOpen]").inner_text())
        do_sets(pg, 2); comment(pg, "Genou un peu sensible"); save(pg)
        r = series_last(pg)
        check("A · carnet : commentaire en colonne J", r and len(r) >= 10 and r[9] == "Genou un peu sensible", str(r))
        check("A · carnet : en-tête J1 « Commentaire » ajouté", pg.evaluate("window.__sheets['%s'].SERIES[0][9]" % APP) == "Commentaire")
        sk = pg.evaluate("(() => { const s = seanceByKey(live.key), e = s.exercices[live.i]; return [s.sheet, s.cols.commentaire, e.row]; })()")
        v = cell(pg, *sk)
        check("A · Sheet du coach : « 8,8 · Genou un peu sensible »", v.startswith("8,8") and v.endswith(" · Genou un peu sensible"), v)
        # l'historique relit toujours les bonnes reps
        check("A · relu comme des reps (8, 8) : pas de série en trop", pg.evaluate("JSON.stringify(setsFromComment(seanceByKey(live.key).exercices[live.i], 20).map(x => x.r))") == "[8,8]")
        # modifier puis effacer le commentaire
        comment(pg, "Ça va mieux"); pg.evaluate("live.rows[live.i].dirty = true"); save(pg)
        check("A · commentaire modifié remplacé chez le coach", cell(pg, *sk).endswith(" · Ça va mieux"), cell(pg, *sk))
        comment(pg, ""); pg.evaluate("live.rows[live.i].dirty = true"); save(pg)
        v2 = cell(pg, *sk); check("A · commentaire effacé : il ne reste que les reps", v2 in ("8,8",) , v2)
        check("A · carnet : colonne J vidée", series_last(pg)[9] == "", str(series_last(pg)))
        # protection : texte écrit à la main dans la case
        pg.evaluate("(() => { const s = seanceByKey(live.key), e = s.exercices[live.i]; const g = window.__sheets['%s'][s.sheet]; g[e.row - 1][s.cols.commentaire - 1] = 'Fais attention au dos'; e.commentaire = 'Fais attention au dos'; })()" % COACH)
        comment(pg, "Mon ressenti"); pg.evaluate("live.rows[live.i].dirty = true"); save(pg)
        check("A · texte écrit à la main jamais remplacé", cell(pg, *sk) == "Fais attention au dos", cell(pg, *sk))
        check("A · … mais le commentaire reste dans le carnet", series_last(pg)[9] == "Mon ressenti")
        # rechargement : la case est pré-remplie depuis le carnet
        pg.evaluate("(async () => { await loadApp(); })()"); pg.wait_for_timeout(2500)
        check("A · relu après rechargement", pg.evaluate("D.series.slice(-1)[0].com") == "Mon ressenti")
    # sans commentaire : la ligne SERIES reste à 9 colonnes (comme avant)
    ok2 = pg.evaluate("""(() => { for (const s of S) { const i = s.exercices.findIndex(e => !liftOf(e.mouvement) && !isTimedEx(e) && !isCardioEx(e) && !comLog(s, e)); if (i >= 0 && s.key !== (window.__ts || [])[0]) { window.__t2 = [s.key, i]; return true; } } return false; })()""")
    if ok2:
        pg.evaluate("live = null; startLive(__t2[0], __t2[1])"); pg.wait_for_timeout(900); do_sets(pg, 1, "10", "30"); save(pg)
        check("sans commentaire : ligne SERIES à 9 colonnes (format inchangé)", len(series_last(pg)) == 9, str(series_last(pg)))
    check("A · aucune erreur JS", not errs, str(errs[:3])); c.close()

    # ---------- B. modèle WEEK sans colonne commentaire : petite case créée ----------
    c, pg, errs = boot(br, {"BLOC 3": [[], [], ["Athlete Info"]], "WEEK 1": week(), "DATA": [["x"]]})
    before = pg.evaluate("JSON.stringify(window.__sheets['%s']['WEEK 1'])" % COACH)
    pg.evaluate("startLive(S[0].key, 0)"); pg.wait_for_timeout(900)
    do_sets(pg, 2, "10", "50"); comment(pg, "3e série dure, prise glissante"); save(pg)
    g = pg.evaluate("window.__sheets['%s']['WEEK 1']" % COACH)
    hr = pg.evaluate("S[0].headerRow"); er = pg.evaluate("S[0].exercices[0].row")
    check("B · en-tête « Commentaire athlète » créé à droite de « Charges » (colonne N)", (g[hr - 1] + [""] * 20)[13] == "Commentaire athlète", str(g[hr - 1]))
    check("B · commentaire en face de l'exercice (sans les reps, qui ont leur colonne)", (g[er - 1] + [""] * 20)[13] == "3e série dure, prise glissante", str(g[er - 1]))
    check("B · reps et charges faites toujours dans L et M", (g[er - 1] + [""] * 20)[11] == "10, 10" and (g[er - 1] + [""] * 20)[12] == "50", str(g[er - 1]))
    b = json.loads(before); diff = [(i + 1, j + 1) for i in range(max(len(b), len(g))) for j in range(max(len(b[i]) if i < len(b) else 0, len(g[i]) if i < len(g) else 0))
            if ((b[i] if i < len(b) else []) + [""] * 30)[j] != ((g[i] if i < len(g) else []) + [""] * 30)[j]]
    check("B · seules 4 cases changées dans le Sheet (L, M, en-tête N, commentaire N)", sorted(diff) == sorted([(er, 12), (er, 13), (hr, 14), (er, 14)]), str(diff))
    check("B · « 3e série dure » jamais relu comme des reps", pg.evaluate("setsFromComment(S[0].exercices[0], 50)") is None)
    check("B · aucune erreur JS", not errs, str(errs[:3])); c.close()

    # ---------- C. modèle WEEK : colonne voisine déjà utilisée -> rien n'est créé ----------
    c, pg, errs = boot(br, {"BLOC 3": [[], [], ["Athlete Info"]], "WEEK 1": week(None, None), "DATA": [["x"]]})
    pg.evaluate("(() => { const g = window.__sheets['%s']['WEEK 1']; const r = S[0].exercices[1].row - 1; while (g[r].length < 14) g[r].push(''); g[r][13] = 'formule du coach'; })()" % COACH)
    before = pg.evaluate("JSON.stringify(window.__sheets['%s']['WEEK 1'][S[0].headerRow - 1])" % COACH)
    pg.evaluate("startLive(S[0].key, 0)"); pg.wait_for_timeout(900)
    do_sets(pg, 1, "10", "50"); comment(pg, "RAS"); save(pg)
    check("C · colonne occupée : aucun en-tête créé", pg.evaluate("JSON.stringify(window.__sheets['%s']['WEEK 1'][S[0].headerRow - 1])" % COACH) == before)
    check("C · commentaire gardé dans le carnet", series_last(pg)[9] == "RAS", str(series_last(pg)))
    check("C · aucune erreur JS", not errs, str(errs[:3])); c.close()

    # ---------- D. modèle WEEK avec une colonne « Ressenti » : écrit dedans ----------
    c, pg, errs = boot(br, {"BLOC 3": [[], [], ["Athlete Info"]], "WEEK 1": week("Ressenti", ""), "DATA": [["x"]]})
    check("D · « Ressenti » reconnu comme colonne du sportif", pg.evaluate("S[0].cols.commentaire") == 14, str(pg.evaluate("S[0].cols")))
    check("D · « Commentaire du coach » / « Indications » jamais reconnus", pg.evaluate("[isAthleteNoteHdr('Commentaire du coach'), isAthleteNoteHdr('Indications'), isAthleteNoteHdr('Notes coach'), isAthleteNoteHdr('Ressenti athlète'), isAthleteNoteHdr('Feedback')].join()") == "false,false,false,true,true")
    pg.evaluate("startLive(S[0].key, 0)"); pg.wait_for_timeout(900)
    do_sets(pg, 1, "10", "50"); comment(pg, "Bonne séance"); save(pg)
    er = pg.evaluate("S[0].exercices[0].row")
    check("D · écrit dans la colonne « Ressenti »", cell(pg, "WEEK 1", 14, er) == "Bonne séance", cell(pg, "WEEK 1", 14, er))
    check("D · aucune colonne créée en plus", cell(pg, "WEEK 1", 15, pg.evaluate("S[0].headerRow")) == "")
    check("D · aucune erreur JS", not errs, str(errs[:3])); c.close()
    br.close()
print("TOUT VERT" if not fails else "ÉCHECS : %s" % fails)
