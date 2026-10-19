/* Street Lifting : fonctionne hors ligne (interface et graphiques). Les données Google ne sont jamais mises en cache ici. */
const V = "sl-v6";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(SHELL))); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const req = e.request, u = new URL(req.url);
  if (req.method !== "GET") return;
  if (/(^|\.)(googleapis\.com|google\.com)$/.test(u.hostname) && u.hostname !== "fonts.googleapis.com") return;
  const put = res => { if (res && (res.ok || res.type === "opaque")) { const c = res.clone(); caches.open(V).then(x => x.put(req, c)); } return res; };
  if (u.origin === location.origin) {
    /* Réseau d'abord : les mises à jour de l'app arrivent dès qu'il y a du réseau. */
    e.respondWith(fetch(req).then(put).catch(() => caches.match(req, {ignoreSearch:true}).then(r => r || caches.match("index.html"))));
  } else {
    /* Chart.js et polices : cache d'abord. */
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(put)));
  }
});
