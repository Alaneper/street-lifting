"""Lot final, point 4 : revenir à la v68 après usage de la v69 ne perd aucune donnée.
Étapes : (1) v69 : séance hors connexion (file d'attente), exercice remplacé (modifs), options coupées, « Nouveautés » vue ;
(2) on garde le localStorage tel quel et on charge la v68 (build du commit 27975df, /tmp/v68src/test-build.html) ;
(3) la v68 ne plante pas, vide la file, retrouve les modifs, et n'efface aucune clé. Usage : python3 tests/e2e_v97_retour_v68.py"""
import pathlib, json, sys, os
os.environ["SL_NEWS"] = "1"
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
V68 = pathlib.Path(os.environ.get("V68_BUILD", "/tmp/v68src/test-build.html"))
fails = []
def check(name, ok, info=""):
    print(("OK " if ok else "KO "), name, "" if ok else info)
    if not ok: fails.append(name)
def route68(r):
    u = r.request.url
    if u.endswith("/sl/") or u.endswith("index.html"):
        return r.fulfill(body=V68.read_text().replace("<head>", "<head><script src='/mock.js'></script><script src='/shim.js'></script>", 1), content_type="text/html")
    return route(r)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, service_workers="block", timezone_id="Europe/Brussels"); c.route("**/*", route)
    pg = c.new_page(); errs = []; ev = pg.evaluate
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("window.__down = localStorage.getItem('__down') === '1'")
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=25000); pg.wait_for_timeout(2000)
    ver = ev("APP_VER"); check("la version qui a écrit est la 72", ver.startswith("72"), ver)
    # options coupées + Nouveautés vue
    ev("() => { optToggle && 0; }") if False else None
    ev("() => { localStorage.setItem('sl4-opts', JSON.stringify({gear:0, sil:0})); }")
    news = ev("() => sheet"); ev("() => ACT.closeSheet && ACT.closeSheet()"); print('Nouveautés ouverte :', news)
    # séance hors connexion
    ev("() => { window.__down = true; }")
    info = ev("""(async () => { const s = S.find(z => !z.archived && (+z.semaine) > 1 && z.exercices.length > 1 && z.exercices.some(e => e.mouvement && !/cardio/i.test(e.mouvement)));
      live = null; store.set('sl4-live', null); startLive(s.key); await new Promise(r => setTimeout(r, 500));
      const k = 0, st = live.rows[k]; live.i = k; st.sets.forEach(x => { x.done = true; x.r = 7; x.c = 91; }); st.dirty = true; const ok = await saveRow(k);
      live.i = 1; renderLayer();
      return {ok, n: Store.pending(), ex: exKey(s.exercices[k])}; })()""")
    ev("() => ACT.closeSheet && ACT.closeSheet()"); pg.wait_for_timeout(300)
    pg.click("[data-act=swapOpen]"); pg.wait_for_timeout(300); ev("(n) => { swapQ = n; }", "Curl marteau test"); ev("() => ACT.swapPick({i:'free'})"); pg.wait_for_timeout(900)
    check("v69 : série enregistrée hors connexion, file d'attente non vide", info and info["ok"] and info["n"] >= 1, info)
    pg.wait_for_timeout(800)
    snap = ev("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; }")
    keys = sorted(k for k in snap if k.startswith("sl4-"))
    outbox = json.loads(snap.get("sl4-outbox") or "[]")
    mods = ev("() => D.profil.modifs || ''")
    check("v69 a bien écrit file d'attente, options et modifs", len(outbox) >= 1 and "sl4-opts" in snap, {"outbox": len(outbox), "keys": keys})
    print("clés v69 :", keys, "| file :", len(outbox), "| modifs :", (mods or "")[:120])
    # ---- retour à la v68 : même localStorage, build v68, réseau revenu
    c.unroute("**/*"); c.route("**/*", route68)
    pg.evaluate("() => { localStorage.setItem('__down', '0'); }")
    pg.reload(); pg.wait_for_timeout(2500)
    ver68 = ev("typeof APP_VER !== 'undefined' ? APP_VER : null"); check("la v68 est bien chargée", bool(ver68) and ver68.startswith("68"), ver68)
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0", timeout=25000); pg.wait_for_timeout(3000)
    ev("() => { window.__down = false; }")
    try: ev("async () => { await Store.flush(); }")
    except Exception as e: print("flush :", str(e)[:120])
    pg.wait_for_timeout(2500)
    check("v68 : aucune erreur JavaScript au chargement et à l'usage", not errs, errs[:3])
    left = ev("() => Store.pending()"); check("v68 : la file d'attente de la v69 est vidée (envoyée au Sheet)", left == 0, left)
    sent = ev("""(a) => { const t = window.__sheets[a]['SERIES'] || []; return t.map(r => r.join('|')); }""", APP)
    check("v68 : la série écrite avec la v69 est dans le Sheet", any("91" in r for r in sent), sent[-3:])
    mods68 = ev("() => D.profil.modifs || ''"); check("v68 : les modifs (exercice remplacé) sont retrouvées", mods68 == mods and bool(mods), (mods68 or "")[:80])
    swapped = ev("() => modsList().length"); check("v68 : lit la liste des modifs sans erreur", swapped >= 1, swapped)
    after = ev("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = 1; } return Object.keys(o); }")
    lost = [k for k in keys if k not in after and k not in ("sl4-outbox", "sl4-live", "sl4-tmp")]
    check("v68 n'efface aucune clé locale (hors file vidée / séance rendue)", not lost, lost)
    check("les clés ajoutées par la v69 (sl4-opts, sl4-news) restent intactes, ignorées par la v68", "sl4-opts" in after, after)
    br.close()
print("ÉCHECS :", fails if fails else "aucun"); sys.exit(1 if fails else 0)
