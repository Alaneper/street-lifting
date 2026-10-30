// Chantier progs, lot 1 (30/10/2026) : unités lb, % stockés en fraction par Excel, durées en fraction de jour, training max.
const P = require("../src/prog_import.js");
const fails = [];
const ok = (c, m) => { if (!c) fails.push(m); };
const ex = (res, w = 0, d = 0, i = 0) => res.weeks[w].days[d].exos[i];
const L = e => JSON.stringify(e.groups.map(g => g.load));

// 1. Feuille annoncée en lbs : charges nues en lb ; une unité écrite dans la case gagne
let r = P.parseWorkbook([{ name: "4 Day", rows: [["Weights in lbs"], ["Exercise", "Set 1", "Set 2"], ["Bench Press", "145 x 8", "60 kg x 5"]] }]);
ok(/"v":145,"u":"lb"/.test(L(ex(r))), "1a lb par défaut : " + L(ex(r)));
ok(/"v":60,"u":"kg"/.test(L(ex(r))), "1b kg écrit gagne : " + L(ex(r)));
// 2. Feuille en lbs mais « 100 kg » écrit dans la case : reste en kg
r = P.parseWorkbook([{ name: "S1", rows: [["Weights in lbs"], ["Exercice", "Séries", "Reps", "Charge"], ["Squat", "4", "5", "100 kg"]] }]);
ok(/"u":"kg"/.test(L(ex(r))), "2 kg écrit dans la case : " + L(ex(r)));
// 3. % en fraction (valeur brute Excel) dans une colonne %, et nombre nu dans une colonne %
r = P.parseProgram("Jour\tExercice\tSéries\tReps\tCharge (kg)\t%\tRepos\nLundi\tSquat\t4\t5\t\t0.75\t0.002083333333333333\nLundi\tDéveloppé couché\t4\t6\t\t72\t\nLundi\tTractions lestées\t4\t6\t15\t\t");
ok(L(ex(r)) === '[{"kind":"pct","v":75}]', "3a fraction : " + L(ex(r)));
ok(ex(r).rest === "3:00", "3b repos : " + ex(r).rest);
ok(L(ex(r, 0, 0, 1)) === '[{"kind":"pct","v":72}]', "3c % nu : " + L(ex(r, 0, 0, 1)));
ok(/"kind":"lest","v":15/.test(L(ex(r, 0, 0, 2))), "3d tractions = lest : " + L(ex(r, 0, 0, 2)));
// 4. Texte : « Training max » n'est pas un exercice ; « lbs » écrit reste en lb
r = P.parseProgram("Training max: squat 315, bench 225\nMonday\nSquat 5x10 @ 205 lbs");
ok(r.weeks[0].days[0].exos.length === 1 && /"v":205,"u":"lb"/.test(L(ex(r))), "4a TM : " + JSON.stringify(r.weeks[0].days[0].exos.map(e => e.name)));
ok(r.meta["TM squat"] === 315, "4b meta TM : " + JSON.stringify(r.meta));
// 5. Texte sans annonce : une charge nue reste en kg (pas de régression)
r = P.parseProgram("Lundi\nSquat 3x5 100");
ok(/"u":"kg"/.test(L(ex(r))), "5 kg par défaut : " + L(ex(r)));
// 6. Écriture : 225 lb → 102,06 kg (facteur exact, 2 décimales), « 225 lb » gardé en commentaire
r = P.parseProgram("Units: lb\nMonday\nBench 3x5 225");
const g = P.toGrid(r, "", "t").flat().join("|");
ok(/\|102,06\|/.test(g) && /225 lb/.test(g), "6 conversion : " + g.slice(0, 400));
console.log("ÉCHECS :", JSON.stringify(fails, null, 1));
