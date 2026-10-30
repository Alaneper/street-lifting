// Chantier progs, lot 3 (30/10/2026) : faiblesses révélées par le lot contrôle. Cas écrits pour CE test (pas ceux du corpus).
const P = require("../src/prog_import.js");
const fails = [];
const ok = (c, m) => { if (!c) fails.push(m); };
const all = r => r.weeks.flatMap(w => w.days.flatMap(d => d.exos.map(e => ({ w: w.label, d: d.label, n: e.name, c: e.canon, g: e.groups.map(P.fmtGroup).join(" + "), e }))));
const show = r => JSON.stringify(all(r).map(x => `${x.w}|${x.d}|${x.n}|${x.g}`));

// 1. Dictée : « soixante-dix kilos », « trente secondes », « avec 5 kilos de lest »
let r = P.parseProgram("Mardi\nfront squat trois séries de six reps à soixante-dix kilos\nplanche trois séries de trente secondes\ndips quatre séries de dix avec 5 kilos de lest");
let E = all(r);
ok(E.length === 3 && E[0].g === "3×6 · 70 kg" && E[1].g === "3×30 s" && E[2].g === "4×10 · +5 kg", "1 " + show(r));
// 2. Export d'app : nom puis « Set 1: 60 kg × 10 » ; « (Weighted) » = lest
r = P.parseProgram("Leg Day\nGoblet Squat\nSet 1: 24 kg × 12\nSet 2: 24 kg × 10\nChin Up (Weighted)\nSet 1: 5 kg × 6");
E = all(r);
ok(E.length === 2 && E[0].g === "1×12 · 24 kg + 1×10 · 24 kg" && E[1].g === "1×6 · +5 kg", "2 " + show(r));
// 3. Préfixes de section et blocs chronométrés
r = P.parseProgram("Jeudi\nForce : Front Squat 4x4 @ 80%\nMetcon: AMRAP 15 min – 10 burpees, 15 wall balls, 20 double unders");
E = all(r);
ok(E.length === 2 && E[0].n === "Front Squat" && E[1].g === "15 min" && /wall balls/.test(E[1].e.note || ""), "3 " + show(r));
// 4. Tractions assistées : une aide, jamais un lest ; tractions avec une charge : un lest
r = P.parseProgram("Lundi\nTractions assistées 3x8 25kg\nTractions 3x5 12kg");
E = all(r);
ok(E[0].e.groups[0].load.kind === "assist" && E[1].g === "3×5 · +12 kg", "4 " + show(r));
// 5. Tableau : « Hold (s) », « Lest (kg) », « Rep range »
r = P.parseWorkbook([{ name: "S1", rows: [["Skills", "Sets", "Rep range", "Hold (s)", "Lest (kg)"], ["Back lever", "4", "", "12", ""], ["Dips", "3", "6-10", "", "15"]] }]);
E = all(r);
ok(E[0].g === "4×12 s" && E[1].g === "3×6-10 · +15 kg", "5 " + show(r));
// 6. Jours en colonnes (« | Mardi | Jeudi »), une case = un exercice complet
r = P.parseWorkbook([{ name: "Semaine 2", rows: [["", "Mardi", "Jeudi"], ["1", "Bench 5x5 @ 90kg", "Squat 5x5 @ 120kg"], ["2", "Rowing 4x8 @ 60kg", "Leg curl 3x12"]] }]);
E = all(r);
ok(E.length === 4 && E[0].w === "Semaine 2" && E[0].d === "Mardi" && E[1].d === "Mardi" && E[2].d === "Jeudi" && E[2].g === "5×5 · 120 kg", "6 " + show(r));
// 7. Colonne « Description » avec semaine et jour, distance à part
r = P.parseWorkbook([{ name: "Plan", rows: [["Semaine", "Jour", "Description", "Distance (km)"], ["1", "Mardi", "Footing 40 min", "7"], ["", "Jeudi", "Squat 3x5 @ 100kg", ""]] }]);
E = all(r);
ok(E.length === 2 && E[0].g === "40 min · 7 km" && E[1].g === "3×5 · 100 kg" && E[0].d !== E[1].d, "7 " + show(r));
// 8. Push press = famille développé militaire
ok(P.canon("Push Press").canon === "Développé militaire", "8 canon");
console.log("ÉCHECS :", JSON.stringify(fails, null, 1));
