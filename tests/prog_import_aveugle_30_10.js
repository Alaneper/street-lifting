// Usage : node tests/prog_import_aveugle_30_10.js  → affiche ce que l'import comprend (pas de note automatique : à comparer au relevé de claude/test-aveugle-import-30-10.md).
// Test à l'aveugle du 30/10 : formats écrits maintenant, jamais vus par l'import, lancés une fois, sans correction.
const { parseProgram, parseWorkbook, fmtGroup } = require("../src/prog_import.js");
const show = (lab, r) => { console.log("\n=== " + lab);
  if (!r || !r.weeks) return console.log("  (rien)");
  r.weeks.forEach(w => w.days.forEach(d => { console.log("  [" + (w.label || "") + " | " + (d.label || "") + "]");
    d.exos.forEach(e => console.log("    - " + e.name + " :: " + (e.groups || []).map(fmtGroup).join(" + ") + (e.note ? "  (note: " + e.note + ")" : ""))); })); };
const T = s => s.trim();
// 1. Note iPhone à cases (style décrit par Audric)
show("1 · note iPhone à cases", parseProgram(T(`
Upper
☐ Développé couché : 3 séries 6 rep 70kg
☐ Tractions : 4 séries max rep
☐ Rowing barre : 3 séries 8 rep 60kg
☐ Élévations latérales : 3 séries 15 rep 8kg
☐ Abdos : 4 séries 12 rep`)));
// 2. Note téléphone avec flèches (style décrit par Lucas)
show("2 · note avec flèches et pièges", parseProgram(T(`
Jeudi
Squat -> 4 x 8/10 | 80kg
Presse -> 3 x 12 | 120kg/côté
Fentes -> 3 x 10 | 23 ou 28kg
Leg curl -> 3 x 12 | 59kg + dernière en dégressive à l'échec
Mollets debout -> 4 x 15 | 40kg`)));
// 3. Splits avec jours en lettres (style décrit par Diego)
show("3 · PPL jours en lettres", parseProgram(T(`
L : Push
- DC 4x6 80
- Dips 3x10
- Écarté poulie 3x12 15
M : Pull
- Tractions 4x8
- Rowing haltère 3x10 30
J : Legs
- Squat 5x5 100
- RDL 3x8 90`)));
// 4. Google Sheet en anglais, un tableau, jours en lignes
show("4 · Sheet anglais un tableau", parseWorkbook([{ name: "Program", rows: [
  ["Day", "Exercise", "Sets", "Reps", "Weight", "Rest", "Notes"],
  ["Day 1 - Push", "", "", "", "", "", ""],
  ["", "Bench Press", "4", "6-8", "80kg", "2 min", "pause at chest"],
  ["", "Overhead Press", "3", "8", "45kg", "90s", ""],
  ["", "Tricep Pushdown", "3", "12", "25kg", "60s", ""],
  ["Day 2 - Pull", "", "", "", "", "", ""],
  ["", "Deadlift", "3", "5", "140kg", "3 min", ""],
  ["", "Lat Pulldown", "3", "10", "60kg", "90s", ""],
  ["", "Barbell Curl", "3", "10", "30kg", "60s", ""]]}]));
// 5. Excel : semaines côte à côte, « 3x8 @ 60kg » dans une case
show("5 · semaines côte à côte", parseWorkbook([{ name: "Bloc", rows: [
  ["Exercice", "Semaine 1", "Semaine 2", "Semaine 3"],
  ["Séance A", "", "", ""],
  ["Squat", "3x8 @ 60kg", "3x8 @ 62,5kg", "3x6 @ 67,5kg"],
  ["Développé couché", "3x8 @ 50kg", "3x8 @ 52,5kg", "3x6 @ 55kg"],
  ["Séance B", "", "", ""],
  ["Soulevé de terre", "3x5 @ 90kg", "3x5 @ 95kg", "3x3 @ 102,5kg"],
  ["Tractions", "3x8", "3x9", "3x10"]]}]));
// 6. Prog de coach en % du 1RM et RPE
show("6 · % 1RM et RPE", parseWorkbook([{ name: "Semaine 1", rows: [
  ["Jour", "Mouvement", "Séries", "Reps", "Intensité", "RPE", "Repos"],
  ["Lundi", "Squat", "4", "5", "75%", "7", "3'"],
  ["", "Bench", "5", "3", "80%", "7,5", "3'"],
  ["", "Rowing", "3", "10", "", "8", "2'"],
  ["Jeudi", "Deadlift", "3", "4", "80%", "8", "4'"],
  ["", "Bench", "3", "8", "70%", "7", "2'"]]}]));
// 7. Tableau de coach : une charge et des reps par série dans une case (style décrit par Ethan)
show("7 · charge × reps par série", parseWorkbook([{ name: "S1", rows: [
  ["Exercice", "Séries x reps", "Fait"],
  ["Curls biceps", "2*8+", "20kg*8 20kg*6"],
  ["Développé incliné haltères", "3*10", "26kg*10 26kg*9 24kg*10"],
  ["Pompes lestées", "3*max", "+10kg*15 +10kg*12 +10kg*10"]]}]));
