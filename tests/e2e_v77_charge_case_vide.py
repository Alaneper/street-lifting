"""v77 : la charge faite est écrite aussi dans une case « Charge » vide (fourchette de reps sans charge prescrite) ; texte et formule restent intouchés."""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(2000)
    r = pg.evaluate("""(() => { setChargeSync(coachId(), true);
      const s = Object.assign({}, S[0], {week:false, archived:false, sheet:'T', cols:{charge:4}});
      const mk = ch => ({mouvement:'X', variation:'', charge:ch, row:9, series:3, reps:'10-20'});
      const done = [{c:106, r:10}, {c:106, r:10}];
      return {vide: chargePlan(s, mk(''), done), absent: chargePlan(s, mk(undefined), done), texte: chargePlan(s, mk('RPE8'), done), formule: chargePlan(s, mk('=A1*2'), done), nombre: chargePlan(s, mk('102,5'), done)}; })()""")
    check("case vide : charge à écrire (106), attendue vide", r["vide"] and r["vide"]["val"] == 106 and "" in r["vide"]["expect"], r["vide"])
    check("case sans valeur (undefined) : idem", r["absent"] and r["absent"]["val"] == 106 and "" in r["absent"]["expect"], r["absent"])
    check("texte (RPE8) : jamais écrasé", r["texte"] is None)
    check("formule : jamais écrasée", r["formule"] is None)
    check("nombre : comme avant", r["nombre"] and r["nombre"]["val"] == 106)
    check("aucune erreur JS", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails if fails else "aucun")
