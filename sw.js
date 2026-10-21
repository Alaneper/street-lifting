/* Street Lifting : ouverture instantanée et hors ligne.
   - L'app (index.html, icônes, table des aliments) s'affiche depuis le téléphone, sans attendre le réseau.
     En arrière-plan, la dernière version est téléchargée ; si elle a changé, l'app est prévenue (bandeau
     « Nouvelle version ») et elle est utilisée à l'ouverture suivante.
   - Chart.js, JSZip et les polices : cache d'abord.
   - Les données Google et Open Food Facts ne passent jamais par ce cache. */
const V = "sl-v20";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png", "aliments.json"];
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(SHELL))); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
const isDoc = (req, u) => req.mode === "navigate" || /\/(index\.html)?$/.test(u.pathname);
async function tell(msg){ (await self.clients.matchAll({type:"window"})).forEach(c => c.postMessage(msg)); }
/* Télécharge la version en ligne ; prévient la page si l'app a changé. */
async function refresh(req, key, old){
  const res = await fetch(req, {cache:"no-store"});
  if (!res || !res.ok) return res;
  const c = await caches.open(V);
  if (old && key === "index.html") {
    const [a, b] = await Promise.all([old.clone().text(), res.clone().text()]);
    if (a !== b) { await c.put("index.html", res.clone()); await c.put("./", res.clone()); await tell({type:"sl-update"}); }
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
    const key = isDoc(req, u) ? "index.html" : req;
    e.respondWith(caches.match(key, {ignoreSearch:true}).then(hit => {
      /* copie de la réponse en cache : l'originale part vers la page, la copie sert à comparer les versions */
      const net = refresh(isDoc(req, u) ? new Request(new URL("index.html", self.registration.scope)) : req, key, hit ? hit.clone() : null);
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
