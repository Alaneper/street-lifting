"""Lot RÉGLAGE — vrais .xlsx (10 progs). Lus comme l'app les lit (valeurs brutes, cellules fusionnées vides)."""
from lib import *

def R09():
    p = Prog("R09", "reglage", "xlsx", "Bloc RPE sur 7 jours : onglets Setup/Aide, repos, jour sur la 1re ligne", ["A1", "A4", "A8", "B6", "B7", "E1", "F1"], "Mignone (sourcé : onglet Setup, semaine sur 7 jours, repos) + RTS (sourcé : Inputs, cellules à compléter)")
    setup = [["PARAMÈTRES", "", ""], ["Mouvement", "1RM (kg)", "Arrondi"], ["Squat", 180, 2.5], ["Développé couché", 125, 2.5], ["Soulevé de terre", 220, 2.5],
             ["", "", ""], ["Remplis les cases jaunes, le reste se calcule.", "", ""]]
    aide = [["MODE D'EMPLOI"], ["1. Saisis tes maxs dans l'onglet Paramètres."], ["2. Les charges suggérées apparaissent dans « Bloc 1 »."], ["3. Note tes reps dans les cases vertes."]]
    rows = []; days_plan = {
        1: [("Squat", "1x5", "7", 135, "3x5 -10%"), ("Développé couché", "1x5", "7", 95, "3x5 -10%"), ("Rowing barre", "3x8", "8", 70, "")],
        3: [("Soulevé de terre", "1x4", "7", 165, "2x4 -8%"), ("Développé militaire", "3x6", "8", 50, ""), ("Tractions", "3x8", "8", "", "")],
        4: [("Développé couché pause", "4x4", "7", 100, ""), ("Squat pause", "3x4", "7", 115, ""), ("Curl barre", "3x10", "8", 30, "")],
        6: [("Squat", "1x3", "8", 150, "3x6 -12%"), ("Soulevé de terre roumain", "3x8", "7", 110, "")]}
    p.noise = ["parametres", "mode d'emploi", "arrondi", "repos"]
    mdi = lambda t: t
    for w in (1, 2):
        rows.append([f"SEMAINE {w}"]); rows.append(["Jour", "Exercice", "Séries x reps", "RPE", "Charge suggérée (kg)", "Back-off", "Reps S1", "Reps S2", "Reps S3"])
        d = -1
        for j in range(1, 8):
            if j not in days_plan: rows.append([f"Jour {j}", "Repos"]); continue
            d += 1
            for k, (nm, sr, rp, ch, bo) in enumerate(days_plan[j]):
                ss, rr = sr.split("x")
                grp = [g(int(ss), rr, kg(ch + (2.5 if w == 2 and ch else 0)) if ch else None)]
                if bo:
                    bs, br = bo.split(" ")[0].split("x"); grp.append(g(int(bs), br, pct(-int(bo.split(" ")[1].strip("-%")))))
                rows.append([f"Jour {j}" if k == 0 else "", nm, sr, rp, (ch + (2.5 if w == 2 else 0)) if ch else "", bo, "", "", ""])
                p.ex(w - 1, d, nm, grp, rpe=rp)
        rows.append([])
    p.xlsx = [dict(name="Paramètres", rows=setup), dict(name="Aide", rows=aide), dict(name="Bloc 1", rows=rows)]
    p.note = "Onglets non-séances, semaine de 7 jours avec 3 repos, « Jour 1 » écrit seulement sur la 1re ligne, back-off dans une colonne, charge vide aux tractions."
    return p

def R10():
    p = Prog("R10", "reglage", "xlsx", "Type nSuns en lb : HELP/LOG, 9 séries « poids x reps », AMRAP « x1+ »", ["A1", "B1", "B9", "D1", "E4"], "nSuns (sourcé : HELP, LOG, « 440 x1+ », séries 9+8, lb)")
    help_ = [["HELP"], ["Entre ton training max dans LOG."], ["Les cases jaunes sont des séries AMRAP."]]
    log = [["Date", "Lift", "Reps AMRAP", "Nouveau TM"], ["2026-10-05", "Bench", 6, 230], ["2026-10-07", "Squat", 8, 320]]
    p.noise = ["help", "log", "reps amrap"]
    def pat(tm, base, rounding=5):
        sch = [(0.65, 8), (0.75, 6), (0.85, 4), (0.85, 4), (0.85, 4), (0.80, 5), (0.75, 6), (0.70, 7), (0.65, 8)]
        return [(int(round(tm * a / rounding) * rounding), r) for a, r in sch]
    def sec(tm):
        sch = [(0.5, 6), (0.6, 5), (0.7, 3), (0.7, 5), (0.7, 7), (0.7, 4), (0.7, 6), (0.7, 8)]
        return [(int(round(tm * a / 5) * 5), r) for a, r in sch]
    rows = [["Weights in lbs"], ["Exercise", "Set 1", "Set 2", "Set 3", "Set 4", "Set 5", "Set 6", "Set 7", "Set 8", "Set 9"]]
    days = [("Day 1", [("Bench Press", pat(225, 0), 9), ("Overhead Press", sec(135), 8)]), ("Day 2", [("Squat", pat(315, 0), 9), ("Sumo Deadlift", sec(300), 8)]),
            ("Day 3", [("Overhead Press", pat(135, 0), 9), ("Incline Bench Press", sec(190), 8)]), ("Day 4", [("Deadlift", pat(365, 0), 9), ("Front Squat", sec(240), 8)])]
    canon = {"Bench Press": "Développé couché", "Overhead Press": "Développé militaire", "Squat": "Squat", "Sumo Deadlift": "Soulevé de terre", "Incline Bench Press": "Développé incliné", "Deadlift": "Soulevé de terre", "Front Squat": "Front squat"}
    for d, (lab, exs) in enumerate(days):
        rows.append([lab])
        for nm, sets, n in exs:
            cells = []; grp = []
            for i, (w_, r_) in enumerate(sets):
                last = (i == 0 and False)
                cells.append(f"{w_} x {r_}")
                grp.append(g(1, r_, lb(w_)))
            if nm in ("Bench Press", "Squat", "Overhead Press", "Deadlift") and n == 9:
                cells[2] = f"{sets[2][0]} x1+"; grp[2] = g(1, 1, lb(sets[2][0]), True)
            rows.append([nm] + cells)
            p.ex(0, d, nm, grp, canon=canon[nm])
    p.xlsx = [dict(name="HELP", rows=help_), dict(name="LOG", rows=log), dict(name="4 Day", rows=rows)]
    p.note = "Poids en lb annoncés dans l'en-tête seulement, 9 colonnes de séries « 135 x 8 », AMRAP sur la 3e série (« 195 x1+ »), onglets HELP/LOG."
    return p

def R11():
    p = Prog("R11", "reglage", "xlsx", "Type Reddit PPL : jour fusionné verticalement, « 4×5 », « 1×5+ », fourchettes", ["A8", "A14", "A15", "B3", "B4", "C1"], "Reddit PPL (sourcé : « 4×5 », « 3×8-12 », « 1×5+ », 6 jours Pull/Push/Legs)")
    rows = [["Day", "Exercise", "Sets × Reps", "Weight (kg)", "Notes"]]; merges = []
    plan = [("Mon – Pull", [("Deadlift", "1×5+", 140, ""), ("Pull Ups", "3×8-12", "", "BW"), ("Barbell Row", "4×5", 70, ""), ("Face Pull", "5×15-20", 25, ""), ("Hammer Curl", "3×8-12", 16, "")]),
            ("Tue – Push", [("Bench Press", "4×5", 85, ""), ("Overhead Press", "3×6-8", 50, ""), ("Incline DB Press", "3×8-12", 28, ""), ("Triceps Pushdown", "3×8-12", 30, ""), ("Lateral Raise", "5×15-20", 10, "")]),
            ("Wed – Legs", [("Squat", "4×5", 120, ""), ("Romanian Deadlift", "3×6-8", 100, ""), ("Leg Press", "3×10-15", 200, ""), ("Leg Curl", "3×8-12", 45, ""), ("Calf Raise", "5×10-15", 80, "")]),
            ("Thu – Pull", [("Barbell Row", "1×5+", 75, ""), ("Pull Ups", "3×8-12", "", "BW"), ("Lat Pulldown", "3×8-12", 60, ""), ("Face Pull", "5×15-20", 25, ""), ("EZ Bar Curl", "3×8-12", 30, "")]),
            ("Fri – Push", [("Overhead Press", "1×5+", 52.5, ""), ("Bench Press", "3×6-8", 80, ""), ("Dips", "3×8-12", "", "BW"), ("Cable Fly", "3×12-15", 15, ""), ("Skull Crusher", "3×8-12", 30, "")]),
            ("Sat – Legs", [("Squat", "1×5+", 125, ""), ("Deadlift", "2×5", 130, "light"), ("Bulgarian Split Squat", "3×8-12", 20, ""), ("Hip Thrust", "3×8-12", 100, ""), ("Seated Calf Raise", "5×10-15", 60, "")])]
    canon = {"Deadlift": "Soulevé de terre", "Pull Ups": "Tractions", "Barbell Row": "Rowing", "Face Pull": "Face pull", "Hammer Curl": "Curl biceps", "Bench Press": "Développé couché",
             "Overhead Press": "Développé militaire", "Incline DB Press": "Développé incliné", "Triceps Pushdown": "Triceps", "Lateral Raise": "Élévations latérales", "Squat": "Squat",
             "Romanian Deadlift": "Soulevé de terre roumain", "Leg Press": "Presse à cuisses", "Leg Curl": "Leg curl", "Calf Raise": "Mollets", "Lat Pulldown": "Tirage vertical", "EZ Bar Curl": "Curl biceps",
             "Dips": "Dips", "Cable Fly": "Écarté", "Skull Crusher": "Triceps", "Bulgarian Split Squat": "Fentes bulgares", "Hip Thrust": "Hip thrust", "Seated Calf Raise": "Mollets"}
    for d, (lab, exs) in enumerate(plan):
        r0 = len(rows) + 1
        for k, (nm, sr, ch, nt) in enumerate(exs):
            rows.append([lab if k == 0 else "", nm, sr, ch, nt])
            parts = []
            for chunk in [c.strip() for c in sr.split(",")]:
                n_, r_ = chunk.replace("x", "×").split("×"); parts.append((int(n_), r_))
            grp = [g(n_, r_.rstrip("+"), kg(ch) if ch != "" else None, r_.endswith("+")) for n_, r_ in parts]
            p.ex(0, d, nm, grp, canon=canon[nm])
        merges.append(f"A{r0}:A{r0+len(exs)-1}")
    cfg = [["Lift", "1RM (kg)"], ["Squat", 160], ["Bench Press", 105], ["Deadlift", 190], ["Overhead Press", 65]]
    p.noise = ["1rm"]
    p.xlsx = [dict(name="PPL", rows=rows, merges=merges), dict(name="Réglages", rows=cfg)]
    p.note = "Le jour est une cellule fusionnée verticalement (vide sous la 1re ligne), signe × Unicode, « 1×5+ », « BW » = poids du corps, onglet de réglages avec 1RM."
    return p

def R12():
    p = Prog("R12", "reglage", "xlsx", "Semaines côte à côte, séances A/B, déload en semaine 6", ["A9", "A11", "B2", "E2"], "observé (test à l'aveugle n° 5) en plus complet ; progression linéaire type Texas/StrongLifts")
    rows = [["Exercice"] + [f"Semaine {i}" for i in range(1, 7)] + ["Notes"]]
    A = [("Squat", [(3, 8, 60), (3, 8, 62.5), (3, 6, 67.5), (3, 6, 70), (3, 5, 75), (2, 5, 60)]), ("Développé couché", [(3, 8, 50), (3, 8, 52.5), (3, 6, 55), (3, 6, 57.5), (3, 5, 60), (2, 5, 50)]),
         ("Rowing barre", [(3, 10, 40), (3, 10, 42.5), (3, 8, 45), (3, 8, 47.5), (3, 8, 50), (2, 8, 40)])]
    B = [("Soulevé de terre", [(3, 5, 90), (3, 5, 95), (3, 3, 102.5), (3, 3, 107.5), (3, 3, 112.5), (2, 3, 90)]), ("Développé militaire", [(3, 8, 30), (3, 8, 32.5), (3, 6, 35), (3, 6, 37.5), (3, 5, 40), (2, 5, 30)]),
         ("Tractions", [(3, 8, None), (3, 9, None), (3, 10, None), (4, 8, None), (4, 9, None), (2, 8, None)])]
    rows.append(["Séance A"] + [""] * 7)
    for nm, ws in A: rows.append([nm] + [f"{s}x{r} @ {str(c).replace('.', ',')}kg" for s, r, c in ws] + [""])
    rows.append(["Séance B"] + [""] * 7)
    for nm, ws in B: rows.append([nm] + [f"{s}x{r}" + (f" @ {str(c).replace('.', ',')}kg" if c else "") for s, r, c in ws] + ["" if nm != "Tractions" else "ajoute 2,5kg dès que 4x10"])
    for w in range(6):
        for d, grp in enumerate((A, B)):
            for nm, ws in grp:
                s, r, c = ws[w]; p.ex(w, d, nm, [g(s, r, kg(c) if c else None)])
    p.noise = ["ajoute"]
    p.xlsx = [dict(name="Programme", rows=rows)]
    p.note = "Semaines en colonnes, virgule décimale dans « @ 62,5kg », bandeaux « Séance A / B » dans la colonne des noms, colonne Notes."
    return p

def R13():
    p = Prog("R13", "reglage", "xlsx", "Coach FR : jour fusionné, % stocké en fraction (0,75), repos en heure", ["A8", "A15", "E5", "F1"], "déduit du code de l'app (readXlsx lit la valeur brute : 75 % formaté = 0.75) ; mise en page type coach Alane/Noa")
    mk = lambda w: [["Jour", "Exercice", "Séries", "Reps", "Charge (kg)", "%", "RPE", "Repos", "Commentaire du coach"]]
    plan = [("Lundi", [("Squat", 4, 5, "", 0.75, 7, "3:00", "descente contrôlée"), ("Développé couché", 4, 6, "", 0.72, 7, "3:00", ""), ("Rowing barre", 3, 10, 60, "", 8, "1:30", ""), ("Gainage", 3, "45s", "", "", "", "1:00", "")]),
            ("Mercredi", [("Soulevé de terre", 3, 4, "", 0.80, 8, "4:00", ""), ("Développé militaire", 4, 6, 45, "", 8, "2:00", ""), ("Tractions lestées", 4, 6, 15, "", 8, "2:00", "+15kg")]),
            ("Vendredi", [("Développé couché pause", 4, 4, "", 0.78, 7, "3:00", "pause 2 s"), ("Squat pause", 3, 4, "", 0.70, 7, "3:00", ""), ("Dips", 3, 10, "", "", 8, "1:30", "")])]
    tabs = []
    for w in (1, 2):
        rows = mk(w); merges = []; fmt = {}
        for d, (jr, exs) in enumerate(plan):
            r0 = len(rows) + 1
            for k, (nm, s, r, ch, pc, rp, rest, com) in enumerate(exs):
                pcv = round(pc + (0.025 if w == 2 else 0), 4) if pc != "" else ""
                chv = (ch + (2.5 if w == 2 else 0)) if ch != "" else ""
                rows.append([jr if k == 0 else "", nm, s, r, chv, pcv, rp, rest, com])
                if pcv != "": fmt[(len(rows), 6)] = "0.0%"
                h, m = rest.split(":"); rows[-1][7] = (int(h) * 60 + int(m)) / 86400; fmt[(len(rows), 8)] = "h:mm"   # « 3:00 » = 3 min stockées comme fraction de jour
                load = pct(round(pcv * 100, 1) if isinstance(pcv, float) else pcv) if pcv != "" else (lest(chv) if nm == "Tractions lestées" else (kg(chv) if chv != "" else None))
                if pcv != "": load = f"{round(pcv * 100, 1):g} %"
                reps = "45 s" if r == "45s" else str(r)
                p.ex(w - 1, d, nm, [g(s, reps, load)], rpe=str(rp) if rp != "" else None)
            merges.append(f"A{r0}:A{r0+len(exs)-1}")
        tabs.append(dict(name=f"Semaine {w}", rows=rows, merges=merges, fmt=fmt))
    p.xlsx = tabs
    p.note = "% stocké en fraction (brut = 0.75, 0.775…), repos en fraction de jour (0.0208…), jour fusionné, charge vide quand il y a un %."
    return p

def R14():
    p = Prog("R14", "reglage", "xlsx", "Calisthenics Recommended Routine : paires A1/A2, échelles de progressions, tempo, maintiens", ["A7", "B13", "B14", "B16", "B17"], "Recommended Routine (sourcé : 3×/sem, paires, tempo 10X0, échelle « a | b | c », maintiens)")
    rows = [["Bloc", "Exercice", "Évolutions (niveau 1 → 4)", "Séries", "Reps / durée", "Tempo", "Repos"]]
    L = [("Échauffement", "Rotations de poignets", "", 1, "10", "", "—"), ("Échauffement", "Chat-vache", "", 1, "10", "", "—"),
         ("Skill", "Handstand au mur", "Chest-to-wall | Shoulder taps | Kick-up | Handstand libre", 3, "30s", "", "90s"),
         ("Force A1", "Tractions", "Traction scapulaire | Suspension arquée | Traction négative | Traction", 3, "5-8", "10X0", "90s"),
         ("Force A2", "Dips", "Dips sur banc | Dips négatifs | Dips barres parallèles | Dips lestés", 3, "5-8", "10X0", "90s"),
         ("Force B1", "Pompes diamant", "Pompes inclinées | Pompes | Pompes diamant | Pompes archer", 3, "8-12", "10X0", "60s"),
         ("Force B2", "Rowing inversé", "Rowing inversé genoux fléchis | Rowing inversé | Rowing pieds surélevés | Rowing une jambe", 3, "8-12", "10X0", "60s"),
         ("Core", "Hollow body hold", "Tuck | Une jambe | Hollow | Hollow bras tendus", 3, "20s", "", "60s")]
    for r in L: rows.append(list(r))
    canon = {"Tractions": "Tractions", "Dips": "Dips", "Pompes diamant": "Pompes", "Rowing inversé": "Rowing inversé", "Hollow body hold": "Gainage"}
    for nm, reps, ten in [("Rotations de poignets", "10", None), ("Chat-vache", "10", None), ("Handstand au mur", "30 s", None), ("Tractions", "5-8", "10X0"), ("Dips", "5-8", "10X0"), ("Pompes diamant", "8-12", "10X0"), ("Rowing inversé", "8-12", "10X0"), ("Hollow body hold", "20 s", None)]:
        n_ = 1 if nm in ("Rotations de poignets", "Chat-vache") else 3
        p.ex(0, 0, nm, [g(n_, reps)], canon=canon.get(nm), tempo=ten)
    p.xlsx = [dict(name="Routine", rows=rows)]
    p.note = "Un seul jour (à répéter 3×/sem), blocs « Force A1/A2 », échelle de progressions séparée par « | », tempo « 10X0 », durées « 30s », repos « — »."
    return p

def R15():
    p = Prog("R15", "reglage", "xlsx", "Hybride : colonnes Moment/Allure/Distance, courses + muscu, miles", ["A12", "A13", "B19", "D3"], "Nick Bare (sourcé : two-a-days, zones, muscu 5 séances) ; unités km/min")
    rows = [["Jour", "Moment", "Exercice", "Séries", "Reps", "Charge (kg)", "Zone / allure", "Distance (km)", "Durée (min)"]]
    D = [("Lundi", [("Matin", "Course facile", 1, "", "", "Z2", 8, 45), ("Soir", "Squat", 4, 6, 100, "", "", ""), ("Soir", "Développé couché", 4, 6, 80, "", "", "")]),
         ("Mardi", [("Matin", "Fractionné", 1, "", "", "5 km", 6, 40), ("Soir", "Soulevé de terre", 3, 5, 140, "", "", ""), ("Soir", "Tractions", 4, 8, "", "", "", "")]),
         ("Mercredi", [("Matin", "Vélo", 1, "", "", "Z2", 22, 60)]),
         ("Jeudi", [("Matin", "Course tempo", 1, "", "", "Seuil", 7, 35), ("Soir", "Développé militaire", 4, 6, 45, "", "", ""), ("Soir", "Fentes", 3, 10, 20, "", "", "")]),
         ("Samedi", [("Matin", "Sortie longue", 1, "", "", "Z2", 16, 90)])]
    for d, (jr, exs) in enumerate(D):
        for k, (mo, nm, s, r, ch, zn, km, mi) in enumerate(exs):
            rows.append([jr if k == 0 else "", mo, nm, s, r, ch, zn, km, mi])
            if mi != "": p.ex(0, d, nm, [g(1, f"{mi} min", f"{km} km")], canon={"Course facile": "Course à pied", "Fractionné": "Fractionné", "Vélo": "Vélo", "Course tempo": "Course à pied", "Sortie longue": "Course à pied"}[nm])
            else: p.ex(0, d, nm, [g(s, r, kg(ch) if ch != "" else None)], canon=nm if nm in ("Squat", "Développé couché", "Soulevé de terre", "Tractions", "Développé militaire", "Fentes") else None)
    p.xlsx = [dict(name="Plan", rows=rows)]
    p.note = "Deux séances par jour (Matin/Soir), course sans séries ni reps (durée + distance), colonne « Zone / allure »."
    return p

def R16():
    p = Prog("R16", "reglage", "xlsx", "Blocs de force à la française : SEANCE n, série/rep/Inc/charge/%/RPE, DATA en erreur", ["A1", "A2", "B5", "B13", "C3", "E3"], "observé (capture de Stéphane le 27/10 : colonnes, « 6 à 8 », « 8/c », « 2ct pause bench », DATA en #DIV/0!) — contenu inventé")
    rows = [["Bloc 6"], ["SEMAINE 1"], ["SEANCE 1"], ["Exercice", "série", "rep", "Inc", "charge", "%", "RPE", "e1RM"]]
    S1 = [("Squat", 1, 5, 0, 140, "78%", "7", 165), ("Squat", 3, 5, 0, 126, "70%", "6 à 7", 150), ("Développé couché 2ct pause", 4, "6 à 8", 2.5, 85, "68%", "8", 112), ("Rowing barre", 3, 10, 0, 65, "", "8 à 9", ""), ("Fentes", 3, "8/c", 0, 20, "", "8", "")]
    S2 = [("Soulevé de terre", 1, 4, 0, 175, "80%", "8", 205), ("Soulevé de terre", 3, 6, 0, 150, "69%", "7", 180), ("Développé militaire", 4, 6, 2.5, 47.5, "", "8", ""), ("Tractions lestées", 4, 6, 0, 15, "", "8 à 9", "")]
    for k, ex in enumerate(S1): rows.append(list(ex))
    rows += [[], ["SEANCE 2"], ["Exercice", "série", "rep", "Inc", "charge", "%", "RPE", "e1RM"]]
    for ex in S2: rows.append(list(ex))
    # vérité : lignes d'un même exercice consécutives = un seul exercice avec plusieurs groupes
    p.ex(0, 0, "Squat", [g(1, 5, kg(140)), g(3, 5, kg(126))], canon="Squat", rpe="7")
    p.ex(0, 0, "Développé couché 2ct pause", [g(4, "6-8", kg(85))], canon="Développé couché pause", rpe="8")
    p.ex(0, 0, "Rowing barre", [g(3, 10, kg(65))], canon="Rowing", rpe="8-9")
    p.ex(0, 0, "Fentes", [g(3, 8, kg(20))], canon="Fentes", side=True, rpe="8")
    p.ex(0, 1, "Soulevé de terre", [g(1, 4, kg(175)), g(3, 6, kg(150))], canon="Soulevé de terre", rpe="8")
    p.ex(0, 1, "Développé militaire", [g(4, 6, kg(47.5))], canon="Développé militaire", rpe="8")
    p.ex(0, 1, "Tractions lestées", [g(4, 6, lest(15))], canon="Tractions", rpe="8-9")
    data = [["DATA"], ["Mouvement", "Record", "Moyenne"], ["Squat", 165, "#DIV/0!"], ["Bench", "#DIV/0!", "#DIV/0!"], ["Deadlift", 205, "#DIV/0!"]]
    p.noise = ["data", "record", "moyenne"]
    p.xlsx = [dict(name="Bloc 6", rows=rows), dict(name="DATA", rows=data)]
    p.note = "Ressemble au modèle de Stéphane (déjà réglé) mais avec exercices neufs, un exercice sur deux lignes (top set + back-off), « 6 à 8 », « 8/c », RPE « 8 à 9 », onglet DATA en erreurs."
    return p

def R17():
    p = Prog("R17", "reglage", "xlsx", "Plan + journal dans le même onglet : « Charge prévue » / « Fait » (S1 rempli, S2 vide)", ["A2", "C1", "F1", "F3"], "RTS/Mignone/Nick Bare/Bridge (sourcé : cases à compléter après la séance, reps réalisées par série)")
    H = ["Exercice", "Séries", "Reps", "Charge prévue", "RPE visé", "Fait S1", "Fait S2", "Fait S3", "Fait S4", "RPE réel"]
    base = [("Squat", 4, 5, 120, 7, [5, 5, 5, 4], 8), ("Développé couché", 4, 6, 85, 7, [6, 6, 6, 5], 8), ("Rowing barre", 3, 10, 70, 8, [10, 10, 9, ""], 9), ("Tractions lestées", 4, 6, 15, 8, [6, 6, 5, 5], 8.5)]
    t1 = [H]; t2 = [H]
    fill = {}
    for k, (nm, s, r, ch, rp, done, rr) in enumerate(base):
        t1.append([nm, s, r, ch, rp] + done + [rr]); t2.append([nm, s, r, ch + 2.5, rp, "", "", "", "", ""])
        for c in range(6, 11): fill[(k + 2, c)] = "C6EFCE"
        p.ex(0, 0, nm, [g(s, r, kg(ch) if nm != "Tractions lestées" else lest(ch))], canon={"Squat": "Squat", "Développé couché": "Développé couché", "Rowing barre": "Rowing", "Tractions lestées": "Tractions"}[nm], rpe=str(rp))
        p.ex(1, 0, nm, [g(s, r, kg(ch + 2.5) if nm != "Tractions lestées" else lest(ch + 2.5))], canon={"Squat": "Squat", "Développé couché": "Développé couché", "Rowing barre": "Rowing", "Tractions lestées": "Tractions"}[nm], rpe=str(rp))
    p.xlsx = [dict(name="Semaine 1", rows=t1, fill=fill), dict(name="Semaine 2", rows=t2, fill=fill)]
    p.note = "En-tête « Charge prévue » (pas « Charge »), colonnes « Fait S1…S4 » remplies en S1 : les chiffres déjà faits ne doivent pas devenir la prescription."
    return p

def R18():
    p = Prog("R18", "reglage", "xlsx", "5/3/1 en Excel : % du training max, 4 semaines dont décharge, BBB", ["A1", "A2", "B2", "E1", "E2"], "5/3/1 (sourcé : 65/75/85 %, 70/80/90 %, 75/85/95 %, décharge 40/50/60 %, BBB 5×10)")
    setup = [["Training max (90 % du 1RM)", ""], ["Squat", 162], ["Développé couché", 112.5], ["Soulevé de terre", 198], ["Développé militaire", 60]]
    rows = [["Jour", "Mouvement", "Série", "% TM", "Reps"]]
    SCH = {1: [(65, "5"), (75, "5"), (85, "5+")], 2: [(70, "3"), (80, "3"), (90, "3+")], 3: [(75, "5"), (85, "3"), (95, "1+")], 4: [(40, "5"), (50, "5"), (60, "5")]}
    LIFTS = [("Lundi", "Squat"), ("Mardi", "Développé couché"), ("Jeudi", "Soulevé de terre"), ("Vendredi", "Développé militaire")]
    for w in (1, 2, 3, 4):
        rows.append([f"Semaine {w}" + (" (décharge)" if w == 4 else "")])
        for d, (jr, lift) in enumerate(LIFTS):
            grp = []
            for k, (pc_, rp_) in enumerate(SCH[w]):
                rows.append([jr if k == 0 else "", lift, k + 1, f"{pc_}%", rp_])
                grp.append(g(1, rp_.rstrip("+"), pct(pc_), rp_.endswith("+")))
            if w < 4:
                rows.append(["", lift + " (BBB)", "4", "50%", "10"]); 
            p.ex(w - 1, d, lift, grp, canon=lift)
            if w < 4: p.ex(w - 1, d, lift + " (BBB)", [g(1, 10, pct(50))] * 1 if False else [g(4, 10, pct(50))], canon=lift)
    p.noise = ["training max"]
    p.xlsx = [dict(name="Paramètres", rows=setup), dict(name="Cycle", rows=rows)]
    p.note = "Une ligne par série (colonne « Série »), % en texte « 65% », AMRAP « 5+ » dans la colonne Reps, bandeau « Semaine 4 (décharge) », BBB sur une ligne (4 séries de 10 à 50 %)."
    return p

ALL = [R09, R10, R11, R12, R13, R14, R15, R16, R17, R18]
