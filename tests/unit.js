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
/* v28 · IPF GL : exemples officiels du PDF IPF 2020 (coefficient et points), puis valeurs de contrôle */
eq("GL exemple IPF (H equipped 92,04 kg, 1035)", glPoints(1035, 92.04, "H", "equipped"), 112.855365);
eq("GL H classic 80 kg 600", glPoints(600, 80, "H", "classic").toFixed(2), "84.62");
eq("GL H classic 87 kg 600", glPoints(600, 87, "H", "classic").toFixed(2), "81.12");
eq("GL F classic 63 kg 400", glPoints(400, 63, "F", "classic").toFixed(2), "87.51");
eq("GL F equipped 63 kg 500", glPoints(500, 63, "F", "equipped").toFixed(2), "90.27");
eq("GL sous 40 kg (H) : pas de points", glPoints(300, 39.9, "H", "classic"), null);
/* catégories : la limite appartient à la catégorie */
eq("street 80,00 → −80", catAuto(80, CATS_H), -80);
eq("street 80,01 → −87", catAuto(80.01, CATS_H), -87);
eq("street 120 → +101", catAuto(120, CATS_H), 101);
eq("IPF 83,00 → −83", catAuto(83, catsIpfFor("H", false)), -83);
eq("IPF 52 kg adulte → −59", catAuto(52, catsIpfFor("H", false)), -59);
eq("IPF 52 kg junior → −53", catAuto(52, catsIpfFor("H", true)), -53);
eq("IPF F 84,01 → +84", catAuto(84.01, catsIpfFor("F", false)), 84);
/* âges IPF en année civile */
eq("2004 en 2026 → Junior + Open", ageCats("2004-03-14", "2026-10-23"), ["JR","OPEN"]);
eq("2008 en 2026 → Sub-junior", ageCats("2008-12-31", "2026-01-01"), ["SJ"]);
eq("14 ans pas encore atteints", ageCats("2012-12-01", "2026-10-23"), []);
eq("14 ans atteints", ageCats("2012-10-01", "2026-10-23"), ["SJ"]);
eq("1986 en 2026 → Master 1 + Open", ageCats("1986-06-01", "2026-10-23"), ["M1","OPEN"]);
eq("1966 en 2026 → Master 3 seul", ageCats("1966-06-01", "2026-10-23"), ["M3"]);
eq("1956 en 2026 → Master 4", ageCats("1956-06-01", "2026-10-23"), ["M4"]);
process.exit(fails ? 1 : 0);`);
