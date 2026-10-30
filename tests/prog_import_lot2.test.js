// Chantier progs, lot 2 (30/10/2026) : lecteur de tableaux unifié, notations de séries, top set / back-off.
// Cas écrits pour CE test (différents du corpus) : ils vérifient des règles générales, pas une prog précise.
const P = require("../src/prog_import.js");
const fails = [];
const ok = (c, m) => { if (!c) fails.push(m); };
const all = r => r.weeks.flatMap(w => w.days.flatMap(d => d.exos.map(e => ({ w: w.label, d: d.label, n: e.name, g: e.groups.map(P.fmtGroup).join(" + "), e }))));
const show = r => JSON.stringify(all(r).map(x => `${x.w}|${x.d}|${x.n}|${x.g}`));

// 1. En-têtes variés : « Movement | Nb sets | Nb reps | Load (lbs) | Rest »
let r = P.parseWorkbook([{ name: "Week 3", rows: [["Movement", "Nb sets", "Nb reps", "Load (lbs)", "Rest"], ["Training day 1"], ["Front Squat", "3", "6", "155", "0.00208333"], ["Training day 2"], ["Chin Ups", "3", "AMRAP", "+25", ""]] }]);
let E = all(r);
ok(E.length === 2 && E[0].w === "Semaine 3" && E[0].g === "3×6 · 155 lb" && E[0].e.rest === "3:00", "1a " + show(r));
ok(E[1].g === "3×max · +25 lb" && E[0].d !== E[1].d, "1b " + show(r));
// 2. Charge ET % sur la même ligne, colonne « % 1RM », écrits tous deux dans le carnet
r = P.parseWorkbook([{ name: "Bloc", rows: [["Exercice", "Séries", "Reps", "Charge", "% 1RM"], ["Soulevé de terre", "2", "3", "180", "0.85"]] }]);
E = all(r);
ok(E[0].g === "2×3 · 180 kg · 85 %", "2a " + show(r));
const gr = P.toGrid(r, "", "t").find(x => x[0] === "Soulevé de terre");
ok(gr && gr[4] === "180" && gr[5] === "85%", "2b carnet : " + JSON.stringify(gr));
// 3. Top set + back-off en texte → deux fiches
r = P.parseProgram("Jeudi\nDéveloppé couché 1x2 @ 8 puis 4x4 à -15%");
E = all(r);
ok(E.length === 2 && /top set/.test(E[0].n) && E[0].g === "1×2" && /back-off/.test(E[1].n) && E[1].g === "4×4 · -15 %" && E[0].e.rpe === "8" && !E[1].e.rpe, "3 " + show(r));
// 4. Colonne « Back-off » dans un tableau → fiche séparée
r = P.parseWorkbook([{ name: "S1", rows: [["Jour", "Exercice", "Séries x reps", "Charge", "Back-off"], ["J1", "Squat", "1x3", "150", "2x5 -12%"]] }]);
E = all(r);
ok(E.length === 2 && E[1].n === "Squat (back-off)" && E[1].g === "2×5 · -12 %" && E[0].g === "1×3 · 150 kg", "4 " + show(r));
// 5. Séries une par une : « 70x10, 80x8, 90x6+ », « 12kg*12 », « +5kg*6 »
r = P.parseProgram("Mardi\nRowing : 70x10, 80x8, 90x6+\nCurl : 12kg*12 12kg*10\nDips : +5kg*6 +5kg*6");
E = all(r);
ok(E[0].g === "1×10 · 70 kg + 1×8 · 80 kg + 1×6+ · 90 kg" && E[1].g === "1×12 · 12 kg + 1×10 · 12 kg" && E[2].g === "1×6 · +5 kg + 1×6 · +5 kg", "5 " + show(r));
// 6. « 3 @ 70%, 3 @ 80%, 3+ @ 90% » ; « 4×(6-8) » ; « 2x40s », « 3x2 min »
r = P.parseProgram("Day 1\nPress: 3 @ 70%, 3 @ 80%, 3+ @ 90%\nLunges 4×(6-8)\nL-sit 2x40s\nPlanche 3x2 min");
E = all(r);
ok(E[0].g === "1×3 · 70 % + 1×3 · 80 % + 1×3+ · 90 %" && E[1].g === "4×6-8" && E[2].g === "2×40 s" && E[3].g === "3×2 min", "6 " + show(r));
// 7. Lignes sans prescription (« Repos », « DELOAD », « TOTAL ») : jamais des exercices ; onglets sans titres de colonnes ignorés
r = P.parseWorkbook([{ name: "Réglages", rows: [["Lift", "1RM (kg)"], ["Squat", "200"]] }, { name: "Plan", rows: [["Jour", "Exercice", "Séries", "Reps"], ["Lundi", "Squat", "5", "5"], ["Mardi", "Repos"], ["Mercredi", "TOTAL", "=SUM(C2)", ""], ["Jeudi", "Bench", "#REF!", "5"]] }]);
E = all(r);
ok(E.length === 2 && E[0].n === "Squat" && E[1].n === "Bench", "7 " + show(r));
// 8. Numéro de série sur des lignes consécutives (1, 2, 3) → un seul exercice ; comptes de séries (1 puis 3) → deux fiches
r = P.parseWorkbook([{ name: "C", rows: [["Mouvement", "Set", "%", "Reps"], ["Bench", "1", "70%", "5"], ["Bench", "2", "80%", "3"], ["Bench", "3", "90%", "1+"], ["Squat", "1", "80%", "3"], ["Squat", "3", "70%", "5"]] }]);
E = all(r);
ok(E.length === 3 && E[0].g === "1×5 · 70 % + 1×3 · 80 % + 1×1+ · 90 %" && E[1].g === "1×3 · 80 %" && E[2].g === "3×5 · 70 %", "8 " + show(r));
// 9. Curl marteau / Hammer curl ≠ leg curl
ok(P.canon("Hammer curl").canon === "Curl biceps" && P.canon("Hamstring curl").canon === "Leg curl", "9 canon");
// 10. Activité chronométrée : « Mobilité 20 min », « Vélo 45 min : 5 x 1 min fort » ; « environ 8 km » n'est pas une consigne
r = P.parseProgram("Samedi\nMobilité 20 min\nVélo 45 min : 5 x 1 min fort\nFooting 50 min (environ 9 km)\nRepos 2 min");
E = all(r);
ok(E.length === 3 && E[0].g === "20 min" && E[1].g === "45 min" && E[2].g === "50 min", "10 " + show(r));
// 11. Notes de téléphone : « -> », « 8/10 », « X ou Y kg », jours en lettres « L : Push »
r = P.parseProgram("L : Haut\nTirage -> 3 x 10/12 | 50 ou 55kg\nMe : Bas\nPresse -> 4 x 12 | 140kg");
E = all(r);
ok(E.length === 2 && E[0].n === "Tirage" && E[0].g === "3×10-12 · 50 kg" && /50 ou 55kg/.test(E[0].e.note || "") && E[0].d !== E[1].d, "11 " + show(r));
console.log("ÉCHECS :", JSON.stringify(fails, null, 1));
