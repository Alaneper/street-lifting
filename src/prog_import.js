/* Import de programmes (v1, sans IA) — module autonome, PAS encore branché dans l'app.
   Entrée : texte collé (notes, tableau Excel/Sheets collé, message, forum…).
   Sortie : { weeks:[{label, notes:[], days:[{label, notes:[], exos:[{raw, name, canon, cat, groups:[{sets,reps,load,amrap}], rpe, tempo, note}]}]}], notes:[], meta:{} }
   Aucune donnée n'est écrite : l'utilisateur valide l'aperçu avant tout enregistrement. */
(function (root) {
  "use strict";

  const NUM_WORDS = { un:1, une:1, deux:2, trois:3, quatre:4, cinq:5, six:6, sept:7, huit:8, neuf:9, dix:10, onze:11, douze:12, quinze:15, vingt:20, trente:30 };
  const DAYS = { lundi:"Lundi", mardi:"Mardi", mercredi:"Mercredi", jeudi:"Jeudi", vendredi:"Vendredi", samedi:"Samedi", dimanche:"Dimanche",
    lun:"Lundi", mar:"Mardi", mer:"Mercredi", jeu:"Jeudi", ven:"Vendredi", sam:"Samedi", dim:"Dimanche",
    monday:"Lundi", tuesday:"Mardi", wednesday:"Mercredi", thursday:"Jeudi", friday:"Vendredi", saturday:"Samedi", sunday:"Dimanche" };

  // Dictionnaire d'exercices : du plus précis au plus général. cat = couleur dans l'app.
  const EXOS = [
    // Cardio (v40) : suivi en minutes, hors total et hors classement
    [/rameur|rowing\s*machine|row\s*erg\b/, "Rameur", "cardio"],
    [/elliptique|elliptical|cross\s*trainer/, "Elliptique", "cardio"],
    [/escaliers?\b|stairmaster|stepper|stair\s*climb/, "Escalier", "cardio"],
    [/natation|swim|\bnage\b/, "Natation", "cardio"],
    [/\bv[ée]lo\b|\bbike\b|cycling|spinning/, "Vélo", "cardio"],
    [/\bmarche\b|(?<!farmer\s)\bwalk\b/, "Marche", "cardio"],
    [/\bcourse\b|running|jogging|footing|tapis/, "Course à pied", "cardio"],
    [/cardio|hiit|zone\s*2/, "Cardio", "cardio"],
    // v42 : course (programmes hybrides), mollets avant les squats (« hack squat mollet »), pauses « 2ct »
    [/fractionn|interval|\bvma\b/, "Fractionné", "cardio"],
    [/sortie\s*(longue|ef\b)|endurance\s*fondamentale|^ef\b/, "Course à pied", "cardio"],
    [/mollet|calf|calves/, "Mollets", ""],
    [/\d\s*ct\b.*squat|squat.*\d\s*ct\b/, "Squat pause", "squat"],
    [/pause\s*squat|squat\s*pause/, "Squat pause", "squat"],
    [/front\s*squat/, "Front squat", "squat"],
    [/hack\s*squat/, "Hack squat", "squat"],
    [/goblet|gobelet/, "Squat gobelet", "squat"],
    [/bulgar|split\s*squat/, "Fentes bulgares", "squat"],
    [/squat|^sq\b|\bsq$/, "Squat", "squat"],
    [/dead\s*bug|bird\s*dog/, "Gainage", ""],
    [/(soulev[ée]|sdt|dead\w*).*roumain|\brdl\b|romanian/, "Soulevé de terre roumain", "deadlift"],
    [/stiff|jambes?\s*tendues/, "Soulevé jambes tendues", "deadlift"],
    [/deficit|déficit/, "Soulevé de terre déficit", "deadlift"],
    [/soulev[ée]\s*de\s*terre|deadlift|\bdead\b|\bsdt\b|\bdl\b/, "Soulevé de terre", "deadlift"],
    [/good\s*morning/, "Good morning", "deadlift"],
    [/hip.?thrust|glute\s*bridge|pont\s*fessier/, "Hip thrust", "squat"],
    [/muscle.?up|^mup?\b|\bmup?$/, "Muscle-up", "mu"],
    [/tractions?\s*australienne|australian|inverted\s*row|rowing\s*invers/, "Rowing inversé", "pull"],
    [/traction|pull.?ups?\b|chin.?ups?/, "Tractions", "pull"],
    [/\bdips?\b/, "Dips", "dip"],
    [/(dc|d[ée]v\w*|bench|banc|press)\s*(couch[ée]\s*)?(halt[eè]res\s*)?incl|incl\w*\s*(db|dumbbell|halt|barbell|bench|press|d[ée]v)/, "Développé incliné", "bench"],
    [/(dc|d[ée]v\w*\s*couch[ée]|bench|banc|\bbp\b).*(serr|close)|close.?grip/, "Développé couché prise serrée", "bench"],
    [/(dc|d[ée]v\w*\s*couch[ée]|bench|banc|\bbp\b).*pause|banc\s*pause|pause.*(bench|banc|couch)|\d\s*ct\b.*(bench|banc)/, "Développé couché pause", "bench"],
    [/pec\w*\s*(push|machine)|chest\s*press|presse\s*pectorale/, "Développé machine", "bench"],
    [/^(dc|banc|couch[ée])\b|d[ée]velopp[ée]\s*couch[ée]|d[ée]v\w*\.?\s*couch|bench|\bbp\b|\bbanc\b|\bdc\b|machine\s*convergente/, "Développé couché", "bench"],
    [/militaire|military|\bohp\b|overhead|strict\s*press|presse?\s*([ée]paules|shoulder)|shoulder\s*press|d[ée]v\w*\.?\s*([ée]paules?|militaire)/, "Développé militaire", "bench"],
    [/tirage\s*menton|upright/, "Tirage menton", ""],
    [/appui\s*poitrine|chest.?supported|pendlay/, "Rowing", "pull"],
    [/tirage\s*(vertical|poitrine|nuque)|lat\s*pull|pull.?down\b(?!s)/, "Tirage vertical", "pull"],
    [/rowing|\brow\b|tirage\s*horizontal|trx/, "Rowing", "pull"],
    [/face\s*pull/, "Face pull", ""],
    [/pull\s*over/, "Pull-over", ""],
    [/fente|lunge/, "Fentes", "squat"],
    [/presse(?!\s*[ée]paule)|legs?\s*press|hack\s*press/, "Presse à cuisses", "squat"],
    [/legs?\s*ext|quadri\w*\s*machine|extensions?\s*(des\s*)?jambes|quad\s*ext/, "Leg extension", "squat"],
    [/legs?\s*curl|legs?\s*ischio|ham\w*\s*curl|ischio\w*\s*(machine|couch|assis)|lying\s*curl/, "Leg curl", "deadlift"],
    [/curl/, "Curl biceps", ""],
    [/triceps|skull\s*crusher|kick.?back|barre\s*au\s*front|barre\s*front|pushdown|extension\s*triceps|extensions?\s*(a\s*la\s*)?(poulie|corde|nuque|halt\w*)/, "Triceps", ""],
    [/[ée]l[ée]v\w*\.?\s*lat|lat(eral)?\s*raise|elev\s*lat|oiseau\s*lat/, "Élévations latérales", ""],
    [/oiseau|rear\s*delt|arriere\w*\s*(d.\s*)?epaules?/, "Oiseau", ""],
    [/[ée]cart[ée]|fly|pec\s*deck|butterfly|papillon/, "Écarté", "bench"],
    [/shrug/, "Shrug", ""],
    [/mollet|calf|calves/, "Mollets", ""],
    [/adducteurs?|adductor/, "Adducteurs", ""],
    [/abducteurs?|abductor|abduction/, "Abducteurs", ""],
    [/back\s*ext|extension\s*lombaire/, "Extensions lombaires", ""],
    [/farmer/, "Farmer walk", ""],
    [/gainage|planche|plank|hollow|l.?sit/, "Gainage", ""],
    [/crunch|sit.?ups?|abdo|relev[ée]s?\s*de\s*jambes|leg\s*raise|ab\w*\s*wheel/, "Abdos", ""],
    [/pompes?|push.?ups?/, "Pompes", "bench"],
    [/burpee|swing|emom|amrap\s*\d+\s*min|sled|corde|jumping/, "Conditionnement", ""],
  ];

  const strip = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const num = s => parseFloat(String(s).replace(",", "."));
  const toNum = w => { if (w == null) return null; const t = strip(w); return NUM_WORDS[t] ?? (isNaN(num(t)) ? null : num(t)); };

  function canon(name) {
    const n = strip(name);
    for (const [re, c, cat] of EXOS) if (re.test(n)) return { canon: c, cat };
    return { canon: null, cat: "" };
  }

  function cleanLine(l) {
    return l.replace(/^\s*[=#~]{2,}\s*|\s*[=#~]{2,}\s*$/g, "").replace(/\*\*|__/g, "").replace(/^\s*[-*•·]\s*(\[[ x]?\]\s*)?/i, "").replace(/^\s*\[[ x]?\]\s*/i, "")
      .replace(/^\s*[A-Z]\d\)\s*/, "").replace(/^\s*\d{1,2}[.)]\s+(?=[A-Za-zÀ-ÿ])/, "").replace(/[\u{1F300}-\u{1FAFF}☀-➿]/gu, "").trim();
  }

  // ---------- lecture d'un schéma de séries ----------
  const RE_PCT_X = /(\d+(?:[.,]\d+)?)\s*%\s*[x×*]\s*(\d+)(?:\s*[x×*]\s*(\d+))?(\+)?/gi;          // 65%x5, 70%x3x3
  const RE_SXR = /(?<![\d.,])(\d+|un|une|deux|trois|quatre|cinq|six)\s*[x×*]\s*(\d+(?:\s*-\s*\d+)*|max\b|amrap\b)(\+)?/gi;  // 4x5, 3 x 8-10, 4xmax
  const RE_LXR = /(?<![\d.,%])(\d{2,3}(?:[.,]\d+)?)\s*(kg|lbs?)?\s*[x×*]\s*(\d+)(?!\s*[x×*%])/gi;  // 140 x5 (charge x reps)
  const RE_PROSE = /(\d+|un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|douze|quinze)\s+s[ée]ries?\s+de\s+(\d+|un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|douze|quinze)/gi;

  const RE_SETS_OF = /(\d+|un|une|deux|trois|quatre|cinq|six)\s*(?:s[ée]ries?|sets?)\s*(?:x|×|of|de)?\s*(\d+(?:\s*-\s*\d+)*|max\b|amrap\b)(?:\s*(?:reps?|r[ée]p[ée]titions?)\b)?/gi;  // 4 séries x 8 reps, 4 sets of 6
  const RE_LIST = /(?<![\d.,\/])(\d{1,2}(?:\s*\/\s*\d{1,2}){2,})(?![\d\/])/g;   // 5/5/4/4/3
  const RE_SINGLE = /(?:(\d+|un|une|deux|trois)\s+)?(?:heavy\s+|lourde?s?\s+)?\b(singles?|doubles?|triples?)\b|heavy\s+(\d+)\b/gi;

  function readLoad(s) {
    const t = s.replace(/\(([^)]*)\)/g, " ");
    let m;
    // v42 : élastique (résistance ou aide, jamais une charge) ; « assistance 14 » (ex. « / -14kg » aux tractions)
    if (/[ée]lastique|\bbands?\b|\bbande\b/i.test(s)) { const v = s.match(/(\d+(?:[.,]\d+)?)\s*kg/i); return { kind: "band", v: v ? num(v[1]) : null, u: "kg" }; }
    if ((m = s.match(/assist\w*\s*(?:de\s*)?(\d+(?:[.,]\d+)?)\s*(?:kg)?/i))) return { kind: "assist", v: num(m[1]), u: "kg" };
    if ((m = t.match(/bw\s*\+\s*(\d+(?:[.,]\d+)?)/i))) return { kind: "lest", v: num(m[1]), u: "kg" };
    if ((m = t.match(/@\s*(\d+(?:[.,]\d+)?)\s*%/))) return { kind: "pct", v: num(m[1]) };
    if ((m = t.match(/[àa@]\s*-\s*(\d+(?:[.,]\d+)?)\s*%/))) return { kind: "rel", v: -num(m[1]) };
    if ((m = t.match(/@\s*\+\s*(\d+(?:[.,]\d+)?)\s*(kg|lbs?)?/i))) return { kind: "lest", v: num(m[1]), u: (m[2] || "kg").replace(/s$/, "") };
    if ((m = t.match(/(?:^|\s)\+\s*(\d+(?:[.,]\d+)?)\s*(?:(kg|lbs?)\b|(?=\s*(?:$|[,:;)(\/]|\d)))/i))) return { kind: "lest", v: num(m[1]), u: (m[2] || "kg").replace(/s$/, "") };
    if ((m = t.match(/@\s*(\d+(?:[.,]\d+)?)(?![\d.,]|\s*%)\s*(kg|lbs?)?/i)) && !/rpe\s*$/i.test(t.slice(0, m.index)) && (m[2] || num(m[1]) > 10)) return { kind: "abs", v: num(m[1]), u: (m[2] || "kg").replace(/s$/, "") };
    if ((m = t.match(/(\d+(?:[.,]\d+)?)\s*(kg|lbs?)\b/i))) return { kind: "abs", v: num(m[1]), u: m[2].toLowerCase().replace(/s$/, "") };
    if ((m = t.match(/(?:\s|^)[àa]\s+(\d{2,3}(?:[.,]\d+)?)(?![\d.,]|\s*%)/))) return { kind: "abs", v: num(m[1]), u: "kg" };
    if ((m = t.match(/(?<![\d.,])(\d+(?:[.,]\d+)?)\s*%/))) return { kind: "pct", v: num(m[1]) };
    for (const pm of s.matchAll(/\(([^)]*)\)/g)) { if (/\d/.test(pm[1]) && !/\(/.test(pm[1]) && /^\s*[+@]?\s*\d|^\s*bw/i.test(pm[1])) { const r = readLoad(" " + pm[1]); if (r) return r; } }
    if ((m = s.match(/\((\d{2,3}(?:[.,]\d+)?)\s*(kg|lbs?)?\)/i))) return { kind: "abs", v: num(m[1]), u: (m[2] || "kg").toLowerCase().replace(/s$/, "") };   // « opener (190) »
    if ((m = t.match(/\s(\d{2,3}(?:[.,]\d+)?)\s*$/))) return { kind: "abs", v: num(m[1]), u: "kg" };  // « 3x8 80 » en fin de ligne
    if ((m = t.match(/\s(\d{2,3}(?:[.,]\d+)?)\s+(?:@\s*(?:10|[5-9](?:[.,]5)?)|rpe\s*\d+(?:[.,]\d+)?(?:\s*-\s*\d+(?:[.,]\d+)?)?)\s*$/i))) return { kind: "abs", v: num(m[1]), u: "kg" };  // « 3x3 140 @8 », « 3x3 140 rpe 8 »
    return null;
  }

  // Cardio (v40) : « vélo 10 min », « 20' de marche », « course 25 minutes 4 km ». Seulement si le nom est du cardio :
  // « repos 2 min » ou « EMOM 10 min » ne deviennent pas des exercices.
  const RE_DUR = /(?<![\d.,])(\d+(?:[.,]\d+)?)\s*(minutes?|mins?|mn|h(?:eures?)?|['’])(?![a-zà-ÿ])/i;
  function readDuration(s) {
    const m = RE_DUR.exec(s); if (!m) return null;
    const nameOf = t => t.replace(/[:\-—–,;@(){}]+/g, " ").replace(/\s+/g, " ").trim();
    let nm = nameOf(s.slice(0, m.index));
    if (canon(nm).cat !== "cardio") nm = nameOf(s.slice(m.index + m[0].length).split(/[,.;]|\s(?:puis|then)\s/i)[0]);
    if (canon(nm).cat !== "cardio") return null;
    const min = /^h/i.test(m[2]) ? num(m[1]) * 60 : num(m[1]);
    const km = (s.match(/(\d+(?:[.,]\d+)?)\s*km\b/i) || [])[1] || null;
    return { name: nm, groups: [{ sets: 1, reps: String(Math.round(min * 10) / 10).replace(".", ",") + " min", load: null, amrap: false, km: km }], rpe: null, tempo: null, side: false };
  }

  // Renvoie {name, groups, rpe, tempo, note} ou null si aucun schéma.
  let ROUNDS = 0;   // v42 : « circuit de 3 tours » → séries des exercices écrits en reps seules
  function readExo(seg) {
    let s = seg.trim();
    // v42 : « 4 x 10 (12kg) + 10 (6kg) » = dégressif dans chaque série : 1re charge gardée, détail en note
    const drop = s.match(/(\d+)\s*\(\s*(\d+(?:[.,]\d+)?)\s*kg\s*\)\s*\+\s*(\d+)\s*\(\s*(\d+(?:[.,]\d+)?)\s*kg\s*\)/i);
    if (drop) s = s.replace(drop[0], drop[1] + " " + drop[2] + "kg");
    const hits = [];
    let m;
    RE_PCT_X.lastIndex = 0;
    while ((m = RE_PCT_X.exec(s))) hits.push({ i: m.index, end: m.index + m[0].length, g: m[3] ? { sets: +m[2], reps: m[3] } : { sets: 1, reps: m[2] }, load: { kind: "pct", v: num(m[1]) }, amrap: !!m[4] });
    RE_SXR.lastIndex = 0;
    while ((m = RE_SXR.exec(s))) {
      if (hits.some(h => m.index < h.end && m.index + m[0].length > h.i)) continue;
      const a = toNum(m[1]); if (a == null || a > 15) continue;
      const reps = /max|amrap/i.test(m[2]) ? "max" : m[2].replace(/\s/g, "");
      hits.push({ i: m.index, end: m.index + m[0].length, g: { sets: a, reps }, amrap: reps === "max" || !!m[3] });
    }
    RE_LXR.lastIndex = 0;
    while ((m = RE_LXR.exec(s))) {
      if (hits.some(h => m.index < h.end && m.index + m[0].length > h.i)) continue;
      if (num(m[1]) <= 15) continue;
      hits.push({ i: m.index, end: m.index + m[0].length, g: { sets: 1, reps: m[3] }, load: { kind: "abs", v: num(m[1]), u: (m[2] || "kg").replace(/s$/, "") } });
    }
    const add = (re, f) => { re.lastIndex = 0; let q; while ((q = re.exec(s))) { if (hits.some(h => q.index < h.end && q.index + q[0].length > h.i)) continue; const h = f(q); if (h) hits.push({ i: q.index, end: q.index + q[0].length, ...h }); } };
    add(RE_SETS_OF, q => { const a = toNum(q[1]); if (a == null || a > 15) return null; const reps = /max|amrap/i.test(q[2]) ? "max" : q[2].replace(/\s/g, ""); return { g: { sets: a, reps }, amrap: reps === "max" }; });
    add(RE_LIST, q => { const l = q[1].replace(/\s/g, "").split("/"); return { g: { sets: l.length, reps: l.every(x => x === l[0]) ? l[0] : l.join("/") } }; });
    RE_SINGLE.lastIndex = 0;
    while ((m = RE_SINGLE.exec(s))) {
      if (hits.some(h => m.index < h.end && m.index + m[0].length > h.i)) continue;
      const reps = m[3] ? +m[3] : ({ single: 1, double: 2, triple: 3 })[strip(m[2]).replace(/s$/, "")];
      hits.push({ i: m.index, end: m.index + m[0].length, g: { sets: toNum(m[1]) || 1, reps: String(reps) } });
    }
    RE_PROSE.lastIndex = 0;
    while ((m = RE_PROSE.exec(s))) if (!hits.some(h => m.index < h.end && m.index + m[0].length > h.i)) hits.push({ i: m.index, end: m.index + m[0].length, g: { sets: toNum(m[1]), reps: String(toNum(m[2])) } });
    if (!hits.length) {   // v42 : « Tractions : 7 répétitions » (street workout, circuits)
      const q = s.match(/(?<![\d.,])(\d{1,3})\s*(?:r[ée]p[ée]titions?|reps?)\b/i);
      if (q && !/repos|rest\b/i.test(s.slice(0, q.index))) hits.push({ i: q.index, end: q.index + q[0].length, g: { sets: ROUNDS || 1, reps: q[1] } });
    }
    if (!hits.length) return readDuration(s);
    hits.sort((a, b) => a.i - b.i);
    // charge de chaque groupe : texte entre la fin du groupe et le début du suivant
    hits.forEach((h, k) => {
      if (!h.load) { const tail = s.slice(h.end, k + 1 < hits.length ? hits[k + 1].i : s.length); h.load = readLoad(" " + tail) || (k === 0 ? readLoad(" " + s.slice(0, h.i)) : null); }
    });
    let name = s.slice(0, hits[0].i).replace(/\s+(@\s*)?\d+(?:[.,]\d+)?\s*%\s*([:\-—–]\s*)?$/, "").replace(/\s\+\s*\d+(?:[.,]\d+)?\s*(kg|lbs?)?/gi, "").replace(/\d+(?:[.,]\d+)?\s*(kg|lbs?)?\s*$/i, "")
      .replace(/(\s|^)(puis|then|et|ensuite)\s*$/i, "").replace(/[:\-—–,@(]+\s*$/, "").trim();
    const rpe = (s.match(/rpe\s*(\d+(?:[.,]\d+)?(?:\s*-\s*\d+(?:[.,]\d+)?)?)/i) || s.match(/@\s*(10|[5-9](?:[.,]5)?)(?![\d.,]|\s*(?:%|kg|lbs?))/i) || [])[1] || null;
    const tempo = (s.match(/tempo\s*(\d-\d-[\dx](?:-\d)?)/i) || [])[1] || null;
    const side = /\/\s*(jambe|bras|c[oô]t[ée])|par\s*(bras|jambe|c[oô]t[ée])|chaque\s*(bras|jambe|c[oô]t[ée])|\/\s*leg|per side|\d\s*\/\s*c\b/i.test(s);
    const groups = hits.map(h => ({ ...h.g, load: h.load || null, amrap: !!h.amrap }));
    // v42 : lest porté (« pompes lestées … 11 kg », « sac lesté 10kg ») ; indications gardées en note
    if (/lest[ée]|\bsac\b|gilet|ceinture/i.test(s)) groups.forEach(g => { if (g.load && g.load.kind === "abs") g.load = { ...g.load, kind: "lest" }; });
    const note = [];
    if (drop) note.push(`dégressif : ${drop[1]} reps à ${drop[2].replace(".", ",")} kg puis ${drop[3]} à ${drop[4].replace(".", ",")} kg`);
    else if (/d[ée]gressi|drop\s*set/i.test(s)) note.push(/derni[eè]re/i.test(s) ? "dernière série en dégressif" : "dégressif");
    if (/derni[eè]re\W+(s[ée]rie\W+)?([àa]\s*l.)?[ée]chec/i.test(s)) note.push("dernière série à l'échec");
    else if (/[àa]\s*l.\s*[ée]chec|to failure/i.test(s)) note.push("à l'échec");
    if (/sur\s*chaque/i.test(s)) note.push("sur chaque");
    const ct = s.match(/(\d)\s*ct\b/i); if (ct) note.push("pause " + ct[1] + " temps");
    return { name, groups, rpe, tempo, side, note: note.join(" · ") || null };
  }

  function mkExo(raw, ex) {
    const c = canon(ex.name);
    return { raw: raw.trim(), name: ex.name || c.canon || "?", canon: c.canon, cat: c.cat, groups: ex.groups, rpe: ex.rpe, tempo: ex.tempo, side: ex.side, note: ex.note || null };
  }

  // Une ligne peut contenir plusieurs exercices (« A / B », « A ; B », « A 3x12, B 3x12 »).
  const ADD_ON = /^(back.?off|top\s*set|warm.?up|[ée]chauff\w*|puis|then|et|ensuite|pareil)\b/i;
  function readExoLine(line) {
    const out = [];
    // v42 : « Nom / 4 x 8 / 50kg » (notes téléphone) : le nom, le schéma et la charge sont recollés ;
    // « A 3x12 / B 3x12 » reste deux exercices.
    const LOADISH = /^(-\s*\d|\d+(?:[.,]\d+)?\s*(kg|lbs?)\b|\d+(?:[.,]\d+)?$|kg\b|lbs?\b|pdc\b|bw\b|poids\s*du\s*corps|[ée]lastique|\+|halt|barre\b|machine\b)/i;
    const hasNm = ex => ex && ex.name && /[a-zà-ÿ]{2,}/i.test(ex.name) && !ADD_ON.test(ex.name.trim());
    const bigs = []; let pend = null;
    for (const t of line.split(/\s+\/\s*|\s*\/\s+|\s*;\s*/).map(x => x.trim())) {
      if (!t) continue;
      const ex = readExo(t);
      if (ex && !hasNm(ex) && pend != null) { bigs.push(pend + " : " + t); pend = null; continue; }
      if (!ex && LOADISH.test(t) && bigs.length && pend == null) { bigs[bigs.length - 1] += " " + (/^-\s*\d/.test(t) ? "assistance " + t.replace(/^-\s*/, "") : t); continue; }
      if (pend != null) { bigs.push(pend); pend = null; }
      if (!ex && /[a-zà-ÿ]{2,}/i.test(t)) { pend = t; continue; }
      bigs.push(t);
    }
    if (pend != null) bigs.push(pend);
    for (const big of bigs) {
      const parts = big.split(/,\s+/);
      let cur = null, pending = "";
      for (const p0 of parts) {
        const p = pending ? pending + " " + p0 : p0;
        const ex = readExo(p);
        if (!ex) { if (cur) cur.raw += ", " + p0; else if (canon(p0).canon) pending = p0; continue; }
        pending = "";
        let name = ex.name;
        // « then 3x10 incline DB 60lb » : le nom est après le schéma
        if (!canon(name).canon) {
          const after = p.replace(/^.*?\d\s*[x×]\s*(\d+|max|amrap)\+?/i, "").replace(/\d+(?:[.,]\d+)?\s*(kg|lbs?|%)/gi, "");
          if (canon(after).canon && !ADD_ON.test(after.trim())) { ex.name = after.trim(); name = ex.name; }
        }
        const hasName = name && /[a-zà-ÿ]{2,}/i.test(name) && !ADD_ON.test(name.trim());
        if (hasName && (canon(name).canon || !cur)) { cur = mkExo(p, ex); out.push(cur); }
        else if (cur) { cur.groups.push(...ex.groups); cur.raw += ", " + p0; if (!cur.rpe) cur.rpe = ex.rpe; }
        else { cur = mkExo(p, ex); out.push(cur); }
      }
    }
    return out;
  }

  // ---------- titres de jour / semaine ----------
  function readHeader(line) {
    const l = line.replace(/\*\*|__/g, "").trim();
    let m;
    if ((m = l.match(/^(sem(?:aines?)?|weeks?|s)\s*(\d+)\b\s*(\([^)]*\))?\s*[:\-—]?\s*(.*)$/i)) && !/^s\s*\d+\s*x/i.test(l)) {
      const up = (m[4] || "").match(/^(?:à|a|au|-|–|to)\s*(\d+)\b\s*[:\-—]?\s*(.*)$/i);   // v42 : « Semaine 1 à 3 »
      return { type: "week", label: (strip(m[1]).startsWith("w") ? "Week " : "Semaine ") + m[2], key: "w" + m[2], rest: up ? up[2] : m[4], extra: m[3] || "", upto: up && +up[1] > +m[2] && +up[1] - +m[2] < 12 ? +up[1] : null };
    }
    if ((m = l.match(/^(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b\s*[:\-—–,]?\s*(.*)$/i)))
      return { type: "day", label: DAYS[strip(m[1])], key: DAYS[strip(m[1])], rest: m[2] };
    if ((m = l.match(/^(lun|mar|mer|jeu|ven|sam|dim)\.?\s+(.*)$/i)) && /\d/.test(m[2]))
      return { type: "day", label: DAYS[strip(m[1])], key: DAYS[strip(m[1])], rest: m[2] };
    if ((m = l.match(/^(mon|tues?|wed|thu(?:rs?)?|fri|sat|sun)\b\.?\s*(?:[:\-—–]\s*)?(.*)$/i)) && (/^[A-Z]{3}/.test(l) || /^\w+\.?\s*([:\-—–]|$)/.test(l))) {
      const d = { mon: "Lundi", tue: "Mardi", tues: "Mardi", wed: "Mercredi", thu: "Jeudi", thur: "Jeudi", thurs: "Jeudi", fri: "Vendredi", sat: "Samedi", sun: "Dimanche" }[strip(m[1])];
      return { type: "day", label: d, key: d, rest: m[2] };
    }
    if ((m = l.match(/^(day|jours?|j)\s*(\d+)\b\s*(.*)$/i)))
      return { type: "day", label: "Jour " + m[2], key: "Jour " + m[2], rest: m[3].replace(/^(accessor(y|ies)|accessoires?)\s*/i, "").replace(/^[:\-—]\s*/, "") };
    if ((m = (l.match(/^(?:s[ée]ances?|workout|training|routine)\s+([a-z0-9]+)\b\s*(.*)$/i) || l.match(/^entra[iî]nement\s+(\d+|[a-z])\b\s*(.*)$/i))))
      return { type: "day", label: "Séance " + m[1].toUpperCase(), key: "Séance " + m[1].toUpperCase(), rest: m[2] };
    if ((m = l.match(/^(push|pull|legs|leg day|jambes|upper|lower|haut du corps|bas du corps|full ?body)(?![-\w])(?!\s*(?:ups?|overs?|downs?|day\s*\d*\s*:?\s*\d|over)\b)\s*(\d*)\s*(.*)$/i)) && !/\d\s*(?:[x×]\s*\d|s[ée]ries?|sets?)/i.test(l))
      return { type: "day", split: true, label: (m[1].toUpperCase() + " " + m[2]).trim(), key: (m[1].toUpperCase() + " " + m[2]).trim(), rest: m[3] };
    return null;
  }

  const NOTES_HDR = /^(notes?|remarques?|tentatives|objectifs?|nutrition|mon avis)\b.*:?\s*$/i;

  // ---------- tableau collé ----------
  // v42 : en-tête reconnu par « Exercice » ou par « Séries » + « Reps » (tableau de coach copié, colonne du nom sans titre) ;
  // plusieurs tableaux empilés sous « SEANCE n » ; colonnes « Semaine 1, 2… » = résultats notés (gardés en note).
  const isHeadRow = r => r.some(c => /^exerci[cs]es?$/i.test(c)) || (r.some(c => /^(s[ée]ries?|sets?)$/i.test(c)) && r.some(c => /^(reps?|r[ée]p[ée]titions?)$/i.test(c)));
  function tableCols(r) {
    const H = r.map(c => strip(c));
    const col = re => H.findIndex(c => re.test(c));
    const C = { w: col(/^(semaine|week|sem)\.?$/), d: col(/^(jour|day|seance)/), e: col(/^exerci/), s: col(/^(series?|sets?)$/), r: col(/^(reps?|repetitions?)$/),
      p: col(/%|charge|load|kg|poids/), ch: col(/charge|load|^kg$|\(kg\)|poids|weight/), pc: col(/%|pourcent/), rpe: col(/rpe/), rest: col(/repos|rest/), n: col(/note|remarque/),
      res: H.map((h, i) => /^(semaine|week|sem|s)\s*\d+$/.test(h) ? i : -1).filter(i => i >= 0), H: r };
    if (C.e < 0) C.e = C.s > 0 ? C.s - 1 : 0;
    return C;
  }
  function cellLoad(pcell) {
    if (!pcell || pcell === "-" || !/\d/.test(pcell)) return null;
    return /bw\s*\+/i.test(pcell) ? { kind: "lest", v: num(pcell.replace(/bw\s*\+/i, "")), u: "kg" }
      : /%/.test(pcell) ? { kind: "pct", v: num(pcell) } : /^\d/.test(pcell) ? { kind: "abs", v: num(pcell), u: /lb/i.test(pcell) ? "lb" : "kg" } : null;
  }
  function parseTable(lines, res, d) {
    const rows = lines.map(l => l.split(d).map(c => c.trim()));
    const hi = rows.findIndex(isHeadRow);
    if (hi < 0) return false;
    let curWeek = null, curDay = null;
    const single = r => { const f = r.filter(Boolean); return f.length === 1 ? readHeader(cleanLine(f[0])) : null; };
    rows.slice(0, hi).forEach(r => { const h = single(r); if (h && h.type === "week") { curWeek = h.label; return; } if (h && h.type === "day") { curDay = h.label; return; } const t = r.filter(Boolean).join(" · "); if (t) res.notes.push(t); });
    // valeurs de « TM » : ligne de titres suivie d'une ligne de nombres
    for (let i = 0; i < hi - 1; i++) if (rows[i].some(c => /\btm\b|max/i.test(c)) && rows[i + 1].every(c => !c || /^\d/.test(c)))
      rows[i].forEach((c, k) => { if (c && rows[i + 1][k]) res.meta[c] = num(rows[i + 1][k]); });
    let C = null;
    for (const r of rows.slice(hi)) {
      if (!r.some(Boolean)) continue;
      if (isHeadRow(r)) { C = tableCols(r); continue; }
      const h = single(r);
      if (h && h.type === "week") { curWeek = h.label; curDay = null; continue; }
      if (h && h.type === "day") { curDay = h.label + (h.rest ? "" : ""); continue; }
      const wk = ensureWeek(res, C.w >= 0 && r[C.w] ? "Semaine " + r[C.w] : curWeek || "Programme");
      const ex = C.e >= 0 ? r[C.e] || "" : "";
      if (!ex || ex === "-" || ex.length < 2 || !/[a-z]/i.test(ex) || /deload|repos/i.test(ex) && (C.s < 0 || !/\d/.test(r[C.s] || ""))) {
        const note = r.filter(c => c && c !== "-").slice(1).join(" · "); if (note) wk.notes.push(note); continue;
      }
      const day = ensureDay(wk, C.d >= 0 && r[C.d] ? r[C.d].replace(/^j\s*(\d+)$/i, "Jour $1") : curDay || "Séance");
      let sets = C.s >= 0 ? toNum(r[C.s]) : null, repsRaw = C.r >= 0 ? r[C.r] || "" : "", side = false, m;
      const notes = [];
      if (sets == null && (m = repsRaw.match(/^\s*(\d+)\s*[x×*]\s*(.+)$/))) { sets = +m[1]; repsRaw = m[2]; }   // « 2*8+ »
      if (/\/\s*c\b|\/\s*c[oô]t|par\s*c[oô]t|\/\s*(jambe|bras)/i.test(repsRaw)) { side = true; repsRaw = repsRaw.replace(/\s*(\/|par)\s*(c[oô]t[ée]s?|c|jambe|bras)\b\.?/i, ""); }
      let amrap = /amrap|max/i.test(repsRaw);
      if (!amrap && /\d\s*\+\s*$/.test(repsRaw)) { amrap = true; repsRaw = repsRaw.replace(/\s*\+\s*$/, ""); }
      repsRaw = repsRaw.replace(/(\d)\s*(?:à|a)\s*(\d)/g, "$1-$2");
      let load;
      if (C.ch >= 0 && C.pc >= 0 && C.ch !== C.pc) { load = cellLoad(r[C.ch]) || cellLoad(r[C.pc]); if (load && load.kind !== "pct" && /\d/.test(r[C.pc] || "")) notes.push(r[C.pc].replace(/\s*%$/, " %")); }
      else load = cellLoad(C.p >= 0 ? r[C.p] : "");
      C.res.forEach(k => { if (r[k]) notes.push("Fait " + C.H[k].toLowerCase() + " : " + r[k]); });
      if (C.n >= 0 && r[C.n]) notes.push(r[C.n]);
      const c = canon(ex);
      const rpe = C.rpe >= 0 && r[C.rpe] && r[C.rpe] !== "-" ? r[C.rpe].replace(/(\d)\s*(?:à|a)\s*(\d)/g, "$1-$2") : null;
      day.exos.push({ raw: r.join(" | "), name: ex, canon: c.canon, cat: c.cat,
        groups: [{ sets: sets || 1, reps: amrap && /max|amrap/i.test(repsRaw) ? "max" : repsRaw, load, amrap }],
        rpe, rest: C.rest >= 0 ? r[C.rest] || null : null, note: notes.join(" · ") || null, tempo: null, side });
    }
    return true;
  }

  function ensureWeek(res, label) {
    let w = res.weeks.find(x => x.label === label);
    if (!w) { w = { label, notes: [], days: [] }; res.weeks.push(w); }
    return w;
  }
  function ensureDay(week, label) {
    let d = week.days.find(x => x.label === label);
    if (!d) { d = { label, notes: [], exos: [] }; week.days.push(d); }
    return d;
  }

  // ---------- point d'entrée ----------
  function parseProgram(text) {
    const res = { weeks: [], notes: [], meta: {} };
    const raw = String(text || "").replace(/\r/g, "");
    const lines = raw.split("\n");
    for (const d of ["\t", ";", ","]) {
      const tl0 = lines.filter(l => l.split(d).length >= 3);
      if (!(tl0.length >= (d === "\t" ? 2 : 3) && tl0.some(l => isHeadRow(l.split(d).map(c => c.trim()))))) continue;
      const tl = d === "\t" ? lines.filter(l => l.split(d).length >= 2 || (l.trim() && readHeader(cleanLine(l)))) : tl0;
      if (parseTable(tl, res, d)) { if (d !== "\t") res.notes.unshift(...lines.filter(l => l.trim() && !l.includes(d))); finish(res); return res; }
    }

    // Texte : les longs paragraphes sont découpés en phrases (prose).
    const flat = [];
    const ALONE = /^\s*(\d+\s*[x×*]\s*(\d+(?:\s*-\s*\d+)*|max)|[+@]?\s*\d+(?:[.,]\d+)?\s*(kg|lbs?|%)|@.*|(rest|repos)\b.*|rpe\s*\d.*)\s*$/i;
    for (const l of lines) {
      // format « une info par ligne » (exports d'apps) : schéma, charge ou repos seuls sur leur ligne → rattachés à l'exercice au-dessus
      if (ALONE.test(l) && flat.length && flat[flat.length - 1].trim() && !readHeader(cleanLine(flat[flat.length - 1]))) { flat[flat.length - 1] += " " + l.trim(); continue; }
      if (l.length > 220) flat.push(...l.split(/(?<=[.!?])\s+/));
      else flat.push(l);
    }
    let week = null, day = null, notesMode = false;
    ROUNDS = 0;
    const W = () => week || (week = ensureWeek(res, "Programme"));
    const DAYLIKE = /^(jour|day|s[ée]ance|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b/i;
    for (const rawLine of flat) {
      const bullet = /^\s*[-*•](\s|\[)/.test(rawLine);
      const line = cleanLine(rawLine);
      if (!line) continue;
      const h = bullet ? null : readHeader(line);
      if (h && h.type === "week") {
        week = ensureWeek(res, h.label); day = null; notesMode = false; ROUNDS = 0;
        if (h.upto) week.upto = h.upto;
        const rest = (h.rest || "").trim();
        if (rest) {
          const exos = readExoLine(rest);
          if (exos.length && !/^voir\b/i.test(rest)) { day = ensureDay(week, "Séance"); day.exos.push(...exos); }
          else week.notes.push(rest);
        } else if (h.extra) week.notes.push(h.extra.replace(/[()]/g, ""));
        continue;
      }
      // v42 : « JAMBES : » ou « Jambes quadri – ischios » sous « Jour 3 » = intitulé de section, pas un nouveau jour
      if (h && h.type === "day" && h.split && day && DAYLIKE.test(day.label) && (!day.exos.length || /:\s*$/.test(line) || line === line.toUpperCase())) {
        if (!day.exos.length && !day.sub) day.sub = line.replace(/\s*:\s*$/, "");
        continue;
      }
      if (h && h.type === "day") {
        notesMode = false; ROUNDS = 0;
        const rest = (h.rest || "").trim();
        // prose : « Lundi tu commences par… » → le reste de la phrase est lu comme contenu
        day = ensureDay(W(), h.label);
        if (rest) {
          const exos = isProse(rest) ? [] : readExoLine(rest);
          if (isProse(rest)) proseLine(rest, day);
          else if (exos.length) day.exos.push(...exos);
          else if (/^\(.*\)$/.test(rest) || rest.length < 40) day.label === h.label && rest && (day.sub = (day.sub ? day.sub + " " : "") + rest.replace(/^[-—:\s]+/, ""));
          else proseLine(rest, day);
        }
        continue;
      }
      if (NOTES_HDR.test(line) && !/\d\s*[x×]\s*\d/.test(line)) { notesMode = true; const t = line.replace(/:\s*$/, ""); if (!/^notes?$/i.test(t)) res.notes.push(t); continue; }
      if (notesMode) { res.notes.push(line); continue; }
      if (isProse(line)) { if (!day) day = ensureDay(W(), "Séance 1"); proseLine(line, day); continue; }
      const exos = readExoLine(line);
      // v42 : jours de course (« Jour 4 : Fractionné », « Sortie EF ») : lignes sans nom rattachées au jour
      const run = day && day.sub && canon(day.sub).cat === "cardio" ? canon(day.sub) : null;
      if (run) exos.forEach(x => { if (!x.canon && (!x.name || x.name === "?" || !/[a-zà-ÿ]{3,}/i.test(x.name))) { x.name = day.sub; x.canon = run.canon; x.cat = "cardio"; x.note = x.note || x.raw; } });
      if (!exos.length && run && !/repos|rest\b|gainage|abdos/i.test(line)) {
        const dm = line.match(/(?<![\d.,])(\d+(?:[.,]\d+)?)\s*(minutes?|mins?|mn|h(?:eures?)?)(?![a-zà-ÿ])/i), km = (line.match(/(\d+(?:[.,]\d+)?)\s*km\b/i) || [])[1] || null;
        if (dm || km) {
          const min = dm ? (/^h/i.test(dm[2]) ? num(dm[1]) * 60 : num(dm[1])) : null;
          day.exos.push({ raw: line, name: day.sub, canon: run.canon, cat: "cardio", groups: [{ sets: 1, reps: min ? String(Math.round(min * 10) / 10).replace(".", ",") + " min" : "", load: null, amrap: false, km }], rpe: null, tempo: null, side: false, note: line });
          continue;
        }
      }
      if (!exos.length) { const tr = line.match(/(\d+)\s*tours?\b/i); if (tr && /circuit|tour/i.test(line)) ROUNDS = +tr[1]; }
      if (exos.length) {
        if (!day) day = ensureDay(W(), "Séance 1");
        day.exos.push(...exos);
      } else if (line.length > 120 && day) proseLine(line, day);
      else (day ? day.notes : week ? week.notes : res.notes).push(line);
    }
    finish(res);
    return res;
  }

  const isProse = t => t.length > 100 && /\b(tu|te|ton|ta|tes|vous|on|je|il)\b/i.test(t);

  // Prose : on coupe en propositions ; le dernier exercice nommé sert pour le schéma qui suit.
  function proseLine(text, day) {
    let names = [], found = false;
    const clauses = text.split(/,\s+|\s+puis\s+|\s+ensuite\s+|\.\s+/i);
    for (const c of clauses) {
      const inClause = [];
      const pair = c.match(/([a-zà-ÿ][a-zà-ÿ ]{2,25})\s+et\s+([a-zà-ÿ][a-zà-ÿ ]{2,25})$/i);
      if (pair && canon(pair[1]).canon && canon(pair[2]).canon) inClause.push(pair[1], pair[2]);
      else { const m = c.match(/(?:du|de la|des|le|la|les|journ[ée]e)\s+([a-zà-ÿ][a-zà-ÿ\- ]{2,40})/i); const k = m && canon(m[1]).canon ? m[1] : canon(c).canon ? c : null; if (k) inClause.push(k); }
      if (inClause.length) names = inClause;
      const ex = readExo(c);
      if (!ex || !names.length) continue;
      for (const n of names) { const k = canon(n); day.exos.push({ raw: c.trim(), name: k.canon, canon: k.canon, cat: k.cat, groups: ex.groups.map(g => ({ ...g })), rpe: ex.rpe, tempo: null, side: false }); }
      found = true; names = [];
    }
    if (!found) day.notes.push(text.trim());
  }

  function finish(res) {
    // v42 : « Semaine 1 à 3 » → la semaine 1 est recopiée en semaines 2 et 3 (sauf si elles sont écrites)
    for (let i = 0; i < res.weeks.length; i++) {
      const w = res.weeks[i], n0 = +((w.label.match(/\d+/) || [])[0]), up = w.upto; delete w.upto;
      if (!up || !n0) continue;
      const pre = w.label.replace(/\d+.*$/, "");
      for (let k = up; k > n0; k--) if (!res.weeks.some(x => x.label === pre + k)) res.weeks.splice(i + 1, 0, { ...JSON.parse(JSON.stringify(w)), label: pre + k });
    }
    for (const w of res.weeks) w.days = w.days.filter(d => d.exos.length || d.notes.length);
    res.weeks = res.weeks.filter(w => w.days.length || w.notes.length);
    let n = 0, ok = 0;
    for (const w of res.weeks) for (const d of w.days) for (const e of d.exos) { n++; if (e.canon) ok++; }
    res.stats = { weeks: res.weeks.length, days: res.weeks.reduce((a, w) => a + w.days.length, 0), exos: n, recognized: ok };
  }

  // Résumé lisible d'un groupe de séries : « 4×5 · 160 kg », « 5×5 · 72 % », « 3×8 · +20 kg »
  function fmtGroup(g) {
    const reps = g.reps === "max" ? "max" : g.reps;
    if (!reps && g.km) return String(g.km).replace(".", ",") + " km";
    if (/min$/.test(String(reps))) return String(reps) + (g.km ? ` · ${String(g.km).replace(".", ",")} km` : "");   // cardio : « 10 min · 3,2 km »
    let s = `${g.sets}×${reps}${g.amrap && g.reps !== "max" ? "+" : ""}`;
    const L = g.load;
    if (L) s += " · " + (L.kind === "pct" ? `${L.v} %` : L.kind === "rel" ? `${L.v} %` : L.kind === "lest" ? `+${L.v} ${L.u}` : L.kind === "band" ? "élastique" + (L.v ? ` ${L.v} kg` : "") : L.kind === "assist" ? `assistance ${L.v} kg` : `${L.v} ${L.u}`);
    return s;
  }

  // Classeur (.xlsx/.ods/Google Sheets) : [{name, rows:[[cellules texte]]}] → même résultat que parseProgram.
  // Repère les en-têtes « Exercice / Mouvement » (même plusieurs côte à côte, une par semaine), puis lit
  // les colonnes Séries / Reps / % / Charge / RPE, ou une colonne par série (« Série 1 », « Set 2 »…).
  const H_NAME = /^(exercices?|exercise|mouvements?|movement|exo)$/;
  const H_SET = /^(s[ée]rie|set)\s*(\d+)$/;
  function parseWorkbook(sheets) {
    const res = { weeks: [], notes: [], meta: {} };
    let any = false; const tableSheets = [];
    for (const sh of sheets) {
      const G = sh.rows.map(r => r.map(c => String(c ?? "").trim()));
      const at = (r, c) => (G[r] && G[r][c]) || "";
      const sheetWeek = (sh.name.match(/^(?:s|sem(?:aine)?|week)\s*(\d+)$/i) || [])[1];
      // v42 : tableaux de coach sans titre « Exercice » (« série | rep | charge | % | RPE » sous « SEANCE n ») → lecteur de tableau collé
      if (G.some(r => isHeadRow(r) && !r.some(v => H_NAME.test(strip(v))))) { tableSheets.push(sh); continue; }
      for (let r = 0; r < G.length; r++) {
        const starts = [];
        G[r].forEach((v, c) => { if (H_NAME.test(strip(v))) starts.push(c); });
        if (!starts.length) continue;
        if (G[r].slice(0, starts[0]).some(v => /^(semaine|week|jour|day|seance)$/.test(strip(v)))) { tableSheets.push(sh); break; }
        starts.forEach((c0, bi) => {
          const c1 = bi + 1 < starts.length ? starts[bi + 1] : Math.max(...G.map(x => x.length));
          const H = []; for (let c = c0; c < c1; c++) H.push(strip(at(r, c)));
          const col = re => { const i = H.findIndex(h => re.test(h)); return i < 0 ? -1 : c0 + i; };
          const C = { v: col(/^variation/), s: col(/^(series|sets?|nb series)$/), r: col(/^(reps?|repetitions?)$/), p: col(/^%$|pourcentage|^pct/),
            ch: col(/^(charge|poids|load|kg|weight)$/), rpe: col(/^rpe(\s*s1)?$|^rpe cible|^intensite/), t: col(/^tempo/), n: col(/^(notes?|commentaire du coach|remarques?)$/) };
          const setCols = H.map((h, i) => H_SET.test(h) ? c0 + i : -1).filter(i => i >= 0);
          // semaines en colonnes : « Exercice | S1 | S2 | S3 » avec « 4x5 @80% » dans chaque case
          const wkCols = H.map((h, i) => /^(s|sem|semaine|week|w)\s*\d+$/.test(h) && !H_SET.test(h) ? c0 + i : -1).filter(i => i >= 0);
          if (C.s < 0 && C.r < 0 && !setCols.length && wkCols.length) {
            any = true;
            const dl = DAYS[strip(sh.name)] || sh.name;
            for (let rr = r + 1; rr < G.length; rr++) {
              const nm = at(rr, c0); if (!nm || H_NAME.test(strip(nm))) break;
              const k = canon(nm);
              for (const c of wkCols) {
                const ex = at(rr, c) && readExo(at(rr, c)); if (!ex) continue;
                const day = ensureDay(ensureWeek(res, "Semaine " + at(r, c).match(/\d+/)[0]), dl);
                day.exos.push({ raw: nm + " | " + at(rr, c), name: nm, canon: k.canon, cat: k.cat, groups: ex.groups, rpe: ex.rpe, tempo: ex.tempo, side: false });
              }
            }
            return;
          }
          if (C.s < 0 && C.r < 0 && !setCols.length) return;
          any = true;
          // semaine : cellule « Semaine | 2 » au-dessus, dans les colonnes du bloc ; sinon nom de la feuille
          let wk = sheetWeek ? "Semaine " + sheetWeek : null, day = null, seance = null;
          for (let rr = r - 1; rr >= 0 && (!wk || !day); rr--) for (let c = c0 - 1; c < c1; c++) {
            const v = at(rr, c), nx = at(rr, c + 1), sv = strip(v);
            if (!wk && /^(semaine|week|sem)\s*\d*$/.test(sv) && (/\d/.test(sv) || /^\d+$/.test(nx))) wk = "Semaine " + (sv.match(/\d+/) || [nx])[0];
            if (!day && rr >= r - 3) {
              if (/^jour$/.test(sv) && nx) day = DAYS[strip(nx)] || nx;
              else if (DAYS[sv] && sv.length > 3) day = DAYS[sv];
              else if (/^(seance|workout|jour|day|j)\s*\w+$/.test(sv)) { seance = seance || v; continue; }
            }
          }
          const week = ensureWeek(res, wk || "Programme");
          const d = ensureDay(week, day || seance || "Séance " + (week.days.length + 1));
          for (let rr = r + 1; rr < G.length; rr++) {
            const nm = at(rr, c0);
            if (!nm || /^(recap|total|bilan)/i.test(nm) || H_NAME.test(strip(nm))) break;
            const varn = C.v >= 0 ? at(rr, C.v) : "";
            const name = (nm + (varn && !/^comp$/i.test(varn) ? " " + varn : "")).replace(/\s+/g, " ").trim();
            const k = canon(name);
            const street = ["Tractions", "Dips", "Muscle-up"].includes(k.canon);
            let groups = [];
            if (C.s >= 0 || C.r >= 0) {
              const reps = C.r >= 0 ? at(rr, C.r) : "", amrap = /amrap|max/i.test(reps);
              const pc = C.p >= 0 ? at(rr, C.p) : "", ch = C.ch >= 0 ? at(rr, C.ch) : "";
              let load = null;
              if (pc && /\d/.test(pc)) load = { kind: "pct", v: num(pc) };
              else if (ch && /^\s*-\s*\d+(?:[.,]\d+)?\s*%/.test(ch)) load = { kind: "rel", v: -num(ch.replace(/^\s*-\s*/, "")) };
              else if (ch && /^\s*(bw\s*)?[+]?\s*\d/i.test(ch)) load = /%/.test(ch) ? { kind: "pct", v: num(ch) } : /bw\s*\+|^\+/i.test(ch) || street ? { kind: "lest", v: num(ch.replace(/bw\s*\+|\+/i, "")), u: "kg" } : { kind: "abs", v: num(ch), u: /lb/i.test(ch) ? "lb" : "kg" };
              groups = [{ sets: toNum(C.s >= 0 ? at(rr, C.s) : "1") || 1, reps: amrap ? "max" : reps.replace(/\s/g, ""), load, amrap }];
              if (ch && !load) groups[0].note = ch;
            } else {
              for (const c of setCols) {
                const v = at(rr, c); if (!v) continue;
                let m, g = null;
                if ((m = v.match(/^\s*(\+?)\s*(\d+(?:[.,]\d+)?)\s*(%|kg|lbs?)?\s*[x×*]\s*(\d+)\s*$/i)))
                  g = { sets: 1, reps: m[4], load: m[3] === "%" ? { kind: "pct", v: num(m[2]) } : m[1] || street ? { kind: "lest", v: num(m[2]), u: "kg" } : { kind: "abs", v: num(m[2]), u: (m[3] || "kg").toLowerCase().replace(/s$/, "") } };
                else if ((m = v.match(/^\s*[x×*]\s*(\d+)\s*$/i))) g = { sets: 1, reps: m[1], load: null };
                else { const ex = readExo("x " + v); if (ex) g = ex.groups[0]; }
                if (!g) continue;
                const last = groups[groups.length - 1];
                if (last && last.reps === g.reps && JSON.stringify(last.load) === JSON.stringify(g.load)) last.sets++;
                else groups.push({ ...g, amrap: false });
              }
            }
            d.exos.push({ raw: G[rr].slice(c0, c1).filter(Boolean).join(" | "), name, canon: k.canon, cat: k.cat, groups,
              rpe: C.rpe >= 0 ? at(rr, C.rpe) || null : null, tempo: C.t >= 0 ? at(rr, C.t) || null : null, note: C.n >= 0 ? at(rr, C.n) || null : null, side: false });
          }
        });
      }
    }
    if (tableSheets.length && any) {   // v42 : classeur mixte → les deux lectures sont réunies
      const t = parseProgram(tableSheets.map(sh => sh.rows.map(r => r.join("\t")).join("\n")).join("\n"));
      res.weeks.push(...t.weeks); res.notes.push(...t.notes);
    }
    if (tableSheets.length && !any) return parseProgram(tableSheets.map(sh => sh.rows.map(r => r.join("\t")).join("\n")).join("\n"));
    if (!any) return parseProgram(sheets.map(sh => sh.rows.map(r => r.join("\t")).join("\n")).join("\n"));
    finish(res);
    return res;
  }


  // Tableau prêt à écrire dans un onglet, au format lu par l'app (semaines, jours, séances, en-tête MOUVEMENT) : résultat de l'import → lignes de cellules.
  // Charge : kg ou lest en nombre ; lb converties en kg ; % et RPE vont dans « INTENSITÉ CIBLE », le reste (tempo, back-off, remarques) dans « COMMENTAIRE DU COACH ».
  const GRID_HEAD = ["Exercice", "Variation", "Séries", "Reps", "Charge (kg)", "Intensité visée", "RPE série 1", "RPE dernière série", "Notes du programme", "Mon commentaire"];
  const GRID_MARK = "Street Lifting · programme";
  const WEEKDAY = /^(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)$/i;
  const fmtN = n => String(Math.round(n * 100) / 100).replace(".", ",");
  function toGrid(res, dateTxt, title) {
    const nd = res.weeks.reduce((a, w) => a + w.days.filter(d => d.exos.length).length, 0), ne = res.weeks.reduce((a, w) => a + w.days.reduce((b, d) => b + d.exos.length, 0), 0);
    const rows = [["", "STREET LIFTING\n" + (title || "Mon programme"), "", "", "", "", "", "", "", (dateTxt ? "Importé le " + dateTxt + "\n" : "") + nd + " séance" + (nd > 1 ? "s" : "") + " · " + ne + " exercice" + (ne > 1 ? "s" : "")],
      ["", GRID_MARK + " importé avec l'app. Les colonnes en couleur (RPE, commentaire, poids de corps) se remplissent pendant la séance ; tu peux modifier toutes les cases, l'app les relit."], []];
    res.weeks.forEach((w, wi) => {
      rows.push(["SEMAINE", String(wi + 1)]);
      let nd = 0;
      w.days.forEach(d => {
        if (!d.exos.length) return;
        nd++;
        rows.push(["JOUR", d.label]);
        const sub = d.sub || (WEEKDAY.test(d.label) ? "" : d.label);
        rows.push(["Séance " + nd + (sub ? " – " + sub : "")]);
        rows.push(GRID_HEAD.slice());
        d.exos.forEach(x => {
          const groups = x.groups.length ? x.groups : [{ sets: "", reps: "", load: null }];
          groups.forEach((g, gi) => {
            const L = g.load, com = [];
            let charge = "", inten = "";
            if (L) {
              if (L.kind === "abs" && L.u === "lb") { charge = fmtN(L.v * 0.45359237); com.push(L.v + " lb"); }
              else if (L.kind === "abs" || L.kind === "lest") charge = fmtN(L.v);
              else if (L.kind === "pct") inten = L.v + "%";
              else if (L.kind === "rel") com.push("Back-off " + String(L.v).replace("-", "−") + " % du top set");
              else if (L.kind === "band") com.push("Élastique" + (L.v ? " " + fmtN(L.v) + " kg" : ""));
              else if (L.kind === "assist") com.push("Assistance " + fmtN(L.v) + " kg");
            }
            if (gi === 0 && x.rpe) { const r = isNaN(+String(x.rpe).replace(",", ".")) ? String(x.rpe) : fmtN(+String(x.rpe).replace(",", ".")); if (inten) com.push("Intensité " + inten); inten = "RPE " + r; }
            if (gi === 0 && x.tempo) com.push("Tempo " + x.tempo);
            if (gi === 0 && x.note) com.push(x.note);
            if (gi === 0 && x.side) com.push("Par côté");
            if (g.km) com.push(String(g.km).replace(".", ",") + " km");
            const reps = g.reps === "max" ? "max" : String(g.reps) + (g.amrap ? "+" : "");
            rows.push([x.canon || x.name, "", String(g.sets), reps, charge, inten, "", "", com.join(" · "), ""]);
          });
        });
        rows.push(["Bilan de séance", "Poids de corps", ""]);
        (d.notes || []).forEach(n => rows.push(["Remarque", n]));
        rows.push([]);
      });
      (w.notes || []).forEach(n => rows.push(["Remarque", n]));
      rows.push([]);
    });
    (res.notes || []).forEach(n => rows.push(["Remarque", n]));
    return rows;
  }

  // Mise en forme de l'onglet (maquette A choisie par Alane le 23/10 : sombre comme l'app, logo, couleur de chaque mouvement).
  // Renvoie les requêtes Google Sheets (batchUpdate) pour l'onglet sheetId ; noFont : sans police Barlow (repli).
  const CAT_COL = { squat: "#F0524A", bench: "#A78BFA", deadlift: "#EC6FB0", pull: "#4C8DF6", dip: "#2BB673", mu: "#E3B341", cardio: "#4FD1C5" };
  const C = { floor: "#0A0B0D", deck: "#16181C", deck2: "#1F2227", deck3: "#2A2E34", seam: "#1C1F24", inbg: "#14171B", recap: "#111317", chalk: "#FFFFFF", dust: "#8A9099", steel: "#B4BAC2", brand: "#1F5FD0", warn: "#E3B341" };
  const WIDTHS = [200, 110, 64, 56, 90, 110, 90, 120, 200, 170];
  const INPUT_COLS = [6, 7, 9];
  function sheetStyle(rows, sheetId, noFont) {
    const rgb = h => ({ red: parseInt(h.slice(1, 3), 16) / 255, green: parseInt(h.slice(3, 5), 16) / 255, blue: parseInt(h.slice(5, 7), 16) / 255 });
    const R = [], n = rows.length, NC = 10;
    const rng = (r0, r1, c0, c1) => ({ sheetId, startRowIndex: r0, endRowIndex: r1, startColumnIndex: c0, endColumnIndex: c1 });
    const tf = (o = {}) => { const t = { foregroundColor: rgb(o.c || C.chalk), fontSize: o.size || 10, bold: !!o.b }; if (!noFont) t.fontFamily = o.f || "Barlow"; return t; };
    const fmt = (range, o) => R.push({ repeatCell: { range, cell: { userEnteredFormat: { backgroundColor: rgb(o.bg || C.floor), textFormat: tf(o), horizontalAlignment: o.al || "LEFT", verticalAlignment: "MIDDLE", wrapStrategy: o.wrap ? "WRAP" : "OVERFLOW_CELL" } }, fields: "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment,wrapStrategy)" } });
    const h = (r0, r1, px) => R.push({ updateDimensionProperties: { range: { sheetId, dimension: "ROWS", startIndex: r0, endIndex: r1 }, properties: { pixelSize: px }, fields: "pixelSize" } });
    const line = (c, w) => ({ style: w || "SOLID", color: rgb(c) });
    R.push({ updateSheetProperties: { properties: { sheetId, tabColor: rgb(C.brand), gridProperties: { hideGridlines: true, frozenRowCount: 2 } }, fields: "tabColor,gridProperties.hideGridlines,gridProperties.frozenRowCount" } });
    WIDTHS.forEach((px, i) => R.push({ updateDimensionProperties: { range: { sheetId, dimension: "COLUMNS", startIndex: i, endIndex: i + 1 }, properties: { pixelSize: px }, fields: "pixelSize" } }));
    fmt(rng(0, n + 20, 0, NC + 4), {});                                  // fond sombre partout
    h(0, n + 20, 26);
    // Bandeau : logo (A1), STREET LIFTING + nom (B1), date et volume (J1)
    fmt(rng(0, 1, 0, NC), { bg: C.brand });
    R.push({ mergeCells: { range: rng(0, 1, 1, 9), mergeType: "MERGE_ALL" } });
    const t1 = String(rows[0][1] || ""), cut = t1.indexOf("\n") + 1;
    R.push({ updateCells: { range: rng(0, 1, 1, 2), rows: [{ values: [{ userEnteredValue: { stringValue: t1 }, textFormatRuns: [{ startIndex: 0, format: tf({ size: 8, b: true }) }, { startIndex: cut, format: tf({ size: 22, b: true, f: "Barlow Condensed" }) }],
      userEnteredFormat: { backgroundColor: rgb(C.brand), verticalAlignment: "MIDDLE", wrapStrategy: "WRAP" } }] }], fields: "userEnteredValue,textFormatRuns,userEnteredFormat(backgroundColor,verticalAlignment,wrapStrategy)" } });
    fmt(rng(0, 1, 9, 10), { bg: C.brand, al: "RIGHT", size: 9, wrap: true });
    h(0, 1, 72);
    fmt(rng(1, 2, 0, NC), { bg: C.deck, c: C.steel, size: 9 });
    R.push({ mergeCells: { range: rng(1, 2, 1, NC), mergeType: "MERGE_ALL" } });
    h(1, 2, 30); h(2, 3, 10);
    for (let i = 3; i < n; i++) {
      const r = rows[i] || [], a = String(r[0] || "");
      if (!r.length || !a) { h(i, i + 1, 10); continue; }
      if (a === "SEMAINE") { fmt(rng(i, i + 1, 0, NC), { size: 12, b: true, f: "Barlow Condensed" }); h(i, i + 1, 32);
        R.push({ updateBorders: { range: rng(i, i + 1, 0, NC), top: line(C.brand, "SOLID_MEDIUM") } }); }
      else if (a === "JOUR") { fmt(rng(i, i + 1, 0, NC), { bg: C.deck, c: C.dust, size: 9 }); fmt(rng(i, i + 1, 1, 2), { bg: C.deck, b: true, size: 11 }); }
      else if (/^Séance /.test(a)) { fmt(rng(i, i + 1, 0, NC), { bg: C.deck, b: true, size: 11 }); h(i, i + 1, 30); }
      else if (a === "Exercice") { fmt(rng(i, i + 1, 0, NC), { bg: C.deck2, c: C.dust, b: true, size: 8 }); INPUT_COLS.forEach(c => fmt(rng(i, i + 1, c, c + 1), { bg: C.deck3, b: true, size: 8 }));
        fmt(rng(i, i + 1, 2, 5), { bg: C.deck2, c: C.dust, b: true, size: 8, al: "CENTER" }); h(i, i + 1, 28); }
      else if (a === "Bilan de séance") { fmt(rng(i, i + 1, 0, NC), { bg: C.recap, c: C.dust, size: 9 }); fmt(rng(i, i + 1, 2, 3), { bg: C.inbg, b: true, al: "CENTER" }); }
      else if (a === "Remarque") fmt(rng(i, i + 1, 0, NC), { c: C.steel, size: 9 });
      else {
        const cat = canon(a).cat, col = CAT_COL[cat] || "#8E9198";
        fmt(rng(i, i + 1, 0, 1), { b: true, size: 11 });
        fmt(rng(i, i + 1, 2, 5), { b: true, size: 11, al: "CENTER" });
        fmt(rng(i, i + 1, 5, 6), { c: C.warn, b: true });
        fmt(rng(i, i + 1, 8, 9), { c: C.steel, size: 9 });
        INPUT_COLS.forEach(c => fmt(rng(i, i + 1, c, c + 1), { bg: C.inbg, al: c === 9 ? "LEFT" : "CENTER", b: c !== 9 }));
        R.push({ updateBorders: { range: rng(i, i + 1, 0, NC), bottom: line(C.seam), innerVertical: line(C.seam) } });
        R.push({ updateBorders: { range: rng(i, i + 1, 0, 1), left: line(col, "SOLID_THICK") } });
        h(i, i + 1, 30);
      }
    }
    return R;
  }

  const api = { parseProgram, parseWorkbook, canon, fmtGroup, toGrid, GRID_MARK, sheetStyle, _readExo: readExo };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.ProgImport = api;
})(typeof window !== "undefined" ? window : globalThis);
