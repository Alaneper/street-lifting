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
const getVals = async (id, range) => (await gapi(API + id + "/values/" + enc(range), {}, true)).values || [];
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
  COMPETITIONS:["Date","Nom","Lieu","Note","Statut"], SERIES:["Date","Bloc","Semaine","Séance","Exercice","Charge (kg)","Reps par série","Source","Note"],
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
  const r = await gapi(API, {method:"POST", body:JSON.stringify({properties:{title:"Street Lifting – " + (p.prenom || "carnet"), locale:"fr_FR"},
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
  const plates = `<div class="hero" style="margin-top:18px;min-height:150px">${DECO}<svg width="64" height="64" viewBox="0 0 40 40" aria-hidden="true" style="position:relative;background:#fff;border-radius:16px;padding:6px"><circle cx="20" cy="10.5" r="4.2" fill="#1F5FD0"/><path d="M7 17h26" stroke="#1F5FD0" stroke-width="3.6" stroke-linecap="round"/><path d="M11 17l4.5 9 4.5-3.5 4.5 3.5 4.5-9" stroke="#1F5FD0" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg><p class="hu" style="margin-top:14px">Ta prog, tes records, ta prochaine compétition.</p></div>`;
  const err = obErr ? `<p class="small" style="color:var(--bad);margin-top:12px">${esc(obErr)}</p>` : "";
  let h = "";
  if (step === "config") h = `<div class="empty"><p>L'identifiant Google de l'app n'est pas encore configuré.</p></div>`;
  else if (step === "login") h = `${plates}<p class="show" style="font-size:44px;font-weight:800;margin-top:22px;line-height:1">Street Lifting</p>
    <p class="muted" style="margin-top:12px">Connecte ton compte Google. Tes données restent dans ton propre Google Sheet : personne d'autre n'y a accès.</p>
    <button class="btn" style="margin-top:22px" data-act="obLogin">Continuer avec Google</button>${err}
    <p class="muted tiny" style="margin-top:14px">Google peut afficher « application non validée » : c'est normal pour une app en test. Touche « Continuer ».</p>`;
  else if (step === "carnet") h = `<p class="show t-m" style="margin-top:18px">Ton carnet de données</p>
    <p class="muted small" style="margin-top:6px">L'app range tes records, pesées, séances et repas dans un Google Sheet à toi.</p>
    <div class="panel" style="margin-top:16px"><p style="font-weight:600">Nouveau ici, avec une prog de coach</p><p class="muted small" style="margin-top:4px">Colle le lien de ta prog : l'app y lit ton prénom, ton poids et tes max, et crée ton carnet.</p>
      <label for="obcoach">Lien de la prog de ton coach</label><input id="obcoach" type="url" placeholder="https://docs.google.com/spreadsheets/d/…">
      <button class="btn" style="margin-top:12px" data-act="obFromCoach" id="obfc">Tout remplir depuis ma prog</button>
      <button class="link small" style="margin-top:12px" data-act="obStep" data-s="create">Je n'ai pas de prog, je remplis moi-même</button></div>
    <div class="panel"><p style="font-weight:600">J'ai déjà un carnet</p><label for="oblink">Lien du Google Sheet</label><input id="oblink" type="url" placeholder="https://docs.google.com/spreadsheets/d/…">
      <button class="btn ghost" style="margin-top:12px" data-act="obLink">Utiliser ce carnet</button></div>${err}`;
  else if (step === "create") { const P = obPre || {}, v = x => x === undefined || x === null ? "" : esc(String(x).replace(".", ","));
    const CK = `<span class="ck" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0A0B0D" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></span>`;
    const dots = L => L.map(l => `<i style="--c:${LCOL[l]}"></i>`).join("");
    h = `<p class="eyebrow" style="margin-top:18px">Création du carnet</p><h1 class="show t-l" style="margin-top:6px">Ton profil</h1>
    <p class="muted" style="margin-top:8px">${obPre ? "Rempli depuis ta prog" + (P.bloc ? " (onglet « " + esc(P.blocTitles[P.bloc].trim()) + " »)" : "") + ". Vérifie et corrige si besoin." : "Quelques infos pour te placer dans la bonne catégorie et calculer ton score."}</p>
    <label for="obp">Prénom</label><input id="obp" autocomplete="given-name" value="${v(P.prenom)}">

    <h2 class="h2">Tes disciplines <span class="muted">une ou plusieurs</span></h2>
    <div class="dgrid">
      <button class="dcard" aria-pressed="true" data-act="obDisc" data-k="street">${CK}<span class="discs" aria-hidden="true">${dots(LIFTS)}</span><b>Street lifting</b><span class="sub">Muscle-up, tractions, dips, squat</span><span class="sc">Score RIS</span></button>
      <button class="dcard" aria-pressed="false" data-act="obDisc" data-k="power">${CK}<span class="discs" aria-hidden="true">${dots(POWER_LIFTS)}</span><b>Powerlifting</b><span class="sub">Squat, Bench, Deadlift</span><span class="sc">Score IPF GL</span></button>
      <button class="dcard" aria-pressed="false" data-act="obDisc" data-k="muscu" style="grid-column:1/-1">${CK}<span class="discs" aria-hidden="true"><i style="--c:var(--steel)"></i><i style="--c:var(--cardio)"></i></span><b>Musculation</b><span class="sub">Machines, haltères, poids du corps, cardio</span><span class="sc">Charges, volume, régularité</span></button>
    </div>
    <div class="reveal" id="obpow" hidden><b style="font-size:15px">En powerlifting, tu tires</b>
      <div class="segc" role="group" aria-label="Classic ou equipped" style="margin-top:10px"><button aria-pressed="true" data-act="obMode" data-k="classic">Classic</button><button aria-pressed="false" data-act="obMode" data-k="equipped">Equipped</button></div>
      <p class="muted small" style="margin-top:8px">Equipped : combinaison et bandes. Le score n'est pas le même, tu pourras changer dans les réglages.</p></div>

    <h2 class="h2">Toi</h2>
    <label style="margin-top:0">Sexe</label>
    <div class="segc" role="group" aria-label="Sexe" style="margin-top:0"><button aria-pressed="true" data-act="obSex" data-k="H">Homme</button><button aria-pressed="false" data-act="obSex" data-k="F">Femme</button></div>
    <div class="grid2"><div><label for="obn">Date de naissance</label><input id="obn" type="date" data-inp="ob"></div><div><label for="obw">Poids de corps (kg)</label><input id="obw" inputmode="decimal" placeholder="73,2" value="${v(P.poids)}" data-inp="ob"></div></div>
    <label for="obpa">Pays</label><select id="obpa">${paysOptions("BE")}</select>

    <div id="obcatsec"><h2 class="h2">Tes catégories <span class="pill">calculées pour toi</span></h2>
    <div class="group" id="obcats"></div>
    <p class="muted small" style="margin-top:10px">D'après ton poids et ta date de naissance. Tu pourras viser la catégorie du dessus ou du dessous dans les réglages.</p></div>

    <div id="obprsec"><h2 class="h2">Tes PR actuels <span class="muted">facultatif</span></h2>
    <div class="grid2">${ALL_LIFTS.map(l => `<div data-lift="${l}"${LIFTS.includes(l) ? "" : " hidden"}><label for="obpr${l}" style="margin-top:0">${LNAME[l]}${BW_LIFTS.includes(l) ? " · lest" : ""}</label><input id="obpr${l}" inputmode="decimal" placeholder="kg" value="${v(P["pr_" + l])}"></div>`).join("")}</div></div>
    <div class="grid2"><div><label for="obd">Début de la pratique</label><input id="obd" type="date"></div><div></div></div>
    <label for="obk">Lien de la prog de ton coach (facultatif)</label><input id="obk" type="url" placeholder="https://docs.google.com/spreadsheets/d/…" value="${P.coach ? sheetUrl(P.coach) : ""}">
    ${P.blocs && P.blocs.length ? `<label for="obbl">Ton bloc en cours</label><select id="obbl">${P.blocs.map(n => `<option value="${n}" ${n === P.bloc ? "selected" : ""}>${esc(/^\s*BLOC\s*\d+\s*$/i.test(P.blocTitles[n]) ? "Bloc " + n : P.blocTitles[n].trim())}</option>`).join("")}</select><p class="muted tiny" style="margin-top:6px">Choisis le bloc que tu fais en ce moment. Tu pourras le changer dans les réglages.</p>` : ""}
    ${P.bloc ? `<label for="obb">Lundi de la semaine 1 de ce bloc</label><input id="obb" type="date"><p class="muted tiny" style="margin-top:6px">Pour dater tes séances. Tu pourras le changer plus tard.</p>` : ""}
    <p class="muted tiny" style="margin-top:6px">La prog doit être partagée avec le compte Google avec lequel tu es connecté.</p>
    <button class="btn" style="margin-top:28px" data-act="obCreate" id="obgo">Créer mon carnet</button>
    <button class="btn ghost" style="margin-top:10px" data-act="obStep" data-s="carnet">Retour</button>${err}`; }
  $("#v-home").innerHTML = `<div class="ob">${h}</div>`;
  if (step === "create") obRefresh();
}
/* Inscription (maquette A) : disciplines, mode, sexe ; catégories recalculées en direct d'après le poids et la date de naissance */
const obOn = k => { const b = document.querySelector(`[data-act=obDisc][data-k=${k}]`); return !!b && b.getAttribute("aria-pressed") === "true"; };
const obSel = a => (document.querySelector(`[data-act=${a}][aria-pressed=true]`) || {dataset:{}}).dataset.k;
function obRefresh(){
  const st = obOn("street"), pw = obOn("power"), sx = obSel("obSex") || "H", w = num(($("#obw") || {}).value), b = ($("#obn") || {}).value || "";
  const ages = ageCats(b, isoOf(new Date())), youth = ages.some(a => a === "SJ" || a === "JR");
  const pp = $("#obpow"); if (pp) pp.hidden = !pw;
  { const f = !st && !pw; ["obcatsec", "obprsec"].forEach(i => { const e = $("#" + i); if (e) e.hidden = f; }); }   /* musculation seule : ni catégorie ni PR */
  document.querySelectorAll("[data-lift]").forEach(e => { const l = e.dataset.lift; e.hidden = !((st && LIFTS.includes(l)) || (pw && POWER_LIFTS.includes(l))); });
  const row = (t, s, val) => `<div class="catrow"><span class="grow"><b>${t}</b><span>${s}</span></span><span class="val"${/kg/.test(val) ? "" : ' style="font-size:22px"'}>${val}</span></div>`;
  const kgv = c => c === null ? "—" : catTxt(c).replace(" kg", "<small>kg</small>");
  const el = $("#obcats"); if (el) el.innerHTML = (st ? row("Street lifting", "Official Streetlifting", w ? kgv(catAuto(w, catsFor(sx))) : "—") : "")
    + (pw ? row("Powerlifting", "IPF", w ? kgv(catAuto(w, catsIpfFor(sx, youth))) : "—") : "")
    + row("Âge", ages.length > 1 ? ages.map(a => AGE_NAME[a]).join(" et ") : ages.length ? "Catégorie d'âge IPF" : b ? "Moins de 14 ans : pas de catégorie IPF" : "Ajoute ta date de naissance", ages.length ? AGE_NAME[ages[0]] : "—");
}
document.addEventListener("input", ev => { if (ev.target && ev.target.dataset && ev.target.dataset.inp === "ob") obRefresh(); });
Object.assign(ACT, {
  obLogin:() => auth.login("select_account"),
  obStep:d => onboard(d.s),
  obDisc:(d, el) => { const b = el.closest("[data-act]"), on = b.getAttribute("aria-pressed") === "true", others = ["street", "power", "muscu"].filter(k => k !== d.k);
    if (on && !others.some(obOn)) return toast("Choisis au moins une discipline", true); b.setAttribute("aria-pressed", String(!on)); obRefresh(); },
  obMode:(d, el) => { document.querySelectorAll("[data-act=obMode]").forEach(x => x.setAttribute("aria-pressed", String(x.dataset.k === d.k))); },
  obSex:(d, el) => { document.querySelectorAll("[data-act=obSex]").forEach(x => x.setAttribute("aria-pressed", String(x.dataset.k === d.k))); obRefresh(); },
  obLink:async () => { const id = idOf($("#oblink").value); if (!id) return onboard("carnet", "Ce lien ne ressemble pas à un lien de Google Sheet.");
    try { const t = await getTitles(id);
      if (!t.includes("PROFIL") && (t.some(x => /^\s*BLOC\s*\d+/i.test(x)) || (await progTabs(id)).order.length)) return onboard("carnet", "Ce lien est celui d'une prog de coach, pas d'un carnet. Colle-le plus haut, dans « Nouveau ici, avec une prog de coach ».");
      await ensureTabs(id); } catch(e){ return onboard("carnet", errMsg(e)); }
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
      obPre = pre; onboard("create", blocs.length ? "" : "Aucun onglet de séances trouvé dans cette prog : remplis ton profil à la main.");
    } catch(e){ b.disabled = false; b.textContent = "Tout remplir depuis ma prog"; toast("Prog inaccessible : " + errMsg(e), true); }
  },
  obCreate:async () => {
    const st = obOn("street"), pw = obOn("power"), mu = obOn("muscu"), sx = obSel("obSex") || "H", w = num($("#obw").value), nai = $("#obn").value || "";
    const p = {prenom:$("#obp").value.trim(), sexe:sx, naissance:nai, disciplines:[st ? "street" : "", pw ? "power" : "", mu ? "muscu" : ""].filter(Boolean).join(","), power_mode:obSel("obMode") || "classic",
      categorie:w && (st || pw) ? catAuto(w, catsFor(sx)) : "", debut:$("#obd").value, poids:$("#obw").value, coach:idOf($("#obk").value),
      taille:obPre && obPre.taille, pays:($("#obpa") || {}).value || "BE", bloc:$("#obbl") ? Number($("#obbl").value) : obPre && obPre.bloc, blocDate:$("#obb") ? $("#obb").value : ""};
    ALL_LIFTS.forEach(l => { const e = $("#obpr" + l); p["pr_" + l] = e && !e.closest("[hidden]") ? e.value : ""; });
    if (!p.prenom) return toast("Indique ton prénom", true);
    if ($("#obk").value.trim() && !p.coach) return toast("Le lien de la prog n'est pas reconnu", true);
    const b = $("#obgo"); b.disabled = true; b.textContent = "Création…";
    try {
      if (p.coach) { try { await getTitles(p.coach); } catch(e){ b.disabled = false; b.textContent = "Créer mon carnet"; return toast("Prog du coach inaccessible : " + errMsg(e), true); } }
      const id = await createBook(p); setCfg({appId:id}); APP_ID = id; toast("Carnet créé"); startApp();
    } catch(e){ b.disabled = false; b.textContent = "Créer mon carnet"; toast(errMsg(e), true); }
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
async function fetchEmail(){
  if (cfg().email) return;
  try { const r = await fetch("https://www.googleapis.com/oauth2/v3/userinfo", {headers:{Authorization:"Bearer " + auth.tok}}); const j = await r.json(); if (j.email) setCfg({email:j.email}); } catch(e){}
}
