// Teste la logique de tools/catalogue.gs (produits proposés) avec de faux services Google.
const fs=require('fs'),vm=require('vm');
const rows=[['cle','code','nom','marque','k','p','g','l','appareils','n','statut','date']];
const cat=[['code','autres','marque','nom','noms','pays','cats','kcal','prot','gluc','sucres','lip','sat','fib','sel','portion'],['3017620422003','','Ferrero','Nutella','{}','','',539,6.3,57.5,56.3,30.9,10.6,0,0.1,15]];
const cache={}, props={};
const sheet=(a)=>({getDataRange:()=>({getValues:()=>a}),appendRow:r=>a.push(r),getRange:(r,c,n,m)=>({setValues:v=>{for(let j=0;j<m;j++)a[r-1][c-1+j]=v[0][j]},setNumberFormat:()=>{}}),});
const sheets={catalogue:sheet(cat),proposes:sheet(rows)};
const ctx={console,JSON,Number,String,Math,Date,isFinite,
 SpreadsheetApp:{getActive:()=>({getSheetByName:n=>sheets[n],insertSheet:n=>sheets[n]})},
 CacheService:{getScriptCache:()=>({get:k=>cache[k],put:(k,v)=>{cache[k]=v},putAll:o=>Object.assign(cache,o),getAll:ks=>Object.fromEntries(ks.filter(k=>k in cache).map(k=>[k,cache[k]])),remove:k=>{delete cache[k]},removeAll:ks=>ks.forEach(k=>delete cache[k])})},
 LockService:{getScriptLock:()=>({waitLock(){},releaseLock(){}})},
 PropertiesService:{getScriptProperties:()=>({getProperty:k=>props[k]||null,setProperty:(k,v)=>{props[k]=v}})},
 Utilities:{formatDate:()=> '20261029'},
 ContentService:{createTextOutput:t=>({t,setMimeType(){return this}}),MimeType:{JSON:1}}};
vm.createContext(ctx); vm.runInContext(fs.readFileSync('tools/catalogue.gs','utf8'),ctx);
const call=q=>JSON.parse(ctx.doGet({parameter:q}).t);
let bad=0; const ok=(c,m)=>{console.log((c?'OK  ':'KO  ')+m); if(!c)bad++};
const A='aaaaaaaa1',B='bbbbbbbb2',base={a:'submit',nom:'Skyr vanille',marque:'Danone',k:63,p:11,g:4,l:0.2,ean:'5412345678900'};
ok(call({...base,dev:A}).st==='prive','1er appareil : privé');
ok(call({...base,dev:A}).st==='deja','même appareil 2 fois : ne compte pas');
ok(call({a:'code',ean:'5412345678900'}).p===null,'privé : introuvable pour les autres');
ok(call({...base,dev:B,k:90,g:9.5}).st==='prive','valeurs très différentes : nouvelle proposition, pas de confirmation');
ok(call({...base,dev:B,k:65}).st==='partage','2e appareil, valeurs proches : partagé');
const f=call({a:'code',ean:'5412345678900'}); ok(f.p&&f.p.comm===1&&f.p.nom==='Skyr vanille','partagé : trouvé par code, marqué communauté');
ok(call({a:'q',q:'skyr vanille'}).r.length===1,'partagé : trouvé par nom');
ok(call({...base,dev:'cccccccc3'}).st==='existe','déjà partagé : renvoie l\'existant');
ok(call({a:'submit',dev:A,nom:'Nutella',marque:'Ferrero',k:539,p:6,g:57,l:31,ean:'03017620422003'}).st==='existe','déjà au catalogue (zéros ignorés)');
ok(call({a:'submit',dev:A,nom:'Truc',k:900,p:1,g:1,l:1}).e==='incoherent','incohérent refusé');
ok(call({a:'submit',dev:'x',nom:'Truc',k:50,p:5,g:5,l:1}).e==='appareil','appareil invalide refusé');
const s2={a:'submit',dev:A,nom:'Pain maison',marque:'',k:250,p:8,g:48,l:2};
ok(call(s2).st==='prive'&&call({...s2,dev:B}).st==='partage','sans code-barres : clé nom+marque');
for(let i=0;i<31;i++) call({...s2,dev:'dddddddd4',nom:'Prod '+i});
ok(call({...s2,dev:'dddddddd4',nom:'Encore'}).e==='limite','limite quotidienne');
console.log(bad?'ÉCHECS '+bad:'TOUT VERT'); process.exit(bad?1:0);
