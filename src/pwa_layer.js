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
  const prof = [["prenom",p.prenom],["sexe",p.sexe],["naissance",""],["taille_cm",p.taille || ""],["categorie",p.categorie],["coach_sheet_id",p.coach || ""],["mu_acquis",p.mu || "NON"],
    ["date_objectif",addMonths(isoOf(new Date()), 12)],["debut_street",p.debut || ""],["debut_coaching",p.debutCoach || ""]];
  const data = Object.keys(TABS).map(t => ({range:t + "!A1", values:[TABS[t]]}));
  data.push({range:"PROFIL!A2", values:prof});
  data.push({range:"RECORDS!A2", values:RECORDS_DEFAULT});
  const prs = LIFTS.filter(l => num(p["pr_" + l])).map(l => [isoOf(new Date()), l, num(p["pr_" + l]), 1, p.coach && obPre ? "Max de la prog du coach" : "Saisi à l'inscription"]);
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
  const MAP = {MU:"MU", "MUSCLE UP":"MU", PU:"PULL", "PULL UP":"PULL", TRACTIONS:"PULL", DIPS:"DIP", DIP:"DIP", SQUAT:"SQUAT"};
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
  const plates = `<div class="hero" style="margin-top:18px;min-height:150px">${DECO}<svg width="64" height="64" viewBox="0 0 40 40" aria-hidden="true" style="position:relative;background:#fff;border-radius:16px;padding:6px"><circle cx="20" cy="10.5" r="4.2" fill="#1F5FD0"/><path d="M7 17h26" stroke="#1F5FD0" stroke-width="3.6" stroke-linecap="round"/><path d="M11 17l4.5 9 4.5-3.5 4.5 3.5 4.5-9" stroke="#1F5FD0" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg><p class="hu" style="margin-top:14px">Ta prog, tes records, ta prochaine compét.</p></div>`;
  const err = obErr ? `<p class="small" style="color:var(--bad);margin-top:12px">${esc(obErr)}</p>` : "";
  let h = "";
  if (step === "config") h = `<div class="empty"><p>L'identifiant Google de l'app n'est pas encore configuré.</p></div>`;
  else if (step === "login") h = `${plates}<p class="show" style="font-size:44px;font-weight:800;margin-top:22px;line-height:1">Street Lifting</p>
    <p class="muted" style="margin-top:12px">Connecte ton compte Google. Tes données restent dans ton propre Google Sheet : personne d'autre n'y a accès.</p>
    <button class="btn" style="margin-top:22px" data-act="obLogin">Continuer avec Google</button>${err}
    <p class="muted tiny" style="margin-top:14px">Google peut afficher « application non validée » : c'est normal pour une app en test. Touche « Continuer ».</p>`;
  else if (step === "carnet") h = `<p class="show t-m" style="margin-top:18px">Ton carnet de données</p>
    <p class="muted small" style="margin-top:6px">L'app range tes PR, pesées et séances dans un Google Sheet à toi.</p>
    <div class="panel" style="margin-top:16px"><p style="font-weight:600">Nouveau ici, avec une prog de coach</p><p class="muted small" style="margin-top:4px">Colle le lien de ta prog : l'app y lit ton prénom, ton poids et tes max, et crée ton carnet.</p>
      <label for="obcoach">Lien de la prog de ton coach</label><input id="obcoach" type="url" placeholder="https://docs.google.com/spreadsheets/d/…">
      <button class="btn" style="margin-top:12px" data-act="obFromCoach" id="obfc">Tout remplir depuis ma prog</button>
      <button class="link small" style="margin-top:12px" data-act="obStep" data-s="create">Je n'ai pas de prog, je remplis moi-même</button></div>
    <div class="panel"><p style="font-weight:600">J'ai déjà un carnet</p><label for="oblink">Lien du Google Sheet</label><input id="oblink" type="url" placeholder="https://docs.google.com/spreadsheets/d/…">
      <button class="btn ghost" style="margin-top:12px" data-act="obLink">Utiliser ce carnet</button></div>${err}`;
  else if (step === "create") { const P = obPre || {}, v = x => x === undefined || x === null ? "" : esc(String(x).replace(".", ","));
    h = `<p class="show t-m" style="margin-top:18px">Ton profil</p>
    ${obPre ? `<p class="muted small" style="margin-top:6px">Rempli depuis ta prog${P.bloc ? " (bloc " + P.bloc + ")" : ""}. Vérifie et corrige si besoin.</p>` : ""}
    <label for="obp">Prénom</label><input id="obp" autocomplete="given-name" value="${v(P.prenom)}">
    <div class="grid2"><div><label for="obs">Sexe (pour le RIS)</label><select id="obs"><option value="H">Homme</option><option value="F">Femme</option></select></div>
      <div><label for="obc">Catégorie</label><select id="obc">${CATS.map(c => `<option value="${c}" ${c === (P.categorie || -80) ? "selected" : ""}>${c > 0 ? "+" + c : c} kg</option>`).join("")}</select></div></div>
    <div class="grid2"><div><label for="obd">Début du street lifting</label><input id="obd" type="date"></div><div><label for="obw">Poids de corps (kg)</label><input id="obw" inputmode="decimal" placeholder="73,2" value="${v(P.poids)}"></div></div>
    <label>Tes PR actuels (kg de lest, laisse vide si tu ne sais pas)</label>
    <div class="grid2">${LIFTS.map(l => `<div><label for="obpr${l}" style="margin-top:0">${LNAME[l]}</label><input id="obpr${l}" inputmode="decimal" value="${v(P["pr_" + l])}"></div>`).join("")}</div>
    <label for="obk">Lien de la prog de ton coach (facultatif)</label><input id="obk" type="url" placeholder="https://docs.google.com/spreadsheets/d/…" value="${P.coach ? sheetUrl(P.coach) : ""}">
    ${P.bloc ? `<label for="obb">Lundi de la semaine 1 du bloc ${P.bloc}</label><input id="obb" type="date"><p class="muted tiny" style="margin-top:6px">Pour dater tes séances. Tu pourras le changer plus tard.</p>` : ""}
    <p class="muted tiny" style="margin-top:6px">La prog doit être partagée avec le compte Google avec lequel tu es connecté.</p>
    <button class="btn" style="margin-top:20px" data-act="obCreate" id="obgo">Créer mon carnet</button>
    <button class="btn ghost" style="margin-top:10px" data-act="obStep" data-s="carnet">Retour</button>${err}`; }
  $("#v-home").innerHTML = `<div class="ob">${h}</div>`;
}
Object.assign(ACT, {
  obLogin:() => auth.login("select_account"),
  obStep:d => onboard(d.s),
  obLink:async () => { const id = idOf($("#oblink").value); if (!id) return onboard("carnet", "Ce lien ne ressemble pas à un lien de Google Sheet.");
    try { await ensureTabs(id); } catch(e){ return onboard("carnet", errMsg(e)); }
    setCfg({appId:id}); APP_ID = id; startApp(); },
  obFromCoach:async () => {
    const id = idOf($("#obcoach").value); if (!id) return toast("Ce lien de Google Sheet n'est pas reconnu", true);
    const b = $("#obfc"); b.disabled = true; b.textContent = "Lecture de ta prog…";
    try {
      const meta = await gapi(API + id + "?fields=" + enc("properties.title,sheets.properties.title"), {}, true);
      const tabs = (meta.sheets || []).map(x => x.properties.title), blocs = tabs.map(t => { const m = t.match(/^\s*BLOC\s*(\d+)/i); return m ? {n:+m[1], t} : null; }).filter(Boolean).sort((a, c) => c.n - a.n);
      const pre = {coach:id, prenom:prenomOf(meta.properties && meta.properties.title)};
      if (blocs.length) { Object.assign(pre, parseCoachProfile(await getVals(id, "'" + blocs[0].t.replace(/'/g, "''") + "'!A1:CZ24")), {bloc:blocs[0].n}); }
      obPre = pre; onboard("create", blocs.length ? "" : "Aucun onglet « BLOC » trouvé : remplis ton profil à la main.");
    } catch(e){ b.disabled = false; b.textContent = "Tout remplir depuis ma prog"; toast("Prog inaccessible : " + errMsg(e), true); }
  },
  obCreate:async () => {
    const p = {prenom:$("#obp").value.trim(), sexe:$("#obs").value, categorie:Number($("#obc").value), debut:$("#obd").value, poids:$("#obw").value, coach:idOf($("#obk").value),
      taille:obPre && obPre.taille, bloc:obPre && obPre.bloc, blocDate:$("#obb") ? $("#obb").value : ""};
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
