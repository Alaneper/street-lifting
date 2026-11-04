/* =====================================================================
   ACCÈS AUX DONNÉES : API Google Sheets, connexion Google, aucun serveur
   Ce fichier est l'ADAPTATEUR GOOGLE de la bêta (connexion, création et choix du carnet, lecture/écriture Sheets).
   À la migration vers la vraie application, il est remplacé en bloc ; l'app n'y accède que via Store, Account et Ranking (src/app.html).
   ===================================================================== */
const CLIENT_ID = "__CLIENT_ID__";
const SCOPE = "https://www.googleapis.com/auth/spreadsheets email";
const API = "https://sheets.googleapis.com/v4/spreadsheets/";
const enc = encodeURIComponent, sleep = ms => new Promise(r => setTimeout(r, ms));
const ck = k => k + "-" + APP_ID;
const idOf = s => { const t = String(s || "").trim(), m = t.match(/\/d\/([a-zA-Z0-9_-]{20,})/); return m ? m[1] : (/^[a-zA-Z0-9_-]{20,}$/.test(t) ? t : ""); };
const sheetUrl = id => "https://docs.google.com/spreadsheets/d/" + id + "/edit";
const cfg = () => store.get("sl-cfg") || {};
const setCfg = o => store.set("sl-cfg", Object.assign(cfg(), o));
const auth = {
  err:null, leaving:false,
  get tok(){ const t = store.get("sl-tok"); return t && t.exp > Date.now() + 60000 ? t.t : null; },
  login(prompt){
    const st = Math.random().toString(36).slice(2); store.set("sl-state", st);
    const p = new URLSearchParams({client_id:CLIENT_ID, redirect_uri:location.origin + location.pathname, response_type:"token", scope:SCOPE, include_granted_scopes:"true", state:st});
    if (cfg().email) p.set("login_hint", cfg().email);
    if (prompt) p.set("prompt", prompt);
    auth.leaving = true;   /* une mise à jour de l'app ne doit pas annuler ce passage chez Google */
    location.href = "https://accounts.google.com/o/oauth2/v2/auth?" + p;
  },
  fromHash(){
    const h0 = location.hash; if (!/access_token=|error=/.test(h0)) return;
    const h = new URLSearchParams(h0.slice(1)); history.replaceState(null, "", location.pathname + location.search);
    if (h.get("state") !== store.get("sl-state")) return; store.del("sl-state");
    if (h.get("access_token")) store.set("sl-tok", {t:h.get("access_token"), exp:Date.now() + (+h.get("expires_in") || 3600) * 1000});
    else auth.err = h.get("error") || "erreur";
  },
  logout(){ const t = store.get("sl-tok"); store.del("sl-tok"); if (t) fetch("https://oauth2.googleapis.com/revoke?token=" + enc(t.t), {method:"POST"}).catch(() => {}); }
};
/* Jeton expiré : la séance en cours est déjà gardée sur le téléphone, on se reconnecte et on la rouvre. */
function reauth(){
  if (!navigator.onLine) throw {code:"offline"};
  if (live) { persistLive(); store.set("sl-resume", 1); }
  toast("Reconnexion à Google…"); setTimeout(() => auth.login(), 700);
  return new Promise(() => {});
}
async function gapi(url, opt, isRead){
  const tok = auth.tok; if (!tok) return reauth();
  for (let i = 0; ; i++) {
    let r;
    /* réseau qui ne répond pas (salle de sport, 1 barre) : au bout de 20 s on considère qu'il n'y a pas de réseau, au lieu de bloquer l'écran */
    const ac = typeof AbortController === "function" ? new AbortController() : null, tm = ac ? setTimeout(() => ac.abort(), 20000) : 0;
    try { r = await fetch(url, Object.assign({}, opt, {headers:{Authorization:"Bearer " + tok, "Content-Type":"application/json"}}, ac ? {signal:ac.signal} : {})); }
    catch(e){ clearTimeout(tm); throw {code:"offline"}; }
    if (r.status === 401) { store.del("sl-tok"); return reauth(); }
    if ((r.status === 429 || r.status >= 500) && isRead && i < 2) { await sleep(1500 * (i + 1) + Math.random() * 500); continue; }
    const j = await r.json().catch(() => ({})); clearTimeout(tm);
    if (ac && ac.signal.aborted) throw {code:"offline"};
    if (!r.ok) throw {code: r.status === 403 ? "forbidden" : r.status === 404 ? "not_found" : r.status === 429 ? "quota" : r.status >= 500 ? "server_unavailable" : "tool_error",
      retryable: r.status === 429 || r.status >= 500, message: (j.error && j.error.message) || ("Erreur " + r.status)};
    return j;
  }
}
const getVals = async (id, range, raw) => (await gapi(API + id + "/values/" + enc(range) + (raw ? "?valueRenderOption=FORMULA" : ""), {}, true)).values || [];   /* raw : la formule telle qu'écrite, pas son résultat */
const getMany = async (id, ranges) => ((await gapi(API + id + "/values:batchGet?" + ranges.map(r => "ranges=" + enc(r)).join("&"), {}, true)).valueRanges || []).map(v => v.values || []);
const putVals = (id, range, values) => gapi(API + id + "/values/" + enc(range) + "?valueInputOption=RAW", {method:"PUT", body:JSON.stringify({values})});
const appendVals = (id, range, values) => gapi(API + id + "/values/" + enc(range) + ":append?valueInputOption=RAW&insertDataOption=INSERT_ROWS", {method:"POST", body:JSON.stringify({values})});
const getTitles = async id => ((await gapi(API + id + "?fields=" + enc("sheets.properties.title"), {}, true)).sheets || []).map(s => s.properties && s.properties.title).filter(Boolean);

/* Enregistrer un fichier : feuille de partage iOS si possible, sinon téléchargement. */
const dlr = {async save({filename, data}){
  const f = new File([data], filename, {type:data.type || "application/octet-stream"});
  if (!/\.ics$/i.test(filename) && navigator.canShare && navigator.canShare({files:[f]})) {
    try { await navigator.share({files:[f]}); return {status:"saved"}; } catch(e){ if (e && e.name === "AbortError") throw e; }
  }
  const u = URL.createObjectURL(data), a = document.createElement("a"); a.href = u; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(u), 60000); return {status:"saved"};
}};

/* ---------- Carnet de données : structure ---------- */
const TABS = {
  PROFIL:["Clé","Valeur","Note"], PR:["Date","Mouvement","Charge (kg)","Reps","Note","RPE","Équipement"], POIDS:["Date","Poids (kg)","Note"],
  OBJECTIFS:["Mouvement","Objectif (kg)","Note"],
  COMPETITIONS:["Date","Nom","Lieu","Note","Statut"], SERIES:["Date","Bloc","Semaine","Séance","Exercice","Charge (kg)","Reps par série","Source","Note","Commentaire"],
  BLOCS:["Bloc","Lundi de la semaine 1","Note"],
  CHECKLIST:["Date compét","Élément","Fait"], BILAN:["Date","Bloc","Semaine","Sommeil","Plaisir","Motivation","Fatigue","Hydratation","Alimentation"],
  HISTORIQUE:["Prog","Onglet","Bloc","Début du bloc","Semaine","Séance","Jour","Ligne","Mouvement","Variation","Séries","Reps","Charge","RPE S1","RPE dernière","Commentaire athlète","Cycle"],
  REPAS:["Date","Heure","Aliment","Source","Code","Quantité (g)","Kcal","Protéines (g)","Glucides (g)","Lipides (g)"], ALIMENTS:["Nom","Marque","Source","Code","Kcal /100 g","Protéines /100 g","Glucides /100 g","Lipides /100 g","Note"],
  MES_REPAS:["Repas","Aliment","Source","Code","Quantité (g)","Kcal","Protéines (g)","Glucides (g)","Lipides (g)"]
};
async function writeMany(id, data){ return gapi(API + id + "/values:batchUpdate", {method:"POST", body:JSON.stringify({valueInputOption:"RAW", data})}); }
async function ensureTabs(id){
  const have = new Set(await getTitles(id)), miss = Object.keys(TABS).filter(t => !have.has(t));
  if (!miss.length) return;
  await gapi(API + id + ":batchUpdate", {method:"POST", body:JSON.stringify({requests:miss.map(t => ({addSheet:{properties:{title:t}}}))})});
  await writeMany(id, miss.map(t => ({range:t + "!A1", values:[TABS[t]]})));
}
/* Nouvel onglet (programme importé) dans le carnet : création puis écriture groupée. */
async function addProgTab(id, title, rows){
  const r = await gapi(API + id + ":batchUpdate", {method:"POST", body:JSON.stringify({requests:[{addSheet:{properties:{title}}}]})});
  await writeMany(id, [{range:q(title) + "!A1", values:rows.map(r => r.map(v => String(v ?? "")))}]);
  /* Logo de l'app en A1, puis mise en forme (maquette A). Un échec ici n'empêche rien : le programme est déjà écrit. */
  const sid = r && r.replies && r.replies[0] && r.replies[0].addSheet ? r.replies[0].addSheet.properties.sheetId : undefined;
  try { await gapi(API + id + "/values:batchUpdate", {method:"POST", body:JSON.stringify({valueInputOption:"USER_ENTERED", data:[{range:q(title) + "!A1", values:[['=IMAGE("' + location.origin + location.pathname.replace(/[^/]*$/, "") + 'icon-192.png";4;56;56)']]}]})}); } catch(e){ console.warn("logo", e); }
  if (sid === undefined) return;
  const style = noFont => gapi(API + id + ":batchUpdate", {method:"POST", body:JSON.stringify({requests:ProgImport.sheetStyle(rows, sid, noFont)})});
  try { await style(false); } catch(e){ try { await style(true); } catch(e2){ console.warn("mise en forme", e2); } }
}
async function createBook(p){
  const r = await gapi(API, {method:"POST", body:JSON.stringify({properties:{title:"B2Strong – " + (p.prenom || "carnet"), locale:"fr_FR"},
    sheets:Object.keys(TABS).map(t => ({properties:{title:t, gridProperties:{frozenRowCount:1}}}))})});
  const id = r.spreadsheetId;
  /* v28 : catégories automatiques d'après la pesée (modifiables dans les réglages) ; plus de « muscle-up acquis » */
  const prof = [["prenom",p.prenom],["sexe",p.sexe],["naissance",p.naissance || ""],["taille_cm",p.taille || ""],["categorie",p.categorie],["categorie_auto","OUI"],["categorie_ipf_auto","OUI"],
    ["disciplines",p.disciplines || "street"],["power_mode",p.power_mode || "classic"],["coach_sheet_id",p.coach || ""],["bloc_actif",p.bloc || ""],
    ["debut_street",p.debut || ""],["debut_coaching",p.debutCoach || ""],["pays",p.pays || "BE"]];
  const data = Object.keys(TABS).map(t => ({range:t + "!A1", values:[TABS[t]]}));
  data.push({range:"PROFIL!A2", values:prof});
  const eqm = p.power_mode === "equipped" && /power/.test(p.disciplines || "");
  const prs = ALL_LIFTS.filter(l => num(p["pr_" + l]) !== null && String(p["pr_" + l]).trim() !== "").map(l => [isoOf(new Date()), l, num(p["pr_" + l]), 1, p.coach && obPre ? "Max de la prog du coach" : "Saisi à l'inscription", "", eqm && POWER_LIFTS.includes(l) ? "EQ" : ""]);
  if (prs.length) data.push({range:"PR!A2", values:prs});
  if (num(p.poids)) data.push({range:"POIDS!A2", values:[[isoOf(new Date()), num(p.poids), ""]]});
  if (p.bloc && p.blocDate) data.push({range:"BLOCS!A2", values:[[p.bloc, p.blocDate, "saisi à l'inscription"]]});
  await writeMany(id, data);
  return id;
}

/* ---------- Accueil, connexion et choix du carnet ---------- */
let obStep = "login", obErr = "", obPre = null;
/* Lit, dans le dernier onglet BLOC de la prog (modèle du coach), les cases MAX ACTUELS et PROFIL. */
function parseCoachProfile(v){
  const out = {}, cell = (r, c) => String((v[r] && v[r][c]) ?? "").trim();
  const numRight = (r, c) => { for (let k = c + 1; k <= c + 3; k++) { const t = cell(r, k); if (t !== "" && num(t) !== null) return num(t); } return null; };
  const MAP = {MU:"MU", "MUSCLE UP":"MU", PU:"PULL", "PULL UP":"PULL", TRACTIONS:"PULL", DIPS:"DIP", DIP:"DIP", SQUAT:"SQUAT", BENCH:"BENCH", "BENCH PRESS":"BENCH", BP:"BENCH", DC:"BENCH", DEADLIFT:"DEADLIFT", DL:"DEADLIFT", SDT:"DEADLIFT"};
  for (let r = 0; r < v.length; r++) for (let c = 0; c < (v[r] || []).length; c++) {
    const t = norm(cell(r, c));
    if (t === "MAX ACTUELS" && out.max === undefined) { out.max = true;
      for (let rr = r + 1; rr < Math.min(v.length, r + 8); rr++) { const k = MAP[norm(cell(rr, c))]; if (k) { const n = numRight(rr, c); if (n) out["pr_" + k] = n; } } }
    if (t === "POIDS" && out.poids === undefined) out.poids = numRight(r, c) ?? undefined;
    if (t === "TAILLE" && out.taille === undefined) { const n = numRight(r, c); if (n) out.taille = n < 3 ? Math.round(n * 100) : n; }
  }
  delete out.max;
  if (out.poids) { const c = CATS.find(x => x < 0 && out.poids <= -x); out.categorie = c ?? CATS.at(-1); }
  return out;
}
function prenomOf(title){
  const w = String(title || "").trim().split(/\s+/).filter(Boolean); if (!w.length) return "";
  const p = w.filter(x => x !== x.toUpperCase()); const n = (p.length ? p : [w.at(-1)]).join(" ");
  return n.charAt(0).toUpperCase() + n.slice(1).toLowerCase();
}
function onboard(step, why){
  obStep = step; obErr = why || ""; document.body.classList.add("ob");
  document.querySelectorAll(".view").forEach(v => v.hidden = v.id !== "v-home");
  const err = obErr ? `<p class="small" style="color:var(--bad);margin-top:12px">${esc(obErr)}</p>` : "";
  const BACK = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>`;
  const head = (n, tot, title, sub) => `<div class="obtop"><button class="obback" data-act="obBack" aria-label="Retour">${BACK}</button></div>
    <div class="obseg" role="progressbar" aria-label="Progression de l'inscription" aria-valuemin="1" aria-valuemax="${tot}" aria-valuenow="${n}">${Array.from({length:tot}, (_, i) => `<i${i < n ? ' class="on"' : ""}></i>`).join("")}</div>
    <p class="obstep">Étape ${n} sur ${tot}</p><h1 class="obh">${title}</h1><p class="obsub">${sub}</p>`;
  const foot = (main, extra) => `<div class="obfoot">${main}${extra || ""}</div>`;
  const next = (t, id) => `<button class="btn" data-act="${id || "obNext"}"${id === "obCreate" ? ' id="obgo"' : ""}>${t || "Continuer"}</button>`;
  let h = "";
  if (step === "config") h = `<div class="empty"><p>L'identifiant Google de l'app n'est pas encore configuré.</p></div>`;
  else if (step === "login") h = `<div class="obbg" aria-hidden="true"><i></i><i></i></div><div class="obw obhome">
    <svg class="oblogo" viewBox="0 0 120 100" aria-label="B2Strong"><g fill="none" stroke="var(--chalk)" stroke-linecap="butt" stroke-linejoin="miter"><line x1="11" y1="0" x2="11" y2="100" stroke-width="22"/><path d="M11 9.5H38A19.25 19.25 0 0 1 38 48H11" stroke-width="19"/><path d="M11 48H43A21.25 21.25 0 0 1 43 90.5H11" stroke-width="19"/></g><path d="M6 30C6 12 20 2 34 2C50 2 61 12 61 27C61 39 53 48 41 58L24 73H61V96H4V77L34 50C40 44 45 38 45 30C45 22 41 17 34 17C26 17 22 23 22 32Z" fill="var(--acc)" transform="translate(76 0) scale(0.44)"/></svg>
    <h1 class="obbig">Be too<br>strong.</h1><p class="obsub" style="margin-top:14px">Le suivi des athlètes de force.<br>Mieux qu'hier, chaque séance.</p>
    <div class="obfoot"><button class="btn" data-act="obLogin">Créer mon compte</button><button class="btn ghost" style="margin-top:12px" data-act="obLogin">J'ai déjà un compte</button>${err}
    <p class="obfine">Connexion avec Google : tes données restent dans ton propre Google Sheet. Google peut afficher « application non validée » : c'est normal pour une app en test, touche « Continuer ».</p></div></div>`;
  else if (step === "carnet") h = `<div class="obw"><div class="obtop"><span></span></div><h1 class="obh" style="margin-top:34px">Ton Google Sheet</h1>
    <p class="obsub">L'app range tes records, pesées, séances et repas dans un Google Sheet à toi.</p>
    <div class="panel" style="margin-top:18px"><p style="font-weight:700;font-size:17px">Nouveau ici, avec une prog de coach</p><p class="muted small" style="margin-top:4px">Colle le lien de ta prog : l'app y lit ton prénom, ton poids et tes max, et crée ton Google Sheet.</p>
      <label for="obcoach">Lien de la prog de ton coach</label><input id="obcoach" type="url" placeholder="https://docs.google.com/spreadsheets/d/…">
      <button class="btn" style="margin-top:12px" data-act="obFromCoach" id="obfc">Tout remplir depuis ma prog</button>
      <button class="link small" style="margin-top:12px" data-act="obStep" data-s="create">Je n'ai pas de prog, je remplis moi-même</button></div>
    <div class="panel"><p style="font-weight:700;font-size:17px">J'ai déjà un Google Sheet</p><label for="oblink">Lien du Google Sheet</label><input id="oblink" type="url" placeholder="https://docs.google.com/spreadsheets/d/…">
      <label class="obcs"><input type="checkbox" id="obcs2"><span>Mon Sheet est ma prog personnelle : mettre à jour la charge avec ce que j'ai fait</span></label><p class="muted tiny" style="margin-top:4px">Facultatif, désactivé par défaut. À cocher seulement si cette prog est la tienne, pas celle d'un coach : l'app mettra la charge faite dans la colonne « Charge » de la semaine en cours, jamais dans les suivantes. Modifiable dans les réglages.</p><button class="btn ghost" style="margin-top:12px" data-act="obLink">Utiliser ce Google Sheet</button></div>${err}</div>`;
  else if (step === "create") { if (!obA) obInit(); const A = obA, P = obPre || {}, STEPS = obSteps(), key = STEPS[obI], n = obI + 1, tot = STEPS.length, v = x => esc(x === undefined || x === null ? "" : String(x));
    const CK = `<span class="ck" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0A0B0D" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></span>`;
    const dots = L => L.map(l => `<i style="--c:${LCOL[l]}"></i>`).join("");
    const opt = (k, t, s, d) => `<button class="dcard" aria-pressed="${A.disc[k]}" data-act="obDisc" data-k="${k}"><span class="discs" aria-hidden="true">${d}</span><span class="dtx"><b>${t}</b><span class="sub">${s}</span></span>${CK}</button>`;
    if (key === "prenom") h = `<div class="obw">${head(n, tot, "Ton prénom ?", obPre ? "Rempli depuis ta prog. Corrige si besoin." : "Ton prénom s'affiche dans l'app.")}
      <input id="obp" class="obin" autocomplete="given-name" placeholder="Prénom" value="${v(A.prenom)}" aria-label="Prénom">${err}${foot(next())}</div>`;
    else if (key === "disc") h = `<div class="obw">${head(n, tot, "Tu soulèves quoi ?", "On adapte les records, les scores et les catégories. Tu peux en choisir plusieurs.")}
      <div class="dgrid">${opt("power", "Powerlifting", "Squat, bench, deadlift · IPF GL", dots(POWER_LIFTS))}${opt("street", "Street lifting", "Tractions, dips, muscle-up lestés · RIS", dots(LIFTS))}${opt("muscu", "Musculation", "Programmes, volume, progression", '<i style="--c:var(--steel)"></i><i style="--c:var(--cardio)"></i>')}</div>
      <div class="reveal" id="obpow" ${A.disc.power ? "" : "hidden"}><b style="font-size:15px">En powerlifting, tu tires</b>
        <div class="segc" role="group" aria-label="Classic ou equipped" style="margin-top:10px"><button aria-pressed="${A.mode === "classic"}" data-act="obMode" data-k="classic">Classic</button><button aria-pressed="${A.mode === "equipped"}" data-act="obMode" data-k="equipped">Equipped</button></div>
        <p class="muted small" style="margin-top:8px">Equipped : combinaison et bandes. Le score n'est pas le même, tu pourras changer dans les réglages.</p></div>${foot(next())}</div>`;
    else if (key === "toi") h = `<div class="obw">${head(n, tot, "Un peu de toi", A.disc.street || A.disc.power ? "Pour te placer dans la bonne catégorie et calculer ton score." : "Pour personnaliser tes repères.")}
      <label style="margin-top:24px">Sexe</label>
      <div class="segc" role="group" aria-label="Sexe" style="margin-top:0"><button aria-pressed="${A.sexe === "H"}" data-act="obSex" data-k="H">Homme</button><button aria-pressed="${A.sexe === "F"}" data-act="obSex" data-k="F">Femme</button></div>
      <div class="grid2"><div><label for="obn">Date de naissance</label><input id="obn" type="date" data-inp="ob" value="${v(A.naissance)}"></div><div><label for="obw">Poids de corps (kg)</label><input id="obw" inputmode="decimal" placeholder="73,2" value="${v(A.poids)}" data-inp="ob"></div></div>
      <label for="obpa">Pays</label><select id="obpa">${paysOptions(A.pays || "BE")}</select>
      <div id="obcatsec"><h2 class="h2">Tes catégories <span class="pill">calculées pour toi</span></h2><div class="group" id="obcats"></div>
        <p class="muted small" style="margin-top:10px">D'après ton poids et ta date de naissance. Tu pourras viser la catégorie du dessus ou du dessous dans les réglages.</p></div>${foot(next())}</div>`;
    else if (key === "barres") { const ls = ALL_LIFTS.filter(l => (A.disc.street && LIFTS.includes(l)) || (A.disc.power && POWER_LIFTS.includes(l)));
      h = `<div class="obw">${head(n, tot, "Tes meilleures barres", "Ton meilleur poids sur une répétition. Laisse vide ce que tu ne connais pas.")}<div id="obprsec">
      ${ls.map(l => `<div class="obrow" data-lift="${l}"><span class="discs" aria-hidden="true"><i style="--c:${LCOL[l]}"></i></span><span class="grow"><b>${LNAME[l]}</b><span>${BW_LIFTS.includes(l) ? "Lest ajouté" : "1 répétition"}</span></span><label class="obkg"><input id="obpr${l}" inputmode="decimal" placeholder="0" value="${v(A.pr[l])}" data-inp="ob" aria-label="${LNAME[l]} en kg"><small>kg</small></label></div>`).join("")}</div>
      <div class="obtot" id="obtot" hidden><b></b><span>Total de départ. On le battra ensemble.</span></div>
      ${foot(next(), `<button class="link obskip" data-act="obSkipPr">Je ne sais pas encore</button>`)}</div>`; }
    else if (key === "coach") h = `<div class="obw">${head(n, tot, "Presque fini", P.bloc ? "Ta prog a été lue. Vérifie ton bloc en cours." : "Deux infos facultatives, tu pourras tout changer dans les réglages.")}
      <label for="obk">Lien de la prog de ton coach <span class="muted">facultatif</span></label><input id="obk" type="url" placeholder="https://docs.google.com/spreadsheets/d/…" value="${v(A.coach)}">
      ${P.blocs && P.blocs.length ? `<label for="obbl">Ton bloc en cours</label><select id="obbl">${P.blocs.map(m => `<option value="${m}" ${m === A.bloc ? "selected" : ""}>${esc(/^\s*BLOC\s*\d+\s*$/i.test(P.blocTitles[m]) ? "Bloc " + m : P.blocTitles[m].trim())}</option>`).join("")}</select>` : ""}
      ${P.bloc ? `<label for="obb">Lundi de la semaine 1 de ce bloc</label><input id="obb" type="date" value="${v(A.blocDate)}"><p class="muted tiny" style="margin-top:6px">Pour dater tes séances. Tu pourras le changer plus tard.</p>` : ""}
      <p class="muted tiny" style="margin-top:6px">La prog doit être partagée avec le compte Google avec lequel tu es connecté.</p>
      <label class="obcs"><input type="checkbox" id="obcs"><span>Mon Sheet est ma prog personnelle : mettre à jour la charge avec ce que j'ai fait</span></label><p class="muted tiny" style="margin-top:4px">Facultatif, désactivé par défaut. À cocher seulement si cette prog est la tienne, pas celle d'un coach : l'app mettra la charge faite dans la colonne « Charge » de la semaine en cours, jamais dans les suivantes. Modifiable dans les réglages.</p>
      <label for="obd">Début de la pratique <span class="muted">facultatif</span></label><div class="grid2"><div><input id="obd" type="date" value="${v(A.debut)}"></div><div></div></div>${err}${foot(next("Créer mon Google Sheet", "obCreate"))}</div>`; }
  $("#v-home").innerHTML = `<div class="ob">${h}</div>`;
  if (step === "create") obRefresh();
}
/* Inscription : une question par écran (maquette Inscription2). Seul l'enchaînement change : les réponses sont gardées dans obA, puis obCreate écrit les mêmes champs qu'avant dans createBook(p). */
let obA = null, obI = 0;
function obInit(){ const P = obPre || {}, s = x => x === undefined || x === null ? "" : String(x).replace(".", ",");
  obA = {prenom:P.prenom || "", disc:{street:true, power:false, muscu:false}, mode:"classic", sexe:"H", naissance:"", poids:s(P.poids), pays:"BE", pr:{}, debut:"", coach:P.coach ? sheetUrl(P.coach) : "", bloc:P.bloc, blocDate:""};
  ALL_LIFTS.forEach(l => { if (P["pr_" + l]) obA.pr[l] = s(P["pr_" + l]); }); obI = 0; }
const obSteps = () => { const D = obA.disc; return ["prenom", "disc", "toi"].concat(D.street || D.power ? ["barres"] : [], ["coach"]); };
/* Recopie les champs visibles dans obA (avant de changer d'écran ou de créer le carnet). */
function obSave(){ if (!obA) return; const g = id => { const e = document.getElementById(id); return e ? e.value : undefined; };
  [["prenom", "obp"], ["naissance", "obn"], ["poids", "obw"], ["pays", "obpa"], ["debut", "obd"], ["coach", "obk"], ["bloc", "obbl"], ["blocDate", "obb"]].forEach(([k, id]) => { const v = g(id); if (v !== undefined) obA[k] = v; });
  ALL_LIFTS.forEach(l => { const v = g("obpr" + l); if (v !== undefined) obA.pr[l] = v; }); }
const obOn = k => !!obA && !!obA.disc[k];
const obSel = a => !obA ? undefined : a === "obSex" ? obA.sexe : a === "obMode" ? obA.mode : undefined;
function obRefresh(){
  const st = obOn("street"), pw = obOn("power"), sx = obA.sexe || "H", w = num(($("#obw") || {}).value), b = ($("#obn") || {}).value || "";
  const ages = ageCats(b, isoOf(new Date())), youth = ages.some(a => a === "SJ" || a === "JR");
  const pp = $("#obpow"); if (pp) pp.hidden = !pw;
  { const f = !st && !pw; ["obcatsec", "obprsec"].forEach(i => { const e = $("#" + i); if (e) e.hidden = f; }); }   /* musculation seule : ni catégorie ni PR */
  const row = (t, s, val) => `<div class="catrow"><span class="grow"><b>${t}</b><span>${s}</span></span><span class="val"${/kg/.test(val) ? "" : ' style="font-size:22px"'}>${val}</span></div>`;
  const kgv = c => c === null ? "—" : catTxt(c).replace(" kg", "<small>kg</small>");
  const el = $("#obcats"); if (el) el.innerHTML = (st ? row("Street lifting", "Official Streetlifting", w ? kgv(catAuto(w, catsFor(sx))) : "—") : "")
    + (pw ? row("Powerlifting", "IPF", w ? kgv(catAuto(w, catsIpfFor(sx, youth))) : "—") : "")
    + row("Âge", ages.length > 1 ? ages.map(a => AGE_NAME[a]).join(" et ") : ages.length ? "Catégorie d'âge IPF" : b ? "Moins de 14 ans : pas de catégorie IPF" : "Ajoute ta date de naissance", ages.length ? AGE_NAME[ages[0]] : "—");
  /* total de départ : somme des trois barres du powerlifting, seulement si elles sont toutes remplies */
  const tt = $("#obtot"); if (tt) { const v = POWER_LIFTS.map(l => num(($("#obpr" + l) || {}).value)); const ok = pw && v.every(x => x !== null && x > 0); tt.hidden = !ok; if (ok) tt.querySelector("b").textContent = fmt(v.reduce((a, c) => a + c, 0)).replace(".", ","); }
}
document.addEventListener("input", ev => { if (ev.target && ev.target.dataset && ev.target.dataset.inp === "ob") obRefresh(); });
Object.assign(ACT, {
  obLogin:() => auth.login("select_account"),
  obStep:d => { if (d.s === "create") { obPre = null; obInit(); } onboard(d.s); },
  obNext:() => { obSave(); const A = obA, k = obSteps()[obI];
    if (k === "prenom" && !A.prenom.trim()) return toast("Indique ton prénom", true);
    if (obI < obSteps().length - 1) { obI++; onboard("create"); } },
  obBack:() => { obSave(); if (obI > 0) { obI--; onboard("create"); } else onboard("carnet"); },
  obSkipPr:() => { obA.pr = {}; if (obI < obSteps().length - 1) { obI++; onboard("create"); } },
  obDisc:(d, el) => { const b = el.closest("[data-act]"), D = obA.disc, on = D[d.k], others = ["street", "power", "muscu"].filter(k => k !== d.k);
    if (on && !others.some(k => D[k])) return toast("Choisis au moins une discipline", true); D[d.k] = !on; b.setAttribute("aria-pressed", String(!on)); obRefresh(); },
  obMode:(d, el) => { obA.mode = d.k; document.querySelectorAll("[data-act=obMode]").forEach(x => x.setAttribute("aria-pressed", String(x.dataset.k === d.k))); },
  obSex:(d, el) => { obA.sexe = d.k; document.querySelectorAll("[data-act=obSex]").forEach(x => x.setAttribute("aria-pressed", String(x.dataset.k === d.k))); obRefresh(); },
  obLink:async () => { const id = idOf($("#oblink").value); if (!id) return onboard("carnet", "Ce lien ne ressemble pas à un lien de Google Sheet.");
    try { const t = await getTitles(id);
      if (!t.includes("PROFIL") && (t.some(x => /^\s*BLOC\s*\d+/i.test(x)) || (await progTabs(id)).order.length)) return onboard("carnet", "Ce lien est celui d'une prog de coach, pas d'un Google Sheet B². Colle-le plus haut, dans « Nouveau ici, avec une prog de coach ».");
      await ensureTabs(id); } catch(e){ return onboard("carnet", errMsg(e)); }
    if ($("#obcs2") && $("#obcs2").checked) store.set("sl4-csync-pend", true);
    setCfg({appId:id}); APP_ID = id; startApp(); },
  obFromCoach:async () => {
    const id = idOf($("#obcoach").value); if (!id) return toast("Ce lien de Google Sheet n'est pas reconnu", true);
    const b = $("#obfc"); b.disabled = true; b.textContent = "Lecture de ta prog…";
    try {
      const meta = await gapi(API + id + "?fields=" + enc("properties.title,sheets.properties.title"), {}, true);
      const pt = await progTabs(id), last = pt.order.at(-1);
      const pre = {coach:id, prenom:prenomOf(meta.properties && meta.properties.title)};
      if (pt.order.length) { Object.assign(pre, parseCoachProfile(await getVals(id, q(pt.names[last]) + "!A1:CZ24")), {bloc:last, blocs:pt.order.slice(), blocTitles:pt.names}); }
      const blocs = pt.order;
      obPre = pre; obInit(); onboard("create", blocs.length ? "" : "Aucun onglet de séances trouvé dans cette prog : remplis ton profil à la main.");
    } catch(e){ b.disabled = false; b.textContent = "Tout remplir depuis ma prog"; toast("Prog inaccessible : " + errMsg(e), true); }
  },
  obCreate:async () => {
    obSave(); const cs = !!($("#obcs") && $("#obcs").checked), A = obA, st = A.disc.street, pw = A.disc.power, mu = A.disc.muscu, sx = A.sexe, w = num(A.poids), nai = A.naissance || "";
    const p = {prenom:A.prenom.trim(), sexe:sx, naissance:nai, disciplines:[st ? "street" : "", pw ? "power" : "", mu ? "muscu" : ""].filter(Boolean).join(","), power_mode:A.mode || "classic",
      categorie:w && (st || pw) ? catAuto(w, catsFor(sx)) : "", debut:A.debut, poids:A.poids, coach:idOf(A.coach),
      taille:obPre && obPre.taille, pays:A.pays || "BE", bloc:A.bloc !== undefined && A.bloc !== "" ? Number(A.bloc) : obPre && obPre.bloc, blocDate:A.blocDate || ""};
    ALL_LIFTS.forEach(l => { p["pr_" + l] = (st && LIFTS.includes(l)) || (pw && POWER_LIFTS.includes(l)) ? (A.pr[l] || "") : ""; });
    if (!p.prenom) { obI = 0; onboard("create"); return toast("Indique ton prénom", true); }
    if (A.coach.trim() && !p.coach) return toast("Le lien de la prog n'est pas reconnu", true);
    const b = $("#obgo"); b.disabled = true; b.textContent = "Création…";
    try {
      if (p.coach) { try { await getTitles(p.coach); } catch(e){ b.disabled = false; b.textContent = "Créer mon Google Sheet"; return toast("Prog du coach inaccessible : " + errMsg(e), true); } }
      const id = await createBook(p); if (cs) setChargeSync(p.coach || id, true); setCfg({appId:id}); APP_ID = id; toast("Google Sheet créé"); startApp();
    } catch(e){ b.disabled = false; b.textContent = "Créer mon Google Sheet"; toast(errMsg(e), true); }
  },
  switchBook:() => { setCfg({appId:""}); APP_ID = ""; D = null; S = []; sheet = null; renderLayer(); onboard("carnet"); },
  logout:() => { auth.logout(); store.set("sl-cfg", {}); APP_ID = ""; D = null; S = []; sheet = null; renderLayer(); onboard("login"); }
});
CHG.coachLink = async (d, el) => {
  const id = idOf(el.value); if (el.value.trim() && !id) return toast("Ce lien de Google Sheet n'est pas reconnu", true);
  if (id) { try { await getTitles(id); } catch(e){ return toast("Prog inaccessible : " + errMsg(e), true); } }
  await CHG.prof({k:"coach_sheet_id"}, {value:id});
  S = []; loadedBlocs.clear(); allLoaded = false; weekMeta = {}; blocNames = {}; progOrder = []; liveIds = new Set(); archMeta = {}; liveCycle = {}; syncAll(false);
};
ACT.coachUnlink = () => CHG.coachLink({}, {value:""});
async function fetchEmail(){
  if (cfg().email) return;
  try { const r = await fetch("https://www.googleapis.com/oauth2/v3/userinfo", {headers:{Authorization:"Bearer " + auth.tok}}); const j = await r.json(); if (j.email) setCfg({email:j.email}); } catch(e){}
}
