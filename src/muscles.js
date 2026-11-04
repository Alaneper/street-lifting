/* Carte musculaire B2Strong (v67 ; illustrations d'écorché depuis la v71).
   muscleFig(lift, {view:"auto"|"front"|"back"|"both"}) → HTML d'une planche craie ; principal = rouge, secondaire = rouge clair.
   Les clés de muscles sont celles du dessin ; MUSCLE_MAP relie chaque mouvement de l'app à ses muscles (1 = principal, 2 = secondaire). */
/* v71 : illustrations d'écorché crème (fond, une image par vue, partagée par toutes les silhouettes) + zones musculaires vectorielles tracées dessus (MUSCLE_ART, généré par tools/gen_muscle_art.py).
   Principal = rouge, secondaire = rose, le reste reste crème. Mêmes clés de muscles que le dessin v67. */
const MUSCLE_SVG = (() => { const o = {}; for (const v of ["front", "back"]) { const a = MUSCLE_ART[v]; o[v] = '<svg class="fig" viewBox="' + a.vb.join(" ") + '" aria-hidden="true"><use href="#mimg-' + v + '"/>' + Object.keys(a.reg).map(k => '<g class="m ' + k + '"><use class="t" href="#mimg-' + v + 'r" mask="url(#mk-' + v + '-' + k + ')"/><use class="s" href="#mimg-' + v + 'p" mask="url(#mk-' + v + '-' + k + ')"/></g>').join("") + "</svg>"; } return o; })();
/* les deux images sont déclarées une seule fois dans la page (évite de les répéter dans chaque vignette) */
function muscleDefs(){
  if (typeof document === "undefined" || !document.body || document.getElementById("mimgs")) return;
  const im = (id, src, v) => '<image id="' + id + '" href="' + src + '" width="' + MUSCLE_ART[v].w + '" height="' + MUSCLE_ART[v].h + '"/>';
  /* v71b : le muscle travaillé n'est pas un aplat de couleur : c'est l'illustration elle-même, recolorée en rouge (principal) ou en rose (secondaire), fibres et séparations visibles, affichée uniquement dans la zone du muscle (masque à bords adoucis) */
  const mk = v => { const a = MUSCLE_ART[v]; return Object.keys(a.reg).map(k => { const b = a.box[k]; return '<mask id="mk-' + v + '-' + k + '" maskUnits="userSpaceOnUse" x="' + (b[0] - 14) + '" y="' + (b[1] - 14) + '" width="' + (b[2] - b[0] + 28) + '" height="' + (b[3] - b[1] + 28) + '"><path d="' + a.reg[k] + '" fill="#fff" filter="url(#mfe)"/></mask>'; }).join(""); };
  document.body.insertAdjacentHTML("afterbegin", '<svg id="mimgs" width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>' + im("mimg-front", MUSCLE_IMG.front, "front") + im("mimg-back", MUSCLE_IMG.back, "back") + im("mimg-frontr", MUSCLE_IMG.frontR, "front") + im("mimg-backr", MUSCLE_IMG.backR, "back") + im("mimg-frontp", MUSCLE_IMG.frontP, "front") + im("mimg-backp", MUSCLE_IMG.backP, "back") + '<filter id="mfe" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.1"/></filter>' + mk("front") + mk("back") + '</defs></svg>');
}
/* vignettes : cadrage carré autour des muscles principaux visibles dans la vue (les autres si aucun principal n'y est) */
function muscleCrop(v, map){
  const a = MUSCLE_ART[v], ks = Object.keys(map).filter(k => a.box[k]), P = ks.filter(k => map[k] === 1), use = P.length ? P : ks;
  if (!use.length) return null;
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; use.forEach(k => { const b = a.box[k]; x0 = Math.min(x0, b[0]); y0 = Math.min(y0, b[1]); x1 = Math.max(x1, b[2]); y1 = Math.max(y1, b[3]); });
  const side = Math.min(a.vb[3], Math.max(340, Math.max(x1 - x0, y1 - y0) * 1.28)), cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  const x = Math.min(Math.max(cx - side / 2, a.vb[0]), a.vb[0] + a.vb[2] - side), y = Math.min(Math.max(cy - side / 2, a.vb[1]), a.vb[1] + a.vb[3] - side);
  return [x, y, side, side].map(n => Math.round(n)).join(" ");
}
/* v71 · correspondance exercice → muscles, reprise de la base d'exercices Liftosaur (https://api3.liftosaur.com/exercises, lue le 04/11/2026) :
   muscle « Target » = principal (1), muscles « Synergist » = secondaires (2). Équivalences : Quads=quadriceps, Glutes (et Abductors)=fessiers, Hamstrings=ischios, Lower Back=lombaires, Abs=abdos,
   Obliques=obliques, Adductors=adducteurs, Calves=mollets, Chest=pectoraux, Front et Side Delts=épaules (face), Rear Delts=épaules (dos), Lats=dorsaux, Upper Back=trapèzes moyens/bas (dos),
   Upper Traps=trapèzes, Forearm=avant-bras. Hip Flexors et Rotator Cuff n'ont pas de zone dessinée : ils ne sont pas affichés.
   Écarts assumés (à relire) : Muscle-up (la source n'a pas de « Target » : tous ses muscles sont principaux) ; Dip (Chest Dip = pectoraux, Triceps Dip = triceps : les deux principaux) ;
   relevés de jambes / genoux à la barre (la source ne cite que les fléchisseurs de hanche, non dessinés : abdominaux principal par choix ; secondaires adducteurs et abducteurs=fessiers d'après la source) ;
   gainage « hollow / dead bug / dragon flag » rangés avec la planche (abdominaux seuls : non vérifiés un par un) ; relevés de jambes : abdos principal par choix. Vérifiés à la source le 04/11/2026 : crunch (abdos + obliques), planche (abdos), planche latérale (obliques), rotation russe (obliques ; lombaires), soulevé de terre (fessiers), sumo (lombaires), pull-over, tirage vertical. */
const MUSCLE_MAP = {
  SQUAT:{quadriceps:1, adducteurs:2, fessiers:2, mollets:2, mollets_d:2},
  BENCH:{pectoral:1, deltoide:2, triceps:2},
  DEADLIFT:{fessiers:1, adducteurs:2, ischios:2, quadriceps:2, mollets:2, mollets_d:2},
  PULL:{dorsaux:1, biceps:2, deltoide_d:2, trapeze:2, trapeze_d:2},
  DIP:{pectoral:1, triceps:1, deltoide:2, dorsaux:2, trapeze:2},
  MU:{dorsaux:1, pectoral:1, triceps:1, biceps:1, deltoide_d:1, trapeze_d:1}
};
/* Exercices de musculation : première famille dont le motif correspond (noms sans accents, en majuscules). Ce qui ne correspond à rien reste sans silhouette (initiale). Format : [clé, motif, muscles, vue]. */
const MUSCLE_EX = [
  ["X_NULL",   /\bSCAPULAR\b|\bFARMER|\bTURKISH\b|\bSNATCH\b|\bARRACHE\b|\bCLEAN\b|\bTHRUSTER\b|\bLANDMINE\b|\bBURPEE|\bSTEP ?OVER/, null, null],
  ["X_CLOSEGRIP",/\bCLOSE[- ]GRIP (BENCH|PRESS)\b|\bDEVELOPPE COUCHE PRISE SERREE\b|\bDIAMOND\b|\bPOMPES? DIAMANT\b/, {triceps:1, deltoide:2, pectoral:2}, "front"],
  ["X_LEGCURL",/\bLEG CURLS?\b|\bCURLS? (JAMBES?|ISCHIOS?)\b|\bNORDIC\b|\bISCHIO-?JAMBIERS? (MACHINE|ALLONGE|ASSIS)\b/, {ischios:1, mollets:2, mollets_d:2}, "back"],
  ["X_LEGEXT", /\bLEG EXTENSIONS?\b|\bEXTENSIONS? (DE )?(JAMBES?|QUADRICEPS|GENOUX?)\b|\bQUADRICEPS (MACHINE|EXTENSION)\b/, {quadriceps:1}, "front"],
  ["X_LEGPRESS", /\bLEG PRESS\b|\bPRESSE (A |À )?(CUISSES?|JAMBES?|INCLINEE)\b|\bPRESSE A CUISSES\b|\bHACK\b/, {quadriceps:1, adducteurs:2, fessiers:2, mollets:2, mollets_d:2}, "front"],
  ["X_LUNGE",  /\bFENTES?\b|\bLUNGES?\b|\bSTEP[- ]?UPS?\b|\bMONTEES? (SUR|AU) (BANC|STEP|BOX)\b/, {quadriceps:1, adducteurs:2, fessiers:2, mollets:2, mollets_d:2}, "front"],
  ["X_HIP",    /\bHIP THRUSTS?\b|\bPONT FESSIER\b|\bGLUTE BRIDGE\b|\bTHRUSTS? DE HANCHES?\b|\bSINGLE LEG BRIDGE\b/, {fessiers:1, quadriceps:2}, "back"],
  ["X_GLUTEK", /\bGLUTE KICK ?BACKS?\b|\bKICK ?BACKS? (FESSIERS?|GLUTES?)\b|\bDONKEY\b/, {fessiers:1, adducteurs:2}, "back"],
  ["X_PULLTHR",/\bPULL[- ]?THROUGH\b/, {fessiers:1, adducteurs:2, ischios:2}, "back"],
  ["X_ABDUCT", /\bHIP ABDUCT|\bABDUCTEURS?\b|\bABDUCTION\b|\bCLAMS?\b|\bSIDE LYING CLAM\b/, {fessiers:1}, "back"],
  ["X_ADDUCT", /\bHIP ADDUCT|\bADDUCTEURS?\b|\bADDUCTION\b|\bCOPENHAGEN\b/, {adducteurs:1}, "front"],
  ["X_RDL",    /\bROMANIAN\b|\bROUMAIN\b|\bRDL\b|\bSINGLE LEG DEADLIFT\b/, {fessiers:1, adducteurs:2, lombaires:2, ischios:2}, "back"],
  ["X_STIFF",  /\bSTIFF[- ]LEG\b|\bSTIFF\b|\bSLDL\b/, {lombaires:1, adducteurs:2, fessiers:2, ischios:2}, "back"],
  ["X_STRAIGHT",/\bSTRAIGHT[- ]LEG\b|\bJAMBES? TENDUES?\b/, {ischios:1, adducteurs:2, lombaires:2, fessiers:2}, "back"],
  ["X_SUMO",   /\bSOULEVE DE TERRE SUMO\b|\bSUMO DEADLIFT\b|\bDEADLIFT SUMO\b|\bSUMO\b/, {lombaires:1, adducteurs:2, fessiers:2, quadriceps:2, mollets:2, mollets_d:2}, "back"],
  ["X_DEADLIFT",/\bSOULEVES? DE TERRE\b|\bDEADLIFTS?\b|\bTRAP BAR\b|\bHEX BAR\b/, {fessiers:1, adducteurs:2, ischios:2, quadriceps:2, mollets:2, mollets_d:2}, "back"],
  ["X_GOODM",  /\bGOOD[- ]MORNINGS?\b/, {ischios:1, adducteurs:2, fessiers:2}, "back"],
  ["X_REVHYP", /\bREVERSE HYPER\b|\bHYPEREXTENSIONS? INVERSEES?\b/, {fessiers:1, ischios:2}, "back"],
  ["X_BACKEXT",/\bHYPER ?EXTENSIONS?\b|\bBACK EXTENSIONS?\b|\bEXTENSIONS? LOMBAIRES?\b|\bLOMBAIRES?\b|\bSUPERMAN\b/, {lombaires:1, adducteurs:2, fessiers:2, ischios:2}, "back"],
  ["X_CALF",   /\bMOLLETS?\b|\bCALF\b|\bCALVES\b/, {mollets:1, mollets_d:1}, "back"],
  ["X_SHRUG",  /\bSHRUGS?\b|\bHAUSSEMENTS? D.?EPAULES?\b/, {trapeze:1, trapeze_d:1}, "back"],
  ["X_FACEPULL",/\bFACE ?PULLS?\b|\bTIRAGE VISAGE\b/, {deltoide_d:1, biceps:2, deltoide:2, trapeze_d:2}, "back"],
  ["X_REAR",   /\bREVERSE FLY\b|\bREVERSE FLYE?S?\b|\bOISEAUX?\b|\bREAR DELTS?\b|\bECARTES? (INVERSES?|ARRIERES?)\b/, {deltoide_d:1, deltoide:2, trapeze_d:2}, "back"],
  ["X_UPRIGHT",/\bUPRIGHT ROW\b|\bROWING MENTON\b|\bTIRAGE MENTON\b/, {deltoide:1, biceps:2, trapeze_d:2}, "front"],
  ["X_LATERAL",/\bELEVATIONS? LATERALES?\b|\bLATERAL RAISES?\b|\bECARTES? LATERAL/, {deltoide:1, trapeze_d:2}, "front"],
  ["X_FRONTR", /\bFRONT RAISES?\b|\bELEVATIONS? FRONTALES?\b/, {deltoide:1, pectoral:2, trapeze_d:2}, "front"],
  ["X_WRISTREV",/\bREVERSE WRIST CURLS?\b|\bCURLS? (DE )?POIGNETS? (INVERSES?|PRONATION)\b/, {avant_bras:1}, "back"],
  ["X_WRIST",  /\bWRIST CURLS?\b|\bCURLS? (DE )?POIGNETS?\b|\bWRIST ROLLER\b/, {avant_bras:1}, "front"],
  ["X_CURL",   /\bCURLS?\b|\bBICEPS\b/, {biceps:1}, "front"],
  ["X_TRI",    /\bTRICEPS\b|\bSKULL ?CRUSHERS?\b|\bBARRE (AU|A LE) FRONT\b|\bFRENCH PRESS\b|\bPUSH ?DOWNS?\b|\bKICK ?BACKS?\b/, {triceps:1}, "back"],
  ["X_OHP",    /\bDEVELOPPE (MILITAIRE|EPAULES?|NUQUE)\b|\bMILITARY PRESS\b|\bOVERHEAD PRESS\b|\bSHOULDER PRESS\b|\bOHP\b|\bARNOLD PRESS\b|\bPUSH PRESS\b|\bBEHIND THE NECK\b|\bPIKE PUSH\b|\bHANDSTAND PUSH\b/, {deltoide:1, pectoral:2, trapeze_d:2, triceps:2}, "front"],
  ["X_PECDECK",/\bPEC DECK\b|\bPAPILLON\b/, {pectoral:1}, "front"],
  ["X_FLY",    /\bECARTES?\b|\bFLYES?\b|\bFLY\b|\bCROISES? (A LA )?POULIE\b|\bCABLE CROSSOVER\b/, {pectoral:1, deltoide:2, biceps:2}, "front"],
  ["X_CHEST",  /\bDEVELOPPE (COUCHE|INCLINE|DECLINE|CONVERGENT)\b|\b(INCLINE|DECLINE|FLAT) (BENCH|PRESS)\b|\bCHEST PRESS\b|\bPOMPES?\b|\bPUSH[- ]?UPS?\b|\bPECTORAUX? (MACHINE|BARRE)\b|\bBENCH PRESS\b/, {pectoral:1, deltoide:2, triceps:2}, "front"],
  ["X_PULLOVER",/\bPULL[- ]?OVER\b/, {dorsaux:1, deltoide_d:2, trapeze:2, pectoral:2, triceps:2, trapeze_d:2}, "back"],
  ["X_PULLDN", /\bPULL ?DOWNS?\b|\bTIRAGE VERTICAL\b|\bTIRAGE (A LA POITRINE|POITRINE|NUQUE)\b/, {dorsaux:1, biceps:2, deltoide_d:2, trapeze:2, trapeze_d:2}, "back"],
  ["X_ROW",    /\bTIRAGE HORIZONTAL\b|\bTIRAGE BUSTE PENCHE\b|\bROWS?\b|\bROWING\b|\bT[- ]?BAR\b|\bTIRAGE (A LA POULIE|BARRE|HALTERE)\b/, {dorsaux:1, trapeze_d:1, biceps:2, deltoide_d:2, pectoral:2}, "back"],
  ["X_ABROLL", /\bAB WHEEL\b|\bROUE ABDOMINALE\b|\bROLLOUT\b|\bROLL ?OUT\b/, {abdos:1, obliques:2, dorsaux:2, deltoide:2}, "front"],
  ["X_SIDEPL", /\bSIDE PLANK\b|\bPLANCHE LATERALE\b|\bGAINAGE LATERAL\b/, {obliques:1}, "front"],
  ["X_OBL",    /\bRUSSIAN TWIST\b|\bROTATIONS? RUSSES?\b|\bTWIST\b|\bSIDE BENDS?\b|\bINCLINAISONS? LATERALES?\b|\bPALLOF\b|\bOBLIQUES?\b|\bBICYCLE\b/, {obliques:1, lombaires:2}, "front"],
  ["X_LEGRAISE",/\bRELEVES? DE JAMBES?\b|\bLEG RAISES?\b|\bKNEE RAISES?\b|\bRELEVES? DE GENOUX\b|\bTOES? TO BAR\b|\bKNEES? TO ELBOWS?\b|\bL[- ]?SIT\b|\bV[- ]?UPS?\b/, {abdos:1, adducteurs:2, fessiers:2}, "front"],
  ["X_PLANK",  /\bGAINAGE\b|\bPLANCHE\b|\bPLANK\b|\bHOLLOW\b|\bDEAD BUG\b|\bDRAGON FLAG\b/, {abdos:1}, "front"],
  ["X_ABS",    /\bCRUNCH(ES)?\b|\bABDOS?\b|\bABDOMINAUX\b|\bSIT[- ]?UPS?\b/, {abdos:1, obliques:2}, "front"],
  ["X_SWING",  /\bKETTLEBELL SWINGS?\b|\bSWINGS?\b/, {fessiers:1, deltoide:1, adducteurs:2, ischios:2, pectoral:2, mollets:2, mollets_d:2}, "back"]
];
MUSCLE_EX.forEach(([k, re, m]) => { if (m) MUSCLE_MAP[k] = m; });
/* texte d'un exercice (sans accents, majuscules) → clé de MUSCLE_MAP, ou null si la correspondance n'est pas sûre */
function exMuscleKey(txt){
  const t = String(txt || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toUpperCase().replace(/[’']/g, "'").replace(/\s+/g, " ").trim();
  if (!t) return null;
  for (const [k, re, m] of MUSCLE_EX) if (re.test(t)) return m ? k : null;
  return null;
}
/* vue la plus parlante d'un mouvement seul (vignettes) */
const MUSCLE_VIEW = {SQUAT:"front", BENCH:"front", DIP:"front", DEADLIFT:"back", PULL:"back", MU:"back"};
MUSCLE_EX.forEach(([k, re, m, v]) => { if (m) MUSCLE_VIEW[k] = v; });
let _muscleN = 0;
const MUSCLE_NAMES = {quadriceps:"Quadriceps", fessiers:"Fessiers", ischios:"Ischio-jambiers", lombaires:"Lombaires", abdos:"Abdominaux", adducteurs:"Adducteurs", mollets:"Mollets", mollets_d:"Mollets", pectoral:"Pectoraux", deltoide:"Épaules", deltoide_d:"Épaules", triceps:"Triceps", biceps:"Biceps", serratus:"Dentelé", dorsaux:"Dorsaux", trapeze_d:"Trapèzes", trapeze:"Trapèzes", avant_bras:"Avant-bras", obliques:"Obliques"};
function muscleMap(lift){   /* un mouvement, ou une liste (séance) : principal l'emporte sur secondaire */
  const L = (Array.isArray(lift) ? lift : [lift]).filter(l => MUSCLE_MAP[l]), out = {};
  L.forEach(l => Object.keys(MUSCLE_MAP[l]).forEach(k => { out[k] = Math.min(out[k] || 9, MUSCLE_MAP[l][k]); }));
  return L.length ? out : null;
}
function muscleFig(lift, o){
  o = o || {};
  if (!o.blk && typeof optOn === "function" && !optOn("sil")) return "";   /* option « Silhouettes de muscles » éteinte (les blocs « Muscles travaillés » passent blk:true) */
  const map = muscleMap(lift); if (!map) return "";
  const has = (v, k) => MUSCLE_SVG[v].includes('class="m ' + k + '"') || MUSCLE_SVG[v].includes('class="m ' + k + ' dk"');
  const score = v => Object.keys(map).reduce((n, k) => n + (map[k] === 1 && has(v, k) ? 2 : map[k] === 2 && has(v, k) ? 1 : 0), 0);
  const pref = !Array.isArray(lift) && MUSCLE_VIEW[lift];
  let views = o.view === "both" ? ["front", "back"] : o.view === "front" || o.view === "back" ? [o.view] : [pref || (score("front") >= score("back") ? "front" : "back")];
  muscleDefs();
  const crop = /(^| )thumb( |$)/.test(o.cls || "");
  const fig = v => {
    const n = ++_muscleN, cvb = crop ? muscleCrop(v, map) : null;
    return MUSCLE_SVG[v]
      .replace(/viewBox="[^"]*"/, m => cvb ? 'viewBox="' + cvb + '"' : m)
      .replace(/(id="|url\(#)(t|al|ar)(\d+)/g, (m, a, b, c) => a + b + c + "-" + n)
      .replace(/class="m ([a-z_]+)( dk)?"/g, (m, k, dk) => 'class="m ' + k + (dk || "") + (map[k] === 1 ? " a1" : map[k] === 2 ? " a2" : "") + '"')
      .replace("<svg ", '<svg role="img" aria-label="Muscles sollicités, vue ' + (v === "front" ? "de face" : "de dos") + '" ').replace(' aria-hidden="true"', "");
  };
  return '<div class="mplate' + (o.cls ? " " + o.cls : "") + '">' + views.map(fig).join("") + "</div>";
}
function muscleList(lift){
  const map = muscleMap(lift) || {}, seen = new Set(), out = {p:[], s:[]};
  Object.keys(map).forEach(k => { const nm = MUSCLE_NAMES[k] || k; if (seen.has(nm)) return; seen.add(nm); (map[k] === 1 ? out.p : out.s).push(nm); });
  return out;
}
