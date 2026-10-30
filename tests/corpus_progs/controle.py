"""Lot CONTRÔLE (14 progs) — écrit le 30/10/2026, GELÉ (voir CONTROLE.lock) et NON LANCÉ dans le lecteur avant l'étape 4.
Familles de mise en page volontairement différentes du lot réglage. Écrit par le même assistant que le lot réglage : moins neutre qu'un assistant séparé (limite à noter)."""
from lib import *

def C01():
    p = Prog("C01", "controle", "note", "Prog rédigée en phrases (français parlé)", ["B3", "B5", "C5"], "inventé : style message vocal retranscrit / mail de coach")
    t = TB(p)
    t.raw("Salut Alane, voilà ce que je te propose pour la semaine.").raw()
    t.day("Lundi, haut du corps.")
    t.exo("Développé couché, 4 séries de 6 à 80 kilos.", "Développé couché", [g(4, 6, kg(80))], canon="Développé couché")
    t.exo("Rowing barre, 4 séries de 8 à 70 kilos.", "Rowing barre", [g(4, 8, kg(70))], canon="Rowing")
    t.exo("Développé militaire, 3 séries de 8 à 40 kilos.", "Développé militaire", [g(3, 8, kg(40))], canon="Développé militaire")
    t.exo("Tractions, 4 séries de 6 avec 10 kilos de lest.", "Tractions", [g(4, 6, lest(10))], canon="Tractions")
    t.exo("Curl biceps, 3 séries de 12 à 15 kilos.", "Curl biceps", [g(3, 12, kg(15))], canon="Curl biceps").raw()
    t.day("Mercredi, bas du corps.")
    t.exo("Squat, 5 séries de 5 à 110 kilos.", "Squat", [g(5, 5, kg(110))], canon="Squat")
    t.exo("Soulevé de terre roumain, 3 séries de 8 à 100 kilos.", "Soulevé de terre roumain", [g(3, 8, kg(100))], canon="Soulevé de terre roumain")
    t.exo("Fentes marchées, 3 séries de 10 avec 20 kilos dans chaque main.", "Fentes marchées", [g(3, 10, kg(20))], canon="Fentes")
    t.exo("Leg curl, 3 séries de 12 à 40 kilos.", "Leg curl", [g(3, 12, kg(40))], canon="Leg curl")
    t.exo("Mollets debout, 4 séries de 15 à 70 kilos.", "Mollets debout", [g(4, 15, kg(70))], canon="Mollets").raw()
    t.day("Vendredi, full body léger.")
    t.exo("Soulevé de terre, 3 séries de 3 à 150 kilos.", "Soulevé de terre", [g(3, 3, kg(150))], canon="Soulevé de terre")
    t.exo("Dips, 3 séries de 10.", "Dips", [g(3, 10)], canon="Dips")
    t.exo("Face pull, 3 séries de 15 à 20 kilos.", "Face pull", [g(3, 15, kg(20))], canon="Face pull")
    t.raw().raw("Dis-moi comment ça se passe. À bientôt !")
    p.noise = ["a bientot", "dis-moi"]
    p.note = "Phrases complètes, « kilos », « avec 10 kilos de lest », « dans chaque main », salutations autour."
    return t.done()

def C02():
    p = Prog("C02", "controle", "note", "Export d'une app de suivi (une ligne par série)", ["B8", "A9"], "format d'export type Strong/Hevy (cité dans « Plus tard » de la feuille de route) — contenu inventé")
    t = TB(p)
    def block(name, canon, sets, **kw):
        t.raw(name)
        for i, (w_, r_) in enumerate(sets, 1): t.raw(f"Set {i}: {w_} kg × {r_}")
        groups = [g(1, r_, kg(w_)) for w_, r_ in sets]
        p.ex(t.w, max(t.d, 0), name.split(" (")[0], groups, canon=canon, **kw)
    t.day("Push Day – 28 oct. 2026")
    block("Bench Press (Barbell)", "Développé couché", [(80, 8), (80, 8), (82.5, 6), (82.5, 6)])
    block("Overhead Press (Barbell)", "Développé militaire", [(45, 8), (45, 7), (45, 6)])
    block("Incline Dumbbell Press", "Développé incliné", [(28, 10), (28, 10), (26, 12)])
    block("Triceps Pushdown (Cable)", "Triceps", [(30, 12), (30, 12), (27.5, 15)])
    t.raw()
    t.day("Pull Day – 30 oct. 2026")
    block("Deadlift (Barbell)", "Soulevé de terre", [(140, 5), (140, 5), (150, 3), (150, 3)])
    block("Pull Up (Weighted)", "Tractions", [(10, 8), (10, 7), (10, 6)])
    block("Bent Over Row (Barbell)", "Rowing", [(70, 8), (70, 8), (70, 8)])
    block("Hammer Curl (Dumbbell)", "Curl biceps", [(16, 12), (16, 10), (14, 12)])
    p.note = "Une ligne par série « Set 2: 80 kg × 8 », nom suivi de « (Barbell) », date dans le titre du jour. Vérité : chaque série garde sa charge (pull-up lesté = ici affichée en kg ; lest attendu +10 kg)."
    for tr in p.truth:
        if tr["name"] == "Pull Up":
            tr["groups"] = [[1, "8", "+10 kg", False], [1, "7", "+10 kg", False], [1, "6", "+10 kg", False]]
    return t.done()

def C03():
    p = Prog("C03", "controle", "note", "GZCL en anglais, lignes « T1: / T2: / T3: », AMRAP en toutes lettres", ["B1", "B18", "C2"], "GZCL (sourcé : T1/T2/T3, AMRAP, « 1-2 reps in the tank »)")
    t = TB(p)
    t.week("WEEK 1")
    t.day("Day 1")
    t.exo("T1: Squat 5x3+ @ 100kg", "Squat", [g(5, 3, kg(100), True)], canon="Squat")
    t.exo("T2: Bench Press 3x10 @ 60kg", "Bench Press", [g(3, 10, kg(60))], canon="Développé couché")
    t.exo("T3: Lat Pulldown 3x15+ @ 45kg (last set AMRAP)", "Lat Pulldown", [g(3, 15, kg(45), True)], canon="Tirage vertical")
    t.day("Day 2")
    t.exo("T1: Overhead Press 5x3+ @ 42.5kg", "Overhead Press", [g(5, 3, kg(42.5), True)], canon="Développé militaire")
    t.exo("T2: Deadlift 3x10 @ 100kg", "Deadlift", [g(3, 10, kg(100))], canon="Soulevé de terre")
    t.exo("T3: Dumbbell Row 3x15+ @ 22kg (last set AMRAP)", "Dumbbell Row", [g(3, 15, kg(22), True)], canon="Rowing")
    t.day("Day 3")
    t.exo("T1: Bench Press 5x3+ @ 80kg", "Bench Press", [g(5, 3, kg(80), True)], canon="Développé couché")
    t.exo("T2: Squat 3x10 @ 80kg", "Squat", [g(3, 10, kg(80))], canon="Squat")
    t.exo("T3: Lat Pulldown 3x15+ @ 47.5kg (last set AMRAP)", "Lat Pulldown", [g(3, 15, kg(47.5), True)], canon="Tirage vertical")
    t.week("WEEK 2")
    t.day("Day 1")
    t.exo("T1: Squat 5x3+ @ 102.5kg", "Squat", [g(5, 3, kg(102.5), True)], canon="Squat")
    t.exo("T2: Bench Press 3x10 @ 62.5kg", "Bench Press", [g(3, 10, kg(62.5))], canon="Développé couché")
    t.exo("T3: Lat Pulldown 3x15+ @ 47.5kg (last set AMRAP)", "Lat Pulldown", [g(3, 15, kg(47.5), True)], canon="Tirage vertical")
    p.note = "Préfixes « T1: », « Week », « last set AMRAP » entre parenthèses, point décimal."
    return t.done()

def C04():
    p = Prog("C04", "controle", "xlsx", "6 semaines type Candito : « Sets x Reps » + « %1RM » en deux colonnes", ["A2", "A4", "B2", "C1"], "Candito 6 semaines / Texas Method (sourcé : 5×5, 2×5, 1×5, % du 1RM, lundi-mercredi-vendredi)")
    rows = [["Semaine", "Jour", "Mouvement", "Sets x Reps", "%1RM"]]; merges = []
    sched = {1: [("Lundi", [("Squat", "5x5", 70), ("Développé couché", "5x5", 70), ("Rowing barre", "4x8", "")]), ("Mercredi", [("Squat", "2x5", 62), ("Développé militaire", "3x6", 65), ("Tractions", "3x8", "")]), ("Vendredi", [("Squat", "1x5", 75), ("Développé couché", "1x5", 75), ("Soulevé de terre", "1x5", 75)])],
             2: [("Lundi", [("Squat", "5x5", 72), ("Développé couché", "5x5", 72), ("Rowing barre", "4x8", "")]), ("Mercredi", [("Squat", "2x5", 64), ("Développé militaire", "3x6", 67), ("Tractions", "3x8", "")]), ("Vendredi", [("Squat", "1x5", 78), ("Développé couché", "1x5", 78), ("Soulevé de terre", "1x5", 78)])]}
    C = {"Squat": "Squat", "Développé couché": "Développé couché", "Rowing barre": "Rowing", "Développé militaire": "Développé militaire", "Tractions": "Tractions", "Soulevé de terre": "Soulevé de terre"}
    for w, days in sched.items():
        r0w = len(rows) + 1
        for d, (jr, exs) in enumerate(days):
            r0 = len(rows) + 1
            for k, (nm, sr, pc_) in enumerate(exs):
                rows.append([f"Semaine {w}" if (d == 0 and k == 0) else "", jr if k == 0 else "", nm, sr, f"{pc_}%" if pc_ != "" else ""])
                a, b = sr.split("x"); p.ex(w - 1, d, nm, [g(int(a), b, pct(pc_) if pc_ != "" else None)], canon=C[nm])
            merges.append(f"B{r0}:B{r0+len(exs)-1}")
        merges.append(f"A{r0w}:A{len(rows)}")
    p.xlsx = [dict(name="Programme", rows=rows, merges=merges)]
    p.note = "Semaine et jour en cellules fusionnées sur deux colonnes, en-tête « Mouvement », « %1RM »."
    return p

def C05():
    p = Prog("C05", "controle", "xlsx", "Powerbuilding : colonne Ordre A1/A2/B1, tempo, repos, deux onglets Upper/Lower", ["B17", "B13", "A3"], "Recommended Routine (sourcé : paires, tempo 10X0, repos) ; inventé")
    H = ["Ordre", "Exercice", "Séries", "Reps", "Tempo", "Repos (s)", "Charge (kg)"]
    up = [H, ["A1", "Développé couché", 4, "6-8", "3-1-1-0", 120, 80], ["A2", "Rowing barre", 4, "6-8", "2-0-1-0", 120, 70], ["B1", "Développé militaire", 3, "8-10", "2-0-1-0", 90, 42.5],
          ["B2", "Tractions", 3, "8-10", "2-1-1-0", 90, ""], ["C", "Élévations latérales", 4, "12-15", "2-0-1-1", 60, 10]]
    lo = [H, ["A", "Squat", 4, "5-6", "3-1-1-0", 180, 115], ["B1", "Soulevé de terre roumain", 3, "8", "3-0-1-0", 120, 100], ["B2", "Fentes bulgares", 3, "10", "2-0-1-0", 90, 20],
          ["C1", "Leg curl", 3, "12", "2-0-1-1", 60, 40], ["C2", "Mollets debout", 4, "15", "2-1-1-1", 60, 70]]
    cn = {"Développé couché": "Développé couché", "Rowing barre": "Rowing", "Développé militaire": "Développé militaire", "Tractions": "Tractions", "Élévations latérales": "Élévations latérales", "Squat": "Squat",
          "Soulevé de terre roumain": "Soulevé de terre roumain", "Fentes bulgares": "Fentes bulgares", "Leg curl": "Leg curl", "Mollets debout": "Mollets"}
    for d, tab in enumerate((up, lo)):
        for r in tab[1:]:
            p.ex(0, d, r[1], [g(r[2], r[3], kg(r[6]) if r[6] != "" else None)], canon=cn[r[1]], tempo=r[4])
    p.xlsx = [dict(name="Upper", rows=up), dict(name="Lower", rows=lo)]
    p.note = "Ordre en lettres/chiffres (A1/A2) à ne pas lire comme des séries, tempo à 4 chiffres, repos en secondes (pas des reps)."
    return p

def C06():
    p = Prog("C06", "controle", "xlsx", "Calisthenics par niveau : « Maintien (s) », colonne Niveau, 3 jours", ["B14", "B16", "B15"], "Recommended Routine / Liftosaur (sourcé : maintiens chronométrés, échelles) ; inventé")
    H = ["Skill", "Niveau", "Séries", "Reps", "Maintien (s)", "Lest (kg)", "Repos (s)"]
    D = [[H, ["Front lever", "Tuck", 5, "", 10, "", 90], ["Tractions", "Strict", 4, "6-8", "", 10, 120], ["Tractions australiennes", "Pieds surélevés", 3, "10-12", "", "", 60], ["Hollow hold", "Standard", 3, "", 30, "", 60]],
         [H, ["Handstand", "Au mur", 5, "", 30, "", 90], ["Dips", "Barres parallèles", 4, "6-8", "", 20, 120], ["Pompes archer", "Standard", 3, "6", "", "", 90], ["Planche lean", "Standard", 4, "", 20, "", 90]],
         [H, ["Pistol squat", "Assisté", 4, "5", "", "", 90], ["Nordic curl", "Excentrique", 3, "5", "", "", 90], ["L-sit", "Jambes pliées", 4, "", 15, "", 60], ["Muscle-up", "Strict", 5, "2", "", "", 150]]]
    cn = {"Tractions": "Tractions", "Tractions australiennes": "Rowing inversé", "Hollow hold": "Gainage", "Dips": "Dips", "Pompes archer": "Pompes", "Pistol squat": "Squat", "L-sit": "Gainage", "Muscle-up": "Muscle-up"}
    for d, tab in enumerate(D):
        for r in tab[1:]:
            reps = f"{r[4]} s" if r[4] != "" else r[3]; load = lest(r[5]) if r[5] != "" else None
            p.ex(0, d, r[0], [g(r[2], reps, load)], canon=cn.get(r[0]))
    p.xlsx = [dict(name=f"Jour {i+1}", rows=t) for i, t in enumerate(D)]
    p.note = "Reps vides quand c'est un maintien (« Maintien (s) »), « Lest (kg) » en colonne, colonne Niveau qui précise l'exercice."
    return p

def C07():
    p = Prog("C07", "controle", "xlsx", "Mise en page transposée : jours en colonnes, une feuille par semaine", ["A2", "A11"], "inventé (agenda hebdomadaire de coach)")
    tabs = []
    for w in (1, 2, 3):
        add = 2.5 * (w - 1)
        rows = [["", "Lundi", "Mercredi", "Vendredi"],
                ["Exercice 1", f"Squat 4x6 @ {100+add:g}kg", f"Soulevé de terre 3x5 @ {140+add:g}kg", f"Squat pause 3x5 @ {90+add:g}kg"],
                ["Exercice 2", f"Développé couché 4x6 @ {80+add:g}kg", f"Développé militaire 4x6 @ {45+add/2:g}kg", f"Développé couché prise serrée 4x8 @ {65+add:g}kg"],
                ["Exercice 3", "Rowing barre 4x8 @ 70kg", "Tractions 4x8", "Rowing haltère 3x10 @ 30kg"],
                ["Exercice 4", "Curl barre 3x12 @ 30kg", "Dips 3x10", "Face pull 3x15 @ 20kg"]]
        tabs.append(dict(name=f"Semaine {w}", rows=rows))
        plan = [[("Squat", 4, 6, kg(100 + add), "Squat"), ("Développé couché", 4, 6, kg(80 + add), "Développé couché"), ("Rowing barre", 4, 8, kg(70), "Rowing"), ("Curl barre", 3, 12, kg(30), "Curl biceps")],
                [("Soulevé de terre", 3, 5, kg(140 + add), "Soulevé de terre"), ("Développé militaire", 4, 6, kg(45 + add / 2), "Développé militaire"), ("Tractions", 4, 8, None, "Tractions"), ("Dips", 3, 10, None, "Dips")],
                [("Squat pause", 3, 5, kg(90 + add), "Squat pause"), ("Développé couché prise serrée", 4, 8, kg(65 + add), "Développé couché prise serrée"), ("Rowing haltère", 3, 10, kg(30), "Rowing"), ("Face pull", 3, 15, kg(20), "Face pull")]]
        for d, day in enumerate(plan):
            for nm, s, r, ld, cn in day: p.ex(w - 1, d, nm, [g(s, r, ld)], canon=cn)
    p.xlsx = tabs
    p.note = "Transposé : les jours sont des colonnes, chaque case contient « Squat 4x6 @ 100kg »."
    return p

def C08():
    p = Prog("C08", "controle", "xlsx", "Préparation semi + force : semaine fusionnée, colonne Détail libre, Distance", ["A12", "A13", "B19", "A8"], "Nick Bare (sourcé : semaine type course + muscu) ; inventé")
    rows = [["Semaine", "Jour", "Séance", "Détail", "Distance (km)"]]; merges = []
    plan = [("Lundi", "Course", "Footing", 50, 8), ("Mardi", "Force", "Squat 4x6 @ 100kg", None, None), ("Mardi", "Force", "Développé couché 4x6 @ 80kg", None, None), ("Jeudi", "Course", "Fractionné", 40, 7), ("Vendredi", "Force", "Soulevé de terre 3x5 @ 140kg", None, None), ("Samedi", "Course", "Sortie longue", 90, 15)]
    for w in (1, 2):
        r0 = len(rows) + 1
        d = -1; last = None
        for k, (jr, typ, det, mi, km) in enumerate(plan):
            if jr != last: d += 1; last = jr
            rows.append([f"Semaine {w}" if k == 0 else "", jr if (k == 0 or plan[k - 1][0] != jr) else "", typ, det if mi is None else f"{det} {mi + 5 * (w - 1)} min", (km + (w - 1)) if km else ""])
            if mi is None:
                nm, rest = det.split(" ", 1) if det.startswith("Squat") else (det.rsplit(" ", 3)[0], "")
                if det.startswith("Squat"): p.ex(w - 1, d, "Squat", [g(4, 6, kg(100))], canon="Squat")
                elif det.startswith("Développé"): p.ex(w - 1, d, "Développé couché", [g(4, 6, kg(80))], canon="Développé couché")
                else: p.ex(w - 1, d, "Soulevé de terre", [g(3, 5, kg(140))], canon="Soulevé de terre")
            else: p.ex(w - 1, d, det, [g(1, f"{mi + 5 * (w - 1)} min", f"{km + (w - 1)} km")], canon={"Footing": "Course à pied", "Fractionné": "Fractionné", "Sortie longue": "Course à pied"}[det])
        merges.append(f"A{r0}:A{len(rows)}")
    p.xlsx = [dict(name="Plan", rows=rows, merges=merges)]
    p.note = "Colonne Détail qui mélange course (« Footing 50 min ») et muscu (« Squat 4x6 @ 100kg »), distance à part, semaine fusionnée."
    return p

def C09():
    p = Prog("C09", "controle", "sheet", "Préparation type CrossFit : bloc force + conditionnement EMOM/AMRAP", ["B19", "A13"], "inventé (programmation de box)")
    rows = [["Lundi"], ["Strength: Back Squat 5x3 @ 85%"], ["Strength: Strict Pull-ups 4x6"], ["WOD: EMOM 12 min – 3 burpees + 6 kettlebell swings"], [],
            ["Mercredi"], ["Strength: Push Press 5x3 @ 75%"], ["Strength: Dips 4x8"], ["WOD: AMRAP 10 min – 5 pull-ups, 10 push-ups, 15 air squats"], [],
            ["Vendredi"], ["Strength: Deadlift 3x5 @ 80%"], ["Strength: Bench Press 4x6 @ 72%"], ["WOD: AMRAP 8 min – 10 thrusters, 10 pull-ups"]]
    d = -1
    out = [("Lundi", [("Back Squat", [g(5, 3, pct(85))], "Squat"), ("Strict Pull-ups", [g(4, 6)], "Tractions"), ("EMOM 12 min", [g(1, "12 min")], None)]),
           ("Mercredi", [("Push Press", [g(5, 3, pct(75))], "Développé militaire"), ("Dips", [g(4, 8)], "Dips"), ("AMRAP 10 min", [g(1, "10 min")], None)]),
           ("Vendredi", [("Deadlift", [g(3, 5, pct(80))], "Soulevé de terre"), ("Bench Press", [g(4, 6, pct(72))], "Développé couché"), ("AMRAP 8 min", [g(1, "8 min")], None)])]
    for d, (jr, exs) in enumerate(out):
        for nm, gr, cn in exs: p.ex(0, d, nm, gr, canon=cn)
    p.sheets = [dict(name="Semaine", rows=rows)]
    p.note = "Préfixes « Strength: / WOD: », EMOM/AMRAP en minutes, circuit en tours."
    return p

def C10():
    p = Prog("C10", "controle", "sheet", "Hypertrophie avec onglet Volume (MEV/MAV/MRV) et colonne RIR", ["A1", "C2"], "inventé (feuille type « landmarks de volume »)")
    vol = [["Groupe", "MEV", "MAV", "MRV"], ["Pectoraux", "8", "12-20", "22"], ["Dos", "10", "14-22", "25"], ["Quadriceps", "8", "12-18", "20"], ["Total séries / semaine", "", "", ""]]
    H = ["Muscle", "Exercice", "Séries", "Fourchette", "Charge", "RIR"]
    s1 = [H, ["Pectoraux", "Développé couché", "4", "6-8", "80", "2"], ["Pectoraux", "Développé incliné haltères", "3", "8-12", "28", "1"], ["Dos", "Rowing barre", "4", "8-10", "70", "2"], ["Dos", "Tirage vertical", "3", "10-12", "60", "1"], ["Triceps", "Triceps corde", "3", "12-15", "25", "0"]]
    s2 = [H, ["Quadriceps", "Squat", "4", "6-8", "110", "2"], ["Ischios", "Soulevé de terre roumain", "3", "8-10", "100", "2"], ["Quadriceps", "Presse à cuisses", "3", "10-15", "200", "1"], ["Mollets", "Mollets debout", "4", "12-15", "70", "0"]]
    cn = {"Développé couché": "Développé couché", "Développé incliné haltères": "Développé incliné", "Rowing barre": "Rowing", "Tirage vertical": "Tirage vertical", "Triceps corde": "Triceps", "Squat": "Squat",
          "Soulevé de terre roumain": "Soulevé de terre roumain", "Presse à cuisses": "Presse à cuisses", "Mollets debout": "Mollets"}
    for d, s in enumerate((s1, s2)):
        for r in s[1:]: p.ex(0, d, r[1], [g(int(r[2]), r[3], kg(r[4]))], canon=cn[r[1]])
    p.noise = ["pectoraux", "mev", "total series"]
    p.sheets = [dict(name="Volume", rows=vol), dict(name="Séance 1", rows=s1), dict(name="Séance 2", rows=s2)]
    p.note = "Onglet de réglages avec des noms de muscles, colonne « Fourchette » (reps), colonne RIR (non évaluée), un onglet par séance."
    return p

def C11():
    p = Prog("C11", "controle", "xlsx", "Une seule colonne « Prescription » aux écritures mélangées", ["B2", "B3", "B1", "D1"], "inventé (feuille remplie à la main sur plusieurs mois)")
    rows = [["Séance", "Prescription"], ["Lundi", ""], ["", "Squat 5x5 @100"], ["", "Développé couché 100kg 5x5"], ["", "Rowing barre 4 séries de 8 à 60 kg"], ["", "Curl haltères 3×12 (14kg)"],
            ["Mercredi", ""], ["", "Soulevé de terre 3x3 @ 85%"], ["", "Développé militaire 6x3 @ 70%"], ["", "Tractions 5x5 +10kg"], ["", "Dips 4x8"]]
    p.ex(0, 0, "Squat", [g(5, 5, kg(100))], canon="Squat"); p.ex(0, 0, "Développé couché", [g(5, 5, kg(100))], canon="Développé couché")
    p.ex(0, 0, "Rowing barre", [g(4, 8, kg(60))], canon="Rowing"); p.ex(0, 0, "Curl haltères", [g(3, 12, kg(14))], canon="Curl biceps")
    p.ex(0, 1, "Soulevé de terre", [g(3, 3, pct(85))], canon="Soulevé de terre"); p.ex(0, 1, "Développé militaire", [g(6, 3, pct(70))], canon="Développé militaire")
    p.ex(0, 1, "Tractions", [g(5, 5, lest(10))], canon="Tractions"); p.ex(0, 1, "Dips", [g(4, 8)], canon="Dips")
    p.xlsx = [dict(name="Prog", rows=rows)]
    p.note = "Cinq écritures différentes dans la même colonne (« 5x5 @100 », « 100kg 5x5 », « 4 séries de 8 à 60 kg », « 3×12 (14kg) », « 3x3 @ 85% »), pas de colonne Exercice."
    return p

def C12():
    p = Prog("C12", "controle", "csv", "CSV exporté d'un Excel français : point-virgule, virgule décimale, guillemets", ["A2", "D1", "E3"], "format d'un « Enregistrer sous CSV » d'Excel en locale française (déduit) — contenu inventé")
    L = ['Jour;Exercice;Séries;Reps;Charge (kg);Commentaire',
         'Lundi;Squat;4;6;102,5;"descente lente; pause en bas"', ';Développé couché;4;6;82,5;', ';Rowing barre;4;8;67,5;', ';Triceps corde;3;12;27,5;',
         'Mercredi;Soulevé de terre;3;5;145;', ';Développé militaire;4;6;47,5;', ';Tractions;4;8;;"lestées 10 kg si 8 reps"',
         'Vendredi;Squat pause;3;4;92,5;', ';Dips;3;10;;', ';Curl barre;3;10;32,5;']
    p.text = "\n".join(L) + "\n"
    p.ex(0, 0, "Squat", [g(4, 6, kg(102.5))], canon="Squat"); p.ex(0, 0, "Développé couché", [g(4, 6, kg(82.5))], canon="Développé couché"); p.ex(0, 0, "Rowing barre", [g(4, 8, kg(67.5))], canon="Rowing"); p.ex(0, 0, "Triceps corde", [g(3, 12, kg(27.5))], canon="Triceps")
    p.ex(0, 1, "Soulevé de terre", [g(3, 5, kg(145))], canon="Soulevé de terre"); p.ex(0, 1, "Développé militaire", [g(4, 6, kg(47.5))], canon="Développé militaire"); p.ex(0, 1, "Tractions", [g(4, 8)], canon="Tractions")
    p.ex(0, 2, "Squat pause", [g(3, 4, kg(92.5))], canon="Squat pause"); p.ex(0, 2, "Dips", [g(3, 10)], canon="Dips"); p.ex(0, 2, "Curl barre", [g(3, 10, kg(32.5))], canon="Curl biceps")
    p.note = "Séparateur « ; », décimale « 102,5 », commentaire entre guillemets contenant un « ; »."
    return p

def C13():
    p = Prog("C13", "controle", "note", "Prog dictée à la voix : nombres écrits en lettres", ["B3", "C5"], "inventé (retranscription vocale d'un téléphone)")
    t = TB(p)
    t.day("Lundi")
    t.exo("squat quatre séries de cinq reps à 100 kilos", "squat", [g(4, 5, kg(100))], canon="Squat")
    t.exo("développé couché trois séries de huit reps à 70 kilos", "développé couché", [g(3, 8, kg(70))], canon="Développé couché")
    t.exo("rowing barre quatre séries de dix reps à 60 kilos", "rowing barre", [g(4, 10, kg(60))], canon="Rowing")
    t.exo("gainage trois séries de quarante-cinq secondes", "gainage", [g(3, "45 s")], canon="Gainage")
    t.day("Jeudi")
    t.exo("soulevé de terre cinq séries de trois reps à 140 kilos", "soulevé de terre", [g(5, 3, kg(140))], canon="Soulevé de terre")
    t.exo("tractions quatre séries de huit reps", "tractions", [g(4, 8)], canon="Tractions")
    t.exo("développé militaire trois séries de dix reps à 40 kilos", "développé militaire", [g(3, 10, kg(40))], canon="Développé militaire")
    t.exo("fentes trois séries de douze reps à 20 kilos", "fentes", [g(3, 12, kg(20))], canon="Fentes")
    p.note = "Pas de signe ×, séries et reps en lettres (« quatre séries de cinq reps »), « quarante-cinq secondes »."
    return t.done()

def C14():
    p = Prog("C14", "controle", "sheet", "Modèle de coach à séances fusionnées : MOUVEMENT / COMMENTAIRE ATHLÈTE", ["A2", "A3", "E5", "F1"], "modèle du coach d'Alane et Noa (connu du lecteur de lien direct) — contenu inventé, ici lu par l'import")
    H = ["MOUVEMENT", "SÉRIES", "REPS", "CHARGE", "%", "RPE", "COMMENTAIRE ATHLÈTE"]
    rows = [["BLOC 2 – SEMAINE 1"], ["SÉANCE 1 – Lundi"], H, ["Squat", "4", "5", "", "75%", "7", ""], ["Développé couché", "4", "6", "", "72%", "7", ""], ["Tractions lestées", "4", "6", "15", "", "8", "trop facile"], ["Rowing barre", "3", "10", "65", "", "8", ""], [],
            ["SÉANCE 2 – Jeudi"], H, ["Soulevé de terre", "3", "4", "", "80%", "8", ""], ["Développé militaire", "4", "6", "45", "", "8", ""], ["Dips", "3", "10", "", "", "8", ""]]
    p.ex(0, 0, "Squat", [g(4, 5, pct(75))], canon="Squat", rpe="7"); p.ex(0, 0, "Développé couché", [g(4, 6, pct(72))], canon="Développé couché", rpe="7")
    p.ex(0, 0, "Tractions lestées", [g(4, 6, lest(15))], canon="Tractions", rpe="8"); p.ex(0, 0, "Rowing barre", [g(3, 10, kg(65))], canon="Rowing", rpe="8")
    p.ex(0, 1, "Soulevé de terre", [g(3, 4, pct(80))], canon="Soulevé de terre", rpe="8"); p.ex(0, 1, "Développé militaire", [g(4, 6, kg(45))], canon="Développé militaire", rpe="8"); p.ex(0, 1, "Dips", [g(3, 10)], canon="Dips", rpe="8")
    p.sheets = [dict(name="BLOC 2", rows=rows)]
    p.note = "Bandeaux « SÉANCE n – Jour » et « BLOC n – SEMAINE n » sur leur propre ligne, en-tête MOUVEMENT répété, commentaire athlète rempli à un endroit."
    return p

ALL = [C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14]
