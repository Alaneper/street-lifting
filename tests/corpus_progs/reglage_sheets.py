"""Lot RÉGLAGE — Sheets simulés (valeurs FORMATÉES comme l'API) + texte tabulé (8 progs)."""
from lib import *

def R19():
    p = Prog("R19", "reglage", "sheet", "Sheet anglais : onglets Week 1/2, bandeaux « Day n – Push », Weight « BW+10kg »", ["A8", "A9", "C1", "C2", "B15"], "observé (test à l'aveugle n° 4) en plus complet ; Reddit PPL/Recommended Routine (sourcé : BW)")
    H = ["Day", "Exercise", "Sets", "Reps", "Weight", "Rest", "Notes"]
    plan = [("Day 1 - Push", [("Bench Press", 4, "6-8", "80kg", "2 min", "pause at chest"), ("Overhead Press", 3, "8", "45kg", "90s", ""), ("Dips", 3, "8-10", "BW+10kg", "90s", ""), ("Tricep Pushdown", 3, "12", "25kg", "60s", "")]),
            ("Day 2 - Pull", [("Deadlift", 3, "5", "140kg", "3 min", ""), ("Pull Ups", 4, "6-8", "BW+5kg", "2 min", ""), ("Lat Pulldown", 3, "10", "60kg", "90s", ""), ("Barbell Curl", 3, "10", "30kg", "60s", "")]),
            ("Day 3 - Legs", [("Back Squat", 4, "6", "110kg", "3 min", ""), ("Leg Press", 3, "10", "200kg", "2 min", ""), ("Leg Curl", 3, "12", "45kg", "60s", ""), ("Standing Calf Raise", 4, "15", "BW", "60s", "slow")])]
    canon = {"Bench Press": "Développé couché", "Overhead Press": "Développé militaire", "Dips": "Dips", "Tricep Pushdown": "Triceps", "Deadlift": "Soulevé de terre", "Pull Ups": "Tractions",
             "Lat Pulldown": "Tirage vertical", "Barbell Curl": "Curl biceps", "Back Squat": "Squat", "Leg Press": "Presse à cuisses", "Leg Curl": "Leg curl", "Standing Calf Raise": "Mollets"}
    tabs = []
    for w in (1, 2):
        rows = [H]
        for d, (lab, exs) in enumerate(plan):
            rows.append([lab, "", "", "", "", "", ""])
            for nm, s, r, ch, rest, nt in exs:
                chv = ch
                if w == 2 and ch.endswith("kg") and "+" not in ch: chv = f"{float(ch[:-2]) + 2.5:g}kg"
                rows.append(["", nm, str(s), r, chv, rest, nt])
                load = None
                if chv.startswith("BW+"): load = lest(chv[3:-2])
                elif chv.endswith("kg"): load = kg(chv[:-2])
                p.ex(w - 1, d, nm, [g(s, r, load)], canon=canon[nm])
        tabs.append(dict(name=f"Week {w}", rows=rows))
    p.sheets = tabs
    p.note = "Titre de jour sur sa propre ligne (« Day 1 - Push »), colonne Day vide ensuite, « BW » et « BW+10kg », Rest en « 2 min »/« 90s »."
    return p

def R20():
    p = Prog("R20", "reglage", "sheet", "Sheet en locale française : « 62,5 », « 75% », repos « 3:00 », onglets S1–S3", ["A2", "E5", "C1"], "déduit de l'API Sheets (valeurs formatées selon la locale du fichier) ; mise en page type coach")
    H = ["Jour", "Exercice", "Séries", "Reps", "Charge", "%", "RPE", "Repos"]
    plan = [("Lundi", [("Squat", 4, 5, "", 75, 7, "3:00"), ("Développé couché", 4, 6, "", 72, 7, "3:00"), ("Rowing barre", 3, 10, 62.5, "", 8, "1:30"), ("Curl haltères", 3, 12, 14, "", 9, "1:00")]),
            ("Mercredi", [("Soulevé de terre", 3, 4, "", 80, 8, "4:00"), ("Développé militaire", 4, 6, 45, "", 8, "2:00"), ("Tractions lestées", 4, 6, 17.5, "", 8, "2:00")]),
            ("Vendredi", [("Squat pause", 3, 4, "", 70, 7, "3:00"), ("Développé couché pause", 4, 4, "", 78, 7, "3:00"), ("Dips", 3, 10, "", "", 8, "1:30")])]
    tabs = []
    for w in (1, 2, 3):
        rows = [H]
        for d, (jr, exs) in enumerate(plan):
            for nm, s, r, ch, pc, rp, rest in exs:
                chv = ch + 2.5 * (w - 1) if ch != "" else ""; pcv = pc + 2.5 * (w - 1) if pc != "" else ""
                rows.append([jr, nm, str(s), str(r), (f"{chv:g}".replace(".", ",") if chv != "" else ""), (f"{pcv:g}".replace(".", ",") + "%" if pcv != "" else ""), str(rp), rest])
                load = f"{pcv:g} %" if pcv != "" else (lest(chv) if nm == "Tractions lestées" else (kg(chv) if chv != "" else None))
                p.ex(w - 1, d, nm, [g(s, r, load)], rpe=str(rp))
        tabs.append(dict(name=f"S{w}", rows=rows))
    p.sheets = tabs
    p.note = "Virgule décimale, % en texte, repos en « 3:00 », jour répété sur chaque ligne, un onglet par semaine nommé S1/S2/S3."
    return p

def R21():
    p = Prog("R21", "reglage", "sheet", "Upper/Lower sur deux onglets + onglet Calculateur de macros", ["A1", "A3"], "nSuns RoflWafflez (sourcé : séances réparties sur « Upper Workouts » et « Lower Workouts », calculateur de macros)")
    H = ["Exercice", "Séries", "Reps", "Charge (kg)"]
    up = [["Upper A"], H, ["Développé couché", "4", "6", "80"], ["Rowing barre", "4", "8", "70"], ["Développé militaire", "3", "8", "45"], ["Tractions", "3", "8", ""], ["Curl barre", "3", "10", "30"], [],
          ["Upper B"], H, ["Développé incliné haltères", "4", "8", "28"], ["Tirage vertical", "4", "10", "60"], ["Dips", "3", "10", ""], ["Élévations latérales", "4", "15", "10"], ["Triceps corde", "3", "12", "25"]]
    lo = [["Lower A"], H, ["Squat", "5", "5", "110"], ["Soulevé de terre roumain", "3", "8", "100"], ["Leg curl", "3", "12", "45"], ["Mollets debout", "4", "15", "80"], [],
          ["Lower B"], H, ["Soulevé de terre", "3", "5", "140"], ["Presse à cuisses", "3", "12", "200"], ["Fentes bulgares", "3", "8", "20"], ["Hip thrust", "3", "10", "100"], ["Abdos", "3", "15", ""]]
    mac = [["CALCULATEUR DE MACROS"], ["Poids (kg)", "78"], ["Calories", "2800"], ["Protéines (g)", "160"], ["Glucides (g)", "340"], ["Lipides (g)", "80"]]
    C = {"Développé couché": "Développé couché", "Rowing barre": "Rowing", "Développé militaire": "Développé militaire", "Tractions": "Tractions", "Curl barre": "Curl biceps", "Développé incliné haltères": "Développé incliné",
         "Tirage vertical": "Tirage vertical", "Dips": "Dips", "Élévations latérales": "Élévations latérales", "Triceps corde": "Triceps", "Squat": "Squat", "Soulevé de terre roumain": "Soulevé de terre roumain",
         "Leg curl": "Leg curl", "Mollets debout": "Mollets", "Soulevé de terre": "Soulevé de terre", "Presse à cuisses": "Presse à cuisses", "Fentes bulgares": "Fentes bulgares", "Hip thrust": "Hip thrust", "Abdos": "Abdos"}
    d = -1
    for tab in (up, lo):
        for row in tab:
            if len(row) == 1: d += 1
            elif len(row) == 4 and row[0] != "Exercice": p.ex(0, d, row[0], [g(int(row[1]), row[2], kg(row[3]) if row[3] else None)], canon=C[row[0]])
    p.noise = ["calculateur", "calories", "proteines", "glucides", "lipides", "poids (kg)"]
    p.sheets = [dict(name="Upper Workouts", rows=up), dict(name="Lower Workouts", rows=lo), dict(name="Macros", rows=mac)]
    p.note = "Quatre séances sur deux onglets, titres « Upper A » (pas « Séance n »), en-tête répété, onglet Macros qui ne doit rien produire."
    return p

def R22():
    p = Prog("R22", "reglage", "sheet", "PPL américain en lb : « Sets x Reps » multi-groupes « 4×5, 1×5+ », Weight (lbs)", ["B1", "B3", "C1", "D1"], "Reddit PPL (sourcé : 1×5+, lb, exercices au choix)")
    rows = [["Weight in lbs unless noted"], ["Exercise", "Sets × Reps", "Weight (lbs)", "Notes"]]
    plan = [("Day 1 - Pull", [("Barbell Deadlift", "1×5+", 275, "", "Soulevé de terre"), ("Pull Ups", "3×8-12", "", "bodyweight", "Tractions"), ("Barbell Row", "4×5, 1×5+", 135, "", "Rowing"), ("Face Pulls", "5×15-20", 60, "", "Face pull")]),
            ("Day 2 - Push", [("Bench Press", "4×5, 1×5+", 185, "", "Développé couché"), ("Overhead Press", "3×6-8", 95, "", "Développé militaire"), ("Incline DB Press", "3×8-12", 55, "per dumbbell", "Développé incliné"), ("Triceps Pushdown", "3×8-12", 70, "", "Triceps")]),
            ("Day 3 - Legs", [("Squat (low bar)", "4×5, 1×5+", 225, "", "Squat"), ("Romanian Deadlift", "3×6-8", 185, "", "Soulevé de terre roumain"), ("Leg Press", "3×10-15", 360, "", "Presse à cuisses"), ("Calf Raises", "5×10-15", 150, "", "Mollets")])]
    for d, (lab, exs) in enumerate(plan):
        rows.append([lab])
        for nm, sr, ch, nt, cn in exs:
            rows.append([nm, sr, str(ch) if ch != "" else "", nt])
            grp = []
            for chunk in sr.split(","):
                n_, r_ = chunk.strip().split("×"); grp.append(g(int(n_), r_.rstrip("+"), lb(ch) if ch != "" else None, r_.endswith("+")))
            p.ex(0, d, nm, grp, canon=cn)
    p.noise = ["weight in lbs"]
    p.sheets = [dict(name="Routine", rows=rows)]
    p.note = "Unité lbs écrite en bandeau et dans l'en-tête « Weight (lbs) », deux groupes dans une cellule (« 4×5, 1×5+ »), fourchettes, « Squat (low bar) »."
    return p

def R23():
    p = Prog("R23", "reglage", "sheet", "GZCLP : colonne Tier T1/T2/T3, « 5x3+ », « 3x15+ », jours A1/B1/A2/B2 fusionnés", ["A8", "B1", "B18"], "GZCL (sourcé : T1/T2/T3, AMRAP, kg et lb)")
    rows = [["Day", "Tier", "Exercise", "Sets x Reps", "Weight (kg)"]]
    plan = [("A1", [("T1", "Squat", "5x3+", 100), ("T2", "Bench Press", "3x10", 60), ("T3", "Lat Pulldown", "3x15+", 40)]),
            ("B1", [("T1", "Overhead Press", "5x3+", 42.5), ("T2", "Deadlift", "3x10", 100), ("T3", "Dumbbell Row", "3x15+", 22)]),
            ("A2", [("T1", "Bench Press", "5x3+", 80), ("T2", "Squat", "3x10", 80), ("T3", "Lat Pulldown", "3x15+", 42.5)]),
            ("B2", [("T1", "Deadlift", "5x3+", 125), ("T2", "Overhead Press", "3x10", 32.5), ("T3", "Dumbbell Row", "3x15+", 24)])]
    C = {"Squat": "Squat", "Bench Press": "Développé couché", "Lat Pulldown": "Tirage vertical", "Overhead Press": "Développé militaire", "Deadlift": "Soulevé de terre", "Dumbbell Row": "Rowing"}
    for d, (lab, exs) in enumerate(plan):
        for k, (tier, nm, sr, ch) in enumerate(exs):
            rows.append([lab if k == 0 else "", tier, nm, sr, f"{ch:g}"])
            n_, r_ = sr.split("x"); p.ex(0, d, nm, [g(int(n_), r_.rstrip("+"), kg(ch), r_.endswith("+"))], canon=C[nm])
    p.sheets = [dict(name="GZCLP", rows=rows)]
    p.note = "Colonne Tier à ne pas confondre avec une série, AMRAP « 5x3+ », même exercice sur plusieurs jours avec des charges différentes."
    return p

def R24():
    p = Prog("R24", "reglage", "sheet", "PPL français sur 4 semaines : Nb séries / Nb reps, PDC, +5, Élastique", ["A8", "C1", "C2", "B15", "F3"], "observé (retours testeurs : progs perso de potes, colonnes maison) ; élastique/lest du glossaire")
    H = ["Séance", "Exo", "Nb séries", "Nb reps", "Poids", "Temps de repos", "Remarque"]
    plan = [("Push", [("Développé couché", 4, "6-8", "80", "2'", "", "Développé couché", kg(80)), ("Développé incliné haltères", 3, "10", "26", "90s", "", "Développé incliné", kg(26)), ("Dips", 3, "8-10", "+10", "90s", "", "Dips", lest(10)),
                      ("Élévations latérales", 4, "15", "9", "60s", "dernière à l'échec", "Élévations latérales", kg(9)), ("Pompes", 3, "max", "PDC", "60s", "", "Pompes", None)]),
            ("Pull", [("Tractions", 4, "6-8", "+5", "2'", "", "Tractions", lest(5)), ("Rowing haltère", 3, "10", "30", "90s", "par bras", "Rowing", kg(30)), ("Tirage vertical", 3, "10", "55", "90s", "", "Tirage vertical", kg(55)),
                      ("Face pull", 3, "15", "Élastique", "60s", "", "Face pull", "élastique"), ("Curl marteau", 3, "12", "14", "60s", "", "Curl biceps", kg(14))]),
            ("Legs", [("Squat", 4, "6", "110", "3'", "", "Squat", kg(110)), ("Soulevé de terre roumain", 3, "8", "100", "2'", "", "Soulevé de terre roumain", kg(100)), ("Fentes", 3, "10", "20", "90s", "par jambe", "Fentes", kg(20)),
                     ("Leg curl", 3, "12", "40", "60s", "", "Leg curl", kg(40)), ("Mollets debout", 4, "15", "70", "60s", "", "Mollets", kg(70))])]
    tabs = []
    for w in (1, 2, 3, 4):
        rows = [H]
        for d, (lab, exs) in enumerate(plan):
            for k, (nm, s, r, ch, rest, rem, cn, load) in enumerate(exs):
                chv = ch
                if w > 1 and ch.replace(".", "").isdigit(): chv = f"{float(ch) + 2.5 * (w - 1):g}"
                ld = load
                if w > 1 and load and load.endswith(" kg") and not load.startswith("+"): ld = kg(float(load[:-3]) + 2.5 * (w - 1))
                rows.append([lab if k == 0 else "", nm, str(s), r, chv, rest, rem])
                p.ex(w - 1, d, nm, [g(s, r, ld, r == "max")], canon=cn, side=("par" in rem))
        tabs.append(dict(name=f"Sem {w}", rows=rows))
    p.sheets = tabs
    p.note = "En-têtes maison (« Nb séries », « Nb reps », « Temps de repos »), séance seulement sur la 1re ligne, Poids = « PDC » / « +5 » / « Élastique » / vide, repos « 2' »."
    return p

def R25():
    p = Prog("R25", "reglage", "sheet", "Journal déjà rempli : colonnes Prévu / Fait / RPE / Commentaire", ["F1", "F3", "B8"], "Mignone/RTS/Bridge (sourcé : reps réalisées par série dans le même fichier)")
    rows = [["Semaine 3"], ["Lundi"], ["Exercice", "Prévu", "Fait", "RPE", "Commentaire"],
            ["Squat", "4x6 @ 100kg", "100x6 100x6 100x5 95x6", "8", "dernière série lourde"], ["Développé couché", "4x6 @ 80kg", "80x6 80x6 80x6 77.5x6", "7.5", ""],
            ["Rowing barre", "3x10 @ 65kg", "65x10 65x10 65x9", "8", ""], ["Gainage", "3x45s", "45 45 40", "", ""], [],
            ["Mercredi"], ["Exercice", "Prévu", "Fait", "RPE", "Commentaire"],
            ["Soulevé de terre", "3x5 @ 140kg", "", "", ""], ["Développé militaire", "4x6 @ 45kg", "", "", ""], ["Tractions lestées", "4x6 +15kg", "", "", ""]]
    p.ex(0, 0, "Squat", [g(4, 6, kg(100))], canon="Squat"); p.ex(0, 0, "Développé couché", [g(4, 6, kg(80))], canon="Développé couché")
    p.ex(0, 0, "Rowing barre", [g(3, 10, kg(65))], canon="Rowing"); p.ex(0, 0, "Gainage", [g(3, "45 s")], canon="Gainage")
    p.ex(0, 1, "Soulevé de terre", [g(3, 5, kg(140))], canon="Soulevé de terre"); p.ex(0, 1, "Développé militaire", [g(4, 6, kg(45))], canon="Développé militaire")
    p.ex(0, 1, "Tractions lestées", [g(4, 6, lest(15))], canon="Tractions")
    p.sheets = [dict(name="Journal", rows=rows)]
    p.note = "La colonne « Fait » contient des séries « 100x6 100x6 100x5 95x6 » qui ne doivent pas écraser le « Prévu » ; seul le lundi est rempli."
    return p

def R26():
    p = Prog("R26", "reglage", "csv", "Tableau copié d'Excel (tabulations) : jours vides, #REF!, ligne de total", ["A8", "E3", "B5"], "observé (tableaux collés depuis Excel/Sheets, retours testeurs)")
    L = ["Jour\tExercice\tSéries\tReps\tCharge\tRemarque",
         "Lundi\tSquat\t4\t6\t100\t",
         "\tDC\t4\t8\t80\tpause 2 s",
         "\tRowing barre\t4\t8\t#REF!\t",
         "\tTractions\t4\tmax\t\tlestées si 12 reps",
         "Mercredi\tSoulevé de terre\t3\t5\t140\t",
         "\tOHP\t4\t6\t45\t",
         "\tLeg curl\t3\t12\t40\t",
         "Vendredi\tSquat pause\t3\t5\t90\t",
         "\tDips\t3\t10\t\t",
         "\tCurl barre\t3\t10\t30\t",
         "TOTAL\t\t=SOMME(C2:C11)\t\t\t"]
    p.text = "\n".join(L) + "\n"
    p.ex(0, 0, "Squat", [g(4, 6, kg(100))], canon="Squat"); p.ex(0, 0, "DC", [g(4, 8, kg(80))], canon="Développé couché"); p.ex(0, 0, "Rowing barre", [g(4, 8)], canon="Rowing"); p.ex(0, 0, "Tractions", [g(4, "max", None, True)], canon="Tractions")
    p.ex(0, 1, "Soulevé de terre", [g(3, 5, kg(140))], canon="Soulevé de terre"); p.ex(0, 1, "OHP", [g(4, 6, kg(45))], canon="Développé militaire"); p.ex(0, 1, "Leg curl", [g(3, 12, kg(40))], canon="Leg curl")
    p.ex(0, 2, "Squat pause", [g(3, 5, kg(90))], canon="Squat pause"); p.ex(0, 2, "Dips", [g(3, 10)], canon="Dips"); p.ex(0, 2, "Curl barre", [g(3, 10, kg(30))], canon="Curl biceps")
    p.noise = ["total"]
    p.note = "Collé depuis Excel : jour seulement sur la 1re ligne, cellule en erreur (#REF!), ligne TOTAL avec formule, colonne Remarque."
    return p

ALL = [R19, R20, R21, R22, R23, R24, R25, R26]
