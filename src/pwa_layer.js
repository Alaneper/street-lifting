/* =====================================================================
   ACCÈS AUX DONNÉES : API Google Sheets, connexion Google, aucun serveur
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
  err:null,
  get tok(){ const t = store.get("sl-tok"); return t && t.exp > Date.now() + 60000 ? t.t : null; },
  login(prompt){
    const st = Math.random().toString(36).slice(2); store.set("sl-state", st);
    const p = new URLSearchParams({client_id:CLIENT_ID, redirect_uri:location.origin + location.pathname, response_type:"token", scope:SCOPE, include_granted_scopes:"true", state:st});
    if (cfg().email) p.set("login_hint", cfg().email);
    if (prompt) p.set("prompt", prompt);
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
    try { r = await fetch(url, Object.assign({}, opt, {headers:{Authorization:"Bearer " + tok, "Content-Type":"application/json"}})); }
    catch(e){ throw {code:"offline"}; }
    if (r.status === 401) { store.del("sl-tok"); return reauth(); }
    if ((r.status === 429 || r.status >= 500) && isRead && i < 2) { await sleep(1500 * (i + 1) + Math.random() * 500); continue; }
    const j = await r.json().catch(() => ({}));
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
  PROFIL:["Clé","Valeur","Note"], PR:["Date","Mouvement","Charge (kg)","Reps","Note"], POIDS:["Date","Poids (kg)","Note"],
  OBJECTIFS:["Mouvement","Objectif (kg)","Note"], RECORDS:["Type","Catégorie","Mouvement","Record (kg)","Détenteur","Source","Vérifié le"],
  COMPETITIONS:["Date","Nom","Lieu","Note","Statut"], SERIES:["Date","Bloc","Semaine","Séance","Exercice","Charge (kg)","Reps par série","Source","Note"],
  BLOCS:["Bloc","Lundi de la semaine 1","Note"], TENTATIVES:["Date compét","Mouvement","Tentative 1","Tentative 2","Tentative 3","Résultat 1","Résultat 2","Résultat 3","Note"],
  CHECKLIST:["Date compét","Élément","Fait"], BILAN:["Date","Bloc","Semaine","Sommeil","Plaisir","Motivation","Fatigue","Hydratation","Alimentation"]
};
/* Records vérifiés le 19/10/2026 sur rankings.officialstreetlifting.com (catégorie -80 kg hommes). Les autres catégories s'ajoutent dans l'onglet RECORDS. */
const OSL = "https://rankings.officialstreetlifting.com/records/male/classes/-80kg";
const RECORDS_DEFAULT = [["WR","-80","TOTAL","538.5","Aubin Chevillard (FRA)",OSL,"2026-10-19"],["WR","-80","MU","47.5","Aubin Chevillard (FRA)",OSL,"2026-10-19"],
  ["WR","-80","PULL","120","Dmitrii Vlasov (RUS)",OSL,"2026-10-19"],["WR","-80","DIP","175","Benjamin Detre (FRA)",OSL,"2026-10-19"],["WR","-80","SQUAT","271.5","Michael Incoronato (ITA)",OSL,"2026-10-19"],
  ["NR BE","-80","MU","40","François Conreur (BEL)",OSL,"2026-10-19"],["NR BE","-80","PULL","100.25","François Conreur (BEL)",OSL,"2026-10-19"],
  ["NR BE","-80","DIP","150","François Conreur (BEL)",OSL,"2026-10-19"],["NR BE","-80","SQUAT","220","Albert Israelyan (BEL)",OSL,"2026-10-19"]];
async function writeMany(id, data){ return gapi(API + id + "/values:batchUpdate", {method:"POST", body:JSON.stringify({valueInputOption:"RAW", data})}); }
async function ensureTabs(id){
  const have = new Set(await getTitles(id)), miss = Object.keys(TABS).filter(t => !have.has(t));
  if (!miss.length) return;
  await gapi(API + id + ":batchUpdate", {method:"POST", body:JSON.stringify({requests:miss.map(t => ({addSheet:{properties:{title:t}}}))})});
  await writeMany(id, miss.map(t => ({range:t + "!A1", values:[TABS[t]]})));
}
async function createBook(p){
  const r = await gapi(API, {method:"POST", body:JSON.stringify({properties:{title:"Street Lifting – " + (p.prenom || "carnet"), locale:"fr_BE"},
    sheets:Object.keys(TABS).map(t => ({properties:{title:t, gridProperties:{frozenRowCount:1}}}))})});
  const id = r.spreadsheetId;
  const prof = [["prenom",p.prenom],["sexe",p.sexe],["naissance",""],["taille_cm",""],["categorie",p.categorie],["coach_sheet_id",p.coach || ""],["mu_acquis",p.mu || "NON"],
    ["date_objectif",addMonths(isoOf(new Date()), 12)],["debut_street",p.debut || ""],["debut_coaching",p.debutCoach || ""]];
  const data = Object.keys(TABS).map(t => ({range:t + "!A1", values:[TABS[t]]}));
  data.push({range:"PROFIL!A2", values:prof});
  data.push({range:"RECORDS!A2", values:RECORDS_DEFAULT});
  const prs = LIFTS.filter(l => num(p["pr_" + l])).map(l => [isoOf(new Date()), l, num(p["pr_" + l]), 1, "Saisi à l'inscription"]);
  if (prs.length) data.push({range:"PR!A2", values:prs});
  if (num(p.poids)) data.push({range:"POIDS!A2", values:[[isoOf(new Date()), num(p.poids), ""]]});
  await writeMany(id, data);
  return id;
}

/* ---------- Accueil, connexion et choix du carnet ---------- */
let obStep = "login", obErr = "";
function onboard(step, why){
  obStep = step; obErr = why || ""; document.body.classList.add("ob");
  document.querySelectorAll(".view").forEach(v => v.hidden = v.id !== "v-home");
  $("#topdate").innerHTML = `Street Lifting<small>${step === "login" ? "Bienvenue" : "Ton carnet"}</small>`;
  const plates = `<svg viewBox="0 0 390 150" width="100%" aria-hidden="true" class="obbar"><rect x="20" y="71" width="350" height="8" rx="4" fill="var(--steel)"/>
    ${[["squat",60,130],["pull",86,112],["dip",108,96],["mu",126,80]].map(([c, x, h], i) => `<rect class="plate" style="animation-delay:${i * 90}ms" x="${x}" y="${75 - h / 2}" width="${i === 0 ? 24 : 18}" height="${h}" rx="4" fill="var(--${c})"/><rect class="plate" style="animation-delay:${i * 90}ms" x="${390 - x - (i === 0 ? 24 : 18)}" y="${75 - h / 2}" width="${i === 0 ? 24 : 18}" height="${h}" rx="4" fill="var(--${c})"/>`).join("")}
    <rect x="150" y="64" width="10" height="22" rx="3" fill="var(--steel-hi)"/><rect x="230" y="64" width="10" height="22" rx="3" fill="var(--steel-hi)"/></svg>`;
  const err = obErr ? `<p class="small" style="color:var(--bad);margin-top:12px">${esc(obErr)}</p>` : "";
  let h = "";
  if (step === "config") h = `<div class="empty"><p>L'identifiant Google de l'app n'est pas encore configuré.</p></div>`;
  else if (step === "login") h = `${plates}<p class="show t-l" style="margin-top:6px">Tes 4 mouvements.<br>Ta prog. Tes records.</p>
    <p class="muted" style="margin-top:12px">Connecte ton compte Google. Tes données restent dans ton propre Google Sheet : personne d'autre n'y a accès.</p>
    <button class="btn" style="margin-top:22px" data-act="obLogin">Continuer avec Google</button>${err}
    <p class="muted tiny" style="margin-top:14px">Google peut afficher « application non validée » : c'est normal pour une app en test. Touche « Continuer ».</p>`;
  else if (step === "carnet") h = `<p class="show t-m" style="margin-top:18px">Ton carnet de données</p>
    <p class="muted small" style="margin-top:6px">L'app range tes PR, pesées et séances dans un Google Sheet à toi.</p>
    <div class="panel" style="margin-top:16px"><p style="font-weight:600">Nouveau ici</p><p class="muted small" style="margin-top:4px">L'app crée ton carnet dans ton Google Drive.</p>
      <button class="btn" style="margin-top:12px" data-act="obStep" data-s="create">Créer mon carnet</button></div>
    <div class="panel"><p style="font-weight:600">J'ai déjà un carnet</p><label for="oblink">Lien du Google Sheet</label><input id="oblink" type="url" placeholder="https://docs.google.com/spreadsheets/d/…">
      <button class="btn ghost" style="margin-top:12px" data-act="obLink">Utiliser ce carnet</button></div>${err}`;
  else if (step === "create") h = `<p class="show t-m" style="margin-top:18px">Ton profil</p>
    <label for="obp">Prénom</label><input id="obp" autocomplete="given-name">
    <div class="grid2"><div><label for="obs">Sexe (pour le RIS)</label><select id="obs"><option value="H">Homme</option><option value="F">Femme</option></select></div>
      <div><label for="obc">Catégorie</label><select id="obc">${CATS.map(c => `<option value="${c}" ${c === -80 ? "selected" : ""}>${c > 0 ? "+" + c : c} kg</option>`).join("")}</select></div></div>
    <div class="grid2"><div><label for="obd">Début du street lifting</label><input id="obd" type="date"></div><div><label for="obw">Poids de corps (kg)</label><input id="obw" inputmode="decimal" placeholder="73,2"></div></div>
    <label>Tes PR actuels (kg de lest, laisse vide si tu ne sais pas)</label>
    <div class="grid2">${LIFTS.map(l => `<div><label for="obpr${l}" style="margin-top:0">${LNAME[l]}</label><input id="obpr${l}" inputmode="decimal"></div>`).join("")}</div>
    <label for="obk">Lien de la prog de ton coach (facultatif)</label><input id="obk" type="url" placeholder="https://docs.google.com/spreadsheets/d/…">
    <p class="muted tiny" style="margin-top:6px">La prog doit être partagée avec le compte Google avec lequel tu es connecté.</p>
    <button class="btn" style="margin-top:20px" data-act="obCreate" id="obgo">Créer mon carnet</button>
    <button class="btn ghost" style="margin-top:10px" data-act="obStep" data-s="carnet">Retour</button>${err}`;
  $("#v-home").innerHTML = `<div class="ob">${h}</div>`;
}
Object.assign(ACT, {
  obLogin:() => auth.login("select_account"),
  obStep:d => onboard(d.s),
  obLink:async () => { const id = idOf($("#oblink").value); if (!id) return onboard("carnet", "Ce lien ne ressemble pas à un lien de Google Sheet.");
    try { await ensureTabs(id); } catch(e){ return onboard("carnet", errMsg(e)); }
    setCfg({appId:id}); APP_ID = id; startApp(); },
  obCreate:async () => {
    const p = {prenom:$("#obp").value.trim(), sexe:$("#obs").value, categorie:Number($("#obc").value), debut:$("#obd").value, poids:$("#obw").value, coach:idOf($("#obk").value)};
    LIFTS.forEach(l => p["pr_" + l] = $("#obpr" + l).value);
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
  S = []; loadedBlocs.clear(); allLoaded = false; weekMeta = {}; blocNames = {}; syncAll(false);
};
async function fetchEmail(){
  if (cfg().email) return;
  try { const r = await fetch("https://www.googleapis.com/oauth2/v3/userinfo", {headers:{Authorization:"Bearer " + auth.tok}}); const j = await r.json(); if (j.email) setCfg({email:j.email}); } catch(e){}
}
