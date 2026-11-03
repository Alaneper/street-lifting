"""Mesure des listes longues (lot A) : 500 pesées et 500 séances. Usage : python3 tests/mesure_listes.py"""
import sys, pathlib, json
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, service_workers="block"); c.route("**/*", route)
    pg = c.new_page(); errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit#gid=0"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4500)
    r = pg.evaluate("""(()=>{
      const out = {}; const base = new Date(D.today+'T12:00:00');
      D.poids = []; for (let i=0;i<500;i++){ const d=new Date(base); d.setDate(d.getDate()-i); D.poids.push({id:1000+i, date:isoOf(d), kg:Math.round((78+Math.sin(i/9)*2.5)*10)/10}); }
      const T=(k,f)=>{ const t=performance.now(); f(); out[k]=Math.round(performance.now()-t); };
      corpsTab='poids'; corpsManual=D.today; T('corps_poids_500', ()=>setTab('corps'));
      T('feuille_pesees_500', ()=>openSheet('pesees'));
      out.dom_pesees = document.querySelectorAll('.sheet *').length;
      ACT.closeSheet&&ACT.closeSheet();
      // historique : 500 séances faites (clones de la première séance faite, une par jour sur 500 jours)
      const z0 = S.find(z=>z.faite && dateOf(z)), jours = ['LUNDI','MARDI','MERCREDI','JEUDI','VENDREDI','SAMEDI','DIMANCHE'];
      let before = S.length; for (let i=0;i<500;i++){ S.push(Object.assign({}, z0, {key:'zz'+i, semaine:1+Math.floor(i/7), jour:jours[i%7], seance:1000+i, faite:true})); }
      histMonth = null; T('histo_500', ()=>setTab('histo'));
      out.seances_ajoutees = S.length - before; out.dom_histo = document.querySelectorAll('#v-histo *').length;
      T('histo_mois_change', ()=>{ histMonth = dateOf(S[S.length-200]).slice(0,7); rHisto(); });
      return out; })()""")
    print(json.dumps(r), errs[:3])
    # fluidité de défilement : longueur de tâche pendant un défilement forcé
    pg.evaluate("setTab('histo')"); pg.wait_for_timeout(500)
    print(pg.evaluate("""new Promise(res=>{ let long=0,last=performance.now(),max=0,frames=0; const t0=performance.now(); function f(){ const n=performance.now(); const dt=n-last; max=Math.max(max,dt); if(dt>34)long++; last=n; frames++; window.scrollBy(0,60); if(n-t0<2000) requestAnimationFrame(f); else res({frames,maxFrameMs:Math.round(max),slowFrames:long,scrollH:document.documentElement.scrollHeight}); } requestAnimationFrame(f); })"""))
    br.close()
