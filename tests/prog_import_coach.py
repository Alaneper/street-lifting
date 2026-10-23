"""Import d'un classeur au format du modèle du coach (structure de tests/fixture_alane_b7.py) via parseWorkbook.
Usage : python3 tests/prog_import_coach.py   (affiche « ÉCHECS : [] » si tout passe)"""
import json, pathlib, subprocess, sys
H = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(H))
import fixture_alane_b7 as f
js = """const {parseWorkbook,fmtGroup}=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{
const r=parseWorkbook(JSON.parse(s));console.log(JSON.stringify(r.weeks.map(w=>({l:w.label,d:w.days.map(d=>({l:d.label,e:d.exos.map(e=>e.canon+' '+e.groups.map(fmtGroup).join(','))}))}))))})"""
out = json.loads(subprocess.run(["node", "-e", js, str(H.parent / "src/prog_import.js")], input=json.dumps([{"name": "BLOC 7", "rows": f.grid()}]), capture_output=True, text=True, check=True).stdout)
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)
check("2 semaines côte à côte", [w["l"] for w in out] == ["Semaine 1", "Semaine 2"], [w["l"] for w in out])
check("jours Lundi, Mercredi, Jeudi, Samedi", [d["l"] for d in out[0]["d"]] == ["Lundi", "Mercredi", "Jeudi", "Samedi"], [d["l"] for d in out[0]["d"]])
L = out[0]["d"][0]["e"]
check("squat 1×3 · 100 kg puis back-off -10 %", L[1] == "Squat 1×3 · 100 kg" and L[2] == "Squat 3×5 · -10 %", L)
check("dips tempo lestés", "Dips 4×4 · +18.75 kg" in L, L)
check("dead bug = gainage (pas soulevé de terre)", L[0].startswith("Gainage"), L)
check("tractions lestées semaine 2", "Tractions 2×2 · +27.5 kg" in out[1]["d"][1]["e"], out[1]["d"][1]["e"])
check("muscle-up à l'élastique : pas de charge inventée", out[0]["d"][3]["e"][0] == "Muscle-up 5×1", out[0]["d"][3]["e"])
print("ÉCHECS :", fails)
