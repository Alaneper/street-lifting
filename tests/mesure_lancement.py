"""Mesure du lancement (lot A, niveau 8,5) : temps avant écran de lancement retiré et avant contenu affiché,
pour 4 réseaux (bon Wi-Fi, lent, très lent, mode avion) × 2 lancements (suivant = données sur le téléphone, premier = sans données).
Usage : python3 tests/mesure_lancement.py [dossier_captures] ; écrit tests/mesure_lancement.json
La latence est ajoutée sur les appels à l'API Sheets ; l'« avion » les fait échouer et force navigator.onLine = false."""
import sys, json, pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
SHOTS = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
if SHOTS: SHOTS.mkdir(parents=True, exist_ok=True)
NETS = {"wifi": 0, "lent": 1200, "tres_lent": 6000, "avion": -1}
INIT = """
(() => {
  const lat = window.__LAT, T = window.__T = {};
  let real = null;
  Object.defineProperty(window, 'fetch', { configurable: true, get(){ return (u, o) => {
    const url = String(u);
    if (url.startsWith('https://sheets.googleapis.com/')) {
      if (lat < 0) return Promise.reject(new TypeError('Failed to fetch'));
      if (lat > 0) return new Promise(r => setTimeout(r, lat)).then(() => real(u, o));
    }
    return real(u, o); } }, set(f){ real = f; } });
  if (lat < 0) Object.defineProperty(navigator, 'onLine', { get: () => false });
  const t0 = performance.now(), mark = k => { if (!(k in T)) T[k] = Math.round(performance.now() - t0); };
  new MutationObserver(() => {
    const sp = document.getElementById('splash');
    if (sp && sp.classList.contains('out')) mark('splash_out');
    if (!sp) mark('splash_gone');
    const v = document.getElementById('v-home'), w = document.getElementById('v-seance');
    const has = el => el && !el.hidden && el.innerHTML.trim() && !el.querySelector('.skel') && !el.querySelector('.empty');
    if (has(v) || has(w)) mark('contenu');
    if (document.querySelector('.syncline') && /Sauvegard/.test(document.querySelector('.syncline').textContent)) mark('sauvegarde');
    if (document.querySelector('.skel') && !sp) mark('squelette_visible');
  }).observe(document, {subtree: true, childList: true, characterData: true, attributes: true});
})();
"""
res = {}
with sync_playwright() as p:
    br = p.chromium.launch()
    # 1. connexion + carnet une fois pour créer les données locales
    c0 = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=1, service_workers="block"); c0.route("**/*", route)
    pg = c0.new_page(); pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4500)
    state = c0.storage_state(); c0.close()
    for net, lat in NETS.items():
        for mode in ("suivant", "premier"):
            ctx = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=1, service_workers="block", storage_state=state); ctx.route("**/*", route)
            ctx.add_init_script(f"window.__LAT={lat};" + INIT)
            if mode == "premier":
                ctx.add_init_script("""(() => { try { Object.keys(localStorage).filter(k => /cache/.test(k)).forEach(k => localStorage.removeItem(k)); } catch(e){} })();""")
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto("http://app.local/sl/", wait_until="commit")
            shots = []
            for i, t in enumerate((120, 380, 700, 1100)):
                pg.wait_for_timeout(t if i == 0 else t - (120, 380, 700, 1100)[i-1])
                if SHOTS and net in ("wifi", "tres_lent", "avion") and pg.evaluate("!!document.getElementById('splash')"):
                    f = SHOTS / f"lancement-{net}-{mode}-{t}.png"; pg.screenshot(path=str(f)); shots.append(f.name)
            pg.wait_for_timeout(max(2500, 600 if lat <= 0 else lat + 2500) )
            T = pg.evaluate("window.__T"); L = pg.evaluate("typeof LAUNCH!=='undefined'?LAUNCH.ms:null"); F = pg.evaluate("typeof LAUNCH!=='undefined'?LAUNCH.forced:null")
            line = pg.evaluate("(document.getElementById('syncline')||{}).textContent")
            if SHOTS and net in ("tres_lent", "avion", "wifi"): pg.screenshot(path=str(SHOTS / f"apres-{net}-{mode}.png"))
            res[f"{net}/{mode}"] = {"T": T, "etapes_ms": L, "ouverture_forcee": F, "ligne_etat": line, "erreurs": errs[:3], "captures": shots}
            print(net, mode, T, L, F, repr(line), errs[:2])
            ctx.close()
    br.close()
(H / "mesure_lancement.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
