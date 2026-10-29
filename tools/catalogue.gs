/**
 * Service « catalogue d'aliments » de Street Lifting (lecture seule, v53).
 * À coller dans Extensions > Apps Script du Google Sheet qui contient le catalogue
 * (onglet « catalogue », colonnes de catalogue-monde-29-10.csv), puis Déployer > Application Web
 * (exécuter en tant que : moi ; accès : tout le monde). L'adresse /exec se copie dans CAT_URL (src/app.html).
 *
 * Appels (GET) :
 *   ?a=code&c=3017620422003            -> {ok:true, p:{code,nom,marque,k,p,g,l,por}} ou {ok:true, p:null}
 *   ?a=q&q=nutella&l=fr&n=15           -> {ok:true, r:[{...}]}
 * Les utilisateurs n'ont jamais accès au Sheet : seul ce script le lit.
 */
var TAB = 'catalogue';
var COL = {code:0, autres:1, marque:2, nom:3, noms:4, pays:5, cats:6, kcal:7, prot:8, gluc:9, sucres:10, lip:11, sat:12, fib:13, sel:14, portion:15};
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
  return f;
}

function reply_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

function doGet(e) {
  try {
    var a = (e.parameter.a || ''), lang = (e.parameter.l || 'fr').slice(0, 5), idx = index_();
    if (a === 'code') {
      var c = String(e.parameter.c || '').replace(/\D/g, '').replace(/^0+/, '');
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
