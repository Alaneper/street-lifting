"""Lot C (niveau 8,5) : planche-échantillon des silhouettes musculaires, NON appliquée à l'app.
Un seul jeu de formes SVG (sprite <symbol>) réutilisé par <use> ; l'intensité passe par des variables CSS (--m1 principal, --m2 secondaire).
Usage : python3 tools/lotC_planche.py <sortie.png> [sortie_poids.json]"""
import sys, json, re, subprocess, pathlib
from playwright.sync_api import sync_playwright
P = pathlib.Path(__file__).resolve().parent.parent
js = (P / "src" / "muscles.js").read_text(encoding="utf-8")
node = "const MUSCLE_SVG=" + js[js.index("const MUSCLE_SVG = ") + 19:js.index(";\nconst MUSCLE_MAP")] + ";console.log(JSON.stringify(MUSCLE_SVG))"
SVG = json.loads(subprocess.run(["node", "-e", node], capture_output=True, text=True, check=True).stdout)
MAP = {"SQUAT": {"quadriceps":1,"fessiers":1,"ischios":2,"lombaires":2,"abdos":2,"adducteurs":2,"mollets":2,"mollets_d":2}, "DEADLIFT": {"ischios":1,"fessiers":1,"lombaires":1,"dorsaux":1,"trapeze_d":2,"quadriceps":2,"avant_bras":2}}
NAMES = sorted({m for v in SVG.values() for m in re.findall(r'class="m ([a-z_]+)', v)})
def symbol(view):
    inner = re.sub(r'^<svg[^>]*>|</svg>$', '', SVG[view])
    return f'<symbol id="mf-{view}" viewBox="0 0 300 722">{inner}</symbol>'
SPRITE = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + symbol("front") + symbol("back") + '</defs></svg>'
CSS = """
:root{--floor:#0C0B0A;--deck:#1B1A18;--deck2:#272522;--deck3:#363330;--chalk:#F5F2EC;--dust:#B4AFA7;--faint:#8A857D;--acc:#FF4A2B;--f:"Helvetica Neue",Arial,sans-serif}
/* ---- silhouette nouvelle génération : directement sur la carte, sans plaque claire. Les règles visent le contenu du <symbol> (un <use> ne voit pas les ancêtres de l'instance) ; seules les variables CSS traversent. ---- */
.mf{display:block;height:var(--h);width:auto;aspect-ratio:300/722;--base:#3A3733;--base2:#33302C;--m1:var(--acc);--m2:#9A3E2D;--sep:rgba(12,11,10,.55);--olc:rgba(245,242,236,.20);--fib:.0}
symbol .sk{fill:#2E2B28;stroke:none}symbol .ol{fill:none;stroke:var(--olc);stroke-width:1.4;stroke-linejoin:round}
symbol .m .b{fill:var(--c,var(--base));stroke:var(--sep);stroke-width:var(--sw,1.2);stroke-linejoin:round}
symbol .m.dk .b{fill:color-mix(in srgb,var(--c,var(--base)) 80%,#000)}
symbol .m .f{fill:none;stroke:rgba(0,0,0,.35);stroke-width:1;opacity:var(--fib);stroke-linecap:round}
.mf.L{--sw:1.4;--fib:.55}.mf.M{--sw:1;--fib:0;--olc:rgba(245,242,236,.14)}.mf.S{--sw:0;--fib:0;--olc:transparent;--sep:transparent}
"""
CSS += "".join(f"symbol .m.{n}{{--c:var(--mc-{n},var(--base))}}" for n in NAMES)
def fig(view, lift, cls, h, level=None):
    mp = MAP[lift]; st = []
    for k, v in mp.items():
        if k in NAMES and (level is None or v == level): st.append(f"--mc-{k}:var(--m{v})")
    return f'<svg class="mf {cls}" style="--h:{h}px;{";".join(st)}" role="img" aria-label="Muscles sollicités"><use href="#mf-{view}"/></svg>'
def cell(title, body, sub=""):
    return f'<div class="cell"><div class="ct">{title}</div><div class="cb">{body}</div><div class="cs">{sub}</div></div>'
sections = []
for view, lift, nom in (("front", "SQUAT", "Face · Squat"), ("back", "DEADLIFT", "Dos · Soulevé de terre")):
    row = []
    # grande : fiche de mouvement (deux vues sur la carte)
    big = lambda lv: fig("front", lift, "L", 190, lv) + fig("back", lift, "L", 190, lv)
    row.append(cell("Grande · fiche", f'<div class="card" style="gap:6px">{fig(view, lift, "L", 210)}{fig("back" if view == "front" else "front", lift, "L", 210)}</div>', "deux vues, 210 px de haut, séparations fines"))
    row.append(cell("Principal seul", f'<div class="card">{fig(view, lift, "L", 210, 1)}</div>', "rouge plein"))
    row.append(cell("Secondaire seul", f'<div class="card">{fig(view, lift, "L", 210, 2)}</div>', "rouge atténué"))
    # moyenne : séance du jour (carte héros)
    row.append(cell("Moyenne · séance du jour", f'<div class="card hero"><div class="ht">Force · bas du corps<br><small>Objectif 150 × 3</small></div><div class="hf">{fig("front", lift, "M", 112)}{fig("back", lift, "M", 112)}</div></div>', "112 px, sans fibres, sans plaque claire"))
    # petite : listes
    small = f'<div class="lrow">{fig(view, lift, "S", 40)}<div><b>{"Squat" if lift == "SQUAT" else "Soulevé de terre"}</b><span>5 × 3 · RPE 8</span></div><i>150 kg</i></div>'
    small += f'<div class="lrow">{fig(view, "DEADLIFT" if lift == "SQUAT" else "SQUAT", "S", 40)}<div><b>{"Soulevé roumain" if lift == "SQUAT" else "Squat"}</b><span>3 × 8 · RPE 7</span></div><i>110 kg</i></div>'
    row.append(cell("Petite · liste", f'<div class="card list">{small}</div>', "40 px, une vue, formes pleines seulement"))
    sections.append(f'<h2>{nom}</h2><div class="row">{"".join(row)}</div>')
HTML = f"""<!doctype html><meta charset=utf-8><style>{CSS}
body{{margin:0;background:var(--floor);color:var(--chalk);font:14px/1.3 var(--f);padding:28px 32px 36px;width:1500px}}
h1{{font:800 26px var(--f);margin:0 0 4px}}h1+p{{color:var(--dust);margin:0 0 20px}}h2{{font:700 17px var(--f);margin:22px 0 10px;color:var(--dust);letter-spacing:.04em;text-transform:uppercase}}
.row{{display:flex;gap:18px;align-items:flex-start}}.cell{{flex:none}}.ct{{font:700 13px var(--f);margin-bottom:6px}}.cs{{font:500 12px var(--f);color:var(--faint);margin-top:6px;max-width:260px}}
.card{{background:var(--deck);border-radius:20px;padding:16px 18px;display:flex;align-items:center;justify-content:center;gap:10px;box-shadow:inset 0 1px 0 rgba(245,242,236,.10),0 6px 18px rgba(0,0,0,.4)}}
.card.hero{{width:300px;justify-content:space-between;padding:16px 0 16px 18px;overflow:hidden;position:relative;background:linear-gradient(180deg,#232120,var(--deck))}}.ht{{font:800 22px/1.1 var(--f)}}.ht small{{font:500 12px var(--f);color:#FF8A73}}.hf{{display:flex;gap:2px;align-self:flex-start;margin-right:10px}}
.card.list{{flex-direction:column;align-items:stretch;width:300px;padding:6px 14px;gap:0}}.lrow{{display:flex;align-items:center;gap:12px;padding:8px 0}}.lrow+.lrow{{border-top:1px solid #24221F}}.lrow>div{{flex:1}}.lrow b{{display:block;font:700 15px var(--f)}}.lrow span{{font:500 12px var(--f);color:var(--dust)}}.lrow i{{font:800 18px var(--f);font-style:normal}}
.lrow .mf{{background:var(--deck2);border-radius:10px;padding:4px 6px;box-sizing:content-box}}
.leg{{display:flex;gap:18px;margin:6px 0 4px;color:var(--dust);font:500 13px var(--f)}}.leg i{{display:inline-block;width:14px;height:14px;border-radius:4px;vertical-align:-2px;margin-right:6px}}
</style>{SPRITE}
<h1>Silhouettes musculaires · planche-échantillon</h1><p>Proposition non appliquée. Même anatomie qu'aujourd'hui, nouveau rendu : pas de plaque claire, un seul jeu de formes réutilisé, niveau de détail selon la taille.</p>
<div class="leg"><span><i style="background:#FF4A2B"></i>Principal</span><span><i style="background:#9A3E2D"></i>Secondaire</span><span><i style="background:#3A3733"></i>Non sollicité</span></div>
{''.join(sections)}"""
out = pathlib.Path(sys.argv[1])
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1564, "height": 800}, device_scale_factor=2)
    pg.set_content(HTML); pg.wait_for_timeout(500); pg.screenshot(path=str(out), full_page=True)
    sprite_bytes = len(SPRITE.encode()); inst = pg.evaluate("document.querySelector('.mf').outerHTML.length")
    br.close()
if len(sys.argv) > 2: pathlib.Path(sys.argv[2]).write_text(json.dumps({"sprite_octets": sprite_bytes, "instance_octets": inst, "anciennes_vues_octets": {k: len(v) for k, v in SVG.items()}}, indent=1))
print("sprite", sprite_bytes, "instance", inst)
