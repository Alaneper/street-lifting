// Contrôle honnête : programmes INÉDITS, écrits après la mise au point, jamais utilisés pour régler l'import.
// Usage : node tests/prog_import_inedits.test.js [--detail]
const fs = require("fs"), path = require("path");
const { parseProgram, fmtGroup } = require("../src/prog_import.js");
const DIR = path.join(__dirname, "fixtures", "programmes_inedits");
const T = {
  H1: { days: 5, checks: [[/Lundi/, "Développé couché", 4, "10", "70 kg"], [/Mardi/, "Tractions", 4, "8", null], [/Mardi/, "Rowing", 4, "10", "60 kg"],
    [/Mercredi/, "Squat", 4, "8", "90 kg"], [/Jeudi/, "Élévations latérales", 4, "15", "8 kg"], [/Vendredi/, "Curl biceps", 4, "10", "30 kg"]] },
  H2: { days: 3, checks: [[/1/, "Développé couché", 4, "8", "75 kg"], [/1/, "Rowing", 3, "12", null], [/1/, "Développé militaire", 4, "12-10-8-6", null],
    [/2/, "Squat", 5, "5", "100 kg"], [/2/, "Soulevé jambes tendues", 3, "10", null], [/3/, "Soulevé de terre", 3, "5", "140 kg"], [/3/, "Tractions", 4, "max", null]] },
  H3: { days: 4, checks: [[/Lundi/, "Développé couché", 4, "6", null], [/Lundi/, "Tractions", 4, "6", null], [/Mardi/, "Squat", 4, "5", null],
    [/Mardi/, "Soulevé de terre roumain", 3, "8", null], [/Jeudi/, "Développé incliné", 4, "10-12", null], [/Jeudi/, "Tirage vertical", 4, "12", null],
    [/Vendredi/, "Hip thrust", 4, "10", null], [/Vendredi/, "Mollets", 4, "15", null]] },
  H4: { days: 3, checks: [[/1/, "Tractions", 2, "5", "+30 kg"], [/1/, "Dips", 3, "5", "+45 kg"], [/1/, "Squat", 4, "5", "110 kg"],
    [/1/, "Muscle-up", 10, "1", null], [/2/, "Tractions", 4, "10", null], [/2/, "Dips", 3, "8", "+40 kg"], [/3/, "Squat", 3, "5", "90 kg"]] },
};
const loadTxt = g => (g.load ? fmtGroup({ sets: 0, reps: 0, load: g.load }).split(" · ")[1] : null);
let tot = 0, ok = 0;
for (const [k, t] of Object.entries(T)) {
  const res = parseProgram(fs.readFileSync(path.join(DIR, k + ".txt"), "utf8"));
  const days = res.weeks.flatMap(w => w.days).filter(d => d.exos.length);
  const items = [[`${t.days} jours`, days.length >= t.days, `trouvé ${days.length}`]];
  for (const [dy, name, sets, reps, load] of t.checks) {
    const pool = days.filter(d => dy.test(d.label)).flatMap(d => d.exos);
    const hit = pool.find(e => e.canon === name && e.groups.some(g => g.sets === sets && String(g.reps) === reps && (!load || loadTxt(g) === load)));
    const near = pool.filter(e => e.canon === name).map(e => e.groups.map(fmtGroup).join(", "));
    items.push([`${name} ${sets}×${reps}${load ? " · " + load : ""}`, !!hit, near.length ? "lu : " + near.join(" | ") : "absent"]);
  }
  const o = items.filter(i => i[1]).length; tot += items.length; ok += o;
  console.log(`${k}  ${o}/${items.length}  (${Math.round(100 * o / items.length)} %) — reconnus ${res.stats.recognized}/${res.stats.exos}`);
  if (process.argv.includes("--detail")) items.filter(i => !i[1]).forEach(i => console.log("   KO", i[0], "→", i[2]));
}
console.log(`\nSCORE INÉDITS : ${ok}/${tot} (${Math.round(100 * ok / tot)} %)`);
