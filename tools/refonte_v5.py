"""Refonte v5 (une seule fois) : nouveau thème, accueil, séance en direct, progrès, fiche mouvement."""
import pathlib, re
P = pathlib.Path(__file__).resolve().parent.parent / "src" / "app.html"
s = P.read_text()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, f"{c} occurrence(s) au lieu de {n} : {a[:90]!r}"
    s = s.replace(a, b)

def cut(start, end, new):
    """Remplace de start (inclus) à end (exclu)."""
    global s
    i = s.index(start); j = s.index(end, i)
    s = s[:i] + new + s[j:]

# ---------------------------------------------------------------- 1. Thème
rep("""/* Direction : le sol de la salle (graphite caoutchouc), la craie (texte), l'acier (barre) et les disques de compétition.
   Un seul élément fort : la barre chargée en ouverture. Le reste est calme, aligné à gauche, une colonne.
   Palette des disques validée daltonisme sur fond sombre : MU or, tractions bleu, dips sarcelle, squat rouge. */""",
"""/* Direction v5 (références : Whoop, Hevy, TrainingPeaks, Garmin) : fond presque noir, cartes sombres,
   un chiffre héros par écran, la couleur réservée aux 4 mouvements. Action principale en blanc craie.
   Palette des disques validée daltonisme sur fond sombre : MU or, tractions bleu, dips sarcelle, squat rouge.
   Échelle : espacements 4/8/12/16/24, rayons 12/16/22, texte 11/12/13/15/17 + titres Big Shoulders. */""")
rep("""  --floor:#17181B; --deck:#1F2125; --deck2:#282B30; --seam:#33363C;
  --chalk:#ECEAE4; --dust:#9C9FA6; --steel:#8E9198; --steel-hi:#C9CBCF;""",
"""  --floor:#0B0C0F; --deck:#15171B; --deck2:#1D2025; --deck3:#24272D; --seam:#24272D;
  --chalk:#F2F0EA; --dust:#9A9EA6; --faint:#6E727A; --steel:#8E9198; --steel-hi:#C9CBCF;""")
rep("""  --go:#E0443B; --ok:#5BC48A;""", """  --go:#F2F0EA; --comp:#E0443B; --ok:#5BC48A;""")
rep("""  --r-lg:20px; --r:14px; --r-sm:10px;""", """  --r-lg:22px; --r:16px; --r-sm:12px; --ease:cubic-bezier(.2,.8,.2,1);""")
rep(""".btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:15px 18px;border-radius:var(--r);background:var(--go);color:#fff;font:700 16px var(--f-text)}""",
""".btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;min-height:52px;padding:14px 18px;border-radius:var(--r);background:var(--chalk);color:var(--floor);font:700 16px var(--f-text);transition:transform .12s var(--ease)}
.btn:active{transform:scale(.97)}""")
rep(""".pill.go{background:var(--go);color:#fff}""", """.pill.go{background:var(--chalk);color:var(--floor)}""")
rep(""".cell.next{box-shadow:inset 0 0 0 2px var(--go);color:var(--chalk)}""", """.cell.next{box-shadow:inset 0 0 0 2px var(--chalk);color:var(--chalk)}""")
rep(""".cal .d.comp{background:var(--go);color:#fff}""", """.cal .d.comp{background:var(--comp);color:#fff}""")
rep(""".cal .d.comp.tbc{background:color-mix(in srgb,var(--go) 35%,var(--deck2));color:var(--chalk)}""", """.cal .d.comp.tbc{background:color-mix(in srgb,var(--comp) 35%,var(--deck2));color:var(--chalk)}""")
rep(""".tabs button[aria-current="page"] svg{color:var(--go)}""", """.tabs button[aria-current="page"] svg{color:var(--chalk)}""")
rep(""".tabs{position:fixed;left:0;right:0;bottom:0;z-index:20;display:flex;background:color-mix(in srgb,var(--floor) 90%,transparent);""",
    """.tabs{position:fixed;left:0;right:0;bottom:0;z-index:20;display:flex;background:color-mix(in srgb,var(--floor) 88%,transparent);""")
rep(""".tabs button{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;padding:5px 0;font:600 11px var(--f-text);color:#7b7e85}""",
    """.tabs button{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;padding:5px 0;font:600 11px var(--f-text);color:var(--faint);transition:color .2s}""")
rep(""".rpe button[aria-pressed="true"]{background:var(--c,var(--chalk));color:#fff}""", """.rpe button[aria-pressed="true"]{background:var(--chalk);color:var(--floor)}""")
rep(""".h2{font-family:var(--f-show);font-weight:800;font-size:24px;margin:30px 0 12px;""", """.h2{font-family:var(--f-show);font-weight:800;font-size:24px;margin:28px 0 12px;""")

NEWCSS = """
/* ---------- v5 : composants ---------- */
.card{background:var(--deck);border-radius:var(--r-lg);padding:16px}
.card+.card,.card+.tiles,.tiles+.card{margin-top:12px}
.eyebrow{font:700 12px var(--f-text);letter-spacing:.08em;text-transform:uppercase;color:var(--dust)}
.rise{animation:rise .5s var(--ease) both}
@keyframes rise{from{opacity:0;transform:translateY(10px)}}
.view>.rise:nth-child(2){animation-delay:.05s}.view>.rise:nth-child(3){animation-delay:.1s}.view>.rise:nth-child(4){animation-delay:.15s}.view>.rise:nth-child(5){animation-delay:.2s}
.exline{display:flex;align-items:center;gap:10px;font-size:15px}
.exline b{flex:1;min-width:0;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.exline span:last-child{color:var(--steel-hi);font-size:14px;font-variant-numeric:tabular-nums;white-space:nowrap}
.dot8{width:8px;height:8px;border-radius:50%;background:var(--c,var(--faint));flex:none}
.week{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin-top:12px}
.week>div{display:flex;flex-direction:column;align-items:center;gap:6px;font:500 11px var(--f-text);color:var(--dust)}
.week .wd{width:100%;max-width:44px;aspect-ratio:1;border-radius:12px;display:grid;place-items:center;font:600 13px var(--f-text);color:var(--faint);background:var(--deck)}
.week .wd.plan{background:none;box-shadow:inset 0 0 0 1px var(--deck3);color:var(--steel-hi)}
.week .wd.done{background:var(--chalk);color:var(--floor)}
.week .wd.today{box-shadow:inset 0 0 0 2px var(--c,var(--chalk));color:var(--chalk);font-weight:800}
.week .wd.comp{background:var(--comp);color:#fff}
.ringwrap{position:relative;width:220px;height:186px;margin:2px auto 0}
.ringwrap svg{position:absolute;top:0;left:0}
.ringwrap .ctr{position:absolute;top:56px;left:0;right:0;text-align:center}
.seg{stroke-dasharray:0 754;animation:segIn 1s var(--ease) forwards}
@keyframes segIn{to{stroke-dasharray:var(--len) 754}}
.stats3{display:grid;grid-template-columns:repeat(3,1fr);margin-top:6px}
.stats3>div{text-align:center;min-width:0}.stats3>div+div{border-left:1px solid var(--seam)}
.stats3 b{display:block;font:800 22px var(--f-show);margin-top:2px;font-variant-numeric:tabular-nums}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.tile{background:var(--deck);border-radius:20px;padding:14px;min-width:0;text-align:left}
.tile .show{font-size:36px;font-weight:900;margin-top:6px;line-height:1}
.liftgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.liftcard{background:var(--deck);border-radius:var(--r-lg);padding:14px;display:flex;flex-direction:column;gap:8px;text-align:left;min-width:0}
.liftcard .show{font-size:44px;font-weight:900;line-height:.9}
.liftcard.locked{box-shadow:inset 0 0 0 1.5px color-mix(in srgb,var(--mu) 35%,var(--deck))}
.liftcard .bar{display:block}
.dp{display:grid;grid-template-columns:repeat(var(--n,3),1fr);gap:4px;margin-top:10px}
.dp i{height:8px;border-radius:4px;background:var(--deck3);overflow:hidden}
.dp i b{display:block;height:100%;border-radius:4px;background:var(--chalk)}
.dp.full i b{background:var(--ok)}
.tag{font:700 12px var(--f-text);border-radius:10px;padding:4px 9px;background:var(--deck3);color:var(--steel-hi);white-space:nowrap}
.tag.ok{background:var(--ok);color:#0B0C0F}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}
.two>div{background:var(--deck2);border-radius:16px;padding:12px;min-width:0}
.two .show{font-size:28px;font-weight:900;margin-top:4px;line-height:1}
.rec{margin-top:12px}.rec .row{font-size:13px}.rec .bar{height:8px;margin-top:6px}
/* Séance en direct : tableau de séries */
.livehead{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:4px 0 10px;position:sticky;top:calc(-1 * env(safe-area-inset-top,0px) - 8px);background:var(--floor);z-index:2}
.endbtn{height:36px;padding:0 14px;border-radius:18px;background:var(--chalk);color:var(--floor);font:700 14px var(--f-text)}
.setgrid{background:var(--deck);border-radius:var(--r-lg);padding:8px 6px;margin-top:14px;--cols:34px minmax(0,1fr) 72px 60px 46px}
.setgrid .hd,.setrow{display:grid;grid-template-columns:var(--cols);gap:6px;align-items:center;padding:6px 8px}
.setgrid .hd{font:700 11px var(--f-text);letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
.setgrid .hd span:nth-child(n+3){text-align:center}
.setrow{border-radius:14px;margin-top:2px;transition:background .25s}
.setrow .n{font:800 18px var(--f-show);text-align:center;color:var(--dust)}
.setrow .pv{font-size:13px;color:var(--dust);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.setrow input{height:42px;text-align:center;font:700 17px var(--f-text);padding:0 2px;background:var(--deck3);border:0;border-radius:10px}
.setrow .ck{width:44px;height:42px;border-radius:10px;border:1.5px solid #3A3E45;display:grid;place-items:center;color:transparent;transition:background .2s,transform .15s}
.setrow.done{background:color-mix(in srgb,var(--c) 16%,transparent)}
.setrow.done input{background:color-mix(in srgb,var(--c) 10%,var(--deck2))}
.setrow.done .ck{background:var(--c);border-color:var(--c);color:#fff;animation:pop .3s var(--ease)}
.setrow.done .n{color:var(--chalk)}
@keyframes pop{50%{transform:scale(1.15)}}
.setrow.cur{box-shadow:inset 0 0 0 1.5px var(--c)}
.nextup{display:flex;align-items:center;gap:10px;margin-top:16px;font-size:14px}
.nextup b{font-weight:600}
/* Chrono de repos flottant */
.restpill{position:fixed;left:12px;right:12px;bottom:calc(env(safe-area-inset-bottom,0px) + 14px);z-index:45;max-width:536px;margin:0 auto;background:var(--chalk);color:var(--floor);border-radius:26px;padding:12px 14px;display:flex;align-items:center;gap:12px;box-shadow:0 18px 40px rgba(0,0,0,.5);animation:up .35s var(--ease)}
.restpill .show{font-size:34px;font-weight:900;line-height:1;font-variant-numeric:tabular-nums}
.restpill .rb{width:44px;height:44px;border-radius:22px;background:#E3E0D8;font:700 13px var(--f-text);color:var(--floor);flex:none}
.restpill .go2{height:44px;padding:0 14px;border-radius:22px;background:var(--floor);color:var(--chalk);font:700 14px var(--f-text);flex:none}
.restpill.over{background:var(--ok)}
.live.resting{padding-bottom:calc(env(safe-area-inset-bottom,0px) + 110px)}
"""
rep("""@media (prefers-reduced-motion:reduce)""", NEWCSS + """@media (prefers-reduced-motion:reduce)""")

# ---------------------------------------------------------------- 2. Accueil
HOME = r'''function ringSVG(){
  /* Anneau du total : chaque mouvement occupe sa part du total visé (objectifs, sinon PR). 270°, r = 120 → 565,5 unités. */
  const tgt = LIFTS.reduce((a, l) => a + ((l === "MU" && !muOn()) ? 0 : Math.max(D.objectifs[l] || 0, best(l) || 0)), 0) || 1, ARC = 565.49;
  let at = 0, segs = "";
  for (const l of ["SQUAT","DIP","PULL","MU"]) { const b = (l === "MU" && !muOn()) ? 0 : best(l) || 0; if (!b) continue;
    const len = Math.max(0, b / tgt * ARC - 4);
    segs += `<circle class="seg" cx="150" cy="150" r="120" fill="none" stroke="${getCss(LCOL[l])}" stroke-width="18" stroke-linecap="round" stroke-dashoffset="${-(at + 2)}" style="--len:${len.toFixed(1)}" transform="rotate(135 150 150)"/>`;
    at += b / tgt * ARC; }
  return {tgt, svg:`<svg width="220" height="220" viewBox="0 0 300 300" aria-hidden="true"><circle cx="150" cy="150" r="120" fill="none" stroke="var(--deck3)" stroke-width="18" stroke-linecap="round" stroke-dasharray="565.49 754" transform="rotate(135 150 150)"/>${segs}</svg>`};
}
function weekStrip(ref){
  const t = dObj(ref), mon = addDays(ref, -((t.getDay() + 6) % 7)), comps = new Set(D.comps.map(c => c.date));
  return `<div class="week">${Array.from({length:7}, (_, i) => { const d = addDays(mon, i), ss = S.filter(z => dateOf(z) === d), sd = ss[0];
    const l = sd ? liftsOf(sd)[0] : null, cls = comps.has(d) ? "comp" : sd && sd.faite ? "done" : sd ? "plan" : "";
    return `<div><span>${"LMMJVSD"[i]}</span><button class="wd ${cls} ${d === D.today ? "today" : ""}" style="--c:${l ? LCOL[l] : "var(--chalk)"}" ${sd ? `data-act="startLive" data-k="${esc(sd.key)}"` : "disabled"} aria-label="${cap(dlong(d))}${sd ? ", " + esc(sd.seance) + (sd.faite ? ", faite" : "") : ""}">${sd && sd.faite ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10"/></svg>` : dObj(d).getDate()}</button></div>`; }).join("")}</div>`;
}
function rHome(){
  const t = total(), r = risOf(t, bw()), ts = todaySeance(), ns = nextSeance(), sess = ts && !ts.faite ? ts : ns, nc = nextComp(), pw = D.poids.at(-1), weighed = pw && pw.date === D.today;
  const ins = insight(), bil = pendingBilan(), lv = store.get("sl4-live"), sessDate = sess && dateOf(sess);
  const mo = Math.max(0, days(D.today, objDate()) / 30.44), bands = LIFTS.map(l => band(l, mo)).filter(Boolean), ring = ringSVG();
  const main = sess ? sess.exercices.filter(e => liftOf(e.mouvement)).slice(0, 3), rest = sess ? sess.exercices.length - main.length : 0;
  $("#v-home").innerHTML = `
    ${S.length ? (sess ? `<section class="card rise" aria-label="Séance">
        <div class="row"><p class="eyebrow">${sess === ts ? "Aujourd'hui" : "Prochaine" + (sessDate ? " · " + dshort(sessDate) : "")}</p><p class="muted small">Bloc ${sess.bloc} · S${esc(sess.semaine)}</p></div>
        <h2 class="show t-m" style="margin:8px 0 12px">${esc(sess.seance)}</h2>
        <div class="stack" style="gap:9px">${main.map(e => { const l = liftOf(e.mouvement);
          return `<div class="exline"><span class="dot8" style="--c:${LCOL[l]}"></span><b>${esc(LNAME[l] + " " + title(e.variation).toLowerCase())}</b><span>${esc(e.series)} × ${esc(e.reps)}${isNumTxt(e.charge) ? " · " + fmt(num(e.charge)) + " kg" : e.tempo ? " · " + esc(e.tempo) : ""}</span></div>`; }).join("")}
          ${rest > 0 ? `<p class="muted small" style="margin-left:18px">+ ${rest} exercice${rest > 1 ? "s" : ""}${main.length ? " de renfo" : ""}</p>` : ""}</div>
        <button class="btn" style="margin-top:16px" data-act="startLive" data-k="${esc(sess.key)}">${lv && lv.key === sess.key ? "Reprendre la séance" : "Commencer la séance"}</button>
        ${weekStrip(sessDate && days(D.today, sessDate) < 7 && dObj(sessDate).getDay() !== 1 || !sessDate ? D.today : (days(D.today, sessDate) < 7 ? D.today : sessDate))}
      </section>` : `<section class="card rise"><p class="show t-m">Bloc ${activeBloc()} terminé</p><p class="muted small" style="margin-top:6px">La prochaine séance apparaîtra dès que ton coach remplira le bloc suivant.</p>${weekStrip(D.today)}</section>`)
      : `<section class="card rise"><div class="row"><span class="muted">${esc(seanceErr) || "Chargement de ta prog…"}</span>${seanceErr ? "" : `<div class="spin"></div>`}</div></section>`}

    <section class="card rise" style="margin-top:12px" aria-label="Total">
      <button style="display:block;width:100%" data-act="tab" data-t="prog" aria-label="Voir ma progression">
        <div class="ringwrap">${ring.svg}<div class="ctr"><p class="eyebrow">Total ${muOn() ? "All-4" : "sans MU"}</p><p class="show" style="font-size:64px;font-weight:900;line-height:.95">${fmt(t)}</p><p class="muted small" style="margin-top:2px">sur ${fmt(ring.tgt)} kg visés</p></div></div>
      </button>
      <div class="stats3"><div><p class="muted tiny">RIS</p><b>${fmt(r, 1)}</b></div><div><p class="muted tiny">Réaliste ${dmon(objDate())}</p><b>${bands.length ? fmt(sum(bands.map(x => x.lo)), 0) + "–" + fmt(sum(bands.map(x => x.hi)), 0) : "–"}</b></div><div><p class="muted tiny">Catégorie</p><b>${cat() > 0 ? "+" + cat() : "−" + Math.abs(cat())}</b></div></div>
    </section>

    <div class="tiles rise" style="margin-top:12px">
      ${nc ? `<button class="tile" data-act="tab" data-t="agenda"><p class="muted small">${esc(nc.nom)}${nc.tbc ? " · à confirmer" : ""}</p><p class="show">J−${days(D.today, nc.date)}</p><p class="muted small" style="margin-top:6px">${cap(dlong(nc.date))}</p></button>`
           : `<button class="tile" data-act="tab" data-t="agenda"><p class="muted small">Compétition</p><p class="show" style="font-size:28px">Aucune</p><p class="muted small" style="margin-top:6px">Ajoute ta prochaine</p></button>`}
      <div class="tile"><p class="muted small">${weighed ? "Poids · ce matin" : "Pesée du jour"}</p>
        ${weighed ? `<p class="show">${fmt(pw.poids, 1)}<span class="unit">kg</span></p><p class="small" style="margin-top:6px;color:${catLimit() && pw.poids > catLimit() ? "var(--bad)" : "var(--ok)"}">${catLimit() ? (pw.poids <= catLimit() ? fmt(catLimit() - pw.poids, 1) + " kg sous la limite" : fmt(pw.poids - catLimit(), 1) + " kg au-dessus") : ""}</p>`
          : `<div class="stepper"><button data-act="stepW" data-d="-0.1" aria-label="Moins 100 g">−</button><input id="hw" inputmode="decimal" value="${pw ? fmt(pw.poids, 1) : ""}" aria-label="Poids en kg"><button data-act="stepW" data-d="0.1" aria-label="Plus 100 g">+</button></div>
             <button class="btn sm" style="width:100%;margin-top:8px" data-act="saveW" data-src="hw">Enregistrer</button>`}
      </div>
    </div>
    ${bil ? `<section class="card rise" style="margin-top:12px"><p class="eyebrow">Pour ton coach</p><p class="show t-s" style="margin-top:6px">Bilan de la semaine ${esc(bil.semaine)}</p><p class="muted small" style="margin:4px 0 12px">Sommeil, fatigue, motivation… en 30 secondes.</p><button class="btn ghost" data-act="bilan" data-w="${esc(bil.sheet + "|" + bil.semaine)}">Faire le bilan</button></section>` : ""}
    ${ins ? `<div class="insight rise"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--chalk)" stroke-width="2" stroke-linecap="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/></svg><p>${ins}</p></div>` : ""}`;
  firstPaint = false;
}
'''
cut("function rHome(){", "/* =====================================================================\n   ONGLET SÉANCE", HOME + "\n")
# la semaine affichée : celle de la séance si elle tombe la semaine suivante
rep("""${weekStrip(sessDate && days(D.today, sessDate) < 7 && dObj(sessDate).getDay() !== 1 || !sessDate ? D.today : (days(D.today, sessDate) < 7 ? D.today : sessDate))}""",
    """${weekStrip(sessDate && sessDate > addDays(D.today, 6 - (dObj(D.today).getDay() + 6) % 7) ? sessDate : D.today)}""")

# ---------------------------------------------------------------- 3. Séance en direct
LIVE = r'''function rLive(){
  const s = seanceByKey(live.key); if (!s) { live = null; return ""; }
  const k = live.i, e = s.exercices[k], st = live.rows[k], l = liftOf(e.mouvement), renfo = norm(e.mouvement) === "RENFO", col = l ? LCOL[l] : "var(--chalk)";
  const prev = prevRowSets(s, k), nx = s.exercices[k + 1], nl = nx ? liftOf(nx.mouvement) : null;
  const el = Math.floor((Date.now() - live.start) / 60000), doneN = st.sets.filter(x => x.done).length, curJ = st.sets.findIndex(x => !x.done);
  const showR1 = !renfo && s.cols.rpe1 && st.sets[0] && st.sets[0].done, showRL = !renfo && s.cols.rpeLast && st.sets.length > 1 && st.sets.at(-1).done;
  const isBW = l && BW_LIFTS.includes(l), name = renfo ? title(e.variation) : l ? LNAME[l] + " " + title(e.variation).toLowerCase() : title(e.mouvement);
  const pv = j => { if (!prev) return "–"; const p = prev.sets[Math.min(j, prev.sets.length - 1)]; return p ? fmt(p.c) + " × " + p.r : "–"; };
  const rpeRow = (f, lab) => `<div class="card" style="margin-top:12px"><div class="row"><p style="font-weight:700">${lab}</p><p class="muted tiny">envoyé au coach</p></div><div class="rpe">${RPE_OPTS.map(v => `<button aria-pressed="${st[f] === v}" data-act="rpe" data-f="${f}" data-v="${v}">${fmt(v)}</button>`).join("")}</div></div>`;
  return `<div class="live ${sheet === "rest" ? "resting" : ""}" role="dialog" aria-label="Séance en cours"><div class="wrap">
    <div class="livehead"><button class="iconbtn" data-act="closeLive" aria-label="Fermer la séance"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
      <div style="text-align:center"><p class="small" style="font-weight:700">${esc(s.seance)}</p><p class="muted tiny">${el} min · exercice ${k + 1} sur ${s.exercices.length}</p></div>
      <button class="endbtn" data-act="finishLive">Terminer</button></div>
    <div class="live-progress">${s.exercices.map((x, j) => { const lj = liftOf(x.mouvement), dn = live.rows[j] && live.rows[j].sets.some(z => z.done);
      return `<i class="${j === k ? "cur" : dn ? "on" : ""}" style="--c:${lj ? LCOL[lj] : "var(--dust)"}"></i>`; }).join("")}</div>
    <p class="eyebrow" style="color:${l ? `color-mix(in srgb,${col} 70%,#fff)` : "var(--dust)"}">${renfo ? "Renforcement" : esc(LNAME[l] || title(e.mouvement))}${e.tempo ? " · tempo " + esc(e.tempo) : ""}</p>
    <h1 class="show" style="font-size:40px;font-weight:900;margin-top:4px;line-height:.95">${esc(name)}</h1>
    <p class="muted small" style="margin-top:8px">${presc(e)}${e.intensite ? ", " + esc(e.intensite) : ""}${prev ? ` · la dernière fois${prev.date ? " (" + dshort(prev.date) + ")" : ""} : ${esc(fmtSets(prev.sets))}` : ""}</p>
    ${e.coach ? `<div class="coachnote"><b>Consigne du coach.</b> ${esc(e.coach)}</div>` : ""}
    ${e.angle ? `<p class="prev">À filmer : ${esc(e.angle)}</p>` : ""}
    <section class="setgrid" style="--c:${col}" aria-label="Séries">
      <div class="hd"><span>Série</span><span>Précédent</span><span>${isBW ? "Lest" : "Kg"}</span><span>Reps</span><span></span></div>
      ${st.sets.map((x, j) => `<div class="setrow ${x.done ? "done" : ""} ${j === curJ ? "cur" : ""}"><span class="n">${j + 1}</span><span class="pv">${pv(j)}</span>
        <input inputmode="decimal" value="${x.c === null || x.c === undefined ? "" : String(x.c).replace(".", ",")}" placeholder="${isBW ? "0" : "kg"}" data-chg="setC" data-j="${j}" aria-label="${isBW ? "Lest" : "Charge"} série ${j + 1}">
        <input inputmode="numeric" value="${x.r ?? ""}" placeholder="–" data-chg="setR" data-j="${j}" aria-label="Reps série ${j + 1}">
        <button class="ck" data-act="doneSet" data-j="${j}" aria-label="Série ${j + 1} faite" aria-pressed="${x.done}"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5 9-10"/></svg></button></div>`).join("")}
      <div class="row" style="padding:8px 10px 4px"><button class="link small" data-act="addSet">+ Ajouter une série</button>${st.sets.length > 1 ? `<button class="link small muted" data-act="delSet">Retirer la dernière</button>` : ""}</div>
    </section>
    ${showR1 ? rpeRow("rpe1", "RPE de la 1re série") : ""}
    ${showRL ? rpeRow("rpeLast", "RPE de la dernière série") : ""}
    <div id="prbox"></div>
    ${nx ? `<div class="nextup"><span class="eyebrow" style="color:var(--faint)">Ensuite</span><span class="dot8" style="--c:${nl ? LCOL[nl] : "var(--faint)"}"></span><b>${esc(norm(nx.mouvement) === "RENFO" ? title(nx.variation) : (nl ? LNAME[nl] : title(nx.mouvement)) + " " + title(nx.variation).toLowerCase())}</b><span class="muted small">${esc(nx.series)} × ${esc(nx.reps)}</span></div>` : ""}
    <div class="grid2" style="margin-top:16px">
      <button class="btn ghost" data-act="liveNav" data-d="-1" ${k === 0 ? "disabled" : ""}>Précédent</button>
      ${k < s.exercices.length - 1 ? `<button class="btn" data-act="liveNav" data-d="1">Exercice suivant</button>` : `<button class="btn" data-act="finishLive">Terminer</button>`}
    </div>
    <p class="muted tiny" style="text-align:center;margin-top:12px">${doneN}/${st.sets.length} séries faites. Tout est enregistré quand tu changes d'exercice.</p>
  </div></div>`;
}
'''
cut("function rLive(){", "function prevRowSets(s, k){", LIVE)
rep("""const tr = document.querySelectorAll(".sets tbody tr")[j];""", """const tr = document.querySelectorAll(".setrow")[j];""")
# Chrono : pastille flottante au lieu d'une feuille plein écran
rep("""  if (sheet) h += `<div class="scrim" data-act="closeSheet"></div><div class="sheet" role="dialog"><div class="wrap"><div class="grab"></div>${rSheet()}</div></div>`;""",
"""  if (sheet === "rest") h += restPill();
  else if (sheet) h += `<div class="scrim" data-act="closeSheet"></div><div class="sheet" role="dialog"><div class="wrap"><div class="grab"></div>${rSheet()}</div></div>`;""")
rep("""function rSheet(){""", """function restPill(){
  return `<section id="restbox" class="restpill" role="timer" aria-label="Repos">
    <svg width="52" height="52" viewBox="0 0 54 54" aria-hidden="true" style="flex:none"><circle cx="27" cy="27" r="23" fill="none" stroke="rgba(11,12,15,.15)" stroke-width="5"/><circle id="restring" cx="27" cy="27" r="23" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" pathLength="628" stroke-dasharray="628" stroke-dashoffset="0" transform="rotate(-90 27 27)" style="transition:stroke-dashoffset .25s linear"/></svg>
    <div style="flex:1;min-width:0"><p class="small" style="font-weight:600;opacity:.7" id="resttitle">Repos</p><p class="show" id="restval">0:00</p></div>
    <button class="rb" data-act="restAdd" data-s="-15" aria-label="Retirer 15 secondes">−15</button><button class="rb" data-act="restAdd" data-s="15" aria-label="Ajouter 15 secondes">+15</button><button class="go2" data-act="closeSheet">Passer</button></section>`;
}
function rSheet(){""")

# ---------------------------------------------------------------- 4. Progrès : cartes des mouvements + double progression
rep("""    <h2 class="h2">Mouvements de compét</h2>
    <div class="list">${LIFTS.map(l => { const b = best(l), o = D.objectifs[l], h = liftSeries(l).map(p => p.v), v = verdictOf(l, o), lock = l === "MU" && !muOn();
      return `<button class="item" data-act="openLift" data-l="${l}"><span class="disc" style="--c:${LCOL[l]};width:16px;height:16px"></span><span class="grow"><span class="ttl" style="display:block">${LNAME[l]}</span>
        <span class="muted small">${lock ? "À débloquer" : o ? "Objectif " + fmt(o) + " kg" + (v ? ", " + v.txt.toLowerCase() : "") : "Pas encore d'objectif"}</span></span>
        ${lock ? "" : sparkSVG(h.slice(-12), getCss(LCOL[l]))}<span class="show t-s" style="width:64px;text-align:right">${lock || !b ? "—" : (l === "SQUAT" ? "" : "+") + fmt(b)}</span></button>`; }).join("")}</div>""",
"""    <h2 class="h2">Mouvements de compét</h2>
    <div class="liftgrid">${["PULL","DIP","SQUAT","MU"].map(l => { const b = best(l), o = D.objectifs[l], v = verdictOf(l, o), lock = l === "MU" && !muOn();
      if (lock) return `<button class="liftcard locked" data-act="openLift" data-l="${l}"><span class="row" style="justify-content:flex-start;gap:8px;font-weight:700;font-size:13px"><span class="dot8" style="--c:transparent;box-shadow:inset 0 0 0 2px var(--mu)"></span>${LNAME[l]}</span><span class="show" style="color:var(--faint)">—</span><span class="small" style="color:var(--steel-hi)">À débloquer. Active-le dès ton premier muscle-up.</span></button>`;
      return `<button class="liftcard" data-act="openLift" data-l="${l}"><span class="row" style="justify-content:flex-start;gap:8px;font-weight:700;font-size:13px"><span class="dot8" style="--c:${LCOL[l]};width:10px;height:10px"></span>${LNAME[l]}</span>
        <span class="show">${b ? (l === "SQUAT" ? "" : "+") + fmt(b) : "—"}</span>
        <span class="bar" style="--c:${LCOL[l]}"><i style="width:${o && b ? pct(b, o) : 0}%"></i></span>
        <span class="muted small">${o ? "Objectif " + fmt(o) + (v ? " · " + v.txt.toLowerCase() : "") : "Pas encore d'objectif"}</span></button>`; }).join("")}</div>
    ${dpHtml()}""")
rep("""function volumeWeeks(){""", r'''/* Double progression : pour chaque exercice de renfo du bloc en cours, où en est la dernière séance par rapport au haut de la fourchette. */
function dpData(){
  const ab = activeBloc(); if (ab === null) return [];
  const pres = {}; S.filter(z => z.bloc === ab).forEach(z => z.exercices.forEach(e => { if (norm(e.mouvement) === "RENFO") pres[exKey(e)] = e; }));
  return exercisePoints().filter(o => pres[o.key] && o.last && o.last.sets.length).map(o => {
    const e = pres[o.key], rr = (String(e.reps).match(/\d+/g) || []).map(Number); if (rr.length < 2) return null;
    const lo = Math.min(...rr), hi = Math.max(...rr), sets = o.last.sets, n = Math.max(num(e.series) || sets.length, sets.length);
    const reps = Array.from({length:n}, (_, i) => sets[i] ? sets[i].r : 0), full = reps.every(r => r >= hi), left = sum(reps.map(r => Math.max(0, hi - r)));
    return {key:o.key, c:o.last.charge, reps, lo, hi, full, left, date:o.last.date};
  }).filter(Boolean).sort((a, b) => (b.full - a.full) || (a.left - b.left));
}
function dpHtml(){
  const L = dpData(); if (!L.length) return "";
  return `<h2 class="h2">Renfo · double progression</h2>
    ${L.map(x => `<button class="card" style="display:block;width:100%;text-align:left" data-act="openEx" data-k="${esc(x.key)}">
      <div class="row"><b style="font-weight:700">${esc(exName(x.key))}</b><span class="tag ${x.full ? "ok" : ""}">${x.full ? "Monte la charge" : "Encore " + x.left + " rep" + (x.left > 1 ? "s" : "")}</span></div>
      <p class="muted small" style="margin-top:4px">${fmt(x.c)} kg · ${x.reps.filter(Boolean).join(" · ")} · fourchette ${x.lo} à ${x.hi}</p>
      <div class="dp ${x.full ? "full" : ""}" style="--n:${x.reps.length}">${x.reps.map(r => `<i><b style="width:${Math.min(100, r / x.hi * 100)}%"></b></i>`).join("")}</div></button>`).join("")}
    <p class="muted tiny" style="margin-top:8px">Chaque barre est une série, pleine au haut de la fourchette. Toutes pleines : tu montes la charge.</p>`;
}
function volumeWeeks(){''')
rep("""    <h2 class="h2">Exercices du bloc ${activeBloc() ?? ""}</h2>""", """    <h2 class="h2">Tous les exercices du bloc ${activeBloc() ?? ""}</h2>""")

# ---------------------------------------------------------------- 5. Fiche mouvement : en-tête, délais, records
rep("""    <p class="muted">${LNAME[l]}${BW_LIFTS.includes(l) ? ", lest" : ""}</p>
    <p class="show t-xl" id="liftbig" style="color:${LCOL[l]}">${lock ? "—" : fmt(b)}<span class="unit">kg</span></p>""",
"""    <p class="eyebrow" style="color:color-mix(in srgb,${LCOL[l]} 70%,#fff)">${LNAME[l]} · record perso</p>
    <p class="show" id="liftbig" style="font-size:88px;font-weight:900;line-height:.9;margin-top:4px">${lock ? "—" : (BW_LIFTS.includes(l) ? "+" : "") + fmt(b)}<span class="unit">kg</span></p>
    ${!lock && hist.length ? `<p class="muted small" style="margin-top:6px">${cap(dlong(D.prs.filter(p => p.lift === l && p.reps === 1).sort((a, c) => c.charge - a.charge)[0]?.date || hist[0].date))}${BW_LIFTS.includes(l) && bw() ? " · " + fmt(b + bw(), 1) + " kg avec ton poids de corps" : ""}</p>` : ""}""")
rep("""      ${v && mt ? `<div class="verdict" style="--vc:${v.c}"><span class="ic"></span><div><p><b>${v.txt}.</b> ${v.k === 0 ? "Tu y es déjà, remonte la barre." : `Il te faut +${fmt(o - b, 1)} kg.`}</p>
        ${v.k === 0 ? "" : `${mTr !== null ? `<p class="small" style="margin-top:6px">À ton rythme actuel : <b>${fmtMonths(mTr)}</b>, vers ${dmon(addMonths(D.today, mTr))}.</p>` : ""}
        <p class="small muted" style="margin-top:4px">Repère de l'étude : ${fmtMonths(mt.early)} à ${fmtMonths(mt.late)}.</p>`}</div></div>`""",
"""      ${v && mt ? `<div class="verdict" style="--vc:${v.c}"><span class="ic"></span><p><b>${v.txt}.</b> ${v.k === 0 ? "Tu y es déjà, remonte la barre." : `Il te faut +${fmt(o - b, 1)} kg.`}</p></div>
        ${v.k === 0 ? "" : `<div class="two"><div><p class="muted tiny">À ton rythme actuel</p><p class="show">${mTr !== null ? cap(dmon(addMonths(D.today, mTr))) : "–"}</p><p class="muted tiny" style="margin-top:4px">${tr && tr.parMois > 0 ? "+" + fmt(tr.parMois, 1) + " kg par mois" : "pas assez de données"}</p></div>
          <div><p class="muted tiny">Repère scientifique</p><p class="show">${mt.early > 120 ? "> 10 ans" : cap(dmon(addMonths(D.today, mt.early))) + (Math.abs(mt.late - mt.early) >= 1 ? "–" + (mt.late > 120 ? "…" : dmon(addMonths(D.today, mt.late))) : "")}</p><p class="muted tiny" style="margin-top:4px">+7,5 à 12,5 % la 1re année</p></div></div>
          <p class="muted tiny" style="margin-top:8px">Un rythme de débutant ralentit avec le temps : la date réaliste se situe entre les deux. Repère : Latella et al., 2023.</p>`}`""")
rep("""    <div class="panel">${[["Record de Belgique", nr], ["Record du monde", wr]].map(([lab, x]) => x ? `<div style="margin-bottom:14px"><div class="row"><span class="small">${lab}</span><b class="small" style="white-space:nowrap">${fmt(x.valeur)} kg</b></div><p class="muted tiny">${esc(x.detenteur)}</p>
      <div class="bar" style="margin-top:8px;--c:${LCOL[l]}"><i style="width:${pct(b, x.valeur)}%"></i></div><p class="muted tiny" style="margin-top:4px">${fmt(pct(b, x.valeur), 0)} %, écart ${fmt(x.valeur - (b || 0), 1)} kg</p></div>` : `<p class="muted small" style="margin-bottom:10px">${lab} : pas encore renseigné.</p>`).join("")}
      <p class="muted tiny">Les records situent le haut de la catégorie, pas un objectif à un an.</p></div>""",
"""    <div class="card">${(() => { const top = Math.max(b || 0, ...[nr, wr].filter(Boolean).map(x => x.valeur)) || 1;
      return `<div class="rec" style="margin-top:0"><div class="row"><b>Toi</b><b>${fmt(b)}</b></div><div class="bar" style="--c:${LCOL[l]}"><i style="width:${(b || 0) / top * 100}%"></i></div></div>`
        + [["Record de Belgique", nr], ["Record du monde", wr]].map(([lab, x]) => x ? `<div class="rec"><div class="row"><span>${lab} · ${esc(x.detenteur)}</span><span style="color:var(--steel-hi)">${fmt(x.valeur)}</span></div><div class="bar" style="--c:#5B5F67"><i style="width:${x.valeur / top * 100}%"></i></div></div>` : `<p class="muted small rec">${lab} : pas encore renseigné.</p>`).join(""); })()}
      <p class="muted tiny" style="margin-top:12px">Les records situent le haut de la catégorie, pas un objectif à un an.</p></div>""")

# Signature : la barre chargée disparaît de l'accueil (l'anneau la remplace) ; on garde la fonction pour la carte de partage.
P.write_text(s)
print("refonte appliquée")
