"""Corpus de programmes SYNTHÉTIQUES pour entraîner et mesurer l'import (aucune donnée réelle).
Chaque cas = un programme tiré au hasard (style power / street / muscu…) rendu dans un format :
textes (notes, anglais, forum, export d'app, listes de reps, CSV…) ou tableurs .xlsx (liste verticale,
semaines côte à côte façon modèle du coach, colonnes par série, semaines en colonnes…).
La vérité terrain est connue pour chaque cas → score automatique.
Usage : python3 tests/gen_corpus.py <dossier> [nombre de programmes par format]
Les formats et noms marqués TEST ne servent JAMAIS à régler l'import : ils mesurent la généralisation."""
import json, pathlib, random, sys
import openpyxl

OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 6

# canon → (catégorie, variantes d'entraînement, variantes TEST jamais vues pendant la mise au point)
EX = {
 "Squat": ("power", ["Squat", "squat barre", "Back squat", "SQUAT COMP", "Squat barre basse", "squatt"], ["Sq", "Squat arrière", "low bar squat"]),
 "Développé couché": ("power", ["Développé couché", "DC", "Bench press", "Bench", "dév couché", "Banc"], ["BP", "developpe couche", "Couché"]),
 "Soulevé de terre": ("power", ["Soulevé de terre", "SDT", "Deadlift", "Dead", "soulevé de terre sumo"], ["DL", "SDT conventionnel", "souleve de terre"]),
 "Tractions": ("street", ["Tractions", "Tractions lestées", "Pull up", "PULL UP COMP", "Weighted pull-ups", "traction pronation"], ["Pull-ups lestés", "Chin up", "tractions supination"]),
 "Dips": ("street", ["Dips", "Dips lestés", "DIPS COMP", "Weighted dips", "dips barres parallèles"], ["Dip", "Dips anneaux"]),
 "Muscle-up": ("street", ["Muscle-up", "Muscle up", "MU", "muscle-up strict"], ["MUP", "Muscle-up lesté"]),
 "Développé militaire": ("muscu", ["Développé militaire", "OHP", "Overhead press", "Dév militaire", "militaire debout"], ["Military press", "Presse épaules barre"]),
 "Rowing": ("muscu", ["Rowing barre", "Barbell row", "Rowing haltère", "rowing", "Tirage horizontal"], ["Row", "Pendlay row", "Rowing T-bar"]),
 "Tirage vertical": ("muscu", ["Tirage vertical", "Lat pulldown", "tirage poitrine", "Tirage nuque"], ["Pulldown", "Lat pull"]),
 "Développé incliné": ("muscu", ["Développé incliné", "Incline bench", "DC incliné", "Incline dumbbell press", "dév incliné haltères"], ["Incliné haltères", "Incline DB"]),
 "Presse à cuisses": ("muscu", ["Presse", "Leg press", "presse à cuisses", "Presse 45°"], ["Presse inclinée", "Hack press"]),
 "Leg curl": ("muscu", ["Leg curl", "Leg curl assis", "Ham curl", "leg curl allongé"], ["Ischios machine", "Lying leg curl"]),
 "Leg extension": ("muscu", ["Leg extension", "Leg ext", "leg extension machine"], ["Quadriceps machine", "Extensions jambes"]),
 "Fentes": ("muscu", ["Fentes", "Fentes marchées", "Walking lunges", "Lunges", "fentes haltères"], ["Fentes avant", "Reverse lunges"]),
 "Hip thrust": ("muscu", ["Hip thrust", "hip thrust barre", "Hip thrusts"], ["Glute bridge barre", "Hip-thrust"]),
 "Curl biceps": ("muscu", ["Curl biceps", "Curl barre", "Curl haltères", "EZ bar curl", "curl marteau", "Curl pupitre"], ["Biceps curl", "Curl incliné"]),
 "Triceps": ("muscu", ["Triceps poulie", "Barre au front", "Extension triceps", "Pushdown", "triceps corde"], ["Skull crusher", "Kickback triceps"]),
 "Élévations latérales": ("muscu", ["Élévations latérales", "Elev lat", "Lateral raise", "élévations latérales haltères"], ["Lat raise", "Oiseau latéral"]),
 "Mollets": ("muscu", ["Mollets", "Mollets debout", "Calf raises", "Mollets assis"], ["Extensions mollets", "Calf raise machine"]),
 "Abdos": ("muscu", ["Abdos", "Crunch", "Relevés de jambes", "Hanging leg raises", "Ab wheel"], ["Sit-up", "Crunch poulie"]),
 "Gainage": ("muscu", ["Gainage", "Planche", "Plank", "L-sit"], ["Gainage latéral", "Hollow hold"]),
 "Face pull": ("muscu", ["Face pull", "face pull corde", "Face pulls"], ["Facepull"]),
}
STYLES = {
 "power": dict(days=4, weeks=(1, 4), main=["Squat", "Développé couché", "Soulevé de terre"], acc=["Rowing", "Tractions", "Dips", "Développé militaire", "Hip thrust", "Leg curl", "Abdos", "Triceps"], pct=True),
 "street": dict(days=4, weeks=(1, 4), main=["Tractions", "Dips", "Muscle-up", "Squat"], acc=["Rowing", "Développé militaire", "Curl biceps", "Triceps", "Gainage", "Abdos", "Fentes"], lest=True),
 "ppl": dict(days=3, weeks=(1, 1), main=["Développé couché", "Tractions", "Squat"], acc=["Développé incliné", "Élévations latérales", "Triceps", "Rowing", "Tirage vertical", "Curl biceps", "Face pull", "Presse à cuisses", "Leg curl", "Leg extension", "Mollets"], kg=True),
 "upper_lower": dict(days=4, weeks=(1, 2), main=["Développé couché", "Squat", "Soulevé de terre", "Développé militaire"], acc=["Rowing", "Tirage vertical", "Curl biceps", "Triceps", "Presse à cuisses", "Leg curl", "Hip thrust", "Mollets", "Abdos"], kg=True),
 "debutant": dict(days=3, weeks=(1, 1), main=["Squat", "Développé couché", "Rowing"], acc=["Développé militaire", "Fentes", "Curl biceps", "Gainage", "Tirage vertical"], kg=True),
}
DAYS_FR = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

def make_program(rnd, style, test_names):
    S = STYLES[style]; nw = rnd.randint(*S["weeks"]); weeks = []
    plan = []
    for d in range(S["days"]):
        mains = rnd.sample(S["main"], k=min(2, len(S["main"]))); accs = rnd.sample(S["acc"], k=rnd.randint(2, 4))
        plan.append(mains + accs)
    names = {c: rnd.choice(EX[c][2] if test_names else EX[c][1]) for c in EX}
    for w in range(nw):
        days = []
        for d, exs in enumerate(plan):
            items = []
            for i, c in enumerate(exs):
                main = i < 2
                sets = rnd.choice([3, 4, 5]) if main else rnd.choice([3, 4])
                reps = rnd.choice(["3", "5", "6", "8"]) if main else rnd.choice(["8", "10", "12", "15", "8-12", "10-12"])
                load = None
                if main and S.get("pct") and c in ("Squat", "Développé couché", "Soulevé de terre"):
                    load = {"kind": "pct", "v": rnd.choice([70, 72.5, 75, 77.5, 80, 82.5, 85]) + 2.5 * w}
                elif S.get("lest") and c in ("Tractions", "Dips", "Muscle-up") and main:
                    load = {"kind": "lest", "v": rnd.choice([5, 10, 15, 20, 25, 30, 40]) + 2.5 * w, "u": "kg"}
                elif main or (S.get("kg") and rnd.random() < .6):
                    base = {"Squat": 100, "Développé couché": 70, "Soulevé de terre": 130, "Développé militaire": 40}.get(c, rnd.choice([20, 30, 40, 50, 60]))
                    load = {"kind": "abs", "v": base + rnd.choice([0, 5, 10, 15, 20]) + 2.5 * w, "u": "kg"}
                if load and load["kind"] == "abs" and c in ("Tractions", "Dips", "Muscle-up"): load = {"kind": "lest", "v": rnd.choice([5, 10, 15, 20]) + 2.5 * w, "u": "kg"}
                if c in ("Gainage",): reps = rnd.choice(["30", "45"]); load = None
                items.append({"canon": c, "name": names[c], "sets": sets, "reps": reps, "load": load,
                              "rpe": rnd.choice([None, None, "7", "8", "7-8", "8.5"]) if main else None})
            days.append(items)
        weeks.append(days)
    return weeks

def fmt_load(L, style="fr"):
    if not L: return ""
    v = ("%g" % L["v"]).replace(".", ",") if style == "fr_comma" else "%g" % L["v"]
    if L["kind"] == "pct": return f"{v}%"
    if L["kind"] == "lest": return f"+{v}kg" if style != "en" else f"+{v}kg"
    return f"{v}kg"

def noisy(rnd, s):
    r = rnd.random()
    return s.upper() if r < .15 else s.lower() if r < .3 else s

# ---------------- rendus texte ----------------
def r_notes(rnd, W, en=False):            # « Squat 4x5 @ 80% rpe 8 »
    L = []
    for wi, days in enumerate(W):
        if len(W) > 1: L.append(f"\n{'Week' if en else 'Semaine'} {wi + 1}")
        for di, items in enumerate(days):
            L.append(f"\n{(DAYS_EN if en else DAYS_FR)[di].upper() if rnd.random() < .5 else (DAYS_EN if en else DAYS_FR)[di]}")
            for it in items:
                ld = fmt_load(it["load"]); s = f"{noisy(rnd, it['name'])} {it['sets']}x{it['reps']}"
                if ld: s += f" @ {ld}" if it["load"]["kind"] == "pct" else f" {ld}"
                if it["rpe"]: s += f" rpe {it['rpe']}"
                L.append(s)
            if rnd.random() < .4: L.append(rnd.choice(["repos 2-3 min entre les séries", "finir par 10 min de cardio", "(si fatigue, enlever le dernier exo)"]))
    return "\n".join(L)

def r_series_reps(rnd, W):               # « Squat : 4 séries x 5 reps (100kg) »
    L = []
    for wi, days in enumerate(W):
        if len(W) > 1: L.append(f"\n=== SEMAINE {wi + 1} ===")
        for di, items in enumerate(days):
            L.append(f"\n🔥 JOUR {di + 1} 🔥")
            for it in items:
                s = f"{it['name']} : {it['sets']} séries x {it['reps']} reps"
                ld = fmt_load(it["load"])
                if ld: s += f" ({ld})" if it["load"]["kind"] != "pct" else f" à {ld}"
                L.append(s)
    return "\n".join(L)

def r_english(rnd, W):                    # « Bench press 4 sets of 6 @ RPE 8 »
    L = []
    for wi, days in enumerate(W):
        if len(W) > 1: L.append(f"\nWEEK {wi + 1}")
        for di, items in enumerate(days):
            L.append(f"\n{['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'][di]} — {rnd.choice(['Upper', 'Lower', 'Push', 'Pull', 'Strength', 'Volume'])}")
            for it in items:
                s = f"{it['name']} {it['sets']} sets of {it['reps']}"
                L_ = it["load"]
                if L_: s += f" @ {'%g' % L_['v']}%" if L_["kind"] == "pct" else f" +{'%g' % L_['v']}kg" if L_["kind"] == "lest" else f" @ {'%g' % L_['v']}kg"
                if it["rpe"]: s += f" (RPE {it['rpe']})"
                L.append(s)
    return "\n".join(L)

def r_forum(rnd, W):                      # puces, cases à cocher, gras
    L = ["**Mon programme (copié du forum)**"]
    for wi, days in enumerate(W):
        if len(W) > 1: L.append(f"\n__Semaine {wi + 1}__")
        for di, items in enumerate(days):
            L.append(f"\n**Séance {'ABCDEF'[di]}**")
            for it in items:
                ld = fmt_load(it["load"])
                L.append(f"{rnd.choice(['- [ ]', '*', '-', '•'])} {it['name']} — {it['sets']} × {it['reps']}{(' — ' + ld) if ld else ''}")
    L.append("\n!!! Repos 90s !!!")
    return "\n".join(L)

def r_export(rnd, W):                     # une info par ligne (exports d'apps)
    L = []
    for wi, days in enumerate(W):
        if len(W) > 1: L.append(f"Week {wi + 1}")
        for di, items in enumerate(days):
            L.append(f"Workout {'ABCDEF'[di]}")
            for it in items:
                L.append(it["name"]); L.append(f"{it['sets']} × {it['reps']}")
                if it["load"]: L.append(fmt_load(it["load"]).replace("kg", " kg"))
                L.append("")
    return "\n".join(L)

def r_replist(rnd, W):                    # « tractions +30 : 5/5/5/5 »
    L = []
    for wi, days in enumerate(W):
        if len(W) > 1: L.append(f"\nsem {wi + 1}")
        for di, items in enumerate(days):
            L.append(f"séance {di + 1}")
            for it in items:
                ld = fmt_load(it["load"]); reps = it["reps"].split("-")[0]
                L.append(f"{it['name'].lower()}{(' ' + ld) if ld else ''} : {'/'.join([reps] * it['sets'])}")
    return "\n".join(L)

def r_csv(rnd, W, sep=";"):
    L = [f"Semaine{sep}Jour{sep}Exercice{sep}Séries{sep}Reps{sep}Charge{sep}RPE"]
    for wi, days in enumerate(W):
        for di, items in enumerate(days):
            for it in items:
                L.append(sep.join([str(wi + 1), DAYS_FR[di], it["name"], str(it["sets"]), it["reps"], fmt_load(it["load"]).replace("kg", "") if it["load"] and it["load"]["kind"] == "abs" else fmt_load(it["load"]).replace("+", "BW+").replace("kg", ""), it["rpe"] or ""]))
    return "\n".join(L)

def r_star_days(rnd, W):                  # TEST : « Lundi : squat 4*6 à 70% ; dc 4*6 »
    L = []
    for wi, days in enumerate(W):
        L.append(f"\nSemaine {wi + 1} :")
        for di, items in enumerate(days):
            parts = []
            for it in items:
                ld = fmt_load(it["load"], "fr_comma")
                parts.append(f"{it['name'].lower()} {it['sets']}*{it['reps']}{(' à ' + ld) if ld and it['load']['kind'] == 'pct' else (' ' + ld) if ld else ''}")
            L.append(f"{DAYS_FR[di]} : " + " ; ".join(parts))
    return "\n".join(L)

# ---------------- rendus tableur (grilles → .xlsx) ----------------
def g_vertical(rnd, W):
    g = [["Programme", rnd.choice(["Prise de masse", "Force", "Bloc 1"])], [], ["Semaine", "Jour", "Exercice", "Séries", "Reps", "Charge", "RPE", "Notes"]]
    for wi, days in enumerate(W):
        for di, items in enumerate(days):
            for it in items:
                L = it["load"]
                g.append([wi + 1, f"J{di + 1}", it["name"], it["sets"], it["reps"], (f"{'%g' % L['v']}%" if L["kind"] == "pct" else f"BW+{'%g' % L['v']}" if L["kind"] == "lest" else L["v"]) if L else "", it["rpe"] or "", ""])
    return {"Programme": g}

def g_coach(rnd, W):                      # semaines côte à côte, blocs par jour (structure du modèle du coach)
    HDR = ["MOUVEMENT", "VARIATION", "TEMPO", "COMMENTAIRE DU COACH", "SÉRIES", "RÉPÉTITIONS", "REPOS", "%", "CHARGE", "RPE S1", "RPE DERNIÈRE SÉRIE", "COMMENTAIRE ATHLÈTE"]
    g = []
    def put(r, c, vals):
        while len(g) <= r: g.append([])
        row = g[r]
        while len(row) < c + len(vals): row.append("")
        for i, v in enumerate(vals): row[c + i] = v
    put(0, 0, ["BLOC", "1"])
    for wi in range(len(W)): put(2, 1 + wi * 14, ["Semaine", wi + 1])
    r = 4
    for di in range(len(W[0])):
        for wi, days in enumerate(W):
            c = 1 + wi * 14
            put(r, c, ["JOUR", DAYS_FR[di]]); put(r + 1, c, [f"Séance {di + 1}"]); put(r + 2, c, HDR)
            for i, it in enumerate(days[di]):
                L = it["load"]; parts = it["name"].split(" ", 1)
                put(r + 3 + i, c, [parts[0].upper(), parts[1].upper() if len(parts) > 1 else "COMP", "", "", it["sets"], it["reps"], "3'",
                                   ("%g" % L["v"]) + "%" if L and L["kind"] == "pct" else "", ("%g" % L["v"]) if L and L["kind"] != "pct" else "", it["rpe"] or "", "", ""])
        r += len(W[0][di]) + 6
    return {"Bloc 1": g}

def g_sets_cols(rnd, W):                  # une colonne par série : « 100 x 5 »
    sheets = {}
    for wi, days in enumerate(W):
        g = [[f"Semaine {wi + 1}"]]
        for di, items in enumerate(days):
            g.append([]); g.append([DAYS_FR[di]]); g.append(["Exercice", "Série 1", "Série 2", "Série 3", "Série 4", "Série 5"])
            for it in items:
                L = it["load"]; reps = it["reps"].split("-")[0]
                cell = (f"{'%g' % L['v']}% x {reps}" if L["kind"] == "pct" else f"+{'%g' % L['v']} x {reps}" if L["kind"] == "lest" else f"{'%g' % L['v']} x {reps}") if L else f"x{reps}"
                g.append([it["name"]] + [cell] * it["sets"])
        sheets[f"S{wi + 1}"] = g
    return sheets

def g_week_cols(rnd, W):                  # TEST : exercices en lignes, semaines en colonnes « 4x5 @80% »
    sheets = {}
    for di in range(len(W[0])):
        g = [["Exercice"] + [f"S{wi + 1}" for wi in range(len(W))]]
        for i, it in enumerate(W[0][di]):
            row = [it["name"]]
            for wi in range(len(W)):
                x = W[wi][di][i]; ld = fmt_load(x["load"])
                row.append(f"{x['sets']}x{x['reps']}" + ((" @" + ld) if ld else ""))
            g.append(row)
        sheets[DAYS_FR[di]] = g
    return sheets

TEXT = {"notes": r_notes, "notes_en": lambda r, W: r_notes(r, W, True), "series_reps": r_series_reps, "english": r_english,
        "forum": r_forum, "export": r_export, "replist": r_replist, "csv": r_csv, "TEST_star_days": r_star_days}
GRID = {"xlsx_vertical": g_vertical, "xlsx_coach": g_coach, "xlsx_sets_cols": g_sets_cols, "TEST_xlsx_week_cols": g_week_cols}

def expand(it):                           # vérité terrain : liste des séries (reps, charge)
    L = it["load"]; ld = None
    if L: ld = (f"{'%g' % L['v']} %" if L["kind"] == "pct" else f"+{'%g' % L['v']} kg" if L["kind"] == "lest" else f"{'%g' % L['v']} kg")
    return {"canon": it["canon"], "sets": it["sets"], "reps": it["reps"], "load": ld}

import os
rnd = random.Random(int(os.environ.get("SEED", "42")))
index = []
for fmt in list(TEXT) + list(GRID):
    for k in range(N):
        style = list(STYLES)[k % len(STYLES)]
        test_names = k % 3 == 2                # un programme sur trois avec des noms jamais vus
        W = make_program(rnd, style, test_names)
        cid = f"{fmt}-{k}"
        if fmt in TEXT:
            if fmt == "replist":
                for days in W:
                    for items in days:
                        for it in items: it["reps"] = it["reps"].split("-")[0]
            (OUT / f"{cid}.txt").write_text(TEXT[fmt](rnd, W))
        else:
            if fmt == "xlsx_sets_cols":
                for days in W:
                    for items in days:
                        for it in items: it["reps"] = it["reps"].split("-")[0]
                        for it in items:
                            if not it["load"]: it["load"] = None
            wb = openpyxl.Workbook(); wb.remove(wb.active)
            for name, g in GRID[fmt](rnd, W).items():
                ws = wb.create_sheet(name)
                for row in g: ws.append(row)
            wb.save(OUT / f"{cid}.xlsx")
        truth = [[[expand(it) for it in items] for items in days] for days in W]
        index.append({"id": cid, "fmt": fmt, "style": style, "test_names": test_names, "file": f"{cid}.{'txt' if fmt in TEXT else 'xlsx'}", "truth": truth})
(OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False))
print(len(index), "cas générés dans", OUT)
