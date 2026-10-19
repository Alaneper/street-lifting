"""Prog dont les onglets ne s'appellent pas « BLOC n » (cas du frère : « Peaking BSLC »…)."""
import pathlib
H = pathlib.Path(__file__).resolve().parent
src = (H / "e2e.py").read_text(); exec(src[:src.index("with sync_playwright()")])
RENAME = """<script>(()=>{const s=window.__sheets['%s'],o={};
 const same = g => { g.forEach(r => r.forEach((x,i) => { if (/^Semaine/.test(x)) r[i+1] = "1"; })); return g; };
 for(const[k,v]of Object.entries(s)){
  if(k==='BLOC 5'){o['BLOC 5']=v;o['B6 ACC 4semaines ']=same(JSON.parse(JSON.stringify(s['BLOC 6'])));}
  else if(k==='BLOC 6')o['B7 Intensif 3 semaines ']=same(v);
  else if(k==='BLOC 7'){o['Peaking BSLC ']=same(v);o['BIBLIOTHÈQUE MOBILITÉ ']=[['Exercice','Lien']];o['FEUILLE DE MATCH ']=[['MOUVEMENT','Tentative 1']];}
  else if(k==='BLOC 2'){o['BLOC 1 POST COMP ']=JSON.parse(JSON.stringify(v));o['BLOC 2']=v;}
  else o[k]=v;}
 window.__sheets['%s']=o;})()</script>""" % (COACH, COACH)
def route2(r):
    if r.request.url.rstrip("/").endswith("/sl") or r.request.url.endswith("/sl/") or r.request.url.endswith("index.html"):
        html = (P / "test-build.html").read_text().replace("<head>", "<head><script src='/mock.js'></script>" + RENAME + "<script src='/shim.js'></script>", 1)
        return r.fulfill(body=html, content_type="text/html")
    return route(r)
with sync_playwright() as p:
    br = p.chromium.launch(); c = br.new_context(viewport={"width":390,"height":844}, service_workers="block"); c.route("**/*", route2)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto("http://app.local/sl/"); pg.wait_for_timeout(1000); pg.click("[data-act=obLogin]"); pg.wait_for_timeout(1500)
    pg.fill("#oblink", f"https://docs.google.com/spreadsheets/d/{APP}/edit"); pg.click("[data-act=obLink]"); pg.wait_for_timeout(4000)
    print("titre semaine :", pg.locator("h2.h2").first.inner_text().replace("\n", " "))
    print("ordre :", pg.evaluate("progOrder.map(n=>blocLabel(n))"))
    print("actif :", pg.evaluate("blocLabel(activeBloc())"))
    pg.click("[data-act=settings]"); pg.wait_for_timeout(500)
    print("options :", pg.locator("#sbl option").all_inner_texts())
    print("semaines peaking :", pg.evaluate("[...new Set(S.filter(x=>x.bloc===activeBloc()).map(x=>x.semaine))]"), "| prochaine :", pg.evaluate("(nextSeance()||{}).key"))
    pg.select_option("#sbl", label="Bloc 5"); pg.wait_for_timeout(2500)
    print("après choix :", pg.evaluate("blocLabel(activeBloc())"), "| profil :", pg.evaluate("D.profil.bloc_actif"))
    pg.screenshot(path=str(OUT / "named-settings.png"))
    # glisser pour fermer
    pg.evaluate("ACT.closeSheet && ACT.closeSheet()"); pg.click("[data-act=settings]"); pg.wait_for_timeout(400)
    pg.evaluate("""(()=>{const el=document.querySelector('.sheet'),T=(y)=>[new Touch({identifier:1,target:el,clientY:y,clientX:100})];
      el.dispatchEvent(new TouchEvent('touchstart',{bubbles:true,touches:T(100)}));el.dispatchEvent(new TouchEvent('touchmove',{bubbles:true,touches:T(300)}));
      el.dispatchEvent(new TouchEvent('touchend',{bubbles:true,touches:[]}));})()""")
    pg.wait_for_timeout(500); print("feuille encore ouverte après glissé :", pg.locator(".sheet").count())
    print("ERRORS:", errs[:10])
