/* Street Lifting : ouverture instantanée et hors ligne.
   - L'app (index.html, icônes, table des aliments) s'affiche depuis le téléphone, sans attendre le réseau.
     En arrière-plan, la version en ligne est relue ; si son numéro de build est plus récent, elle remplace
     l'ancienne et l'app est prévenue (installée tout de suite si rien n'a été touché, sinon bandeau).
   - Chart.js, JSZip et les polices : cache d'abord.
   - Les données Google et Open Food Facts ne passent jamais par ce cache. */
const V = "sl-v26";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png", "aliments.json", "zxing.min.js"];
/* cache:"reload" : ignore le cache HTTP du navigateur (GitHub Pages garde les fichiers 10 min). */
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(SHELL.map(u => new Request(u, {cache:"reload"}))))); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
const isDoc = (req, u) => req.mode === "navigate" || /\/(index\.html)?$/.test(u.pathname);
const buildOf = html => +((html.match(/<meta name="sl-build" content="(\d+)">/) || [])[1] || 0);
async function tell(msg){ (await self.clients.matchAll({type:"window"})).forEach(c => c.postMessage(msg)); }
/* Relit la version en ligne (« no-cache » : réponse 304 si rien n'a changé). Pour l'app, on ne garde
   la version en ligne que si elle est plus récente : jamais de retour en arrière si un serveur en sert une ancienne. */
async function refresh(req, key, old){
  const res = await fetch(req, {cache:"no-cache"});
  if (!res || !res.ok) return res;
  const c = await caches.open(V);
  if (old && key === "index.html") {
    const [a, b] = await Promise.all([old.text(), res.clone().text()]);
    if (buildOf(b) > buildOf(a)) { await c.put("index.html", res.clone()); await c.put("./", res.clone()); await tell({type:"sl-update"}); }
    return res;
  }
  await c.put(key, res.clone());
  return res;
}
self.addEventListener("fetch", e => {
  const req = e.request, u = new URL(req.url);
  if (req.method !== "GET") return;
  if (/(^|\.)(googleapis\.com|google\.com)$/.test(u.hostname) && u.hostname !== "fonts.googleapis.com") return;
  if (/openfoodfacts\.org$/.test(u.hostname)) return; /* recherches de marques : toujours en direct */
  if (u.origin === location.origin) {
    const doc = isDoc(req, u), key = doc ? "index.html" : req;
    e.respondWith(caches.match(key, {ignoreSearch:true}).then(hit => {
      /* copie de la réponse en cache : l'originale part vers la page, la copie sert à comparer les versions */
      const net = refresh(doc ? new Request(new URL("index.html", self.registration.scope)) : req, key, hit ? hit.clone() : null);
      if (hit) { e.waitUntil(net.catch(() => {})); return hit; }
      return net.catch(() => caches.match("index.html"));
    }));
  } else {
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {
      if (res && (res.ok || res.type === "opaque")) { const c = res.clone(); caches.open(V).then(x => x.put(req, c)); }
      return res;
    })));
  }
});
