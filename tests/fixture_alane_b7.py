"""Extrait réel de la prog d'Alane (BLOC 7, semaines 1 et 2) : lignes de compét et variantes."""
SEANCES = [
 ("Lundi", "Séance 1", [
  [("RENFO","LOADED DEAD BUG","","5","15\"","","","",""), ("RENFO","LOADED DEAD BUG","","5","15\"","","","","")],
  [("SQUAT","COMP","","1","3","100","6,5","",""), ("SQUAT","COMP","","1","3","105","8","","")],
  [("SQUAT","COMP","","3","5","-10%/-5%  ( 92,5 )","6,5","7,5",""), ("SQUAT","COMP","","3","5","-12,5%/-5%","7,5","7,5","")],
  [("DIPS","ISO","30''","2","1","","7","",""), ("DIPS","ISO","30''","2","1","","","","")],
  [("DIPS","TEMPO ","3/2/0","4","4","18,75","6,5","7",""), ("DIPS","TEMPO ","3/2/0","4","4","22,5","","","")],
 ]),
 ("Mercredi", "Séance 2", [
  [("PULL UP","COMP","","2","2","23,75","6","6,5",""), ("PULL UP","COMP","","2","2","27,5","","","")],
  [("PULL UP","Comp","","4","4","16,25","6","6,5",""), ("PULL UP","Comp","","4","4","20","","","")],
  [("PULL UP","TEMPO","4/1/0","2","3","","6","6",""), ("PULL UP","TEMPO","4/1/0","2","3","","","","")],
  [("RENFO","STEATED DB OHP","","3","8-12","26","","","8,7,7,"), ("RENFO","STEATED DB OHP","","3","8-12","","","","")],
 ]),
 ("Jeudi", "Séance 3", [
  [("SQUAT","ZERCHER SQUAT","","3","6-10","95","6","6,5",""), ("SQUAT","ZERCHER SQUAT","","3","6-10","","","","")],
  [("DIPS","COMP","","1","3","35","5","",""), ("DIPS","COMP","","1","3","41,25","","","")],
  [("DIPS","COMP","","4","5","22,5","4","5",""), ("DIPS","COMP","","4","5","28,75","","","")],
 ]),
 ("Samedi", "Séance 4", [
  [("MUSCLE UP","COMP","","5","1","elastique 3 ","7","7,5",""), ("MUSCLE UP","COMP","","5","1","elastique 2+0,5","","","")],
  [("PULL UP","PAUSED","2CT","3","3","16,25","8,5","9",""), ("PULL UP","PAUSED","2CT","3","3","18,75","","","")],
  [("PULL UP","COMP","","2","6","16,25","8,5","9",""), ("PULL UP","COMP","","2","6","17,5","","","")],
  [("SQUAT","PAUSED","2CT","4","5","80","7","7",""), ("SQUAT","PAUSED","2CT","4","5","85","","","")],
 ]),
]
HDR = ["MOUVEMENT ","VARIATION ","TEMPO","COMMENTAIRE DU COACH ","SÉRIES","RÉPÉTITIONS ","REPOS","%","CHARGE","E1RM","INTENSITÉ CIBLE ","","RPE S1","RPE DERNIÈRE SÉRIE ","ANGLE A FILMER","COMMENTAIRE ATHLÈTE "]
COLS = [2, 22]
def grid():
    g = []
    def put(r, c, vals):
        while len(g) <= r: g.append([])
        row = g[r]
        while len(row) < c + len(vals): row.append("")
        for i, v in enumerate(vals): row[c + i] = v
    put(2, 6, ["MU", "0"]); put(3, 6, ["PU", "35"]); put(4, 6, ["DIPS", "40"]); put(5, 6, ["SQUAT", "110"])
    for w, c in enumerate(COLS):
        put(18, c, ["BLOC ", "6"]); put(23, c, ["Semaine ", str(w + 1)])
    r = 25
    for jour, nom, rows in SEANCES:
        for w, c in enumerate(COLS):
            put(r, c, ["JOUR ", jour]); put(r + 1, c, [nom]); put(r + 2, c, HDR)
            for i, row in enumerate(rows):
                m, v, t, se, re, ch, r1, rl, com = row[w]
                put(r + 3 + i, c, [m, v, t, "", se, re, "", "", ch, "", "", "", r1, rl, "", com])
            put(r + 3 + len(rows) + 1, c, ["RECAP ", "POIDS DE CORPS ", ""])
        r += len(rows) + 7
    return g
EXPECT = {"SQUAT": {3: 105, 5: 92.5}, "PULL": {2: 23.75, 4: 16.25, 6: 16.25}, "DIP": {3: 35, 5: 22.5}, "MU": {}}
