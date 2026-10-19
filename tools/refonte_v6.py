"""Refonte v6 (une seule fois) : concept 2 « Cap sur la compét » appliqué à toute l'app."""
import pathlib, re
P = pathlib.Path(__file__).resolve().parent.parent / "src" / "app.html"
s = P.read_text()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, f"{c} occurrence(s) au lieu de {n} : {a[:90]!r}"
    s = s.replace(a, b)

def cut(start, end, new):
    global s
    i = s.index(start); j = s.index(end, i)
    s = s[:i] + new + s[j:]

# ---------------------------------------------------------------- polices et jetons
rep("""<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@600;800;900&family=Archivo:wght@400;500;600;700&display=swap">""",
    """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Barlow+Condensed:wght@600;700;800&display=swap">""")
s = s.replace("font-family:\"Archivo\"", "font-family:\"Barlow\"")
rep("""  --floor:#0B0C0F; --deck:#15171B; --deck2:#1D2025; --deck3:#24272D; --seam:#24272D;
  --chalk:#F2F0EA; --dust:#9A9EA6; --faint:#6E727A; --steel:#8E9198; --steel-hi:#C9CBCF;""",
"""  --floor:#0A0B0D; --deck:#16181C; --deck2:#1F2227; --deck3:#2A2E34; --seam:#1C1F24;
  --chalk:#FFFFFF; --dust:#8A9099; --faint:#5E646D; --steel:#8E9198; --steel-hi:#B4BAC2; --brand:#1F5FD0;""")
rep("""  --mu:#B98A10; --pull:#3B7DDD; --dip:#1E9E86; --squat:#E0443B;""", """  --mu:#E3B341; --pull:#4C8DF6; --dip:#2BB673; --squat:#F0524A;""")
rep("""  --go:#F2F0EA; --comp:#E0443B; --ok:#5BC48A;""", """  --go:#FFFFFF; --comp:#1F5FD0; --ok:#2BB673;""")
rep("""  --f-show:"Big Shoulders Display","Arial Narrow",Impact,sans-serif;
  --f-text:"Archivo",-apple-system,"Segoe UI",Roboto,sans-serif;""",
"""  --f-show:"Barlow Condensed","Arial Narrow",sans-serif;
  --f-text:"Barlow",-apple-system,"Segoe UI",sans-serif;""")
rep("""  --r-lg:22px; --r:16px; --r-sm:12px;""", """  --r-lg:24px; --r:16px; --r-sm:12px;""")
s = s.replace("'Big Shoulders Display', Impact, sans-serif", "'Barlow Condensed', sans-serif").replace("'Big Shoulders Display'", "'Barlow Condensed'")
s = s.replace("600 40px Archivo", "600 40px Barlow").replace("Archivo, sans-serif", "Barlow, sans-serif").replace('font:{family:"Archivo"', 'font:{family:"Barlow"')
rep(""".btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;min-height:52px;padding:14px 18px;border-radius:var(--r);""",
    """.btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;min-height:54px;padding:14px 18px;border-radius:28px;""")
rep(""".show{font-family:var(--f-show);font-weight:800;letter-spacing:.005em;font-variant-numeric:tabular-nums;line-height:.92}""",
    """.show{font-family:var(--f-show);font-weight:700;letter-spacing:0;font-variant-numeric:tabular-nums;line-height:.92}""")
rep(""".h2{font-family:var(--f-show);font-weight:800;font-size:24px;margin:28px 0 12px;""", """.h2{font-family:var(--f-text);font-weight:700;font-size:18px;margin:26px 0 8px;""")
rep(""".h2 .muted{font:500 13px var(--f-text)}""", """.h2 .muted{font:500 14px var(--f-text)}""")

V6CSS = """
/* ---------- v6 « Cap sur la compét » ---------- */
.topbar{display:flex;align-items:center;justify-content:space-between;height:44px}
.brandmark{display:flex;align-items:center;gap:8px;font:700 17px var(--f-text)}
.hero{position:relative;overflow:hidden;background:var(--hc,var(--brand));border-radius:24px;padding:20px;color:#fff;margin-top:14px}
.hero.plain{--hc:var(--deck2)}
.hero .deco{position:absolute;right:-40px;top:-30px;opacity:.22;pointer-events:none}
.hero .hs{font:600 15px var(--f-text);color:rgba(255,255,255,.84);position:relative}
.hero .hb{font:800 76px/.9 var(--f-show);margin-top:6px;position:relative;letter-spacing:-.005em}
.hero .hb small{font:700 .42em var(--f-show);margin-left:4px}
.hero .hu{font:500 15px var(--f-text);color:rgba(255,255,255,.84);margin-top:8px;position:relative}
.hero .seg3{display:flex;height:8px;border-radius:4px;overflow:hidden;background:rgba(255,255,255,.22);margin-top:16px;position:relative;gap:2px}
.hero .seg3 i{display:block;height:100%}
.hero .hbtns{display:grid;grid-template-columns:52px 1fr 52px;gap:8px;margin-top:16px;position:relative}
.hero .hbtns button,.hero .hbtns input{height:50px;border-radius:14px;border:0}
.hero .hbtns .pm{background:rgba(255,255,255,.12);color:#fff;font:600 24px var(--f-text)}
.hero .hbtns input{background:rgba(255,255,255,.12);color:#fff;text-align:center;font:700 24px var(--f-show)}
.vrow{display:flex;gap:12px;align-items:center;padding:13px 0;border-bottom:1px solid var(--seam);width:100%;text-align:left}
.vrow:last-child{border-bottom:0}
.vrow .grow{flex:1;min-width:0}
.vrow .grow b{display:block;font:600 16px var(--f-text)}
.vrow .grow span{font-size:14px;color:var(--dust)}
.vrow .val{font:700 21px var(--f-show);white-space:nowrap}
.vrow .dots{display:flex;gap:4px}
.vrow .dots i,.d10{width:10px;height:10px;border-radius:50%;background:var(--c);display:inline-block;flex:none}
.day{display:flex;gap:14px;align-items:center;padding:12px 0;border-bottom:1px solid var(--seam);width:100%;text-align:left}
.day .dn{width:38px;text-align:center;flex:none}
.day .dn b{display:block;font:700 21px var(--f-show)}
.day .dn span{font-size:12px;color:var(--dust)}
.day .grow{flex:1;min-width:0;font-size:15px}
.day .grow b{display:block;font:600 16px var(--f-text)}
.day .grow span{font-size:14px;color:var(--dust)}
.day.done{color:var(--faint)}.day.done .dn b,.day.done .dn span{color:var(--faint)}
.day.next{background:var(--deck);border-radius:16px;border-bottom:0;padding:14px 12px;margin:6px -12px;width:calc(100% + 24px)}
.day.today .dn b{color:var(--pull)}
.liftrow{display:block;width:100%;text-align:left;padding:14px 0;border-bottom:1px solid var(--seam)}
.liftrow .top{display:flex;align-items:center;gap:10px}
.liftrow .top b{flex:1;font:700 16px var(--f-text)}
.liftrow .top .val{font:700 22px var(--f-show)}
.liftrow .bar{height:6px;margin:10px 0 6px;background:var(--deck2)}
.liftrow .meta{display:flex;justify-content:space-between;font-size:13px;color:var(--dust)}
.segc{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;background:var(--deck);border-radius:12px;padding:3px;margin-top:6px}
.segc button{padding:8px 0;border-radius:9px;font:600 13px var(--f-text);color:var(--dust)}
.segc button[aria-pressed="true"]{background:var(--deck2);color:#fff}
.tiles2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.tiles2>*{background:var(--deck);border-radius:16px;padding:14px;min-width:0;text-align:left}
.tiles2 .show{font-size:30px;font-weight:800;margin-top:4px;line-height:1}
.emptycard{background:var(--deck);border-radius:18px;padding:22px 18px;text-align:center}
.emptycard b{display:block;font:600 16px var(--f-text)}
.emptycard p{font-size:14px;color:var(--dust);margin-top:6px;line-height:1.45}
.homegrid{display:block}
@media (min-width:760px){
  main{max-width:1120px}
  body{padding-left:max(32px,env(safe-area-inset-left,0px));padding-right:max(32px,env(safe-area-inset-right,0px))}
  .homegrid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:28px;align-items:start}
  #v-seance,#v-prog,#v-corps,#v-agenda{max-width:720px;margin:0 auto}
  .page>.wrap,.live>.wrap,.sheet>.wrap{max-width:680px}
}
"""
rep("""@media (prefers-reduced-motion:reduce)""", V6CSS + """@media (prefers-reduced-motion:reduce)""")
# composants existants alignés sur le concept
rep(""".cell.done{background:color-mix(in srgb,var(--ok) 20%,var(--deck2));color:var(--ok)}""", """.cell.done{background:var(--deck);color:var(--faint)}""")
rep(""".exo{display:flex;gap:12px;padding:14px 0;border-top:1px solid var(--seam);align-items:flex-start;width:100%;text-align:left}""",
    """.exo{display:flex;gap:12px;padding:14px 0;border-top:1px solid var(--seam);align-items:center;width:100%;text-align:left}""")
rep(""".exo .bar-v{width:4px;align-self:stretch;border-radius:4px;background:var(--c,var(--seam));flex:none}""",
    """.exo .bar-v{width:10px;height:10px;border-radius:50%;background:var(--c,var(--deck3));flex:none}""")
rep(""".setgrid{background:var(--deck);border-radius:var(--r-lg);padding:8px 6px;margin-top:14px;--cols:34px minmax(0,1fr) 72px 60px 46px}""",
    """.setgrid{margin-top:4px;--cols:28px minmax(0,1fr) 66px 52px 46px}""")
rep(""".setgrid .hd,.setrow{display:grid;grid-template-columns:var(--cols);gap:6px;align-items:center;padding:6px 8px}""",
    """.setgrid .hd,.setrow{display:grid;grid-template-columns:var(--cols);gap:8px;align-items:center;padding:10px 0}""")
rep(""".setgrid .hd{font:700 11px var(--f-text);letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}""", """.setgrid .hd{font:600 12px var(--f-text);color:var(--faint);padding:0}""")
rep(""".setrow{border-radius:14px;margin-top:2px;transition:background .25s}""", """.setrow{border-bottom:1px solid var(--seam);transition:background .25s}""")
rep(""".setrow .n{font:800 18px var(--f-show);text-align:center;color:var(--dust)}""", """.setrow .n{font:700 19px var(--f-show);color:var(--dust)}""")
rep(""".setrow input{height:42px;text-align:center;font:700 17px var(--f-text);padding:0 2px;background:var(--deck3);border:0;border-radius:10px}""",
    """.setrow input{height:44px;text-align:center;font:700 22px var(--f-show);padding:0 2px;background:var(--deck2);border:0;border-radius:12px}""")
rep(""".setrow .ck{width:44px;height:42px;border-radius:10px;border:1.5px solid #3A3E45;""", """.setrow .ck{width:44px;height:44px;border-radius:12px;border:2px solid var(--deck3);""")
rep(""".setrow.done{background:color-mix(in srgb,var(--c) 16%,transparent)}""", """.setrow.done{background:none}""")
rep(""".setrow.done input{background:color-mix(in srgb,var(--c) 10%,var(--deck2))}""", """.setrow.done input{background:none}""")
rep(""".setrow.cur{box-shadow:inset 0 0 0 1.5px var(--c)}""", """.setrow.cur{background:var(--deck);border-radius:16px;border-bottom-color:transparent;padding:10px;margin:6px -10px}
.setrow.cur .ck{border-color:var(--c)}""")
rep(""".restpill{position:fixed;left:12px;right:12px;bottom:calc(env(safe-area-inset-bottom,0px) + 14px);z-index:45;max-width:536px;margin:0 auto;background:var(--chalk);color:var(--floor);border-radius:26px;""",
    """.restpill{position:fixed;left:12px;right:12px;bottom:calc(env(safe-area-inset-bottom,0px) + 14px);z-index:45;max-width:536px;margin:0 auto;background:#fff;color:var(--floor);border-radius:28px;""")
rep(""".restpill .show{font-size:34px;font-weight:900;""", """.restpill .show{font-size:32px;font-weight:800;""")
rep(""".restpill .rb{width:44px;height:44px;border-radius:22px;background:#E3E0D8;""", """.restpill .rb{width:44px;height:44px;border-radius:22px;background:#EEF0F3;""")
rep(""".restpill.over{background:var(--ok)}""", """.restpill.over{background:var(--ok);color:#fff}""")
rep(""".rpe button{flex:none;min-width:44px;height:40px;border-radius:var(--r-sm);background:var(--deck2);font:800 18px var(--f-show);color:var(--dust)}""",
    """.rpe button{flex:none;min-width:48px;height:44px;border-radius:12px;background:var(--deck);font:700 19px var(--f-show);color:var(--steel-hi)}""")
rep(""".chip[aria-pressed="true"]{background:var(--chalk);color:var(--floor)}""", """.chip[aria-pressed="true"]{background:#fff;color:var(--floor)}""")

# ---------------------------------------------------------------- en-tête et navigation
rep("""<div class="top"><div class="date" id="topdate">Street Lifting<small>Connexion à tes Google Sheets…</small></div><button class="avatar" data-act="settings" aria-label="Réglages et synchronisation"><span id="initial">·</span><span class="dot busy" id="syncdot"></span></button></div>""",
    """<div class="topbar"><div class="brandmark" id="topdate"><svg width="28" height="28" viewBox="0 0 40 40" aria-hidden="true"><path d="M20 4v8" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/><circle cx="20" cy="24" r="11" fill="none" stroke="#fff" stroke-width="4"/><circle cx="20" cy="24" r="3" fill="#fff"/></svg>Street Lifting</div><button class="avatar" data-act="settings" aria-label="Réglages et synchronisation"><span id="initial">·</span><span class="dot busy" id="syncdot"></span></button></div>""")
rep("""  const t = dObj(D.today);
  $("#topdate").innerHTML = `${cap(JOURS[t.getDay()])} ${t.getDate()} ${MOIS_L[t.getMonth()]}<small>${tab === "home" ? "Salut " + esc(D.profil.prenom || "") : ({seance:"Ta prog", prog:"Ta progression", corps:"Poids de corps", agenda:"Compétitions et calendrier"})[tab]}</small>`;""",
    """  /* l'en-tête reste fixe : logo et profil */""")
s = re.sub(r'<button data-tab="seance">(<svg.*?</svg>)Séance</button>', r'<button data-tab="seance">\1Prog</button>', s)
s = re.sub(r'<button data-tab="corps"><svg.*?</svg>Corps</button>', '<button data-tab="corps"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2"/></svg>Corps</button>', s)
s = re.sub(r'<button data-tab="agenda"><svg.*?</svg>Agenda</button>', '<button data-tab="agenda"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M17 6h3a3 3 0 0 1-3 4M7 6H4a3 3 0 0 0 3 4"/></svg>Compét</button>', s)
s = re.sub(r'<button data-tab="home" aria-current="page"><svg.*?</svg>Aujourd\'hui</button>', '<button data-tab="home" aria-current="page"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/></svg>Aujourd\'hui</button>', s)
for t in ("Prog", "Corps", "Compét", "Aujourd'hui"):
    assert f">{t}</button>" in s, t

# ---------------------------------------------------------------- briques communes + accueil
HOME = r'''const DECO = `<svg class="deco" width="220" height="220" viewBox="0 0 220 220" aria-hidden="true"><circle cx="110" cy="110" r="90" fill="none" stroke="#fff" stroke-width="2"/><circle cx="110" cy="110" r="66" fill="none" stroke="#fff" stroke-width="2"/><circle cx="110" cy="110" r="42" fill="none" stroke="#fff" stroke-width="2"/></svg>`;
/* Carte héros : un seul élément fort par écran. */
function heroCard(o){
  return `<section class="hero ${o.plain ? "plain" : ""}" style="${o.color ? "--hc:" + o.color : ""}" ${o.act || ""}>${o.deco === false || o.plain ? "" : DECO}
    <p class="hs">${o.small}</p><p class="hb">${o.big}</p>${o.sub ? `<p class="hu">${o.sub}</p>` : ""}${o.extra || ""}</section>`;
}
const vrow = (title, sub, val, c, act) => `<${act ? "button" : "div"} class="vrow" ${act || ""}>${c ? `<span class="d10" style="--c:${c}"></span>` : ""}<span class="grow"><b>${title}</b>${sub ? `<span>${sub}</span>` : ""}</span><span class="val">${val}</span></${act ? "button" : "div"}>`;
const kg = (v, d) => v === null || v === undefined ? "—" : fmt(v, d) + " kg";
function sessLabel(s){
  const ls = liftsOf(s); return `${esc(s.seance)}${ls.length ? " · " + ls.map(l => LNAME[l].toLowerCase()).join(", ") : ""}`;
}
function weekRows(ref){
  const t = dObj(ref), mon = addDays(ref, -((t.getDay() + 6) % 7)), sun = addDays(mon, 6), ns = nextSeance();
  const list = S.filter(z => { const d = dateOf(z); return d && d >= mon && d <= sun; }).sort((a, b) => dateOf(a) < dateOf(b) ? -1 : 1);
  return list.map(z => { const d = dateOf(z), dd = dObj(d), ls = liftsOf(z), main = z.exercices.find(e => liftOf(e.mouvement));
    const cls = z.faite ? "done" : z === ns ? "next" : "", jour = ["dim.","lun.","mar.","mer.","jeu.","ven.","sam."][dd.getDay()];
    const sub = z === ns && main ? `${esc(main.series)} × ${esc(main.reps)}${isNumTxt(main.charge) ? " à " + kg(num(main.charge)) : ""}` : "";
    return `<button class="day ${cls} ${d === D.today ? "today" : ""}" data-act="openSeance" data-k="${esc(z.key)}"><span class="dn"><b>${dd.getDate()}</b><span>${jour}</span></span>
      <span class="grow">${z === ns ? `<b>${sessLabel(z)}</b>${sub ? `<span>${sub}</span>` : ""}` : sessLabel(z)}</span>
      ${z.faite ? `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--ok)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-label="Faite"><path d="M5 12l5 5 9-10"/></svg>` : `<span class="dots" style="display:flex;gap:4px">${ls.map(l => `<i class="d10" style="--c:${LCOL[l]}"></i>`).join("")}</span>`}</button>`; }).join("");
}
function remainingInBloc(){ const b = activeBloc(); return b === null ? 0 : S.filter(z => z.bloc === b && !z.faite).length; }
function rHome(){
  const t = total(), r = risOf(t, bw()), ts = todaySeance(), ns = nextSeance(), sess = ts && !ts.faite ? ts : ns, nc = nextComp(), pw = D.poids.at(-1), weighed = pw && pw.date === D.today;
  const bil = pendingBilan(), lv = store.get("sl4-live"), sessDate = sess && dateOf(sess), rem = remainingInBloc();
  const weekRef = sessDate && sessDate > addDays(D.today, 6 - (dObj(D.today).getDay() + 6) % 7) ? sessDate : D.today, wr = S.length ? weekRows(weekRef) : "";
  const jourBtn = sessDate ? (sessDate === D.today ? "d'aujourd'hui" : "de " + JOURS[dObj(sessDate).getDay()]) : "";
  const tgt = LIFTS.reduce((a, l) => a + ((l === "MU" && !muOn()) ? 0 : (D.objectifs[l] || best(l) || 0)), 0);
  const heroH = nc ? heroCard({small:`${esc(nc.nom)}, ${dlong(nc.date)}${nc.tbc ? " (à confirmer)" : ""}`, big:days(D.today, nc.date) === 0 ? "Jour J" : "J−" + days(D.today, nc.date), sub:rem ? `encore ${rem} séance${rem > 1 ? "s" : ""} dans le bloc ${activeBloc()}` : "", act:`data-act="tab" data-t="agenda" role="button" tabindex="0"`})
    : heroCard({small:"Mon total", big:`${fmt(t)}<small>kg</small>`, sub:`RIS ${fmt(r, 1)} · objectif ${fmt(tgt)} kg`, act:`data-act="tab" data-t="prog" role="button" tabindex="0"`});
  const left = `${heroH}
    <h2 class="h2">Cette semaine <span class="muted">${sess ? "Bloc " + sess.bloc + ", semaine " + esc(sess.semaine) : ""}</span></h2>
    ${S.length ? (wr || `<p class="muted small">Aucune séance datée cette semaine.</p>`) : `<div class="row" style="padding:14px 0"><span class="muted">${esc(seanceErr) || "Chargement de ta prog…"}</span>${seanceErr ? "" : `<div class="spin"></div>`}</div>`}
    ${sess ? `<button class="btn" style="margin-top:16px" data-act="startLive" data-k="${esc(sess.key)}">${lv && lv.key === sess.key ? "Reprendre la séance" : "Commencer la séance " + jourBtn}</button>` : ""}`;
  const right = `${nc ? `<div class="desk-only">${heroCard({plain:true, small:"Mon total", big:`${fmt(t)}<small>kg</small>`, sub:`RIS ${fmt(r, 1)} · objectif ${fmt(tgt)} kg`})}</div>` : ""}
    <h2 class="h2">Mes records</h2>
    ${LIFTS.filter(l => l !== "MU" || muOn()).map(l => vrow(LNAME[l], D.objectifs[l] ? "objectif " + kg(D.objectifs[l]) : "pas encore d'objectif", kg(best(l)), LCOL[l], `data-act="openLift" data-l="${l}"`)).join("")}
    ${!weighed ? `<h2 class="h2">Pesée du jour <span class="muted">${pw ? "dernière : " + kg(pw.poids, 1) : ""}</span></h2>
      <div class="stepper"><button data-act="stepW" data-d="-0.1" aria-label="Moins 100 g">−</button><input id="hw" inputmode="decimal" value="${pw ? fmt(pw.poids, 1) : ""}" aria-label="Poids en kg"><button data-act="stepW" data-d="0.1" aria-label="Plus 100 g">+</button></div>
      <button class="btn ghost" style="margin-top:8px" data-act="saveW" data-src="hw">Enregistrer ma pesée</button>` : ""}
    ${bil ? `<h2 class="h2">Pour ton coach</h2>${vrow("Bilan de la semaine " + esc(bil.semaine), "sommeil, fatigue, motivation… en 30 secondes", "›", null, `data-act="bilan" data-w="${esc(bil.sheet + "|" + bil.semaine)}"`)}` : ""}`;
  $("#v-home").innerHTML = `<div class="homegrid"><div>${left}</div><div>${right}</div></div>`;
  firstPaint = false;
}
'''
cut("const DECO", "function ringSVG(){", "") if "const DECO" in s else None
cut("function ringSVG(){", "/* =====================================================================\n   ONGLET SÉANCE", HOME + "\n")
rep(""".homegrid{display:block}""", """.homegrid{display:block}
.desk-only{display:none}
@media (min-width:760px){.desk-only{display:block}}""")

# ---------------------------------------------------------------- onglet Prog : lignes de séance au style du concept
rep("""    <div class="row" style="margin:24px 0 4px">
      <div><p class="show t-l">${esc(s.seance)}</p><p class="muted small" style="margin-top:4px">${d ? cap(dlong(d)) : esc(s.jour || "")}, semaine ${esc(s.semaine)}</p></div>
      ${s.faite ? `<span class="pill ok">Faite</span>` : s === ns ? `<span class="pill go">À faire</span>` : `<span class="pill">À venir</span>`}
    </div>""",
"""    ${heroCard({color:liftsOf(s)[0] ? LCOL[liftsOf(s)[0]] : "var(--brand)", small:`${d ? cap(dlong(d)) : esc(s.jour || "")} · bloc ${s.bloc}, semaine ${esc(s.semaine)}`, big:esc(s.seance), sub:s.faite ? "Faite" : s === ns ? "Prochaine séance" : "À venir"})}""")
rep("""    <div class="panel" style="margin-top:12px">
      <div class="row"><p class="show t-s">Bloc ${s.bloc}</p><p class="muted small">${inB.filter(x => x.faite).length} / ${inB.length} séances faites</p></div>
      <p class="muted tiny" style="margin-top:6px">Une ligne par semaine, une colonne par séance.</p>""",
"""    <h2 class="h2">Bloc ${s.bloc} <span class="muted">${inB.filter(x => x.faite).length} sur ${inB.length} séances faites</span></h2>
    <div>""")

# ---------------------------------------------------------------- séance en direct : carte héros à la couleur du mouvement
rep("""    <p class="eyebrow" style="color:${l ? `color-mix(in srgb,${col} 70%,#fff)` : "var(--dust)"}">${renfo ? "Renforcement" : esc(LNAME[l] || title(e.mouvement))}${e.tempo ? " · tempo " + esc(e.tempo) : ""}</p>
    <h1 class="show" style="font-size:40px;font-weight:900;margin-top:4px;line-height:.95">${esc(name)}</h1>
    <p class="muted small" style="margin-top:8px">${presc(e)}${e.intensite ? ", " + esc(e.intensite) : ""}${prev ? ` · la dernière fois${prev.date ? " (" + dshort(prev.date) + ")" : ""} : ${esc(fmtSets(prev.sets))}` : ""}</p>""",
"""    ${(() => { const cur = st.sets[curJ < 0 ? st.sets.length - 1 : curJ] || {}, c0 = cur.c ?? chargeGuess(e);
      return heroCard({color:l ? col : "var(--deck2)", deco:!!l, small:`Exercice ${k + 1} sur ${s.exercices.length} · ${esc(name)}`, big:c0 !== null && c0 !== undefined && c0 !== "" ? `${fmt(num(c0))}<small>kg</small>` : (isBW ? "PDC" : esc(e.charge || "—")), sub:`${esc(e.series)} série${num(e.series) > 1 ? "s" : ""} de ${esc(e.reps)}${e.tempo ? " · tempo " + esc(e.tempo) : ""}${e.repos ? " · repos " + esc(e.repos) : ""}`}); })()}
    <h2 class="h2">Séries <span class="muted">${prev ? "la dernière fois : " + esc(fmtSets(prev.sets)) : esc(e.intensite || "")}</span></h2>""")
rep("""    <section class="setgrid" style="--c:${col}" aria-label="Séries">""", """    <section class="setgrid" style="--c:${l ? col : "var(--brand)"}" aria-label="Séries">""")
rep("""  const rpeRow = (f, lab) => `<div class="card" style="margin-top:12px"><div class="row"><p style="font-weight:700">${lab}</p><p class="muted tiny">envoyé au coach</p></div><div class="rpe">""",
    """  const rpeRow = (f, lab) => `<div><h2 class="h2">${lab} <span class="muted">pour ton coach</span></h2><div class="rpe">""")

# ---------------------------------------------------------------- progrès
rep("""  $("#v-prog").innerHTML = `
    <div class="totalrow" style="margin-top:10px"><div><p class="muted small">Total actuel</p><p class="show t-xl">${fmt(t)}<span class="unit">kg</span></p></div><div class="ris"><p class="muted small">RIS</p><b class="show t-l">${fmt(r, 1)}</b></div></div>
    <div class="grid3" style="margin-top:14px">
      <div><p class="muted small">Réaliste au ${dfr(objDate())}</p><p class="show t-s" style="margin-top:4px">${bands.length ? fmt(sum(bands.map(b => b.lo)), 0) + "–" + fmt(sum(bands.map(b => b.hi)), 0) : "–"}</p></div>
      <div><p class="muted small">Ton objectif</p><p class="show t-s" style="margin-top:4px">${fmt(oT, 1)}</p></div>
      <div><p class="muted small">RIS visé</p><p class="show t-s" style="margin-top:4px">${fmt(risOf(oT, bw()), 1)}</p></div>
    </div>""",
"""  const seg = `<div class="seg3">${["SQUAT","DIP","PULL","MU"].filter(l => best(l)).map((l, i) => `<i style="width:${(best(l) / (oT || 1) * 100).toFixed(1)}%;background:rgba(255,255,255,${[1, .75, .55, .4][i]})"></i>`).join("")}</div>`;
  $("#v-prog").innerHTML = `
    ${heroCard({small:"Mon total", big:`${fmt(t)}<small>kg</small>`, sub:`RIS ${fmt(r, 1)} · objectif ${fmt(oT, 1)} kg`, extra:seg, deco:false})}
    <div class="tiles2" style="margin-top:12px"><div><p class="muted small">Réaliste au ${dfr(objDate())}</p><p class="show">${bands.length ? fmt(sum(bands.map(b => b.lo)), 0) + "–" + fmt(sum(bands.map(b => b.hi)), 0) : "–"}</p></div><div><p class="muted small">RIS visé</p><p class="show">${fmt(risOf(oT, bw()), 1)}</p></div></div>""")
rep("""    <div class="liftgrid">${["PULL","DIP","SQUAT","MU"].map(l => { const b = best(l), o = D.objectifs[l], v = verdictOf(l, o), lock = l === "MU" && !muOn();
      if (lock) return `<button class="liftcard locked" data-act="openLift" data-l="${l}"><span class="row" style="justify-content:flex-start;gap:8px;font-weight:700;font-size:13px"><span class="dot8" style="--c:transparent;box-shadow:inset 0 0 0 2px var(--mu)"></span>${LNAME[l]}</span><span class="show" style="color:var(--faint)">—</span><span class="small" style="color:var(--steel-hi)">À débloquer. Active-le dès ton premier muscle-up.</span></button>`;
      return `<button class="liftcard" data-act="openLift" data-l="${l}"><span class="row" style="justify-content:flex-start;gap:8px;font-weight:700;font-size:13px"><span class="dot8" style="--c:${LCOL[l]};width:10px;height:10px"></span>${LNAME[l]}</span>
        <span class="show">${b ? (l === "SQUAT" ? "" : "+") + fmt(b) : "—"}</span>
        <span class="bar" style="--c:${LCOL[l]}"><i style="width:${o && b ? pct(b, o) : 0}%"></i></span>
        <span class="muted small">${o ? "Objectif " + fmt(o) + (v ? " · " + v.txt.toLowerCase() : "") : "Pas encore d'objectif"}</span></button>`; }).join("")}</div>""",
"""    <div>${["PULL","DIP","SQUAT","MU"].map(l => { const b = best(l), o = D.objectifs[l], v = verdictOf(l, o), lock = l === "MU" && !muOn();
      if (lock) return `<button class="vrow" data-act="openLift" data-l="${l}"><span class="d10" style="--c:transparent;box-shadow:inset 0 0 0 2px var(--mu)"></span><span class="grow"><b style="color:var(--steel-hi)">${LNAME[l]}</b></span><span class="muted small">à débloquer</span></button>`;
      return `<button class="liftrow" data-act="openLift" data-l="${l}"><span class="top"><span class="d10" style="--c:${LCOL[l]}"></span><b>${LNAME[l]}</b><span class="val">${kg(b)}</span></span>
        <span class="bar" style="display:block;--c:${LCOL[l]}"><i style="width:${o && b ? pct(b, o) : 0}%"></i></span>
        <span class="meta"><span>${o ? "objectif " + kg(o) : "pas encore d'objectif"}</span><span>${v ? v.txt.toLowerCase() : ""}</span></span></button>`; }).join("")}</div>""")
rep("""  return `<h2 class="h2">Renfo · double progression</h2>
    ${L.map(x => `<button class="card" style="display:block;width:100%;text-align:left" data-act="openEx" data-k="${esc(x.key)}">""",
    """  return `<h2 class="h2">Renfo <span class="muted">double progression</span></h2>
    ${L.map(x => `<button class="vrow" style="display:block" data-act="openEx" data-k="${esc(x.key)}">""")

# ---------------------------------------------------------------- fiche mouvement
rep("""    <p class="eyebrow" style="color:color-mix(in srgb,${LCOL[l]} 70%,#fff)">${LNAME[l]} · record perso</p>
    <p class="show" id="liftbig" style="font-size:88px;font-weight:900;line-height:.9;margin-top:4px">${lock ? "—" : (BW_LIFTS.includes(l) ? "+" : "") + fmt(b)}<span class="unit">kg</span></p>
    ${!lock && hist.length ? `<p class="muted small" style="margin-top:6px">${cap(dlong(D.prs.filter(p => p.lift === l && p.reps === 1).sort((a, c) => c.charge - a.charge)[0]?.date || hist[0].date))}${BW_LIFTS.includes(l) && bw() ? " · " + fmt(b + bw(), 1) + " kg avec ton poids de corps" : ""}</p>` : ""}""",
"""    ${heroCard({color:LCOL[l], small:`${LNAME[l]} · record perso${!lock && hist.length ? " · " + dlong(D.prs.filter(p => p.lift === l && p.reps === 1).sort((a, c) => c.charge - a.charge)[0]?.date || hist[0].date) : ""}`, big:lock ? "—" : `${fmt(b)}<small>kg</small>`, sub:!lock && BW_LIFTS.includes(l) && bw() ? fmt(b + bw(), 1) + " kg avec ton poids de corps" : (lock ? "à débloquer" : "")})}""")
rep("""    <div class="card">${(() => { const top = Math.max(b || 0, ...[nr, wr].filter(Boolean).map(x => x.valeur)) || 1;""",
    """    <div>${(() => { const top = Math.max(b || 0, ...[nr, wr].filter(Boolean).map(x => x.valeur)) || 1;""")

# ---------------------------------------------------------------- corps
rep("""    <div class="totalrow" style="margin-top:10px"><div><p class="muted small">${last ? "Dernière pesée, " + dlong(last.date) : "Aucune pesée"}</p><p class="show t-xl">${last ? fmt(last.poids, 1) : "–"}<span class="unit">kg</span></p></div>
      ${lim && last ? `<span class="pill ${last.poids <= lim ? "ok" : "bad"}">${last.poids <= lim ? "Marge " + fmt(lim - last.poids, 1) + " kg sous " + lim : "+" + fmt(last.poids - lim, 1) + " kg sur " + lim}</span>` : ""}</div>
    <div class="panel" style="margin-top:16px">
      <p style="font-weight:600">${tw ? "Pesée du jour : " + fmt(tw.poids, 1) + " kg" : "Pesée du jour"}</p>
      <div class="stepper"><button data-act="stepW" data-d="-0.1" aria-label="Moins 100 g">−</button><input id="cw" inputmode="decimal" value="${last ? fmt(tw ? tw.poids : last.poids, 1) : ""}" aria-label="Poids en kg"><button data-act="stepW" data-d="0.1" aria-label="Plus 100 g">+</button></div>
      <div class="grid2" style="margin-top:8px"><input id="cwd" type="date" value="${D.today}" aria-label="Date"><button class="btn" data-act="saveW" data-src="cw">${tw ? "Corriger" : "Enregistrer"}</button></div>
    </div>
    <div class="chips" style="margin-top:20px">${RANGES.map(([k, t]) => `<button class="chip" aria-pressed="${k === pwRange}" data-act="pwRange" data-k="${k}">${t}</button>`).join("")}</div>
    <div class="panel" style="margin-top:10px">""",
"""    ${heroCard({plain:true, small:tw ? "Pesée de ce matin" : last ? "Dernière pesée, " + dlong(last.date) : "Aucune pesée", big:last ? `${fmt(last.poids, 1)}<small>kg</small>` : "—",
      sub:lim && last ? (last.poids <= lim ? fmt(lim - last.poids, 1) + " kg sous la limite des −" + lim : fmt(last.poids - lim, 1) + " kg au-dessus de la limite des −" + lim) : "",
      extra:`<div class="hbtns"><button class="pm" data-act="stepW" data-d="-0.1" aria-label="Moins 100 g">−</button><input id="cw" inputmode="decimal" value="${last ? fmt(tw ? tw.poids : last.poids, 1) : ""}" aria-label="Poids en kg"><button class="pm" data-act="stepW" data-d="0.1" aria-label="Plus 100 g">+</button></div>
        <div class="grid2" style="margin-top:8px;position:relative"><input id="cwd" type="date" value="${D.today}" aria-label="Date" style="background:rgba(255,255,255,.12);border:0;color:#fff"><button class="btn" style="min-height:48px" data-act="saveW" data-src="cw">${tw ? "Corriger" : "Enregistrer"}</button></div>`})}
    <h2 class="h2">Évolution</h2>
    <div class="segc">${RANGES.map(([k, t]) => `<button aria-pressed="${k === pwRange}" data-act="pwRange" data-k="${k}">${t}</button>`).join("")}</div>
    <div style="margin-top:14px">""")
rep("""      ${V.length > 1 ? `<canvas id="c-pw" aria-label="Courbe de poids"></canvas>` : `<p class="muted small" style="text-align:center;padding:18px 0">${V.length ? "Une seule pesée sur cette période." : "Aucune pesée sur cette période."}</p>`}""",
    """      ${V.length > 1 ? `<canvas id="c-pw" aria-label="Courbe de poids"></canvas>` : `<div class="emptycard"><b>${V.length ? "Une seule pesée sur cette période" : "Aucune pesée sur cette période"}</b><p>Pèse-toi chaque matin, à jeun. La courbe apparaît dès la 2e pesée.</p></div>`}""")
rep("""    <h2 class="h2">Importer un historique</h2>
    <div class="panel"><p class="small muted">""", """    <h2 class="h2">Importer un historique</h2>
    <div><p class="small muted">""")
rep("""    <div class="panel"><table>${P.slice().reverse().slice(0, 15).map(p => `<tr><td>${cap(dlong(p.date))}</td><td><b>${fmt(p.poids, 1)} kg</b></td></tr>`).join("")}</table></div>`;""",
    """    <h2 class="h2">Dernières pesées</h2><div>${P.slice().reverse().slice(0, 15).map(p => vrow(cap(dlong(p.date)), "", kg(p.poids, 1))).join("")}</div>`;""")

# ---------------------------------------------------------------- compét
rep("""    ${nc ? `<div style="margin-top:10px"><p class="muted">${esc(nc.nom)}${nc.tbc ? ", date à confirmer" : ""}</p><p class="show t-xl" style="margin-top:2px">J-${days(t, nc.date)}</p><p class="muted small">${cap(dlong(nc.date))}${nc.lieu ? ", " + esc(nc.lieu) : ""}</p></div>` : `<p class="muted" style="margin-top:12px">Aucune compétition prévue.</p>`}""",
    """    ${nc ? heroCard({small:`${esc(nc.nom)}${nc.tbc ? " · date à confirmer" : ""}`, big:days(t, nc.date) === 0 ? "Jour J" : "J−" + days(t, nc.date), sub:`${cap(dlong(nc.date))}${nc.lieu ? ", " + esc(nc.lieu) : ""}`}) : `<div class="emptycard" style="margin-top:14px"><b>Aucune compétition prévue</b><p>Ajoute ta prochaine compét plus bas : l'app compte les jours et prépare ta checklist.</p></div>`}""")
rep("""    <div class="panel"><div class="cal">""", """    <div><div class="cal">""")
rep("""      <div class="row"><span class="pill ${c.tbc ? "warn" : d >= 0 ? "go" : ""}">""" if False else """<span class="pill ${c.tbc ? "warn" : d >= 0 ? "go" : ""}">""", """<span class="pill ${c.tbc ? "warn" : d >= 0 ? "go" : ""}">""")
s = s.replace("""<p style="font-weight:600">Pesée</p>""", """<p style="font-weight:700">Pesée</p>""")

rep("""  tab:d => setTab(d.t),""", """  tab:d => setTab(d.t),
  openSeance:d => { sel = d.k; setTab("seance"); },""")
P.write_text(s)
print("v6 appliquée")
