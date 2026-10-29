/**
 * Service « catalogue d'aliments » de Street Lifting.
 * À coller dans Extensions > Apps Script du Google Sheet qui contient le catalogue
 * (onglet « catalogue », colonnes de catalogue-monde-29-10.csv), puis Déployer > Application Web
 * (exécuter en tant que : moi ; accès : tout le monde). L'adresse /exec se copie dans CAT_URL (src/app.html).
 *
 * Appels (GET) :
 *   ?a=code&ean=3017620422003           -> {ok:true, p:{code,nom,marque,k,p,g,l,por}} ou {ok:true, p:null}
 *   ?a=q&q=nutella&l=fr&n=15           -> {ok:true, r:[{...}]}
 *   ?a=flush                           -> vide la mémoire (à faire après toute modification du Sheet)
 *   ?a=submit&dev=…&ean=…&nom=…&marque=…&k=…&p=…&g=…&l=…   -> propose un produit absent
 * Les utilisateurs n'ont jamais accès au Sheet : seul ce script le lit.
 *
 * Produits proposés par les utilisateurs : onglet « proposes » (créé tout seul), colonnes
 *   cle | code | nom | marque | k | p | g | l | appareils | n | statut | date
 * Un produit devient « partage » (visible par tous) quand 2 APPAREILS DIFFÉRENTS envoient des valeurs proches (±10 %).
 * Avant cela, il reste privé : seul celui qui l'a créé le voit, dans son propre Sheet.
 */
var TAB = 'catalogue';
var COL = {code:0, autres:1, marque:2, nom:3, noms:4, pays:5, cats:6, kcal:7, prot:8, gluc:9, sucres:10, lip:11, sat:12, fib:13, sel:14, portion:15};
var PTAB = 'proposes', MAXDAY = 30;
var CHUNK = 90000;   // limite d'une valeur du cache : 100 Ko

function norm_(s) {
  return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
}

/** Index compact en cache (6 h) : une ligne par produit, champs séparés par \u0001. */
function index_() {
  var cache = CacheService.getScriptCache(), n = Number(cache.get('idx_n') || 0), out = [];
  if (n) {
    var keys = []; for (var i = 0; i < n; i++) keys.push('idx_' + i);
    var got = cache.getAll(keys), ok = true, txt = '';
    for (var j = 0; j < n; j++) { if (got['idx_' + j] === undefined) { ok = false; break; } txt += got['idx_' + j]; }
    if (ok) return JSON.parse(txt);
  }
  var sh = SpreadsheetApp.getActive().getSheetByName(TAB), v = sh.getDataRange().getValues();
  for (var r = 1; r < v.length; r++) {
    var x = v[r], noms = {}; try { noms = JSON.parse(x[COL.noms] || '{}'); } catch (e) {}
    var all = [x[COL.nom], x[COL.marque]]; for (var l in noms) all.push(noms[l]);
    out.push({c:String(x[COL.code]), o:String(x[COL.autres] || ''), m:String(x[COL.marque] || ''), n:String(x[COL.nom]), nn:noms,
      h:norm_(all.join(' ')), k:Number(x[COL.kcal]), p:Number(x[COL.prot]), g:Number(x[COL.gluc]), l:Number(x[COL.lip]), s:Number(x[COL.portion]) || 0});
  }
  var s = JSON.stringify(out), parts = Math.ceil(s.length / CHUNK), put = {};
  for (var k = 0; k < parts; k++) put['idx_' + k] = s.substr(k * CHUNK, CHUNK);
  try { cache.putAll(put, 21600); cache.put('idx_n', String(parts), 21600); } catch (e) {}
  return out;
}

function food_(x, lang) {
  var nom = (x.nn && x.nn[lang]) || x.n;
  var f = {code:x.c, nom:nom, marque:x.m, k:x.k, p:x.p, g:x.g, l:x.l};
  if (x.s >= 5 && x.s <= 1000) f.por = Math.round(x.s);
  if (x.comm) f.comm = 1;
  return f;
}


/* ---------- produits proposés ---------- */
function pSheet_() {
  var ss = SpreadsheetApp.getActive(), sh = ss.getSheetByName(PTAB);
  if (!sh) { sh = ss.insertSheet(PTAB); sh.appendRow(['cle','code','nom','marque','k','p','g','l','appareils','n','statut','date']); sh.getRange('A:C').setNumberFormat('@'); }
  return sh;
}
function zeros_(c) { return String(c || '').replace(/\D/g, '').replace(/^0+/, ''); }
function pKey_(ean, nom, marque) { var z = zeros_(ean); return z ? 'c' + z : 'n' + norm_(nom) + '|' + norm_(marque); }
function close_(a, b, abs, rel) { return Math.abs(a - b) <= Math.max(abs, rel * Math.max(a, b)); }
function sameVals_(r, k, p, g, l) { return close_(Number(r[4]), k, 10, .1) && close_(Number(r[5]), p, 1, .1) && close_(Number(r[6]), g, 1, .1) && close_(Number(r[7]), l, 1, .1); }
function shared_() {   // produits partagés (cache 5 min), même forme que index_()
  var cache = CacheService.getScriptCache(), hit = cache.get('prop_idx');
  if (hit) return JSON.parse(hit);
  var v = pSheet_().getDataRange().getValues(), out = [];
  for (var i = 1; i < v.length; i++) { var x = v[i]; if (x[10] !== 'partage') continue;
    out.push({c:String(x[1]), o:'', m:String(x[3]), n:String(x[2]), nn:{}, h:norm_(x[2] + ' ' + x[3]), k:Number(x[4]), p:Number(x[5]), g:Number(x[6]), l:Number(x[7]), s:0, comm:1}); }
  try { cache.put('prop_idx', JSON.stringify(out), 300); } catch (e) {}
  return out;
}
function submit_(e) {
  var q = e.parameter, dev = String(q.dev || ''), nom = String(q.nom || '').trim(), marque = String(q.marque || '').trim();
  var k = Number(q.k), p = Number(q.p || 0), g = Number(q.g || 0), l = Number(q.l || 0), ean = zeros_(q.ean);
  if (!/^[A-Za-z0-9]{8,40}$/.test(dev)) return {ok:false, e:'appareil'};
  if (nom.length < 2 || nom.length > 80 || marque.length > 60) return {ok:false, e:'nom'};
  if (![k, p, g, l].every(isFinite) || k < 0 || k > 950 || p < 0 || g < 0 || l < 0 || p + g + l > 100.5) return {ok:false, e:'valeurs'};
  var est = 4 * p + 4 * g + 9 * l;
  if ((est > 0 && Math.abs(k - est) > Math.max(40, est * .3)) || (k >= 40 && est < 5)) return {ok:false, e:'incoherent'};
  if (ean && (ean.length < 6 || ean.length > 14)) return {ok:false, e:'code'};
  var lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    var props = PropertiesService.getScriptProperties(), day = Utilities.formatDate(new Date(), 'Europe/Brussels', 'yyyyMMdd'), rk = 'r_' + dev + '_' + day, used = Number(props.getProperty(rk) || 0);
    if (used >= MAXDAY) return {ok:false, e:'limite'};
    // déjà dans le catalogue (ou déjà partagé) : on ne crée rien, on renvoie l'existant
    var all = index_().concat(shared_()), key = pKey_(ean, nom, marque);
    for (var i = 0; i < all.length; i++) { var a = all[i];
      if (ean ? (zeros_(a.c) === ean || (a.o && a.o.split(';').some(function (z) { return zeros_(z) === ean; }))) : (pKey_('', a.n, a.m) === key))
        return {ok:true, st:'existe', p:food_(a, 'fr')}; }
    var sh = pSheet_(), v = sh.getDataRange().getValues(), now = new Date(), hit = -1;
    for (var r = 1; r < v.length; r++) if (v[r][0] === key && sameVals_(v[r], k, p, g, l)) { hit = r; break; }
    props.setProperty(rk, String(used + 1));
    if (hit < 0) { sh.appendRow([key, ean || '', nom, marque, k, p, g, l, dev, 1, 'prive', now]); return {ok:true, st:'prive'}; }
    var devs = String(v[hit][8]).split(';');
    if (devs.indexOf(dev) >= 0) return {ok:true, st:'deja'};
    devs.push(dev);
    var st = devs.length >= 2 ? 'partage' : 'prive';
    sh.getRange(hit + 1, 9, 1, 4).setValues([[devs.join(';'), devs.length, st, now]]);
    if (st === 'partage') CacheService.getScriptCache().remove('prop_idx');
    return {ok:true, st:st};
  } finally { lock.releaseLock(); }
}

function reply_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

function doGet(e) {
  try {
    var a = (e.parameter.a || '');
    if (a === 'flush') { CacheService.getScriptCache().removeAll(['idx_n', 'prop_idx']); return reply_({ok:true, flushed:true}); }   // à appeler après toute modification du Sheet
    if (a === 'submit') return reply_(submit_(e));
    var lang = (e.parameter.l || 'fr').slice(0, 5), idx = index_().concat(shared_());
    if (a === 'code') {
      var c = String(e.parameter.ean || '').replace(/\D/g, '').replace(/^0+/, '');
      if (!c) return reply_({ok:false});
      for (var i = 0; i < idx.length; i++) {
        var x = idx[i];
        if (x.c.replace(/^0+/, '') === c || (x.o && x.o.split(';').some(function (z) { return z.replace(/^0+/, '') === c; })))
          return reply_({ok:true, p:food_(x, lang)});
      }
      return reply_({ok:true, p:null});
    }
    if (a === 'q') {
      var q = norm_(e.parameter.q), max = Math.min(Number(e.parameter.n) || 15, 30);
      var toks = q.split(' ').filter(function (t) { return t.length >= 2; });
      if (!toks.length) return reply_({ok:true, r:[]});
      var hits = [];
      for (var j = 0; j < idx.length; j++) {
        var y = idx[j], sc = 0, good = true;
        for (var t = 0; t < toks.length; t++) { var pos = y.h.indexOf(toks[t]); if (pos < 0) { good = false; break; } sc += (pos === 0 ? 3 : 1); }
        if (!good) continue;
        if (norm_(y.n) === q) sc += 10; else if (norm_(y.n).indexOf(q) === 0) sc += 5;
        hits.push([sc, j]);
      }
      hits.sort(function (u, v) { return v[0] - u[0] || u[1] - v[1]; });   // à score égal : le plus populaire d'abord (le CSV est trié par popularité)
      return reply_({ok:true, r:hits.slice(0, max).map(function (h) { return food_(idx[h[1]], lang); })});
    }
    return reply_({ok:false});
  } catch (err) { return reply_({ok:false, e:String(err)}); }
}
