"""Construit index.html (la web app) à partir de src/app.html et src/pwa_layer.js.
Usage : python3 tools/build.py [CLIENT_ID]   (sans argument : l'ID de production)"""
import sys, pathlib, re, json
ROOT = pathlib.Path(__file__).resolve().parent.parent
HERE = ROOT / "src"
SRC = (HERE / "app.html").read_text()
OUT = ROOT
PROD_ID = "592660864473-s7ek1c4i0iknvrnpsmdpi77l7bpr2k8c.apps.googleusercontent.com"
CLIENT_ID = sys.argv[1] if len(sys.argv) > 1 else PROD_ID
DEST = sys.argv[2] if len(sys.argv) > 2 else "index.html"
s = SRC

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, f"{n} occurrences (attendu {count}) : {old[:70]!r}"
    s = s.replace(old, new)

def cut(start, end, new):
    """Remplace du marqueur start (inclus) jusqu'au marqueur end (exclu)."""
    global s
    i = s.index(start); j = s.index(end, i)
    s = s[:i] + new + s[j:]

# 1. En-tête de page complet
head = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0A0B0D">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Street Lifting">
<meta name="description" content="Suivi de street lifting : PR, total, RIS, prog du coach, poids de corps et compétitions.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png"><link rel="icon" type="image/png" href="icon-192.png">
"""
rep('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
s = head + s
rep("</style>\n\n<main", """/* Web app */
body{padding-top:calc(env(safe-area-inset-top,0px) + 8px)}
body.ob .tabs,body.ob .avatar,body.ob .topbar{display:none}
.ob{max-width:520px;margin:0 auto;padding-bottom:40px}
.obbar{margin-top:12px}
.obbar .plate{transform-box:fill-box;transform-origin:center;animation:obin .6s cubic-bezier(.2,.9,.2,1) both}
@keyframes obin{from{transform:scaleY(.2);opacity:0}}
</style>
</head><body>

<main""")
rep('<p class="muted small" style="margin-top:14px">La première fois, Claude te demande d\'autoriser l\'accès à Google Sheets. Touche « Autoriser ».</p>', "")

# 2. Couche de données : l'ancienne (connecteur Claude) est retirée, la nouvelle est injectée avant la synchro
cut("/* =====================================================================\n   ACCÈS AUX DONNÉES", "/* =====================================================================\n   DONNÉES PERSO", "")
rep('const SHEETS = "Google Sheets";\nconst APP_ID = "10OP7QRneqxxU1ad4BbVaYulLQUBDmaj7Hcu3n3IQBtA";', "let APP_ID = \"\";")
rep("let mcp = null, D = null", "let D = null")
rep("Promise.all(R.map(r => getVals(APP_ID, r)))", "getMany(APP_ID, R)")
rep("const coachId = () => D.profil.coach_sheet_id;", "const coachId = () => idOf(D.profil.coach_sheet_id);")
rep('"sl4-cache"', 'ck("sl4-cache")', 2)
n = s.count('"sl4-live"'); s = s.replace('"sl4-live"', 'ck("sl4-live")'); assert n >= 4, n
rep('window.claude?.use("downloads").catch(() => null)', "Promise.resolve(dlr)", 2)
layer = (HERE / "pwa_layer.js").read_text().replace("__CLIENT_ID__", CLIENT_ID)

# 3. Messages d'erreur propres à la web app
rep("function errMsg(e){\n  const c = e && e.code;\n", """function errMsg(e){
  const c = e && e.code;
  if (c === "offline") return "Pas de connexion internet. Ce que tu saisis en séance reste sur le téléphone.";
  if (c === "forbidden") return "Ce compte Google n'a pas accès à ce Sheet. Vérifie qu'il est partagé avec " + (cfg().email || "ton adresse Google") + ".";
  if (c === "not_found") return "Google Sheet introuvable. Vérifie le lien.";
  if (c === "quota") return "Trop de requêtes vers Google en une minute. Réessaie dans un instant.";
""")

# 4. Réglages : compte et carnet
rep('<h2 class="h2" style="font-size:20px">Méthodes et sources</h2>', """<h2 class="h2" style="font-size:20px">Compte et carnet</h2>
    <p class="muted small">${cfg().email ? "Connecté avec " + esc(cfg().email) : "Connecté à Google"}.</p>
    <label for="scoach">Lien de la prog du coach</label><input id="scoach" type="url" value="${coachId() ? sheetUrl(coachId()) : ""}" placeholder="https://docs.google.com/spreadsheets/d/…" data-chg="coachLink">
    <div class="grid2" style="margin-top:12px"><a class="btn ghost sm" href="${sheetUrl(APP_ID)}" target="_blank" rel="noopener">Ouvrir mon carnet</a><button class="btn ghost sm" data-act="relogin">Se reconnecter</button></div>
    <div class="grid2" style="margin-top:8px"><button class="btn ghost sm" data-act="switchBook">Changer de carnet</button><button class="btn ghost sm" data-act="logout">Se déconnecter</button></div>
    <h2 class="h2" style="font-size:20px">Méthodes et sources</h2>""")

# 5. Démarrage
cut("/* =====================================================================\n   SYNCHRO ET DÉMARRAGE", "async function syncAll", layer + """
/* =====================================================================
   SYNCHRO ET DÉMARRAGE
   ===================================================================== */
""")
rep("if (syncing || !mcp) return;", "if (syncing || !APP_ID) return;")
rep('function fatal(msg){ $("#v-home").innerHTML = `<div class="empty"><p>${esc(msg)}</p><button class="btn ghost sm" data-act="boot">Réessayer</button></div>`; }',
    'function fatal(msg){ $("#v-home").innerHTML = `<div class="empty"><p>${esc(msg)}</p><button class="btn ghost sm" data-act="boot">Réessayer</button><button class="btn ghost sm" data-act="switchBook">Changer de carnet</button></div>`; }')
cut("async function boot(){", "</script>", """ACT.relogin = () => { if (live) persistLive(); auth.login(); };
async function startApp(){
  document.body.classList.remove("ob");
  document.querySelectorAll(".view").forEach(v => v.hidden = v.id !== "v-" + tab);
  $("#v-home").innerHTML = `<div class="skel" style="height:190px;margin-top:18px"></div><div class="skel" style="height:150px;margin-top:14px"></div>`;
  const cached = loadCache(); if (cached) render();
  if (!auth.tok) {
    setDot("off");
    if (navigator.onLine && !auth.err) return auth.login();
    if (auth.err) toast("Connexion Google refusée. Réglages, Se reconnecter.", true);
    if (!cached) fatal(auth.err ? "Connexion Google refusée ou annulée." : "Pas de connexion internet. Reviens quand tu as du réseau.");
    return;
  }
  fetchEmail();
  await syncAll(true);
  if (store.get("sl-resume")) { store.del("sl-resume"); const lv = store.get(ck("sl4-live")); if (lv && seanceByKey(lv.key)) startLive(lv.key); }
}
async function boot(){
  auth.fromHash();
  if (!/\\.apps\\.googleusercontent\\.com$/.test(CLIENT_ID)) return onboard("config");
  APP_ID = cfg().appId || "";
  if (APP_ID) return startApp();
  if (!auth.tok) return onboard("login", auth.err ? "Connexion annulée (" + auth.err + "). Réessaie." : "");
  fetchEmail(); onboard("carnet");
}
boot();
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
""")
s = s.rstrip() + "\n</body></html>\n"
assert "mcp" not in s.replace("mcp_", ""), [m.start() for m in re.finditer("mcp", s)]
assert "window.claude" not in s
(OUT / DEST).write_text(s)
print(DEST, len(s), "octets")
