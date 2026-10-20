"""Extrait réel de la prog de Noa (onglet « B8 force 3 semaines », section du bas), lignes de compét + quelques renfos.
Chaque ligne : (mouvement, variation, tempo, séries, reps, charge, rpe1, rpeLast, commentaire) pour S1, S2, S3."""
SEANCES = [
 ("Lundi", "Séance 1", [
  [("DIPS","COUDIÈRES ","COMP","2","2","86,25","6,5","6,5",""), ("DIPS","COUDIÈRES ","COMP","2","2","95","7,5","7,5",""), ("DIPS","COUDIÈRES ","COMP","2","2","103,75","8,5","9","")],
  [("DIPS","","","4","2","75","5","5",""), ("DIPS","","","4","2","82,5","6","6",""), ("DIPS","","","4","2","91,25","7,5","8,5","")],
  [("SQUAT","PAUSED SQUAT","2CT","3","4","152,5","6,5","6,5",""), ("SQUAT","PAUSED SQUAT","2CT","3","4","157,5","7,5","8",""), ("SQUAT","PAUSED SQUAT","2CT","3","4","162,5","7,5","8","")],
  [("RENFO","EXTENSIONS TRICEPS UNILATÉRAL ","","2","12","27+2,3","","",""), ("RENFO","EXTENSIONS TRICEPS UNILATÉRAL ","","2","12","27+2,3","","",""), ("RENFO","EXTENSIONS TRICEPS UNILATÉRAL ","","2","12","27+2,3","","","")],
 ]),
 ("Mardi", "Séance 2", [
  [("MUSCLE UP","COMP","","1","1","-25","5","",""), ("MUSCLE UP","COMP","","1","1","-15","6","",""), ("MUSCLE UP","COMP","","1","1","-15","5","","")],
  [("MUSCLE UP","COMP","","4","1","-15","6","6",""), ("MUSCLE UP","COMP","","4","1","0","7,5","8",""), ("MUSCLE UP","COMP","","4","1","0","7","7,5","")],
  [("MUSCLE UP","COMP","","2","1","0","7","7",""), ("MUSCLE UP","COMP","","2","1","1,25","Echec","Echec",""), ("MUSCLE UP","COMP","","2","1","1,25","8,5","8,5","")],
  [("PULL UP","COMP","","1","2","33,75","6","",""), ("PULL UP","COMP","","1","2","40","7,5","",""), ("PULL UP","COMP","","1","2","46,25","8,5","","")],
  [("PULL UP","COMP","","3","4","28,75","6,5","7",""), ("PULL UP","COMP","","3","4","33,75","7,5","8",""), ("PULL UP","COMP","","3","4","40","8,5","9,5","")],
  [("RENFO","LOW INCLINE DUMBBELL BENCH PRESS","","3","8-12","42","","","10+10+10. 16x32kg  26x22kg"), ("RENFO","LOW INCLINE DUMBBELL BENCH PRESS","","3","8-12","42","","","10+10+11.    17x32kg. 27x22kg"), ("RENFO","LOW INCLINE DUMBBELL BENCH PRESS","","3","8-12","42","","","10+11+11.    18x32kg. 28x22kg")],
 ]),
 ("Jeudi", "Séance 3", [
  [("SQUAT","COMP","","1","3","170","6","",""), ("SQUAT","COMP","","1","3","182,5","7","",""), ("SQUAT","COMP","","1","3","192,5-200","9","","200")],
  [("SQUAT","COMP","","3","5","-10%/-5%","5","6","150/155/157,5"), ("SQUAT","COMP","","3","5","-15%/-10%","5","6,5","155/160/167,5"), ("SQUAT","COMP","","3","5","-15%/-10%","6,5","8,5","160/167,5/175")],
  [("DIPS","COMP RAW PAUSÉ","","4","4","62,5","7","7",""), ("DIPS","COMP RAW PAUSÉ","","4","4","66,25","6,5","7",""), ("DIPS","COMP RAW PAUSÉ","","4","4","70","7,5","8","")],
 ]),
 ("Vendredi", "Séance 4", [
  [("PULL UP","PAUSÉ","","5","3","23,75","6","6,5",""), ("PULL UP","PAUSÉ","","5","3","26,25","7","7",""), ("PULL UP","PAUSÉ","","5","3","30","7,5","7,5","")],
 ]),
]
HDR = ["MOUVEMENT ","VARIATION ","TEMPO","COMMENTAIRE DU COACH ","SÉRIES","RÉPÉTITIONS ","REPOS","%","CHARGE","E1RM","INTENSITÉ CIBLE ","","RPE S1","RPE DERNIÈRE SÉRIE ","ANGLE A FILMER","COMMENTAIRE ATHLÈTE "]
COLS = [2, 23, 43]
def grid():
    g = []
    def put(r, c, vals):
        while len(g) <= r: g.append([])
        row = g[r]
        while len(row) < c + len(vals): row.append("")
        for i, v in enumerate(vals): row[c + i] = v
    # vieux modèle recopié en haut (doit être ignoré)
    for c in COLS:
        put(17, c, ["BLOC ", "1"]); put(22, c, ["Semaine ", "1"]); put(24, c, ["JOUR ", "Lundi"]); put(25, c, ["Séance 1"]); put(26, c, HDR)
        put(27, c, ["SQUAT","COMP","","","1","3","","","300","","","","9","9","",""])
    r0 = 149
    for w, c in enumerate(COLS):
        put(r0, c, ["BLOC ", "8"]); put(r0 + 5, c, ["Semaine ", f"{w+1}/3"])
    r = r0 + 7
    for jour, nom, rows in SEANCES:
        for w, c in enumerate(COLS):
            put(r, c, ["JOUR ", jour]); put(r + 1, c, [nom]); put(r + 2, c, HDR)
            for i, row in enumerate(rows):
                m, v, t, se, re, ch, r1, rl, com = row[w]
                put(r + 3 + i, c, [m, v, t, "", se, re, "", "", ch, "", "", "", r1, rl, "", com])
            put(r + 3 + len(rows) + 1, c, ["RECAP ", "POIDS DE CORPS ", "85"])
        r += len(rows) + 7
    return g
EXPECT = {"SQUAT": {3: 200, 5: 175}, "PULL": {2: 46.25, 4: 40}, "DIP": {2: 103.75}, "MU": {1: 1.25}}
