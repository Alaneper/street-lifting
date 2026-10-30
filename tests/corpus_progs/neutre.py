"""Lot « neutre » : 12 progs réalistes + vérité terrain. Données inventées."""
from lib import *
import unicodedata

def nz(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().strip()

def noise(p, *lines): p.noise = [nz(x) for x in lines]; return p

# ---------------- N01 note WhatsApp ----------------
def N01():
    p = Prog("N01", "neutre", "note", "WhatsApp coach Maxime - semaine PPL",
             ["messages horodatés au milieu", "superset A1/A2", "échauffement à ignorer", "DC/Tracs/Élév lat abréviations", "dips lestés +10kg", "gainage chronométré"],
             "Export WhatsApp d'un coach fictif (Maxime) à son client Théo")
    t = TB(p)
    t.week("[12/10 08:14] Coach Maxime: Salut Théo, voici ta semaine")
    t.day("LUNDI - Push")
    t.raw("Echauff: 10 min rameur + 2x15 élastiques (ça compte pas)")
    t.exo("DC 4x8 @80", "DC", [g(4, 8, kg(80))], canon="Développé couché")
    t.exo("Dév incliné haltères 3 x 10 @28kg", "Dév incliné haltères", [g(3, 10, kg(28))])
    t.exo("A1 Dips lestés 3x6 +10kg", "Dips lestés", [g(3, 6, lest(10))])
    t.exo("A2 Tracs poulie 3x12", "Tracs poulie", [g(3, 12)])
    t.exo("Élév lat 4×15 @8kg", "Élév lat", [g(4, 15, kg(8))])
    t.raw("[12/10 08:16] Coach Maxime: Pense à bien boire entre les séries")
    t.day("[12/10 08:17] Coach Maxime: MERCREDI - Pull")
    t.exo("Tractions lestées 5x5 +15kg", "Tractions lestées", [g(5, 5, lest(15))])
    t.exo("Rowing barre 4x8 @70", "Rowing barre", [g(4, 8, kg(70))])
    t.exo("Tirage horizontal 3x12 @55", "Tirage horizontal", [g(3, 12, kg(55))])
    t.exo("A1 Curl barre EZ 3x10 @30", "Curl barre EZ", [g(3, 10, kg(30))])
    t.exo("A2 Face pull 3x15 @20", "Face pull", [g(3, 15, kg(20))])
    t.raw("Si t'es mort après le rowing tu peux sauter le tirage hein")
    t.day("VENDREDI - Legs")
    t.raw("Echauff: 5 min vélo + squat à vide x15")
    t.exo("Squat 5x5 @100", "Squat", [g(5, 5, kg(100))])
    t.exo("RDL 4x8 @90", "RDL", [g(4, 8, kg(90))], canon="Soulevé de terre roumain")
    t.exo("Presse 3x12 @180", "Presse", [g(3, 12, kg(180))])
    t.exo("Leg curl 3x12 @40", "Leg curl", [g(3, 12, kg(40))])
    t.exo("Mollets debout 4x15 @60", "Mollets debout", [g(4, 15, kg(60))])
    t.exo("Gainage 3 x 45s", "Gainage", [g(3, "45 s")])
    t.raw("[12/10 08:25] Coach Maxime: Semaine prochaine on monte de 2,5kg partout si ça passe")
    t.done()
    return noise(p, "Echauff: 10 min rameur + 2x15 élastiques (ça compte pas)", "Echauff: 5 min vélo + squat à vide x15",
                 "Pense à bien boire entre les séries", "Si t'es mort après le rowing tu peux sauter le tirage hein",
                 "Semaine prochaine on monte de 2,5kg partout si ça passe", "LUNDI - Push", "MERCREDI - Pull", "VENDREDI - Legs",
                 "Salut Théo, voici ta semaine")

# ---------------- N02 note téléphone ----------------
def N02():
    p = Prog("N02", "neutre", "note", "Notes iPhone en vrac - Karim",
             ["notations hétérogènes (100kg x 5 x 3, 8/8/6/6, 3 séries de 10)", "fautes de frappe", "unilatéral 'chaque bras/jambe'", "commentaires et échauffement"],
             "Note de téléphone d'un pratiquant fictif (Karim)")
    t = TB(p)
    t.week("prog sept")
    t.day("lundi haut")
    t.raw("(echauf 2x10 barre vide)")
    t.exo("dc 100kg x 5 x 3", "dc", [g(3, 5, kg(100))], canon="Développé couché")
    t.exo("dév incliné hlt 4x10 @26", "dév incliné hlt", [g(4, 10, kg(26))])
    t.exo("oh press 8/8/6/6 @40", "oh press", [g(2, 8, kg(40)), g(2, 6, kg(40))], canon="Développé militaire")
    t.exo("trac 3 séries de 10", "trac", [g(3, 10)], canon="Tractions")
    t.exo("rowing haltere 4x10 @32 chaque bras", "rowing haltere", [g(4, 10, kg(32))], side=True)
    t.exo("curl marteau 3x12 @14", "curl marteau", [g(3, 12, kg(14))])
    t.raw("ça passe pas sur le dernier set de dc, rester 2 min de repos")
    t.day("mercredi bas")
    t.exo("squat 5x5 @110", "squat", [g(5, 5, kg(110))])
    t.exo("sdt roumain 4x8 @100", "sdt roumain", [g(4, 8, kg(100))])
    t.exo("fentes bulgares 3x10 @20 chaque jambe", "fentes bulgares", [g(3, 10, kg(20))], side=True)
    t.exo("leg ext 3x15 @45", "leg ext", [g(3, 15, kg(45))])
    t.exo("mollets 4x20 @80", "mollets", [g(4, 20, kg(80))])
    t.exo("gainage 3x45s", "gainage", [g(3, "45 s")])
    t.day("samedi")
    t.exo("tractions lestées 4x6 +20kg", "tractions lestées", [g(4, 6, lest(20))])
    t.exo("dips 3 x max", "dips", [g(3, "max")])
    t.exo("dc léger 3x12 @60", "dc léger", [g(3, 12, kg(60))])
    t.exo("tracs corde 3x15 @25", "tracs corde", [g(3, 15, kg(25))])
    t.exo("abdos roue 3x10", "abdos roue", [g(3, 10)])
    t.done()
    return noise(p, "prog sept", "lundi haut", "mercredi bas", "samedi", "(echauf 2x10 barre vide)",
                 "ça passe pas sur le dernier set de dc, rester 2 min de repos")

# ---------------- N03 Notion markdown ----------------
def N03():
    p = Prog("N03", "neutre", "note", "Programme Force - Notion",
             ["% de 1RM annoncé en haut", "semaine 2 deload", "cases à cocher markdown", "tempo 3-1-X-0", "ligne de total", "échauffement coché"],
             "Page Notion exportée en markdown, coach fictif")
    t = TB(p)
    t.raw("# Programme Force - Cycle 1")
    t.raw("> 1RM actuels : squat 140 kg, développé couché 100 kg")
    t.raw("> 💡 Semaine 2 = deload, on garde la technique")
    t.raw("")
    for wk, (title, rows) in enumerate([
        ("## Semaine 1", [
            [("Squat 5x5 @ 75%", "Squat", [g(5, 5, pct(75))], {}),
             ("Squat pause 3x3 @ 60%", "Squat pause", [g(3, 3, pct(60))], {}),
             ("Presse à cuisses 3x10 @140kg tempo 3-1-X-0", "Presse à cuisses", [g(3, 10, kg(140))], {"tempo": "3-1-X-0"}),
             ("Leg curl 3x12 @40kg", "Leg curl", [g(3, 12, kg(40))], {}),
             ("Mollets debout 4x15 @70kg", "Mollets debout", [g(4, 15, kg(70))], {})],
            [("Développé couché 5x5 @ 75%", "Développé couché", [g(5, 5, pct(75))], {}),
             ("DC prise serrée 3x8 @ 65%", "DC prise serrée", [g(3, 8, pct(65))], {}),
             ("Tractions 4x6", "Tractions", [g(4, 6)], {}),
             ("Rowing T 3x10 @50kg", "Rowing T", [g(3, 10, kg(50))], {}),
             ("Face pull 3x15 @20kg", "Face pull", [g(3, 15, kg(20))], {})]]),
        ("## Semaine 2 (deload)", [
            [("Squat 3x5 @ 60%", "Squat", [g(3, 5, pct(60))], {}),
             ("Squat pause 2x3 @ 50%", "Squat pause", [g(2, 3, pct(50))], {}),
             ("Presse à cuisses 2x10 @120kg tempo 3-1-X-0", "Presse à cuisses", [g(2, 10, kg(120))], {"tempo": "3-1-X-0"}),
             ("Leg curl 2x12 @30kg", "Leg curl", [g(2, 12, kg(30))], {}),
             ("Mollets debout 3x15 @60kg", "Mollets debout", [g(3, 15, kg(60))], {})],
            [("Développé couché 3x5 @ 60%", "Développé couché", [g(3, 5, pct(60))], {}),
             ("DC prise serrée 2x8 @ 55%", "DC prise serrée", [g(2, 8, pct(55))], {}),
             ("Tractions 3x6", "Tractions", [g(3, 6)], {}),
             ("Rowing T 2x10 @40kg", "Rowing T", [g(2, 10, kg(40))], {}),
             ("Face pull 2x15 @15kg", "Face pull", [g(2, 15, kg(15))], {})]])]):
        t.week(title)
        for di, (dt, day) in enumerate(zip(["### Jour 1 - Squat", "### Jour 2 - Bench"], rows)):
            t.day(dt)
            t.raw("- [x] Échauffement : 10 min vélo + 3 séries progressives (à ignorer)")
            for line, name, grp, kw in day: t.exo("- [ ] " + line, name, grp, **kw)
        t.raw("**Total semaine : %d séries**" % (41 if wk == 0 else 27))
        t.raw("")
    t.done()
    return noise(p, "# Programme Force - Cycle 1", "1RM actuels : squat 140 kg, développé couché 100 kg",
                 "Semaine 2 = deload, on garde la technique", "Échauffement : 10 min vélo + 3 séries progressives (à ignorer)",
                 "Total semaine : 41 séries", "Total semaine : 27 séries", "Jour 1 - Squat", "Jour 2 - Bench")

# ---------------- N04 CSV ; et virgule décimale (export d'app, 1 série/ligne) ----------------
def N04():
    p = Prog("N04", "neutre", "csv", "Export app de suivi - CSV Excel FR",
             ["une série par ligne", "séparateur ; et virgule décimale", "lignes d'échauffement W", "lignes de volume total", "colonne RIR à ignorer"],
             "Export CSV d'une app de suivi fictive, locale FR")
    plan = [("Haut", [("Développé couché", [8, 8, 6], 80), ("Rowing barre", [10, 10, 10], 70), ("Développé militaire", [8, 8, 8], 42.5),
                      ("Tractions", [8, 7, 6], None), ("Curl biceps", [12, 10, 10], 27.5)]),
            ("Bas", [("Squat", [6, 6, 6, 6], 100), ("Romanian deadlift", [8, 8, 8], 90), ("Presse à cuisses", [12, 12, 12], 180), ("Leg curl", [12, 12, 10], 40)])]
    f = lambda x: f"{x:g}".replace(".", ",")
    L = ["Date;Semaine;Jour;Exercice;Série;Reps;Charge (kg);RIR"]
    dates = [["06/10/2026", "08/10/2026"], ["13/10/2026", "15/10/2026"]]
    for w in range(2):
        for d, (day, exs) in enumerate(plan):
            vol = 0
            for i, (name, reps, load) in enumerate(exs):
                ld = None if load is None else load + 2.5 * w
                if i == 0: L.append(f"{dates[w][d]};S{w+1};{day};{name} (échauffement);W;10;{f(ld*0.5) if ld else ''};")
                for s, r in enumerate(reps, 1):
                    L.append(f"{dates[w][d]};S{w+1};{day};{name};{s};{r};{f(ld) if ld is not None else ''};{2 if s < len(reps) else 1}")
                    vol += r * (ld or 0)
                    p.ex(w, d, name, [g(1, r, kg(ld) if ld is not None else None)])
            L.append(f"{dates[w][d]};S{w+1};{day};Volume total;;;{f(vol)};")
    p.text = "\n".join(L) + "\n"
    return noise(p, "squat (échauffement)", "développé couché (échauffement)", "volume total",
                 *[f"{e[0]} (échauffement)" for _, ex in plan for e in ex])

# ---------------- N05 CSV , et point, lb, 5/3/1 ----------------
def N05():
    p = Prog("N05", "neutre", "csv", "5/3/1 BBB - CSV anglais",
             ["lb", "AMRAP '5+'", "séries de montée une par ligne", "champ entre guillemets avec virgule", "BW", "lignes warmup/total"],
             "CSV d'un template 5/3/1 Boring But Big (fictif)")
    L = ["Day,Exercise,Sets,Reps,Weight,Notes"]
    def R(day, d, name, sets, reps, w, note="", groups=None, **kw):
        L.append(f'{day},{name},{sets},{reps},{w},{note}')
        p.ex(0, d, name, groups, **kw)
    top = lambda day, d, name, ws: [R(day, d, name, 1, r, f"{w}lb", n, [g(1, 5, lb(w), amrap=(r == "5+"))])
                                    for (r, w, n) in ws]
    L.append('Mon,Warmup,2,10,bar,"empty bar, then 95lb"')
    top("Mon", 0, "Squat", [("5", 165, "first set"), ("5", 190, ""), ("5+", 215, '"AMRAP, leave 1 in the tank"')])
    R("Mon", 0, "Squat BBB", 5, 10, "135lb", "supplemental", [g(5, 10, lb(135))])
    R("Mon", 0, "Leg curl", 4, 12, "70lb", "", [g(4, 12, lb(70))])
    R("Mon", 0, "Ab wheel", 4, 15, "BW", "", [g(4, 15)])
    L.append('Mon,Total reps,,,,"~120, all sets"')
    L.append('Wed,Warmup,2,10,bar,"empty bar, then 65lb"')
    top("Wed", 1, "Bench press", [("5", 105, "first set"), ("5", 120, ""), ("5+", 135, '"AMRAP, no spotter so careful"')])
    R("Wed", 1, "Bench BBB", 5, 10, "85lb", "supplemental", [g(5, 10, lb(85))])
    R("Wed", 1, "DB row", 5, 10, "60lb", '"each arm, dumbbells"', [g(5, 10, lb(60))], side=True)
    R("Wed", 1, "Chin-up", 5, 10, "BW", "", [g(5, 10)])
    L.append('Fri,Warmup,2,5,bar,"empty bar, then 135lb"')
    top("Fri", 2, "Deadlift", [("5", 225, "first set"), ("5", 255, ""), ("5+", 290, '"AMRAP, reset each rep"')])
    R("Fri", 2, "DL BBB", 5, 10, "185lb", "supplemental", [g(5, 10, lb(185))])
    R("Fri", 2, "Hanging leg raise", 5, 10, "BW", "", [g(5, 10)])
    R("Fri", 2, "Face pull", 5, 15, "40lb", "", [g(5, 15, lb(40))])
    L.append('Fri,Total reps,,,,"~135, all sets"')
    p.text = "\n".join(L) + "\n"
    return noise(p, "warmup", "total reps")

# ---------------- xlsx helper ----------------
def sheet(name, rows, merges=(), fmt=None, fill=None): return {"name": name, "rows": rows, "merges": list(merges), "fmt": fmt or {}, "fill": fill or {}}

# ---------------- N06 xlsx fusions + couleurs + onglets ----------------
def N06():
    p = Prog("N06", "neutre", "xlsx", "Hypertrophie Léa - 2 séances",
             ["cellules fusionnées (titre, blocs verticaux)", "couleurs de fond", "onglet Légende", "ligne de volume", "fourchette de reps 6-8", "tempo en remarque", "unilatéral par jambe"],
             "Classeur Excel d'une coach fictive (Léa Dumont)")
    H = ["Bloc", "Exercice", "Séries", "Reps", "Charge (kg)", "Remarques"]
    A = [["PROGRAMME HYPERTROPHIE - Séance A (haut du corps)", "", "", "", "", ""],
         ["Coach : Léa Dumont", "", "", "", "", ""], H,
         ["Force", "Développé couché barre", 4, "6-8", 80, ""],
         ["", "Tractions prise large", 4, 8, None, "poids du corps"],
         ["", "Rowing Yates", 3, 10, 60, ""],
         ["Hypertrophie", "Développé incliné haltères", 3, 10, 30, ""],
         ["", "Élévations latérales", 4, 15, 10, ""],
         ["", "Oiseau poulie", 3, 15, 15, ""],
         ["", "Curl incliné", 3, 12, 12, ""],
         ["", "Volume séance : 24 séries", "", "", "", ""]]
    B = [["PROGRAMME HYPERTROPHIE - Séance B (bas du corps)", "", "", "", "", ""],
         ["Coach : Léa Dumont", "", "", "", "", ""], H,
         ["Force", "Squat", 4, "6-8", 100, "tempo 3-1-X-0"],
         ["", "RDL", 3, 8, 90, ""],
         ["Hypertrophie", "Presse à cuisses", 3, 12, 200, ""],
         ["", "Fentes marchées", 3, 10, 24, "par jambe"],
         ["", "Leg curl assis", 3, 12, 45, ""],
         ["", "Mollets debout", 4, 15, 80, ""],
         ["", "Volume séance : 20 séries", "", "", "", ""]]
    L = [["Légende", ""], ["Jaune = bloc force", ""], ["Bleu = bloc hypertrophie", ""], ["Repos : 2 min force, 90 s hypertrophie", ""]]
    p.xlsx = [sheet("Séance A", A, ["A1:F1", "A2:F2", "A4:A6", "A7:A10"], fill={(1, 1): "FFC000", (3, 1): "D9D9D9", (4, 1): "FFF2CC", (7, 1): "DDEBF7"}),
              sheet("Séance B", B, ["A1:F1", "A2:F2", "A4:A5", "A6:A9"], fill={(1, 1): "FFC000", (3, 1): "D9D9D9", (4, 1): "FFF2CC", (6, 1): "DDEBF7"}),
              sheet("Légende", L)]
    for r in ([("Développé couché barre", [g(4, "6-8", kg(80))], {}), ("Tractions prise large", [g(4, 8)], {}), ("Rowing Yates", [g(3, 10, kg(60))], {}),
               ("Développé incliné haltères", [g(3, 10, kg(30))], {}), ("Élévations latérales", [g(4, 15, kg(10))], {}),
               ("Oiseau poulie", [g(3, 15, kg(15))], {}), ("Curl incliné", [g(3, 12, kg(12))], {})]):
        p.ex(0, 0, r[0], r[1])
    for r in ([("Squat", [g(4, "6-8", kg(100))], {"tempo": "3-1-X-0"}), ("RDL", [g(3, 8, kg(90))], {}), ("Presse à cuisses", [g(3, 12, kg(200))], {}),
               ("Fentes marchées", [g(3, 10, kg(24))], {"side": True}), ("Leg curl assis", [g(3, 12, kg(45))], {}), ("Mollets debout", [g(4, 15, kg(80))], {})]):
        p.ex(0, 1, r[0], r[1], **r[2])
    return noise(p, "PROGRAMME HYPERTROPHIE - Séance A (haut du corps)", "PROGRAMME HYPERTROPHIE - Séance B (bas du corps)", "Coach : Léa Dumont",
                 "Volume séance : 24 séries", "Volume séance : 20 séries", "Légende", "Jaune = bloc force", "Bleu = bloc hypertrophie",
                 "Repos : 2 min force, 90 s hypertrophie", "Force", "Hypertrophie")

# ---------------- N07 xlsx semaines en colonnes ----------------
def N07():
    p = Prog("N07", "neutre", "xlsx", "Cycle force 4 semaines - semaines en colonnes",
             ["semaines en colonnes (S1..S4)", "prescription entière dans une cellule", "×, x, virgule décimale, +lest", "S4 deload", "titre fusionné", "note de bas de page"],
             "Classeur Excel d'un cycle de force, coach fictif")
    data = {
        "Jour A - Push": [
            ("Dév couché", ["4x8 @70kg", "4x8 @72,5kg", "4x6 @77,5kg", "3x8 @55kg"], [[g(4, 8, kg(70))], [g(4, 8, kg(72.5))], [g(4, 6, kg(77.5))], [g(3, 8, kg(55))]]),
            ("Dév militaire", ["3×8 @40kg", "3×8 @42,5kg", "3×6 @45kg", "2×8 @32,5kg"], [[g(3, 8, kg(40))], [g(3, 8, kg(42.5))], [g(3, 6, kg(45))], [g(2, 8, kg(32.5))]]),
            ("Dips", ["4 x 8 +10kg", "4 x 8 +12,5kg", "4 x 6 +15kg", "3 x 8"], [[g(4, 8, lest(10))], [g(4, 8, lest(12.5))], [g(4, 6, lest(15))], [g(3, 8)]])],
        "Jour B - Pull et Legs": [
            ("Squat", ["5x5 @100kg", "5x5 @105kg", "5x3 @115kg", "3x5 @80kg"], [[g(5, 5, kg(100))], [g(5, 5, kg(105))], [g(5, 3, kg(115))], [g(3, 5, kg(80))]]),
            ("SDT", ["3x5 @120kg", "3x5 @127,5kg", "3x3 @140kg", "2x5 @100kg"], [[g(3, 5, kg(120))], [g(3, 5, kg(127.5))], [g(3, 3, kg(140))], [g(2, 5, kg(100))]]),
            ("Tractions", ["5x5 +5kg", "5x5 +7,5kg", "5x4 +10kg", "3x5"], [[g(5, 5, lest(5))], [g(5, 5, lest(7.5))], [g(5, 4, lest(10))], [g(3, 5)]])]}
    sh = []
    for d, (name, exs) in enumerate(data.items()):
        rows = [["Cycle force - 4 semaines", "", "", "", ""], ["Exercice", "S1", "S2", "S3", "S4 deload"]]
        for ex, cells, gs in exs:
            rows.append([ex] + cells)
            for w in range(4): p.ex(w, d, ex, gs[w])
        rows.append(["S4 = deload (volume réduit)", "", "", "", ""])
        sh.append(sheet(name, rows, ["A1:E1"], fill={(2, c): "BDD7EE" for c in range(1, 6)}))
    p.xlsx = sh
    return noise(p, "Cycle force - 4 semaines", "Exercice", "S4 = deload (volume réduit)")

# ---------------- N08 xlsx 12 semaines en % ----------------
def N08():
    p = Prog("N08", "neutre", "xlsx", "Plan 12 semaines en % du 1RM",
             ["% stocké en fraction (0.725)", "kg ET % sur le squat", "1RM annoncé en haut", "deload S4 et S8", "colonne Remarque"],
             "Plan linéaire 12 semaines squat/bench, coach fictif")
    sq_sr = [(5, 5), (5, 5), (5, 4), (3, 5), (5, 4), (5, 3), (4, 3), (3, 5), (4, 3), (3, 3), (3, 2), (2, 2)]
    sq_p = [.70, .725, .75, .60, .75, .775, .80, .60, .825, .85, .875, .90]
    bn_sr = [(4, 8), (4, 8), (4, 6), (3, 6), (4, 6), (4, 5), (4, 4), (3, 6), (4, 4), (3, 3), (3, 2), (2, 2)]
    bn_p = [.65, .675, .70, .55, .70, .725, .75, .55, .775, .80, .825, .85]
    rows = [["Plan 12 semaines - Squat / Bench", "", "", "", "", "", "", "", ""],
            ["1RM Squat (kg)", 140, "1RM Bench (kg)", 100, "", "", "", "", ""], [""] * 9,
            ["Sem", "Squat S", "Squat R", "Squat %", "Squat kg", "Bench S", "Bench R", "Bench %", "Remarque"]]
    fmt = {}
    for w in range(12):
        sq_kg = round(140 * sq_p[w], 1)
        rem = {3: "Deload", 7: "Deload", 11: "Pic - viser une belle top série"}.get(w, "")
        rows.append([f"S{w+1}", sq_sr[w][0], sq_sr[w][1], sq_p[w], sq_kg, bn_sr[w][0], bn_sr[w][1], bn_p[w], rem])
        fmt[(5 + w, 4)] = "0.0%"; fmt[(5 + w, 8)] = "0.0%"
        p.ex(w, 0, "Squat", [g(sq_sr[w][0], sq_sr[w][1], f"{sq_kg:g} kg · {sq_p[w]*100:g} %")])
        p.ex(w, 0, "Bench", [g(bn_sr[w][0], bn_sr[w][1], f"{bn_p[w]*100:g} %")])
    p.xlsx = [sheet("Plan", rows, ["A1:I1"], fmt=fmt)]
    return noise(p, "Plan 12 semaines - Squat / Bench", "1RM Squat (kg)", "1RM Bench (kg)", "Deload", "Pic - viser une belle top série")

# ---------------- N09 Sheet : cases à cocher ----------------
def N09():
    p = Prog("N09", "neutre", "sheet", "Suivi Sheet avec cases à cocher",
             ["colonne Fait TRUE/FALSE", "jour affiché seulement sur la 1re ligne du jour", "virgule décimale 62,5", "onglet par semaine", "ligne TOTAL et légende"],
             "Google Sheet partagé coach/client fictifs")
    H = ["Jour", "Exercice", "Séries", "Reps", "Charge (kg)", "Fait", "Notes"]
    days = [("Lundi - Push", [("Développé couché", 4, 8, ["62,5", "65"], 62.5, 65, "facile, +2,5 la semaine prochaine"),
                              ("Écartés poulie", 3, 12, ["15", "15"], 15, 15, ""),
                              ("Développé militaire haltères", 3, 10, ["20", "22,5"], 20, 22.5, ""),
                              ("Triceps corde", 3, 12, ["25", "25"], 25, 25, "")]),
            ("Mercredi - Pull", [("Tractions", 4, 6, ["", ""], None, None, "7 reps en semaine 2"),
                                 ("Rowing barre", 4, 8, ["60", "62,5"], 60, 62.5, ""),
                                 ("Curl marteau", 3, 12, ["14", "14"], 14, 14, ""),
                                 ("Face pull", 3, 15, ["22,5", "22,5"], 22.5, 22.5, "")])]
    sheets = []
    for w in range(2):
        rows = [H]
        for d, (dn, exs) in enumerate(days):
            for i, (name, s, r, loads, l1, l2, note) in enumerate(exs):
                reps = r + (1 if (w == 1 and name == "Tractions") else 0)
                ld = [l1, l2][w]
                rows.append([dn if i == 0 else "", name, str(s), str(reps), loads[w], "TRUE" if w == 0 else "FALSE", note if w == 0 else ""])
                p.ex(w, d, name, [g(s, reps, kg(ld) if ld is not None else None)])
        rows.append(["", "TOTAL séries", "28" if w == 0 else "28", "", "", "", ""])
        rows.append(["Légende : Fait = case cochée quand la séance est terminée", "", "", "", "", "", ""])
        sheets.append({"name": f"Semaine {w+1}", "rows": rows})
    p.sheets = sheets
    return noise(p, "TOTAL séries", "Légende : Fait = case cochée quand la séance est terminée", "Lundi - Push", "Mercredi - Pull")

# ---------------- N10 Sheet RPE/tempo/unilatéral/repos ----------------
def N10():
    p = Prog("N10", "neutre", "sheet", "Sheet RPE / tempo / repos",
             ["colonne Repos '3:00' (pas des reps)", "RPE simple et fourchette 8-9", "tempo 3-1-X-0", "'3x10 / jambe' unilatéral", "% et kg mélangés", "lignes de jour et légende"],
             "Google Sheet d'un coach fictif, 3 jours")
    rows = [["1RM : squat 140 / deadlift 170 / bench 100", "", "", "", "", "", ""],
            ["Exercice", "Séries x Reps", "Charge", "RPE", "Tempo", "Repos", "Notes"],
            ["JOUR 1 - Jambes", "", "", "", "", "", ""]]
    def add(d, name, sr, ch, rpe, tempo, rest, notes, groups, **kw):
        rows.append([name, sr, ch, rpe, tempo, rest, notes]); p.ex(0, d, name, groups, rpe=(rpe or None), tempo=(tempo or None), **kw)
    add(0, "Squat", "4x6", "80%", "7", "3-1-X-0", "3:00", "", [g(4, 6, pct(80))])
    add(0, "RDL", "3x8", "90", "8", "", "2:30", "", [g(3, 8, kg(90))])
    add(0, "Fentes bulgares", "3x10 / jambe", "20", "", "", "1:30", "", [g(3, 10, kg(20))], side=True)
    add(0, "Leg curl couché", "3x12", "35", "9", "2-0-1-0", "1:30", "", [g(3, 12, kg(35))])
    rows.append(["JOUR 2 - Haut", "", "", "", "", "", ""])
    add(1, "Développé couché", "5x5", "77,5", "8", "", "3:00", "", [g(5, 5, kg(77.5))])
    add(1, "Tractions", "4x6", "", "8-9", "", "2:00", "", [g(4, 6)])
    add(1, "Dips", "3x10", "+10 kg", "", "", "2:00", "", [g(3, 10, lest(10))])
    add(1, "Rowing haltère", "3x10 / bras", "30", "", "", "1:30", "", [g(3, 10, kg(30))], side=True)
    rows.append(["JOUR 3 - Full body", "", "", "", "", "", ""])
    add(2, "Soulevé de terre", "3x3", "85%", "8", "", "4:00", "", [g(3, 3, pct(85))])
    add(2, "Presse à cuisses", "3x12", "180", "", "", "2:00", "", [g(3, 12, kg(180))])
    add(2, "Hip thrust", "3x10", "100", "", "", "2:00", "", [g(3, 10, kg(100))])
    add(2, "Gainage latéral", "3x30 s / côté", "", "", "", "1:00", "", [g(3, "30 s")], side=True)
    add(2, "Mollets debout", "4x15", "60", "", "", "1:00", "", [g(4, 15, kg(60))])
    rows.append(["Légende : RPE = effort perçu sur 10, Repos = pause entre séries (min:s)", "", "", "", "", "", ""])
    p.sheets = [{"name": "Programme", "rows": rows}]
    return noise(p, "1RM : squat 140 / deadlift 170 / bench 100", "JOUR 1 - Jambes", "JOUR 2 - Haut", "JOUR 3 - Full body",
                 "Légende : RPE = effort perçu sur 10, Repos = pause entre séries (min:s)")

# ---------------- N11 Sheet powerlifting top set / back-off ----------------
def N11():
    p = Prog("N11", "neutre", "sheet", "Powerlifting top set + back-off",
             ["top set et back-off = 2 entrées", "RPE en fourchette 8-9", "onglet par semaine", "ligne tonnage", "légende"],
             "Google Sheet d'un powerlifter fictif (Yanis)")
    H = ["Mouvement", "Type", "Séries x reps", "Charge (kg)", "RPE", "Notes"]
    wk = [dict(sq=(140, 120), pb=80, bn=(95, 82.5), dl=(180, 150), rw=65),
          dict(sq=(142.5, 122.5), pb=82.5, bn=(97.5, 85), dl=(185, 155), rw=67.5)]
    sheets = []
    for w in range(2):
        c = wk[w]
        f = lambda x: f"{x:g}".replace(".", ",")
        rows = [H, ["JOUR 1", "", "", "", "", ""],
                ["Squat", "Top set", "1x3", f(c['sq'][0]), "8-9", "arrêter si la vitesse chute"],
                ["Squat", "Back-off", "3x5", f(c['sq'][1]), "7", ""],
                ["Pause bench", "Volume", "4x4", f(c['pb']), "7", "pause 2 s"],
                ["Rowing barre", "Accessoire", "4x8", f(c['rw']), "", ""],
                ["JOUR 2", "", "", "", "", ""],
                ["Bench", "Top set", "1x3", f(c['bn'][0]), "8-9", ""],
                ["Bench", "Back-off", "3x6", f(c['bn'][1]), "7", ""],
                ["Soulevé de terre", "Top set", "1x2", f(c['dl'][0]), "8-9", ""],
                ["Soulevé de terre", "Back-off", "2x5", f(c['dl'][1]), "7", ""],
                ["Tractions", "Accessoire", "4x6", "", "", "poids du corps"],
                ["Tonnage séance", "", "", "", "", ""],
                ["Légende : RPE 8-9 = 1 à 2 reps en réserve", "", "", "", "", ""]]
        sheets.append({"name": f"Sem {w+1}", "rows": rows})
        p.ex(w, 0, "Squat", [g(1, 3, kg(c['sq'][0]))], rpe="8-9")
        p.ex(w, 0, "Squat", [g(3, 5, kg(c['sq'][1]))], rpe="7")
        p.ex(w, 0, "Pause bench", [g(4, 4, kg(c['pb']))], rpe="7")
        p.ex(w, 0, "Rowing barre", [g(4, 8, kg(c['rw']))])
        p.ex(w, 1, "Bench", [g(1, 3, kg(c['bn'][0]))], rpe="8-9")
        p.ex(w, 1, "Bench", [g(3, 6, kg(c['bn'][1]))], rpe="7")
        p.ex(w, 1, "Soulevé de terre", [g(1, 2, kg(c['dl'][0]))], rpe="8-9")
        p.ex(w, 1, "Soulevé de terre", [g(2, 5, kg(c['dl'][1]))], rpe="7")
        p.ex(w, 1, "Tractions", [g(4, 6)])
    p.sheets = sheets
    return noise(p, "JOUR 1", "JOUR 2", "Tonnage séance", "Légende : RPE 8-9 = 1 à 2 reps en réserve")

# ---------------- N12 xlsx un onglet par jour, drop sets ----------------
def N12():
    p = Prog("N12", "neutre", "xlsx", "Bodybuilding 3 jours - drop sets",
             ["drop set 12/10/8 avec charges dégressives", "superset A1/A2", "AMRAP pompes", "'3 x max'", "onglet Résumé à ignorer", "cellules fusionnées et fond"],
             "Classeur Excel d'un coach fictif (Sofiane)")
    H = ["Exercice", "Prescription", "Charge (kg)", "Notes"]
    def day(title, body): return [[title, "", "", ""], ["Coach Sofiane - repos 90 s entre séries", "", "", ""], H] + body
    D1 = day("LUNDI - Poitrine / Dos", [
        ["Développé couché", "4x10", 80, ""],
        ["A1 Rowing 1 bras", "3x12", 30, "par bras"],
        ["A2 Pompes", "1xAMRAP", None, "enchaîné sans repos"],
        ["Pec deck (drop set)", "12 / 10 / 8", "45 → 35 → 25", "sans repos entre les paliers"],
        ["Tractions", "3 x max", None, ""]])
    D2 = day("MARDI - Jambes", [
        ["Squat", "4x8", 100, ""],
        ["Presse à cuisses", "3x15", 200, ""],
        ["Leg extension (drop set)", "15 / 12 / 10", "60 → 50 → 40", ""],
        ["RDL", "3x10", 80, ""],
        ["Mollets debout", "4x20", 80, ""]])
    D3 = day("JEUDI - Épaules / Bras", [
        ["Développé militaire", "4x8", 45, ""],
        ["Élévations latérales", "4x15", 10, ""],
        ["Curl barre", "3x10", 30, ""],
        ["Barre front", "3x10", 35, ""],
        ["Gainage", "3x60s", None, ""]])
    R = [["Résumé de la semaine", "", "", ""], ["Séries totales : 55", "", "", ""], ["Séances : 3", "", "", ""]]
    p.xlsx = [sheet("Lundi", D1, ["A1:D1", "A2:D2"], fill={(1, 1): "C6E0B4", (3, 1): "D9D9D9"}),
              sheet("Mardi", D2, ["A1:D1", "A2:D2"], fill={(1, 1): "F8CBAD", (3, 1): "D9D9D9"}),
              sheet("Jeudi", D3, ["A1:D1", "A2:D2"], fill={(1, 1): "BDD7EE", (3, 1): "D9D9D9"}),
              sheet("Résumé", R)]
    p.ex(0, 0, "Développé couché", [g(4, 10, kg(80))])
    p.ex(0, 0, "Rowing 1 bras", [g(3, 12, kg(30))], side=True)
    p.ex(0, 0, "Pompes", [g(1, "max", None, amrap=True)])
    p.ex(0, 0, "Pec deck", [g(1, 12, kg(45)), g(1, 10, kg(35)), g(1, 8, kg(25))])
    p.ex(0, 0, "Tractions", [g(3, "max")])
    p.ex(0, 1, "Squat", [g(4, 8, kg(100))])
    p.ex(0, 1, "Presse à cuisses", [g(3, 15, kg(200))])
    p.ex(0, 1, "Leg extension", [g(1, 15, kg(60)), g(1, 12, kg(50)), g(1, 10, kg(40))])
    p.ex(0, 1, "RDL", [g(3, 10, kg(80))])
    p.ex(0, 1, "Mollets debout", [g(4, 20, kg(80))])
    p.ex(0, 2, "Développé militaire", [g(4, 8, kg(45))])
    p.ex(0, 2, "Élévations latérales", [g(4, 15, kg(10))])
    p.ex(0, 2, "Curl barre", [g(3, 10, kg(30))])
    p.ex(0, 2, "Barre front", [g(3, 10, kg(35))])
    p.ex(0, 2, "Gainage", [g(3, "60 s")])
    return noise(p, "LUNDI - Poitrine / Dos", "MARDI - Jambes", "JEUDI - Épaules / Bras", "Coach Sofiane - repos 90 s entre séries",
                 "Résumé de la semaine", "Séries totales : 55", "Séances : 3")

PROGS = [N01(), N02(), N03(), N04(), N05(), N06(), N07(), N08(), N09(), N10(), N11(), N12()]

# Correctif de vérité (avant gel, sans lecteur) : N04 est un export « une série par ligne » ;
# les séries consécutives d'un même exercice sont UN exercice à plusieurs groupes.
for _p in PROGS:
    if _p.id == "N04":
        _m = []
        for _t in _p.truth:
            if _m and (_m[-1]["w"], _m[-1]["d"], _m[-1]["name"]) == (_t["w"], _t["d"], _t["name"]):
                _m[-1]["groups"] += _t["groups"]
            else: _m.append(_t)
        _p.truth = _m
