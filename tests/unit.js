// Tests sur des extraits réels de la prog (BLOC 6 S4, BLOC 7 S3)
const fs = require("fs");
const html = fs.readFileSync(require("path").join(__dirname, "..", "src", "app.html"), "utf8");
const js = html.match(/<script>([\s\S]*)<\/script>/)[1];
const start = js.indexOf("const LIFTS"), stop = js.indexOf("/* =====================================================================\n   DONNÉES PERSO");
const pre = js.slice(start, stop).replace(/function toast[\s\S]*?\n}\n/, "");
const helpers = js.slice(js.indexOf("function fixJours"), js.indexOf("function parseBloc"));
const trendSrc = js.slice(js.indexOf("function trend4w"), js.indexOf("function volumeWeeks"));
const document = {querySelector:()=>null};
eval(pre + helpers + trendSrc + `
let fails = 0; const eq = (n, a, b) => { const ok = JSON.stringify(a) === JSON.stringify(b); if (!ok) fails++; console.log(ok ? "OK " : "KO ", n, ok ? "" : JSON.stringify(a)); };
eq("charges notées à la place des reps", setsFromComment({commentaire:"85,90,95,", reps:"5"}, 95), [{r:5,c:85},{r:5,c:90},{r:5,c:95}]);
eq("reps normales", setsFromComment({commentaire:"12,10,9,", reps:"8-12"}, 28), [{r:12,c:28},{r:10,c:28},{r:9,c:28}]);
eq("3*15", setsFromComment({commentaire:"3*15", reps:"10-15"}, 34), [{r:15,c:34},{r:15,c:34},{r:15,c:34}]);
eq("absurde rejeté", setsFromComment({commentaire:"200,200", reps:"5"}, 30), null);
const ss = [1,2,3,4].flatMap(w => [["Lundi",0],["Mercredi",1],[w===3?"Mercredi":"Jeudi",2],["Samedi",3]].map(([j,i]) => ({semaine:String(w), idx:i, jour:j})));
fixJours(ss); eq("jour en double corrigé", ss.filter(s => s.semaine==="3").map(s => s.jour), ["Lundi","Mercredi","Jeudi","Samedi"]);
eq("noms", ["SCAPULAR CAR'S","RDL","STEATED DB OHP","HIP TRUST BAR","45° BACK EXTENSION"].map(title), ["Scapular Car's","RDL","Seated DB OHP","Hip Thrust Bar","45° Back Extension"]);
const P = (d, v) => ({date:d, e1rm:v});
eq("tendance 4 sem.", Math.round(trend4w([P("2026-08-01",50),P("2026-09-20",60),P("2026-10-01",62),P("2026-10-15",66)])), 10);
eq("aberrant ignoré", Math.round(trend4w([P("2026-09-01",60),P("2026-09-20",600),P("2026-10-15",66)])), 10);
process.exit(fails ? 1 : 0);`);
