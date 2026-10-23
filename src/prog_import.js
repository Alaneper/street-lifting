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
    [/traction|pull.?ups?\b|chin.?ups?/, "Tractions", "pull"],
    [/\bdips?\b/, "Dips", "dip"],
    [/(dc|d[ée]v\w*|bench|banc|press)\s*(couch[ée]\s*)?(halt[eè]res\s*)?incl|incl\w*\s*(db|dumbbell|halt|barbell|bench|press|d[ée]v)/, "Développé incliné", "bench"],
    [/(dc|d[ée]v\w*\s*couch[ée]|bench|banc|\bbp\b).*(serr|close)|close.?grip/, "Développé couché prise serrée", "bench"],
    [/(dc|d[ée]v\w*\s*couch[ée]|bench|banc|\bbp\b).*pause|banc\s*pause/, "Développé couché pause", "bench"],
    [/^(dc|banc|couch[ée])\b|d[ée]velopp[ée]\s*couch[ée]|d[ée]v\w*\.?\s*couch|bench|\bbp\b|\bbanc\b|\bdc\b|machine\s*convergente/, "Développé couché", "bench"],
    [/militaire|military|\bohp\b|overhead|presse?\s*([ée]paules|shoulder)|shoulder\s*press|d[ée]v\w*\.?\s*([ée]paules?|militaire)/, "Développé militaire", "bench"],
    [/tirage\s*menton|upright/, "Tirage menton", ""],
    [/tirage\s*(vertical|poitrine|nuque)|lat\s*pull|pull.?down\b(?!s)/, "Tirage vertical", "pull"],
    [/rowing|\brow\b|tirage\s*horizontal|trx/, "Rowing", "pull"],
    [/face\s*pull/, "Face pull", ""],
    [/pull\s*over/, "Pull-over", ""],
    [/fente|lunge/, "Fentes", "squat"],
    [/presse(?!\s*[ée]paule)|leg\s*press|hack\s*press/, "Presse à cuisses", "squat"],
    [/leg\s*ext|quadri\w*\s*machine|extensions?\s*(des\s*)?jambes|quad\s*ext/, "Leg extension", "squat"],
    [/leg\s*curl|ham\w*\s*curl|ischio\w*\s*(machine|couch|assis)|lying\s*curl/, "Leg curl", "deadlift"],
    [/curl/, "Curl biceps", ""],
    [/triceps|skull\s*crusher|kick.?back|barre\s*au\s*front|barre\s*front|pushdown|extension\s*triceps/, "Triceps", ""],
    [/[ée]l[ée]v\w*\.?\s*lat|lat(eral)?\s*raise|elev\s*lat|oiseau\s*lat/, "Élévations latérales", ""],
    [/oiseau|rear\s*delt/, "Oiseau", ""],
    [/[ée]cart[ée]|fly/, "Écarté", "bench"],
    [/shrug/, "Shrug", ""],
    [/mollet|calf|calves/, "Mollets", ""],
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
      .replace(/^\s*[A-Z]\d\)\s*/, "").replace(/[\u{1F300}-\u{1FAFF}☀-➿]/gu, "").trim();
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
    if ((m = t.match(/bw\s*\+\s*(\d+(?:[.,]\d+)?)/i))) return { kind: "lest", v: num(m[1]), u: "kg" };
    if ((m = t.match(/@\s*(\d+(?:[.,]\d+)?)\s*%/))) return { kind: "pct", v: num(m[1]) };
    if ((m = t.match(/[àa@]\s*-\s*(\d+(?:[.,]\d+)?)\s*%/))) return { kind: "rel", v: -num(m[1]) };
    if ((m = t.match(/@\s*\+\s*(\d+(?:[.,]\d+)?)\s*(kg|lbs?)?/i))) return { kind: "lest", v: num(m[1]), u: (m[2] || "kg").replace(/s$/, "") };
    if ((m = t.match(/(?:^|\s)\+\s*(\d+(?:[.,]\d+)?)\s*(?:(kg|lbs?)\b|(?=\s*(?:$|[,:;)(\/]|\d)))/i))) return { kind: "lest", v: num(m[1]), u: (m[2] || "kg").replace(/s$/, "") };
    if ((m = t.match(/@\s*(\d+(?:[.,]\d+)?)(?![\d.,]|\s*%)\s*(kg|lbs?)?/i)) && !/rpe\s*$/i.test(t.slice(0, m.index))) return { kind: "abs", v: num(m[1]), u: (m[2] || "kg").replace(/s$/, "") };
    if ((m = t.match(/(\d+(?:[.,]\d+)?)\s*(kg|lbs?)\b/i))) return { kind: "abs", v: num(m[1]), u: m[2].toLowerCase().replace(/s$/, "") };
    if ((m = t.match(/(?:\s|^)[àa]\s+(\d{2,3}(?:[.,]\d+)?)(?![\d.,]|\s*%)/))) return { kind: "abs", v: num(m[1]), u: "kg" };
    if ((m = t.match(/(?<![\d.,])(\d+(?:[.,]\d+)?)\s*%/))) return { kind: "pct", v: num(m[1]) };
    for (const pm of s.matchAll(/\(([^)]*)\)/g)) { if (/\d/.test(pm[1]) && !/\(/.test(pm[1]) && /^\s*[+@]?\s*\d|^\s*bw/i.test(pm[1])) { const r = readLoad(" " + pm[1]); if (r) return r; } }
    if ((m = s.match(/\((\d{2,3}(?:[.,]\d+)?)\s*(kg|lbs?)?\)/i))) return { kind: "abs", v: num(m[1]), u: (m[2] || "kg").toLowerCase().replace(/s$/, "") };   // « opener (190) »
    if ((m = t.match(/\s(\d{2,3}(?:[.,]\d+)?)\s*$/))) return { kind: "abs", v: num(m[1]), u: "kg" };  // « 3x8 80 » en fin de ligne
    return null;
  }

  // Renvoie {name, groups, rpe, tempo, note} ou null si aucun schéma.
  function readExo(seg) {
    const s = seg.trim();
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
    if (!hits.length) return null;
    hits.sort((a, b) => a.i - b.i);
    // charge de chaque groupe : texte entre la fin du groupe et le début du suivant
    hits.forEach((h, k) => {
      if (!h.load) { const tail = s.slice(h.end, k + 1 < hits.length ? hits[k + 1].i : s.length); h.load = readLoad(" " + tail) || (k === 0 ? readLoad(" " + s.slice(0, h.i)) : null); }
    });
    let name = s.slice(0, hits[0].i).replace(/\s+(@\s*)?\d+(?:[.,]\d+)?\s*%\s*([:\-—–]\s*)?$/, "").replace(/\s\+\s*\d+(?:[.,]\d+)?\s*(kg|lbs?)?/gi, "").replace(/\d+(?:[.,]\d+)?\s*(kg|lbs?)?\s*$/i, "")
      .replace(/(\s|^)(puis|then|et|ensuite)\s*$/i, "").replace(/[:\-—–,@(]+\s*$/, "").trim();
    const rpe = (s.match(/rpe\s*(\d+(?:[.,]\d+)?(?:\s*-\s*\d+(?:[.,]\d+)?)?)/i) || [])[1] || null;
    const tempo = (s.match(/tempo\s*(\d-\d-[\dx](?:-\d)?)/i) || [])[1] || null;
    const side = /\/\s*(jambe|bras|c[oô]t[ée])|par bras|chaque bras|\/\s*leg|per side/i.test(s);
    return { name, groups: hits.map(h => ({ ...h.g, load: h.load || null, amrap: !!h.amrap })), rpe, tempo, side };
  }

  function mkExo(raw, ex) {
    const c = canon(ex.name);
    return { raw: raw.trim(), name: ex.name || c.canon || "?", canon: c.canon, cat: c.cat, groups: ex.groups, rpe: ex.rpe, tempo: ex.tempo, side: ex.side };
  }

  // Une ligne peut contenir plusieurs exercices (« A / B », « A ; B », « A 3x12, B 3x12 »).
  const ADD_ON = /^(back.?off|top\s*set|warm.?up|[ée]chauff\w*|puis|then|et|ensuite|pareil)\b/i;
  function readExoLine(line) {
    const out = [];
    for (const big of line.split(/\s+\/\s+|\s*;\s*/)) {
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
    if ((m = l.match(/^(sem(?:aine)?|week|s)\s*(\d+)\b\s*(\([^)]*\))?\s*[:\-—]?\s*(.*)$/i)) && !/^s\s*\d+\s*x/i.test(l))
      return { type: "week", label: (strip(m[1]).startsWith("w") ? "Week " : "Semaine ") + m[2], key: "w" + m[2], rest: m[4], extra: m[3] || "" };
    if ((m = l.match(/^(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b\s*[:\-—–,]?\s*(.*)$/i)))
      return { type: "day", label: DAYS[strip(m[1])], key: DAYS[strip(m[1])], rest: m[2] };
    if ((m = l.match(/^(lun|mar|mer|jeu|ven|sam|dim)\.?\s+(.*)$/i)) && /\d/.test(m[2]))
      return { type: "day", label: DAYS[strip(m[1])], key: DAYS[strip(m[1])], rest: m[2] };
    if ((m = l.match(/^(mon|tues?|wed|thu(?:rs?)?|fri|sat|sun)\b\.?\s*(?:[:\-—–]\s*)?(.*)$/i)) && (/^[A-Z]{3}/.test(l) || /^\w+\.?\s*([:\-—–]|$)/.test(l))) {
      const d = { mon: "Lundi", tue: "Mardi", tues: "Mardi", wed: "Mercredi", thu: "Jeudi", thur: "Jeudi", thurs: "Jeudi", fri: "Vendredi", sat: "Samedi", sun: "Dimanche" }[strip(m[1])];
      return { type: "day", label: d, key: d, rest: m[2] };
    }
    if ((m = l.match(/^(day|jour|j)\s*(\d+)\b\s*(.*)$/i)))
      return { type: "day", label: "Jour " + m[2], key: "Jour " + m[2], rest: m[3].replace(/^(accessor(y|ies)|accessoires?)\s*/i, "").replace(/^[:\-—]\s*/, "") };
    if ((m = l.match(/^(?:s[ée]ance|workout|training|routine|entra[iî]nement)\s+([a-z0-9]+)\b\s*(.*)$/i)))
      return { type: "day", label: "Séance " + m[1].toUpperCase(), key: "Séance " + m[1].toUpperCase(), rest: m[2] };
    if ((m = l.match(/^(push|pull|legs|leg day|jambes|upper|lower|haut du corps|bas du corps|full ?body)(?![-\w])(?!\s*(?:ups?|overs?|downs?|day\s*\d*\s*:?\s*\d|over)\b)\s*(\d*)\s*(.*)$/i)) && !/\d\s*(?:[x×]\s*\d|s[ée]ries?|sets?)/i.test(l))
      return { type: "day", label: (m[1].toUpperCase() + " " + m[2]).trim(), key: (m[1].toUpperCase() + " " + m[2]).trim(), rest: m[3] };
    return null;
  }

  const NOTES_HDR = /^(notes?|remarques?|tentatives|objectifs?|nutrition|mon avis)\b.*:?\s*$/i;

  // ---------- tableau collé ----------
  function parseTable(lines, res, d) {
    const rows = lines.map(l => l.split(d).map(c => c.trim()));
    const hi = rows.findIndex(r => r.some(c => /^exerci[cs]es?$/i.test(c)));
    if (hi < 0) return false;
    const H = rows[hi].map(c => strip(c));
    const col = re => H.findIndex(c => re.test(c));
    const C = { w: col(/^(semaine|week|sem)/), d: col(/^(jour|day|seance)/), e: col(/^exerci/), s: col(/^(series|sets?)$/), r: col(/^(reps?|repetitions)$/),
      p: col(/%|charge|load|kg|poids/), rpe: col(/rpe/), rest: col(/repos|rest/), n: col(/note|remarque/) };
    rows.slice(0, hi).forEach(r => { const t = r.filter(Boolean).join(" · "); if (t) res.notes.push(t); });
    // valeurs de « TM » : ligne de titres suivie d'une ligne de nombres
    for (let i = 0; i < hi - 1; i++) if (rows[i].some(c => /\btm\b|max/i.test(c)) && rows[i + 1].every(c => !c || /^\d/.test(c)))
      rows[i].forEach((c, k) => { if (c && rows[i + 1][k]) res.meta[c] = num(rows[i + 1][k]); });
    for (const r of rows.slice(hi + 1)) {
      if (!r.some(Boolean)) continue;
      const wk = ensureWeek(res, C.w >= 0 && r[C.w] ? "Semaine " + r[C.w] : "Programme");
      const ex = C.e >= 0 ? r[C.e] : "";
      if (!ex || ex === "-" || !/[a-z]/i.test(ex) || /deload|repos/i.test(ex) && (C.s < 0 || !/\d/.test(r[C.s] || ""))) {
        const note = r.filter(c => c && c !== "-").slice(1).join(" · "); if (note) wk.notes.push(note); continue;
      }
      const day = ensureDay(wk, C.d >= 0 && r[C.d] ? r[C.d].replace(/^j\s*(\d+)$/i, "Jour $1") : "Séance");
      const sets = C.s >= 0 ? toNum(r[C.s]) : null, repsRaw = C.r >= 0 ? r[C.r] : "";
      const amrap = /amrap|max/i.test(repsRaw);
      const pcell = C.p >= 0 ? r[C.p] : "";
      const load = !pcell || pcell === "-" ? null : /bw\s*\+/i.test(pcell) ? { kind: "lest", v: num(pcell.replace(/bw\s*\+/i, "")), u: "kg" }
        : /%/.test(pcell) ? { kind: "pct", v: num(pcell) } : /^\d/.test(pcell) ? { kind: "abs", v: num(pcell), u: /lb/i.test(pcell) ? "lb" : "kg" } : null;
      const c = canon(ex);
      day.exos.push({ raw: r.join(" | "), name: ex, canon: c.canon, cat: c.cat,
        groups: [{ sets: sets || 1, reps: amrap ? "max" : repsRaw, load, amrap }],
        rpe: C.rpe >= 0 && r[C.rpe] && r[C.rpe] !== "-" ? r[C.rpe] : null, rest: C.rest >= 0 ? r[C.rest] || null : null,
        note: C.n >= 0 ? r[C.n] || null : null, tempo: null, side: false });
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
      const tl = lines.filter(l => l.split(d).length >= 3);
      if (tl.length >= 3 && tl.some(l => /exerci[cs]e/i.test(l)) && parseTable(tl, res, d)) { if (d !== "\t") res.notes.unshift(...lines.filter(l => l.trim() && !l.includes(d))); finish(res); return res; }
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
    const W = () => week || (week = ensureWeek(res, "Programme"));
    for (const rawLine of flat) {
      const bullet = /^\s*[-*•](\s|\[)/.test(rawLine);
      const line = cleanLine(rawLine);
      if (!line) continue;
      const h = bullet ? null : readHeader(line);
      if (h && h.type === "week") {
        week = ensureWeek(res, h.label); day = null; notesMode = false;
        const rest = (h.rest || "").trim();
        if (rest) {
          const exos = readExoLine(rest);
          if (exos.length && !/^voir\b/i.test(rest)) { day = ensureDay(week, "Séance"); day.exos.push(...exos); }
          else week.notes.push(rest);
        } else if (h.extra) week.notes.push(h.extra.replace(/[()]/g, ""));
        continue;
      }
      if (h && h.type === "day") {
        notesMode = false;
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
    for (const w of res.weeks) w.days = w.days.filter(d => d.exos.length || d.notes.length);
    res.weeks = res.weeks.filter(w => w.days.length || w.notes.length);
    let n = 0, ok = 0;
    for (const w of res.weeks) for (const d of w.days) for (const e of d.exos) { n++; if (e.canon) ok++; }
    res.stats = { weeks: res.weeks.length, days: res.weeks.reduce((a, w) => a + w.days.length, 0), exos: n, recognized: ok };
  }

  // Résumé lisible d'un groupe de séries : « 4×5 · 160 kg », « 5×5 · 72 % », « 3×8 · +20 kg »
  function fmtGroup(g) {
    const reps = g.reps === "max" ? "max" : g.reps;
    let s = `${g.sets}×${reps}${g.amrap && g.reps !== "max" ? "+" : ""}`;
    const L = g.load;
    if (L) s += " · " + (L.kind === "pct" ? `${L.v} %` : L.kind === "rel" ? `${L.v} %` : L.kind === "lest" ? `+${L.v} ${L.u}` : `${L.v} ${L.u}`);
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
    if (tableSheets.length && !any) return parseProgram(tableSheets.map(sh => sh.rows.map(r => r.join("\t")).join("\n")).join("\n"));
    if (!any) return parseProgram(sheets.map(sh => sh.rows.map(r => r.join("\t")).join("\n")).join("\n"));
    finish(res);
    return res;
  }

  const api = { parseProgram, parseWorkbook, canon, fmtGroup, _readExo: readExo };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.ProgImport = api;
})(typeof window !== "undefined" ? window : globalThis);
