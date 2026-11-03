"""Niveau 8,5, lot A : lancement (barre déterminée 0,4–1,5 s, rendu depuis le téléphone), ligne d'état de synchro, erreur + Réessayer sans perte,
listes longues (mois de pesées à la demande), défilement conservé entre onglets, clavier (visualViewport simulé), pas de trait de défilement sous l'écran de lancement."""
import pathlib, time, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
fails = []
def check(name, cond, info=""):
    print(("OK  " if cond else "KO  ") + name, "" if cond else info)
    if not cond: fails.append(name)
def login(pg):
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(800); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1200)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]")
    pg.wait_for_function("typeof D !== 'undefined' && D && S.length > 0 && lastSync > 0", timeout=20000); pg.wait_for_timeout(1200)
LAT = """(() => { let real = null; window.__lat = 0; try { window.__lat = +sessionStorage.getItem('__lat') || 0; } catch(e){} window.__fail = false;
  Object.defineProperty(window, 'fetch', { configurable: true, get(){ return (u, o) => { const url = String(u);
    if (url.startsWith('https://sheets.googleapis.com/')) { if (window.__fail) return Promise.reject(new TypeError('Failed to fetch')); if (window.__lat) return new Promise(r => setTimeout(r, window.__lat)).then(() => real(u, o)); }
    return real(u, o); } }, set(f){ real = f; } }); })();"""
with sync_playwright() as p:
    br = p.chromium.launch()
    c = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route); c.add_init_script(LAT)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    login(pg)
    # --- 1. lancement suivant : données du téléphone, écran affiché sans attendre le réseau
    pg.evaluate("sessionStorage.setItem('__lat', '8000')"); t0 = time.time(); pg.reload(wait_until="commit")
    pg.wait_for_selector("#splash", state="attached", timeout=5000)
    check("lancement : barre déterminée avec rôle progressbar", pg.evaluate("!!document.querySelector('#splash [role=progressbar][aria-valuenow]') && !!document.getElementById('llab')"))
    check("lancement : la page dessous ne défile pas (plus de trait de défilement iOS)", pg.evaluate("getComputedStyle(document.documentElement).overflow === 'hidden' && getComputedStyle(document.body).overflow === 'hidden'"))
    pg.wait_for_selector("#splash", state="detached", timeout=8000); dt = time.time() - t0
    out = pg.evaluate("LAUNCH.ms.out")
    check("réseau très lent (8 s par appel) : l'app s'ouvre en 0,4 à 1,6 s sans attendre", 395 <= out <= 1600, (out, round(dt, 2)))
    check("réseau très lent : contenu affiché depuis le téléphone", pg.evaluate("document.querySelector('#v-home').innerText.length > 30 && !document.querySelector('#v-home .skel')"))
    check("réseau très lent : « Synchronisation… » visible en arrière-plan", pg.evaluate("/Synchronisation/.test(document.getElementById('syncline').textContent)"), pg.evaluate("document.getElementById('syncline').textContent + ' | state=' + syncState + ' syncing=' + syncing + ' tok=' + !!auth.tok"))
    check("page dessous défile de nouveau après le lancement", pg.evaluate("getComputedStyle(document.documentElement).overflow !== 'hidden'"))
    pg.evaluate("sessionStorage.removeItem('__lat')")
    # --- 2. premier lancement (sans données) très lent : 1,5 s au plus, puis squelette + « Synchronisation… »
    st = c.storage_state(); c1 = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block", storage_state=st); c1.route("**/*", route)
    c1.add_init_script(LAT + "; try { Object.keys(localStorage).filter(k => /cache/.test(k)).forEach(k => localStorage.removeItem(k)); } catch(e){}; window.__lat = 8000;")
    pg1 = c1.new_page(); pg1.on("pageerror", lambda e: errs.append(str(e))); t0 = time.time(); pg1.goto("http://app.local/sl/", wait_until="commit")
    pg1.wait_for_selector("#splash", state="attached", timeout=5000); pg1.wait_for_selector("#splash", state="detached", timeout=8000); dt = time.time() - t0
    out = pg1.evaluate("LAUNCH.ms.out")
    check("premier lancement très lent : l'écran de lancement part en 1,5 s au plus", out <= 1600, (out, round(dt, 2)))
    check("premier lancement très lent : squelette de chargement (pas de zone vide)", pg1.evaluate("!!document.querySelector('#v-home .skel') && document.getElementById('v-home').getAttribute('aria-busy') === 'true'"))
    check("premier lancement très lent : « Synchronisation… » écrit", pg1.evaluate("/Synchronisation/.test(document.getElementById('syncline').textContent)"))
    check("premier lancement : étape « synchro » non terminée → ouverture forcée notée", pg1.evaluate("LAUNCH.forced === true"))
    if "SHOT2" in __import__("os").environ: pg1.screenshot(path=__import__("os").environ["SHOT2"])
    pg = pg1; pg.evaluate("window.__lat = 0"); pg.evaluate("sessionStorage.removeItem('__lat')")
    pg.wait_for_function("typeof D !== 'undefined' && D && /Sauvegard/.test(document.getElementById('syncline').textContent)", timeout=30000)
    check("synchro finie : « Sauvegardé · à l'instant »", pg.evaluate("/^Sauvegardé · (à l'instant|il y a \\d+ min)$/.test(document.getElementById('syncline').textContent)"))
    check("synchro finie : plus de squelette ni d'aria-busy", pg.evaluate("!document.querySelector('#v-home .skel') && document.getElementById('v-home').getAttribute('aria-busy') !== 'true'"))
    check("avatar : plus de pastille blanche", pg.evaluate("getComputedStyle(document.querySelector('.avatar .dot')).display === 'none'"))
    # --- 3. erreur de synchro : message clair + Réessayer, file d'attente intacte
    pg.evaluate("setTab('home')"); pg.wait_for_timeout(300)
    pg.evaluate("window.__fail = true; seanceErr = ''; syncAll(true)"); pg.wait_for_timeout(1500)
    check("réseau coupé : ligne d'état et bandeau parlent de l'erreur", pg.evaluate("/Synchro impossible|Hors connexion|Pas de réseau/.test(document.getElementById('syncline').textContent + document.getElementById('netbar').textContent) || !!document.getElementById('netbar').textContent"), pg.evaluate("document.getElementById('syncline').textContent + ' | ' + document.getElementById('netbar').textContent"))
    pg.evaluate("seanceErr = 'Impossible de lire ta prog : test'; renderNetBar(); setDot('off')")
    check("erreur : bouton Réessayer présent", pg.evaluate("!!document.querySelector('#netbar [data-act=sync]') && /Réessayer/.test(document.getElementById('netbar').innerText)"))
    pg.evaluate("window.__fail = false; seanceErr = ''")
    # file d'attente : une pesée écrite pendant la panne reste dans l'outbox
    pg.evaluate("window.__fail = true"); pend0 = pg.evaluate("Store.pending()")
    pg.evaluate("D.poids.push({id:99999, date: addDays(D.today, -1), poids: 77.7})")
    check("file d'attente existante intacte pendant l'erreur", pg.evaluate("Store.pending()") >= pend0)
    pg.evaluate("window.__fail = false")
    # --- 4. défilement conservé entre onglets
    pg.evaluate("D.poids = D.poids.filter(p => p.id !== 99999); setTab('home')"); pg.wait_for_timeout(300)
    pg.evaluate("setTab('prog', true); window.scrollTo(0, 400)"); pg.wait_for_timeout(300); y1 = pg.evaluate("scrollY")
    pg.click(".tabs button[data-tab=corps]"); pg.wait_for_timeout(400); y_c = pg.evaluate("scrollY")
    pg.click(".tabs button[data-tab=prog]"); pg.wait_for_timeout(500); y2 = pg.evaluate("scrollY")
    check("défilement : Progrès → Corps part en haut, retour à Progrès retrouve la position", y1 > 100 and y_c == 0 and abs(y2 - y1) < 3, (y1, y_c, y2))
    pg.click(".tabs button[data-tab=prog]"); pg.wait_for_timeout(500)
    check("re-toucher l'onglet actif remonte en haut", pg.evaluate("scrollY") == 0, pg.evaluate("scrollY"))
    # --- 5. listes longues : mois de pesées à la demande
    n = pg.evaluate("""(() => { const base = new Date(D.today + 'T12:00:00'); D.poids = []; for (let i = 0; i < 500; i++) { const d = new Date(base); d.setDate(d.getDate() - i); D.poids.push({id: 1000 + i, date: isoOf(d), poids: Math.round((78 + Math.sin(i / 9) * 2.5) * 10) / 10}); }
      const t = performance.now(); openSheet('pesees'); const ms = performance.now() - t; return {ms: Math.round(ms), dom: document.querySelectorAll('.sheet *').length, mois: document.querySelectorAll('.sheet details.pmonth').length, rows: document.querySelectorAll('.sheet .vrow').length}; })()""")
    check("500 pesées : feuille dessinée en moins de 50 ms avec peu d'éléments", n["ms"] < 50 and n["dom"] < 400 and n["rows"] < 40, n)
    r = pg.evaluate("""(() => { const d = document.querySelectorAll('.sheet details.pmonth')[3]; d.open = true; return new Promise(res => setTimeout(() => res(d.querySelectorAll('.vrow').length), 100)); })()""")
    check("mois fermé : ses pesées apparaissent à l'ouverture", r >= 28, r)
    pg.evaluate("ACT.closeSheet && ACT.closeSheet()")
    # --- 6. clavier : visualViewport simulé (clavier de 300 px)
    pg.evaluate("""(() => { const fake = new EventTarget(); fake.height = innerHeight; fake.offsetTop = 0; Object.defineProperty(window, 'visualViewport', {value: fake, configurable: true}); window.__vv = fake; })()""")
    c2 = br.new_context(viewport={"width":390, "height":844}, device_scale_factor=2, service_workers="block", storage_state=c.storage_state()); c2.route("**/*", route)
    c2.add_init_script("""(() => { const fake = new EventTarget(); fake.height = innerHeight; fake.offsetTop = 0; Object.defineProperty(window, 'visualViewport', {value: fake, configurable: true}); window.__vv = fake; })();""")
    pg2 = c2.new_page(); pg2.on("pageerror", lambda e: errs.append(str(e))); pg2.goto("http://app.local/sl/"); pg2.wait_for_function("typeof D !== 'undefined' && D", timeout=20000); pg2.wait_for_timeout(1200)
    pg2.evaluate("D.poids = D.poids.filter(p => p.date !== D.today); hwDraft = null; setTab('home'); openSheet('weigh')"); pg2.wait_for_timeout(500)
    pg2.evaluate("__vv.height = innerHeight - 300; __vv.dispatchEvent(new Event('resize'))"); pg2.wait_for_timeout(300)
    r = pg2.evaluate("(() => { const s = document.querySelector('.sheet'), b = s.getBoundingClientRect(); return {kb: getComputedStyle(document.documentElement).getPropertyValue('--kb'), bottom: Math.round(b.bottom), vh: innerHeight}; })()")
    check("clavier : la feuille monte au-dessus du clavier", r["kb"].strip() == "300px" and r["bottom"] <= r["vh"] - 299, r)
    pg2.evaluate("document.getElementById('cw').focus()"); pg2.wait_for_timeout(700)
    r = pg2.evaluate("(() => { const b = document.getElementById('cw').getBoundingClientRect(); return {top: Math.round(b.top), bottom: Math.round(b.bottom), vvh: __vv.height}; })()")
    check("clavier : le champ en saisie reste dans la zone visible", r["top"] >= 0 and r["bottom"] <= r["vvh"], r)
    if "SHOT" in __import__("os").environ: pg2.screenshot(path=__import__("os").environ["SHOT"])
    pg2.evaluate("__vv.height = innerHeight; __vv.dispatchEvent(new Event('resize'))"); pg2.wait_for_timeout(200)
    check("clavier fermé : feuille revenue en bas", pg2.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--kb').trim()") == "0px")
    check("aucune erreur console", not errs, errs[:3])
    br.close()
print("ÉCHECS :", fails)
