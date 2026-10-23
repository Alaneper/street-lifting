// Programmes AVEUGLES : écrits après toute la mise au point, lancés UNE fois, jamais utilisés pour régler l'import.
const fs = require("fs"), path = require("path");
const { parseProgram, fmtGroup } = require("../src/prog_import.js");
const DIR = path.join(__dirname, "fixtures", "programmes_aveugles");
const T = {
  B1: { days: 4, checks: [[/1/, "Squat", 1, "3", null], [/1/, "Squat", 3, "5", "-10 %"], [/1/, "Presse à cuisses", 3, "10-12", null],
    [/2/, "Développé couché", 3, "6", "-12 %"], [/2/, "Développé incliné", 3, "10", "30 kg"], [/3/, "Soulevé de terre", 1, "2", "180 kg"],
    [/3/, "Soulevé de terre", 2, "4", "160 kg"], [/3/, "Hip thrust", 3, "8", "120 kg"], [/3/, "Tractions", 3, "6", "+10 kg"], [/4/, "Dips", 4, "10", null]] },
  B2: { days: 2, checks: [[/A/, "Squat", 3, "5", "80 kg"], [/A/, "Développé couché", 3, "5", "60 kg"], [/A/, "Rowing", 3, "8", "50 kg"],
    [/B/, "Squat", 3, "5", "82.5 kg"], [/B/, "Développé militaire", 3, "5", "35 kg"], [/B/, "Soulevé de terre", 1, "5", "100 kg"]] },
  B3: { days: 3, checks: [[/Lundi/, "Squat", 4, "6", "70 %"], [/Lundi/, "Tractions", 4, "8", null], [/Mercredi/, "Soulevé de terre", 3, "5", "75 %"],
    [/Mercredi/, "Dips", 3, "10", null], [/Vendredi/, "Développé couché", 5, "5", "75 %"], [/Vendredi/, "Rowing", 4, "10", null]], weeks: 2 },
};
const loadTxt = g => (g.load ? fmtGroup({ sets: 0, reps: 0, load: g.load }).split(" · ")[1] : null);
let tot = 0, ok = 0;
for (const [k, t] of Object.entries(T)) {
  const res = parseProgram(fs.readFileSync(path.join(DIR, k + ".txt"), "utf8"));
  const w1 = res.weeks[0] || { days: [] };
  const items = [[`${t.days} jours`, w1.days.filter(d => d.exos.length).length >= t.days, `trouvé ${w1.days.filter(d => d.exos.length).length}`]];
  if (t.weeks) items.push([`${t.weeks}+ semaines`, res.weeks.length >= t.weeks, `trouvé ${res.weeks.length}`]);
  for (const [dy, name, sets, reps, load] of t.checks) {
    const pool = w1.days.filter(d => dy.test(d.label)).flatMap(d => d.exos);
    const hit = pool.find(e => e.canon === name && e.groups.some(g => g.sets === sets && String(g.reps) === reps && (!load || loadTxt(g) === load)));
    const near = pool.filter(e => e.canon === name).map(e => e.groups.map(fmtGroup).join(", "));
    items.push([`${name} ${sets}×${reps}${load ? " · " + load : ""}`, !!hit, near.length ? "lu : " + near.join(" | ") : "absent"]);
  }
  const o = items.filter(i => i[1]).length; tot += items.length; ok += o;
  console.log(`${k}  ${o}/${items.length}  (${Math.round(100 * o / items.length)} %)`);
  items.filter(i => !i[1]).forEach(i => console.log("   KO", i[0], "→", i[2]));
}
console.log(`\nSCORE AVEUGLE : ${ok}/${tot} (${Math.round(100 * ok / tot)} %)`);
