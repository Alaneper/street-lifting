// Lit un JSON [{id, text | sheets}] sur l'entrée standard, applique le lecteur d'import (src/prog_import.js), écrit ce que l'aperçu afficherait.
const { parseProgram, parseWorkbook, fmtGroup } = require(process.argv[2]);
let s = ""; process.stdin.on("data", d => s += d).on("end", () => {
  const out = {};
  for (const c of JSON.parse(s)) {
    let r; try { r = c.text != null ? parseProgram(c.text) : parseWorkbook(c.sheets); } catch (e) { out[c.id] = { error: String(e) }; continue; }
    out[c.id] = { weeks: r.weeks.map(w => ({ label: w.label, days: w.days.filter(d => d.exos.length).map(d => ({ label: d.label, exos: d.exos.map(e => ({
      canon: e.canon, name: e.name, rpe: e.rpe, tempo: e.tempo, side: !!e.side,
      sets: e.groups.flatMap(g => {
        const f = fmtGroup(g), load = g.load || g.km ? f.split(" · ").slice(1).join(" · ") : "";   // la distance d'une course s'affiche comme sa « charge »
        const n = Math.min(300, Math.max(1, (+g.sets) | 0));
        return Array(n).fill((g.reps == null ? "" : String(g.reps)) + (g.amrap && g.reps !== "max" ? "+" : "") + "|" + load);
      }) })) })) })) };
  }
  console.log(JSON.stringify(out));
});
