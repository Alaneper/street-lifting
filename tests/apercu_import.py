"""Maquettes de l'écran « Importer un programme » rendues à partir du VRAI résultat de src/prog_import.js.
Usage : python3 tests/apercu_import.py <dossier de sortie>   (n'utilise ni l'app ni les données de personne)"""
import json, pathlib, subprocess, sys, html
from playwright.sync_api import sync_playwright
H = pathlib.Path(__file__).resolve().parent; R = H.parent
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
CASES = [("P4", "programmes", "Musculation · push/pull/legs 6 jours", "notes de téléphone"),
         ("H3", "programmes_inedits", "Musculation · haut/bas 4 jours", "post Instagram en anglais"),
         ("P3", "programmes", "Street lifting · 4 séances", "message WhatsApp du coach"),
         ("P2", "programmes", "Powerlifting · bloc 6 semaines", "tableau Excel collé")]
js = """const {parseProgram,fmtGroup}=require(process.argv[1]);const fs=require('fs');
const out={};for(const [k,dir] of JSON.parse(process.argv[2])){const r=parseProgram(fs.readFileSync(process.argv[3]+'/'+dir+'/'+k+'.txt','utf8'));
r.weeks.forEach(w=>w.days.forEach(d=>d.exos.forEach(e=>e.fmt=e.groups.map(fmtGroup))));out[k]=r}console.log(JSON.stringify(out))"""
data = json.loads(subprocess.check_output(["node", "-e", js, str(R / "src/prog_import.js"), json.dumps([[c[0], c[1]] for c in CASES]), str(H / "fixtures")]))
COL = {"squat": "#F0524A", "bench": "#A78BFA", "deadlift": "#EC6FB0", "pull": "#4C8DF6", "dip": "#2BB673", "mu": "#E3B341", "": "#8E9198"}
CSS = """<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Barlow+Condensed:wght@600;700;800&display=swap" rel="stylesheet">
<style>*{box-sizing:border-box;margin:0}body{background:#0A0B0D;color:#fff;font-family:Barlow,-apple-system,"Segoe UI",sans-serif;width:390px;padding:58px 16px 40px}
.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}.back{color:#8A9099;font-size:15px}.ttl{font-weight:700;font-size:17px}
.hero{background:#1F5FD0;border-radius:24px;padding:18px 18px 16px;margin-bottom:12px}.hero small{opacity:.85;font-size:13px}.hero h1{font-family:"Barlow Condensed","Arial Narrow",sans-serif;font-size:30px;line-height:1;margin:6px 0 8px}
.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{background:rgba(255,255,255,.16);border-radius:999px;padding:5px 10px;font-size:12px;font-weight:600}
.ok{background:rgba(43,182,115,.25)}.warnc{background:rgba(227,179,65,.25)}
.src{color:#8A9099;font-size:12.5px;margin:2px 2px 14px}.tabs{display:flex;gap:6px;overflow:hidden;margin-bottom:12px}.tab{background:#1F2227;border-radius:999px;padding:7px 13px;font-size:13px;font-weight:600;color:#B4BAC2;white-space:nowrap}.tab.on{background:#fff;color:#0A0B0D}
.day{background:#16181C;border-radius:16px;padding:14px 14px 6px;margin-bottom:10px}.dh{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}.dh b{font-size:16px}.dh span{color:#8A9099;font-size:12.5px}
.ex{display:flex;gap:10px;padding:9px 0;border-top:1px solid #1C1F24}.ex:first-of-type{border-top:0}.dot{width:9px;height:9px;border-radius:50%;margin-top:6px;flex:none}.exn{font-weight:600;font-size:15px}
.raw{color:#7D838C;font-size:11.5px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:300px}.sets{display:flex;gap:5px;flex-wrap:wrap;margin-top:5px}.set{background:#1F2227;border-radius:8px;padding:3px 8px;font-size:12.5px;font-weight:600;font-variant-numeric:tabular-nums}
.tag{font-size:11px;color:#E3B341;margin-left:6px;font-weight:600}.note{background:#16181C;border-radius:12px;padding:10px 12px;font-size:12.5px;color:#B4BAC2;margin:8px 0}.note b{color:#fff}
.btns{display:flex;gap:8px;margin-top:14px}.btn{flex:1;text-align:center;border-radius:14px;padding:13px;font-weight:700;font-size:15px}.b1{background:#1F2227;color:#fff}.b2{background:#fff;color:#0A0B0D}
.row{display:flex;justify-content:space-between;align-items:center;padding:8px 2px;border-bottom:1px solid #1C1F24}.row .exn{font-size:14px}.row .set{background:none;color:#B4BAC2;padding:0}.sec{color:#8A9099;font-size:11.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin:16px 2px 4px}
</style>"""
e = html.escape
def page(k, title, src, variant="A"):
    r = data[k]; st = r["stats"]; w = r["weeks"][0]
    days = [d for d in w["days"] if d["exos"]]
    unk = st["exos"] - st["recognized"]
    h = [CSS, f"<div class=top><span class=back>‹ Annuler</span><span class=ttl>Importer un programme</span><span style='width:52px'></span></div>"]
    h.append(f"<div class=hero><small>Aperçu · vérifie avant d'enregistrer</small><h1>{e(title)}</h1><div class=chips>"
             f"<span class=chip>{st['weeks']} semaine{'s' if st['weeks'] > 1 else ''}</span><span class=chip>{len(days)} jours</span><span class=chip>{st['exos']} exercices</span>"
             f"<span class='chip {'ok' if not unk else 'warnc'}'>{st['recognized']}/{st['exos']} reconnus</span></div></div>")
    h.append(f"<div class=src>Collé depuis : {e(src)} · rien n'est enregistré tant que tu ne valides pas.</div>")
    if len(r["weeks"]) > 1: h.append("<div class=tabs>" + "".join(f"<span class='tab{' on' if i == 0 else ''}'>{e(x['label'])}</span>" for i, x in enumerate(r["weeks"][:5])) + "</div>")
    if variant == "A":
        for d in days[:4]:
            h.append(f"<div class=day><div class=dh><b>{e(d['label'])}</b><span>{e(d.get('sub') or '')} · {len(d['exos'])} exos</span></div>")
            for x in d["exos"][:7]:
                nm = x["canon"] or x["name"]; tag = "" if x["canon"] else "<span class=tag>à vérifier</span>"
                extra = [f"RPE {x['rpe']}"] if x.get("rpe") else []
                h.append(f"<div class=ex><span class=dot style='background:{COL.get(x['cat'], '#8E9198')}'></span><div><div class=exn>{e(nm)}{tag}</div>"
                         f"<div class=sets>{''.join(f'<span class=set>{e(s)}</span>' for s in x['fmt'] + extra)}</div><div class=raw>« {e(x['raw'][:70])} »</div></div></div>")
            h.append("</div>")
        if len(days) > 4: h.append(f"<div class=src>+ {len(days) - 4} autres jours…</div>")
    else:
        for d in days[:4]:
            h.append(f"<div class=sec>{e(d['label'])} {('· ' + e(d['sub'])) if d.get('sub') else ''}</div>")
            for x in d["exos"][:7]:
                h.append(f"<div class=row><span class=exn><span class=dot style='display:inline-block;margin:0 8px 1px 0;background:{COL.get(x['cat'], '#8E9198')}'></span>{e(x['canon'] or x['name'])}</span><span class=set>{e(' + '.join(x['fmt']))}</span></div>")
    notes = r["notes"][:3]
    if notes: h.append("<div class=note><b>Remarques gardées</b><br>" + "<br>".join(e(n[:90]) for n in notes) + "</div>")
    h.append("<div class=btns><span class='btn b1'>Corriger</span><span class='btn b2'>Enregistrer</span></div>")
    return "".join(h)

with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    shots = []
    for k, _, title, src in CASES:
        pg.set_content(page(k, title, src)); pg.wait_for_timeout(600); f = OUT / f"import-{k}.png"; pg.screenshot(path=str(f), full_page=True); shots.append(f)
    k, _, title, src = CASES[0]
    pg.set_content(page(k, title, src, "B")); pg.wait_for_timeout(600); pg.screenshot(path=str(OUT / f"import-{k}-B.png"), full_page=True)
    br.close()
print("\n".join(map(str, shots)))
