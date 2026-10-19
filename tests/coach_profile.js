// Lecture du profil dans la prog du coach (extrait réel du bloc 7, lignes 1 à 11)
const fs = require("fs"), path = require("path");
const app = fs.readFileSync(path.join(__dirname, "..", "src", "app.html"), "utf8"), js = app.match(/<script>([\s\S]*)<\/script>/)[1];
const base = js.slice(js.indexOf("const LIFTS"), js.indexOf("const BW_LIFTS")) + js.slice(js.indexOf("const CATS"), js.indexOf("const JOUR_IDX"))
  + js.slice(js.indexOf("const norm ="), js.indexOf("const isNumTxt"));
const layer = fs.readFileSync(path.join(__dirname, "..", "src", "pwa_layer.js"), "utf8");
const fn = layer.slice(layer.indexOf("function parseCoachProfile"), layer.indexOf("Object.assign(ACT"));
const pre = fn.slice(0, fn.indexOf("function onboard"));
const v = [[],["","","","","","","MAX ACTUELS","","","","","","OBJECTIF DU BLOC "],["","","","","","","MU","0"],["","","","","","","PU","35"],["","","","","","","DIPS","40"],["","","","","","","SQUAT","110"],[],["","","","","","","PROFIL "],["","","","","","","TAILLE ","","182"],["","","","","","","POIDS","","73,2"],["","","","","","","ÂGE ","","19"]];
eval(base + pre + `
const out = parseCoachProfile(v), ok = JSON.stringify(out) === JSON.stringify({pr_PULL:35, pr_DIP:40, pr_SQUAT:110, taille:182, poids:73.2, categorie:-80});
console.log(ok ? "OK " : "KO ", "profil depuis la prog", JSON.stringify(out));
const n = prenomOf("PRESER Alane"); console.log(n === "Alane" ? "OK " : "KO ", "prénom depuis le titre", n);
process.exit(ok && n === "Alane" ? 0 : 1);`);
