/* Street Lifting · service du classement (Google Apps Script, gratuit).
   À installer une seule fois par Alane : voir docs/classement.md.
   Chaque app envoie ses records avec son jeton de connexion Google ; le service vérifie auprès de Google
   qui l'envoie (et que le jeton vient bien de l'app Street Lifting), range la ligne de cette personne,
   puis renvoie le classement de tout le monde, sans les adresses e-mail. */
const CLIENT_ID = "592660864473-s7ek1c4i0iknvrnpsmdpi77l7bpr2k8c.apps.googleusercontent.com";
const SHEET_ID = "1LnIqPu1p7j9Cr0CHUYSBBnstqhcxjQTeNNApjJW36EA";   /* fichier « Street Lifting – Classement » */
const HEAD = ["Email", "Prénom", "Pays", "Sexe", "Catégorie", "Muscle-up", "Tractions", "Dips", "Squat", "Total", "RIS", "Mis à jour"];

function feuille_(){
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let s = ss.getSheetByName("CLASSEMENT");
  if (!s) { s = ss.insertSheet("CLASSEMENT"); s.appendRow(HEAD); s.setFrozenRows(1); }
  return s;
}
function json_(o){ return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function nb_(x, max){ const v = typeof x === "number" ? x : parseFloat(String(x == null ? "" : x).replace(",", ".")); return isFinite(v) && v >= -200 && v <= max ? Math.round(v * 100) / 100 : ""; }
function lignes_(s, email){
  const v = s.getDataRange().getValues().slice(1).filter(r => r[0]);
  return v.map(r => ({nom:String(r[1] || "").slice(0, 30), pays:String(r[2] || ""), sexe:String(r[3] || ""), cat:r[4], MU:r[5] === "" ? null : r[5], PULL:r[6] === "" ? null : r[6],
    DIP:r[7] === "" ? null : r[7], SQUAT:r[8] === "" ? null : r[8], total:r[9] || 0, ris:r[10] === "" ? null : r[10],
    maj:r[11] instanceof Date ? Utilities.formatDate(r[11], "Europe/Brussels", "yyyy-MM-dd") : String(r[11] || ""), me:!!email && String(r[0]).toLowerCase() === email}));
}
function doGet(){ return json_({rows:lignes_(feuille_(), null)}); }
function doPost(e){
  let b; try { b = JSON.parse(e.postData.contents); } catch(err){ return json_({error:"format"}); }
  if (!b || !b.token) return json_({error:"auth"});
  const res = UrlFetchApp.fetch("https://oauth2.googleapis.com/tokeninfo?access_token=" + encodeURIComponent(b.token), {muteHttpExceptions:true});
  let t = {}; try { t = JSON.parse(res.getContentText()); } catch(err){}
  if (res.getResponseCode() !== 200 || !t.email || (t.aud !== CLIENT_ID && t.azp !== CLIENT_ID)) return json_({error:"auth"});
  const email = String(t.email).toLowerCase(), d = b.data || {};
  const ligne = [email, String(d.prenom || "").slice(0, 30), String(d.pays || "").toUpperCase().slice(0, 2), d.sexe === "F" ? "F" : "M", nb_(d.cat, 200),
    nb_(d.MU, 300), nb_(d.PULL, 300), nb_(d.DIP, 300), nb_(d.SQUAT, 600), nb_(d.total, 1500) || 0, nb_(d.ris, 2000),
    Utilities.formatDate(new Date(), "Europe/Brussels", "yyyy-MM-dd")];
  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    const s = feuille_(), mails = s.getRange(1, 1, Math.max(s.getLastRow(), 1), 1).getValues().map(r => String(r[0]).toLowerCase());
    const i = mails.indexOf(email);
    if (i > 0) s.getRange(i + 1, 1, 1, ligne.length).setValues([ligne]); else s.appendRow(ligne);
    return json_({rows:lignes_(s, email)});
  } finally { lock.releaseLock(); }
}
