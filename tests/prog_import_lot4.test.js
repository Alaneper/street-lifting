// Lot 4 (v65) : leçons du lot « neutre » (progs écrites par un assistant séparé). Cas généraux, pas les progs elles-mêmes.
const { parseProgram, parseWorkbook, fmtGroup } = require("../src/prog_import.js");
const fails = []; let n = 0;
const flat = r => r.weeks.flatMap(w => w.days.map(d => ({ w: w.label, d: d.label, exos: d.exos })));
const sets = e => e.groups.map(g => fmtGroup(g));
const t = (name, ok, info) => { n++; if (!ok) fails.push(name + (info ? " → " + info : "")); };

// préfixes de messagerie : le jour écrit dans un message est un vrai jour
let r = flat(parseProgram("[12/10 08:14] Coach: Salut\nLUNDI - Push\nDC 4x8 @80\n[12/10 08:17] Coach: MERCREDI - Pull\nRowing barre 4x8 @70\n12/10/2026, 08:20 - Coach: Squat 5x5 @100"));
t("chat : 2 jours détectés", r.length === 2 && r[1].d === "Mercredi", JSON.stringify(r.map(x => x.d)));
// échauffements : jamais des exercices
r = flat(parseProgram("Lundi\nEchauff: 10 min rameur + 2x15 élastiques\n(echauf 2x10 barre vide)\nWarm-up : 5 min vélo\nSquat 5x5 @100"));
t("échauffements ignorés", r[0].exos.length === 1 && r[0].exos[0].name === "Squat", JSON.stringify(r[0].exos.map(e => e.name)));
// charge d'abord : 100kg x 5 x 3 = 3 séries de 5
let e = flat(parseProgram("Lundi\ndc 100kg x 5 x 3"))[0].exos[0];
t("100kg x 5 x 3", e.groups.length === 1 && e.groups[0].sets === 3 && e.groups[0].reps === "5" && Number(e.groups[0].load.v) === 100, JSON.stringify(e.groups));
// liste de reps : 8/8/6/6 = 2×8 + 2×6
e = flat(parseProgram("Lundi\noh press 8/8/6/6 @40"))[0].exos[0];
t("8/8/6/6", e.canon === "Développé militaire" && sets(e).join("|") === "2×8 · 40 kg|2×6 · 40 kg", sets(e).join("|") + " " + e.canon);
// dégressif : une charge par série
e = flat(parseProgram("Lundi\nPec deck 12/10/8 45 → 35 → 25 kg"))[0].exos[0];
t("dégressif 45→35→25", sets(e).join("|") === "1×12 · 45 kg|1×10 · 35 kg|1×8 · 25 kg", sets(e).join("|"));
// abréviation « trac » seule = tractions ; « tracs corde » ne l'est pas
t("trac = tractions", parseProgram("Lundi\ntrac 3 séries de 10").weeks[0].days[0].exos[0].canon === "Tractions");
// « Jour A – Push »
r = flat(parseProgram("Jour A - Push\nDC 4x8 @80\nJour B - Legs\nSquat 5x5 @100"));
t("Jour A / Jour B", r.length === 2 && r[0].d === "Jour A" && r[1].d === "Jour B", JSON.stringify(r.map(x => x.d)));
// CSV avec guillemets : la virgule d'une note ne coupe pas la cellule
r = flat(parseProgram('Day,Exercise,Sets,Reps,Weight,Notes\nMon,Warmup,2,10,bar,"empty bar, then 95lb"\nMon,DB row,5,10,60lb,"each arm, dumbbells"\nMon,Squat,3,5,225lb,'));
t("CSV guillemets : échauffement ignoré, côté lu", r[0].exos.length === 2 && r[0].exos[0].side === true, JSON.stringify(r[0].exos.map(x => [x.name, x.side])));
// export d'app : série « W » et ligne de volume ignorées
r = flat(parseProgram("Date;Semaine;Jour;Exercice;Série;Reps;Charge (kg);RIR\n06/10/2026;S1;Haut;Squat;W;10;50;\n06/10/2026;S1;Haut;Squat;1;6;100;2\n06/10/2026;S1;Haut;Squat;2;6;100;2\n06/10/2026;S1;Haut;Volume total;;;1200;"));
t("export : W et volume ignorés", r[0].exos.length === 1 && sets(r[0].exos[0]).join() === "1×6 · 100 kg,1×6 · 100 kg", JSON.stringify(r[0].exos.map(x => [x.name, sets(x)])));
// un onglet = un jour, semaines en colonnes (dont « S4 deload »)
let wb = parseWorkbook([{ name: "Jour A - Push", rows: [["Exercice", "S1", "S2", "S4 deload"], ["Dips", "4x8 +10kg", "4x8 +12,5kg", "3x8"]] }, { name: "Jour B - Legs", rows: [["Exercice", "S1", "S2", "S4 deload"], ["Squat", "5x5 @100kg", "5x5 @105kg", "3x5 @80kg"]] }]);
t("onglets-jours × semaines en colonnes", wb.weeks.length === 3 && wb.weeks.every(w => w.days.length === 2), JSON.stringify(wb.weeks.map(w => w.days.map(d => d.label))));
// plan « une ligne par semaine, colonnes par mouvement »
wb = parseWorkbook([{ name: "Plan", rows: [["1RM Squat (kg)", "140"], ["Sem", "Squat S", "Squat R", "Squat %", "Squat kg", "Bench S", "Bench R", "Bench %", "Remarque"], ["S1", "5", "5", "0.7", "98", "4", "8", "0.65"], ["S2", "5", "5", "0.725", "101.5", "4", "8", "0.675", "Deload"]] }]);
const w2 = flat(wb)[1];
t("plan par mouvement", wb.weeks.length === 2 && sets(w2.exos[0])[0] === "5×5 · 101.5 kg · 72.5 %" && sets(w2.exos[1])[0] === "4×8 · 67.5 %", JSON.stringify(w2.exos.map(sets)));
console.log(`LOT 4 : ${n - fails.length}/${n}`); console.log("ÉCHECS :", JSON.stringify(fails, null, 1));
process.exit(fails.length ? 1 : 0);
