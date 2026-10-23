// Test de l'import de programmes sur le jeu de test (programmes synthétiques, tests/fixtures/programmes).
// Usage : node tests/prog_import.test.js [--detail]   → score par programme et score global.
// Ne touche ni à l'app ni aux données de personne.
const fs = require("fs"), path = require("path");
const { parseProgram, fmtGroup } = require("../src/prog_import.js");
const DIR = path.join(__dirname, "fixtures", "programmes");

// Vérité terrain : ce qu'un humain lit dans chaque programme.
// [semaine (regex ou null), jour (regex), exercice reconnu, séries, reps, charge attendue (texte) ou null]
const T = {
  P1: { days: 4, checks: [
    [null, /Lundi/, "Squat", 4, "4", "160 kg"], [null, /Lundi/, "Squat pause", 3, "3", "120 kg"],
    [null, /Lundi/, "Développé couché", 4, "5", "110 kg"], [null, /Lundi/, "Dips", 3, "8", "+20 kg"],
    [null, /Mardi/, "Soulevé de terre", 3, "3", "195 kg"], [null, /Mardi/, "Tractions", 4, "5", "+15 kg"],
    [null, /Jeudi/, "Développé militaire", 4, "6", "55 kg"], [null, /Vendredi/, "Fentes", 3, "10", "24 kg"],
  ], notes: [/deload/i, /max actuels/i] },
  P2: { weeks: 6, checks: [
    [/Semaine 1/, /Jour 1/, "Squat", 5, "5", "72 %"], [/Semaine 1/, /Jour 2/, "Soulevé de terre", 4, "5", "75 %"],
    [/Semaine 1/, /Jour 3/, "Dips", 3, "10", "+10 kg"], [/Semaine 3/, /Jour 2/, "Soulevé de terre", 4, "3", "82.5 %"],
    [/Semaine 6/, /Jour 1/, "Squat", 1, "max", "87.5 %"], [/Semaine 1/, /Jour 3/, "Développé militaire", 4, "8", null],
  ], weekNotes: [[/Semaine 4/, /deload/i]] },
  P3: { days: 4, checks: [
    [null, /Séance A/, "Tractions", 3, "5", "-10 %"], [null, /Séance A/, "Muscle-up", 5, "2", null],
    [null, /Séance B/, "Dips", 3, "5", "-10 %"], [null, /Séance C/, "Squat", 5, "5", "100 kg"],
    [null, /Séance C/, "Tractions", 5, "6", null], [null, /Séance D/, "Muscle-up", 6, "1", "+5 kg"],
  ], notes: [/traction \+50kg/i] },
  P4: { days: 3, checks: [
    [null, /PUSH 1/, "Développé incliné", 4, "8-10", null], [null, /PUSH 1/, "Élévations latérales", 4, "15", null],
    [null, /PULL 1/, "Tractions", 4, "max", null], [null, /PULL 1/, "Curl biceps", 3, "12", null],
    [null, /PULL 1/, "Curl biceps", 3, "10", null], [null, /LEGS 1/, "Squat", 4, "6-8", null], [null, /LEGS 1/, "Mollets", 5, "12", null],
  ] },
  P5: { weeks: 3, checks: [
    [/Week 1/, /Jour 1/, "Squat", 5, "5", "70 %"], [/Week 1/, /Jour 1/, "Squat", 1, "max", "70 %"],
    [/Week 1/, /Jour 1/, "Presse à cuisses", 3, "12", null], [/Week 1/, /Jour 2/, "Développé incliné", 3, "10", "60 lb"],
    [/Week 1/, /Jour 2/, "Tractions", 4, "max", null], [/Week 2/, /Jour 3/, "Soulevé de terre", 3, "3", "85 %"],
  ] },
  P6: { days: 3, checks: [
    [null, /Lundi/, "Squat", 5, "5", "120 kg"], [null, /Lundi/, "Développé couché", 4, "8", null],
    [null, /Lundi/, "Rowing", 4, "10", null], [null, /Mercredi/, "Soulevé de terre", 3, "3", "180 kg"],
    [null, /Mercredi/, "Hip thrust", 4, "10", null], [null, /Vendredi/, "Développé militaire", 3, "12", "30 kg"],
  ] },
  P7: { days: 4, checks: [
    [null, /Lundi/, "Squat", 5, "3", "85 %"], [null, /Lundi/, "Tractions", 5, "3", null],
    [null, /Mercredi/, "Développé couché", 6, "2", "90 %"], [null, /Mercredi/, "Dips", 4, "4", "+30 kg"],
    [null, /Jeudi/, "Soulevé de terre", 4, "4", "80 %"], [null, /Jeudi/, "Good morning", 3, "8", null],
  ] },
  P8: { weeks: 8, checks: [
    [/Semaine 8/, /Lundi/, "Squat", 4, "4", "80 %"], [/Semaine 8/, /Mercredi/, "Soulevé de terre", 4, "3", "82.5 %"],
    [/Semaine 7/, /Vendredi/, "Développé couché", 4, "3", "85 %"], [/Semaine 4/, /./, "Squat", 3, "2", "87.5 %"],
    [/Semaine 2/, /./, "Squat", 1, "1", "190 kg"],
  ], notes: [/202\.5/] },
  P9: { days: 2, checks: [
    [null, /./, "Squat gobelet", 3, "10", null], [null, /./, "Développé militaire", 2, "12", null],
    [null, /Séance B/, "Soulevé de terre roumain", 3, "10", null], [null, /Séance B/, "Tractions", 3, "max", null],
    [null, /Séance B/, "Fentes", 3, "8", null],
  ] },
};

const loadTxt = g => (g.load ? fmtGroup({ sets: 0, reps: 0, load: g.load }).split(" · ")[1] : null);
const detail = process.argv.includes("--detail");
let tot = 0, okTot = 0;
const report = {};
for (const [k, t] of Object.entries(T)) {
  const res = parseProgram(fs.readFileSync(path.join(DIR, k + ".txt"), "utf8"));
  const items = [];
  if (t.days) { const d = Math.max(...res.weeks.map(w => w.days.filter(x => x.exos.length).length), 0); items.push([`${t.days} jours d'entraînement`, d >= t.days, `trouvé ${d}`]); }
  if (t.weeks) items.push([`${t.weeks} semaines`, res.weeks.length >= t.weeks, `trouvé ${res.weeks.length}`]);
  for (const [wk, dy, name, sets, reps, load] of t.checks) {
    const pool = res.weeks.filter(w => !wk || wk.test(w.label)).flatMap(w => w.days.filter(d => dy.test(d.label))).flatMap(d => d.exos);
    const hit = pool.find(e => e.canon === name && e.groups.some(g => g.sets === sets && String(g.reps) === reps && (!load || loadTxt(g) === load)));
    const near = pool.filter(e => e.canon === name).map(e => e.groups.map(fmtGroup).join(", "));
    items.push([`${name} ${sets}×${reps}${load ? " · " + load : ""}`, !!hit, near.length ? "lu : " + near.join(" | ") : "exercice absent"]);
  }
  for (const re of t.notes || []) items.push([`remarque « ${re.source} » gardée`, res.notes.concat(...res.weeks.flatMap(w => [w.notes, ...w.days.map(d => d.notes)]), res.weeks.flatMap(w => w.days.flatMap(d => d.exos.map(e => e.raw)))).some(n => re.test(n)), ""]);
  for (const [wk, re] of t.weekNotes || []) items.push([`note « ${re.source} » sur ${wk.source}`, res.weeks.some(w => wk.test(w.label) && w.notes.some(n => re.test(n))), ""]);
  const ok = items.filter(i => i[1]).length;
  tot += items.length; okTot += ok;
  report[k] = { ok, n: items.length, stats: res.stats, fails: items.filter(i => !i[1]) };
  console.log(`${k}  ${ok}/${items.length}  (${Math.round(100 * ok / items.length)} %)  — exercices reconnus ${res.stats.recognized}/${res.stats.exos}`);
  if (detail) items.filter(i => !i[1]).forEach(i => console.log("   KO", i[0], "→", i[2]));
}
console.log(`\nSCORE GLOBAL : ${okTot}/${tot} (${Math.round(100 * okTot / tot)} %)`);

