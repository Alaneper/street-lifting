// v42 : formats réels repérés chez des testeurs, réécrits avec des données INVENTÉES (aucune prog réelle dans le dépôt).
// Usage : node tests/prog_import_v42.test.js   → « ÉCHECS : [] » si tout est bon
const { parseProgram, parseWorkbook, fmtGroup, toGrid } = require("../src/prog_import.js");
const fails = [];
const all = r => r.weeks.flatMap(w => w.days.flatMap(d => d.exos.map(e => ({ ...e, day: d.label, week: w.label }))));
const g0 = e => e && fmtGroup(e.groups[0]);
function chk(label, cond, got) { if (!cond) fails.push(label + " → " + got); }

// 1. Notes téléphone « Nom / séries x reps / charge », sections en majuscules, charges vides, dégressif
const T1 = `Jour 1
Haut – Bras

PECTORAUX :

Développé couché / 4 x 5-7 / 30kg haltère
Dips / 3 x 9 / pdc
Écarté poulie basse / 3 x 10 / 12kg

Jour 2
Jambes avant – arrière

JAMBES :

Squat / 5 x 5 / 70kg barre
Leg curl / 3 x 10 - 12 / 35kg + dernière dégressif
Hack squat mollet / 3 x 20 / kg
Élévation lat. / 3 x 12-12-12 / 8kg dégressif
+ 15 minutes cardio`;
let r = parseProgram(T1), E = all(r);
chk("T1 2 jours", r.stats.days === 2, r.stats.days);
chk("T1 sections pas des jours", !r.weeks[0].days.some(d => /JAMBES|PECTORAUX/.test(d.label)), r.weeks[0].days.map(d => d.label));
chk("T1 couché nom+charge", g0(E.find(e => e.canon === "Développé couché")) === "4×5-7 · 30 kg", g0(E[0]));
chk("T1 dips pdc", g0(E.find(e => e.canon === "Dips")) === "3×9", g0(E.find(e => e.canon === "Dips")));
chk("T1 leg curl dégressif", /dégressif/.test((E.find(e => e.canon === "Leg curl") || {}).note || ""), (E.find(e => e.canon === "Leg curl") || {}).note);
chk("T1 mollets (pas hack squat)", !!E.find(e => e.canon === "Mollets") && !E.find(e => e.canon === "Hack squat"), E.map(e => e.canon));
chk("T1 tout reconnu", r.stats.recognized === r.stats.exos, `${r.stats.recognized}/${r.stats.exos}`);

// 2. Programme hybride : semaines « 1 à 3 », « Jours 5 », course, assistance « -12kg », dégressif entre parenthèses
const T2 = `Semaine 1 à 3
Jour 1 : Pecs / Dos
Développé couché barre / 4 x 6 / 60,5kg
Tractions / 3 x 7 / -12kg
Élévations latérales / 3 x 12 (10kg) + 12 (5kg)
Jour 2 : Fractionné
4 x 8 -> 30´accélérer/30´décélérer
2 minutes de repos/série
Jours 3 : Sortie EF
45min -> max 135bpm
+ gainage et abdos
Semaine 4 DELOAD
Jour 1 :
Squat léger / 3 x 5
Jour 2 : Sortie longue
6km`;
r = parseProgram(T2); E = all(r);
chk("T2 semaines 1,2,3,4", r.weeks.map(w => w.label).join(",") === "Semaine 1,Semaine 2,Semaine 3,Semaine 4", r.weeks.map(w => w.label));
chk("T2 Jours 3 lu", r.weeks[0].days.some(d => d.label === "Jour 3"), r.weeks[0].days.map(d => d.label));
const tr = E.find(e => e.canon === "Tractions");
chk("T2 assistance (pas 12 kg)", tr && tr.groups[0].load && tr.groups[0].load.kind === "assist", JSON.stringify(tr && tr.groups[0].load));
const el = E.find(e => e.canon === "Élévations latérales");
chk("T2 dégressif parenthèses", el && g0(el) === "3×12 · 10 kg" && /puis 12 à 5 kg/.test(el.note || ""), g0(el) + " " + (el && el.note));
chk("T2 fractionné", E.some(e => e.canon === "Fractionné" && g0(e) === "4×8"), E.filter(e => e.cat === "cardio").map(g0));
chk("T2 sortie EF 45 min", E.some(e => e.canon === "Course à pied" && g0(e) === "45 min"), E.filter(e => e.cat === "cardio").map(g0));
chk("T2 sortie longue 6 km", E.some(e => e.week === "Semaine 4" && g0(e) === "6 km"), E.filter(e => e.week === "Semaine 4").map(g0));
chk("T2 couché virgule", E.some(e => e.canon === "Développé couché" && e.groups[0].load && e.groups[0].load.v === 60.5), "");

// 3. Street workout : circuit en tours, reps seules, lest, élastique, par jambe
const T3 = `Organisation : circuit de 4 tours, 2 min de repos.

1. Tractions : 6 répétitions
2. Pompes lestées : 18 répétitions avec 10 kg.
3. Tractions australiennes : 12 répétitions
4. Curl biceps avec élastique de 20kg de résistance: 15 répétitions.

Séances jambes (lundi et jeudi)

1. Fentes avec sac lesté 8kg: 3 × 12 répétitions par jambe.`;
r = parseProgram(T3); E = all(r);
chk("T3 tractions 4 tours", g0(E.find(e => e.canon === "Tractions")) === "4×6", g0(E.find(e => e.canon === "Tractions")));
chk("T3 pompes lest", g0(E.find(e => e.canon === "Pompes")) === "4×18 · +10 kg", g0(E.find(e => e.canon === "Pompes")));
chk("T3 australiennes ≠ tractions", !!E.find(e => e.canon === "Rowing inversé"), E.map(e => e.canon));
const cu = E.find(e => e.canon === "Curl biceps");
chk("T3 élastique pas une charge", cu && cu.groups[0].load && cu.groups[0].load.kind === "band", JSON.stringify(cu && cu.groups[0].load));
const fe = E.find(e => e.canon === "Fentes");
chk("T3 fentes lest + par jambe", fe && g0(fe) === "3×12 · +8 kg" && fe.side, g0(fe) + " side=" + (fe && fe.side));
chk("T3 2 séances", r.stats.days === 2, r.stats.days);

// 4. Tableau de coach collé (power) : en-têtes sans « Exercice », SEANCE n, « 6 à 8 », « 8/c », charge + %
const T4 = ["SEMAINE 2", "SEANCE 1", "\tsérie\trep\tInc\tcharge\t%\tRPE", "Competition squat\t3\t4\t2,5\t120\t70%\t", "Tirage appui poitrine machine\t3\t6 à 8\t\t\t\t8 à 9",
  "SEANCE 2", "\tsérie\trep\tInc\tcharge\t%\tRPE", "2ct pause bench\t4\t2\t0\t70\t72%\t", "Squat bulgare haltère\t2\t10/c\t\t\t\t7"].join("\n");
r = parseProgram(T4); E = all(r);
chk("T4 2 séances", r.stats.days === 2 && r.weeks[0].label === "Semaine 2", r.weeks.map(w => w.label + ":" + w.days.map(d => d.label)));
const sq = E.find(e => e.canon === "Squat");
chk("T4 squat charge + % en note", sq && g0(sq) === "3×4 · 120 kg" && /70 %/.test(sq.note || ""), g0(sq) + " " + (sq && sq.note));
chk("T4 « 6 à 8 » et RPE « 8 à 9 »", E.some(e => e.canon === "Rowing" && g0(e) === "3×6-8" && e.rpe === "8-9"), E.map(g0));
chk("T4 2ct = pause", E.some(e => e.canon === "Développé couché pause"), E.map(e => e.canon));
const bu = E.find(e => e.canon === "Fentes bulgares");
chk("T4 8/c = par côté", bu && g0(bu) === "2×10" && bu.side, g0(bu));
const wb = parseWorkbook([{ name: "Bloc 3", rows: T4.split("\n").map(l => l.split("\t")) }]);
chk("T4 classeur .xlsx", wb.stats.exos === 4 && wb.stats.recognized === 4, JSON.stringify(wb.stats));

// 5. Tableau de suivi : « rep » = « 2*8+ », résultats par semaine en colonnes (gardés en note)
const T5 = ["Exercices\trep\tsemaine 1\tsemaine 2", "Curl biceps\t2*10+\t15kg*10 15kg*8\t15kg*11 15kg*9", "Gainage\t3*30s"].join("\n");
r = parseProgram(T5); E = all(r);
chk("T5 2*10+", g0(E[0]) === "2×10+", g0(E[0]));
chk("T5 pas de fausses semaines", r.weeks.length === 1, r.weeks.map(w => w.label));
chk("T5 résultats en note", /Fait semaine 1 : 15kg\*10 15kg\*8/.test(E[0].note || ""), E[0].note);
chk("T5 ligne courte gardée", E.length === 2, E.length);

// 6. Écriture dans l'onglet : élastique, assistance et « par côté » ne deviennent pas des kilos
const grid = toGrid(parseProgram(T3 + "\n" + "Tractions / 3 x 5 / -15kg"), "", "t");
const rowOf = n => grid.find(x => x[0] === n);
chk("T6 élastique sans charge", rowOf("Curl biceps") && rowOf("Curl biceps")[4] === "" && /Élastique 20 kg/.test(rowOf("Curl biceps")[8]), JSON.stringify(rowOf("Curl biceps")));
chk("T6 par côté noté", rowOf("Fentes") && /Par côté/.test(rowOf("Fentes")[8]), JSON.stringify(rowOf("Fentes")));

console.log("ÉCHECS :", JSON.stringify(fails, null, 1));
process.exitCode = fails.length ? 1 : 0;
