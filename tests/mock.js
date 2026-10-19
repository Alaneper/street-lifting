// Banc d'essai : simule le connecteur Google Sheets avec une prog de 7 blocs au format ATS.
(function(){
  const APP = "10OP7QRneqxxU1ad4BbVaYulLQUBDmaj7Hcu3n3IQBtA", COACH = "1PLTt-6Qb7kdPXTornMlyJfiH-Pxo3V-2FPD-BkRW2LU";
  const sheets = {}; // id -> {title -> 2D array}
  const fr = n => String(n).replace(".", ",");
  function grid(){ return []; }
  function put(g, r, c, arr){ while (g.length <= r) g.push([]); arr.forEach((v, i) => { const row = g[r]; while (row.length <= c + i) row.push(""); row[c + i] = v; }); }
  const HDR = ["MOUVEMENT ","VARIATION ","TEMPO","COMMENTAIRE DU COACH ","SÉRIES","RÉPÉTITIONS ","REPOS","%","CHARGE","E1RM","INTENSITÉ CIBLE ","","RPE S1","RPE DERNIÈRE SÉRIE ","ANGLE A FILMER","COMMENTAIRE ATHLÈTE "];
  const coach = {};
  for (let b = 1; b <= 7; b++) {
    const g = grid();
    put(g, 18, 2, ["BLOC ", String(b)]);
    for (let w = 1; w <= 4; w++) {
      const c = 2 + (w - 1) * 20, done = b < 7 || (b === 7 && w === 1), prog = (b - 1) * 4 + w; // semaines depuis le début
      put(g, 23, c, ["Semaine ", String(w)]);
      const sq = 85 + prog * 0.9, dp = 15 + prog * 1.05, pu = 12 + prog * 0.75;
      const S1 = [["RENFO","LOADED DEAD BUG","","Garde le dos plaqué au sol.","5","15\"","","","","","","","","","",""],
        ["SQUAT","COMP","","","1","3","3-5'","",fr(Math.round(sq*4)/4),fr(Math.round(sq*1.21*4)/4),"","",done?"6,5":"","","",""],
        ["SQUAT","COMP","","","3","5","3-5'","","-10%/-5%  ( "+fr(Math.round(sq*.92*4)/4)+" )","","","",done?"6,5":"",done?"7,5":"","",""],
        ["DIPS","TEMPO ","3/2/0","","4","4","3-5´","",fr(Math.round(dp*.5*4)/4),fr(Math.round(dp*1.1*4)/4),"","",done?"6,5":"",done?"7":"","",""],
        ["RENFO","LOW INCLINE DB BENCH PRESS","","","3","8-12","3'","",String(26 + Math.floor(prog/6)*2),"","","","","","",done ? [8,8,9].map(x=>x+(prog%4)).join(",")+"," : ""],
        ["RENFO","CURL BICEPS","","SUPERSET","3","8-12","2'","",String(14 + Math.floor(prog/8)),"","","","","","",done ? "10,10,9," : ""]];
      const S2 = [["RENFO","SCAPULAR CAR'S","","","2","5","","","","","","","","","",""],
        ["PULL UP","COMP","","","2","2","","",fr(Math.round(pu*.75*4)/4),fr(Math.round(pu*1.08*4)/4),"","",done?"6":"",done?"6,5":"","",""],
        ["PULL UP","Comp","","","4","4","3-5'","",fr(Math.round(pu*.5*4)/4),"","","",done?"6":"",done?"6,5":"","",""],
        ["RENFO","TIRAGE HORIZONTAL MACHINE","","Prise large marteau","3","8-12","3'","",fr(80+prog),"","","","","","",done?"12,11,10,":""]];
      const S3 = [["SQUAT","ZERCHER SQUAT","","","3","6-10","3-5'","",String(70+prog),"","","",done?"6":"",done?"6,5":"","",""],
        ["DIPS","COMP","","","1","3","2'","",fr(Math.round(dp*.8*4)/4),fr(Math.round(dp*1.12*4)/4),"","",done?"5":"","","",""],
        ["RENFO","LEG CURL","","SUPERSET","3","10-20","2'","",String(55+prog),"","","","","","",""]];
      const S4 = [["MUSCLE UP","COMP","","","5","1","","","elastique 3","","","",done?"7":"",done?"7,5":"","",""],
        ["PULL UP","PAUSED","2CT","","3","3","","",fr(Math.round(pu*.45*4)/4),"","","",done?"8,5":"",done?"9":"","",""],
        ["SQUAT","PAUSED","2CT","FOCUS TECHNIQUE","4","5","3-5'","",String(60+prog),"","","",done?"7":"",done?"7":"","",""],
        ["RENFO","RDL","","","3","8-12","2'","",String(60+prog),"","","","","","",done?"10,10,10,":""]];
      const blocks = [["Lundi","Séance 1",S1],["Mercredi","Séance 2",S2],["Jeudi","Séance 3",S3],["Samedi","Séance 4",S4]];
      let r = 25;
      for (const [jour, nom, rows] of blocks) {
        put(g, r, c, ["JOUR ", jour]); put(g, r + 1, c, [nom]); put(g, r + 2, c, HDR);
        rows.forEach((x, i) => put(g, r + 3 + i, c, x));
        put(g, r + 3 + rows.length + 1, c, ["RECAP ","POIDS DE CORPS ", done ? "73,1" : "", "", "29", "92741"]);
        r += rows.length + 8;
      }
      put(g, r + 2, c, ["Note ta semaine de 1 à 10 sur chaque critères "]);
      ["Sommeil ","Plaisir ","Motivation ","Fatigue ","Hydratation ","Alimentation "].forEach((k, i) => put(g, r + 3 + i, c, [k, done && b < 7 ? "7" : ""]));
    }
    coach["BLOC " + b + (b === 1 ? "  " : "")] = g;
  }
  coach["TUTORIEL"] = [["x"]]; coach["INFOS GENERALES"] = [["x"]];
  sheets[COACH] = coach;
  const today = new Date(), iso = d => d.toISOString().slice(0, 10), back = n => { const d = new Date(today); d.setDate(d.getDate() - n); return iso(d); };
  const poids = [["Date","Poids (kg)","Note"]]; for (let i = 80; i >= 0; i -= 1) if (i % 3 !== 1) poids.push([back(i), fr((74.4 - (80 - i) * 0.015 + Math.sin(i / 3) * 0.35).toFixed(1)), ""]);
  sheets[APP] = {
    PROFIL:[["Clé","Valeur","Note"],["prenom","Alane"],["sexe","H"],["naissance","2006-12-27"],["taille_cm","182"],["categorie","-80"],["coach_sheet_id",COACH],["mu_acquis","NON"],["date_objectif","2027-10-19"],["debut_street","2025-11-04"],["debut_coaching","2026-04-27"]],
    PR:[["Date","Mouvement","Charge (kg)","Reps","Note"],[back(150),"SQUAT","95","1",""],[back(90),"SQUAT","102,5","1",""],[back(0),"SQUAT","110","1","PR déclaré"],[back(120),"PULL","25","1",""],[back(0),"PULL","32,5","1",""],[back(100),"DIP","35","1",""],[back(0),"DIP","45","1",""]],
    POIDS:poids,
    OBJECTIFS:[["Mouvement","Objectif (kg)","Note"],["MU",""],["PULL","40"],["DIP","55"],["SQUAT","130"]],
    RECORDS:[["Type","Catégorie","Mouvement","Record (kg)","Détenteur","Source","Vérifié le"],["WR","-80","TOTAL","538,5","Aubin Chevillard (FRA)","https://rankings.officialstreetlifting.com/records/male/classes/-80kg","2026-10-19"],["WR","-80","PULL","120","Dmitrii Vlasov (RUS)","x","2026-10-19"],["WR","-80","DIP","175","Benjamin Detre (FRA)","x","2026-10-19"],["WR","-80","SQUAT","271,5","Michael Incoronato (ITA)","x","2026-10-19"],["NR BE","-80","PULL","100,25","François Conreur (BEL)","x","2026-10-19"],["NR BE","-80","DIP","150","François Conreur (BEL)","x","2026-10-19"],["NR BE","-80","SQUAT","220","Albert Israelyan (BEL)","x","2026-10-19"]],
    COMPETITIONS:[["Date","Nom","Lieu","Note","Statut"],["2026-11-14","NOAA BSLC","","Date à confirmer","À confirmer"],["2026-12-06","Rookie","","","Confirmée"]],
    SERIES:[["Date","Bloc","Semaine","Séance","Exercice","Charge (kg)","Reps par série","Source","Note"]],
    BLOCS:[["Bloc","Lundi de la semaine 1","Note"]], TENTATIVES:[["h"]], CHECKLIST:[["h"]], BILAN:[["h"]]
  };
  const parseRange = rng => { const m = rng.match(/^(?:'((?:[^']|'')+)'|([^!]+))!/); return {t:(m[1] || m[2]).replace(/''/g, "'")}; };
  const trim = g => g.map(r => { const x = r.slice(); while (x.length && (x[x.length - 1] === "" || x[x.length - 1] == null)) x.pop(); return x; });
  window.__calls = []; window.__sheets = sheets;
  const mcp = {
    async callTool(server, tool, input){
      window.__calls.push([tool, input && input.range]);
      await new Promise(r => setTimeout(r, 20));
      const book = sheets[input.spreadsheetId];
      if (tool === "get_spreadsheet") return {payload:{sheets:Object.keys(book).map(t => ({properties:{title:t}}))}};
      const {t} = parseRange(input.range), g = book[t] || (book[t] = [[]]);
      if (tool === "get_values") return {payload:{range:input.range, values:trim(g)}};
      if (tool === "append_values") { const start = g.length; input.values.forEach(v => g.push(v.map(x => typeof x === "number" ? fr(x) : x))); return {payload:{updates:{updatedRange:t + "!A" + (start + 1) + ":I" + g.length}}}; }
      if (tool === "update_values") { const m = input.range.match(/!([A-Z]+)(\d+)/), col = m[1].split("").reduce((a, ch) => a * 26 + ch.charCodeAt(0) - 64, 0) - 1, row = +m[2] - 1;
        input.values.forEach((v, i) => put(g, row + i, col, v.map(x => typeof x === "number" ? fr(x) : x))); return {payload:{updatedRange:input.range}}; }
      throw {code:"bad_request", message:"tool " + tool};
    }
  };
  const dl = {async save(o){ window.__saved = o.filename; return {status:"saved"}; }};
  window.claude = {use: async n => n === "mcp" ? mcp : n === "downloads" ? dl : null};
})();
