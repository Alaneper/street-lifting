"""Maquettes du parcours « Ajouter mon programme » (écran d'ajout + aperçu A + aperçu B), rendues avec le vrai résultat de src/prog_import.js,
dans le cadre d'un iPhone (barre d'état simulée). Usage : python3 tests/maquettes_import.py <dossier de sortie>"""
import sys, pathlib, html as _h
H = pathlib.Path(__file__).resolve().parent
src = (H / "apercu_import.py").read_text()
exec(src[:src.index("with sync_playwright()")])           # définit data, page, CSS, COL, CASES, OUT
from PIL import Image, ImageDraw, ImageFont
m = (H / "mockups.py").read_text()
exec(m[m.index("FONT ="):m.index("def board")])             # définit FONT, statusbar

STEPS = CSS + """<style>.stp{display:flex;gap:6px;align-items:center;margin:0 0 14px}.stp i{font-style:normal;width:26px;height:26px;border-radius:50%;background:#1F2227;color:#8A9099;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700}.stp i.on{background:#1F5FD0;color:#fff}.stp i.done{background:#2BB673;color:#0A0B0D}.stp u{flex:1;height:2px;background:#1F2227;text-decoration:none}.stp span{margin-left:8px;font-size:13px;color:#B4BAC2;font-weight:600}
.card{background:#16181C;border-radius:16px;padding:14px;margin-bottom:12px}.lab{font-size:13px;color:#8A9099;margin-bottom:8px;font-weight:600}
.ta{background:#0F1114;border:1px solid #2A2E34;border-radius:12px;padding:12px;font-size:13.5px;line-height:1.45;color:#B4BAC2;height:230px;overflow:hidden;white-space:pre-wrap;font-family:Barlow,sans-serif}
.opt{display:flex;align-items:center;gap:12px;background:#16181C;border-radius:16px;padding:14px;margin-bottom:10px}.ic{width:40px;height:40px;border-radius:12px;background:#1F2227;display:flex;align-items:center;justify-content:center;font-size:18px}
.opt b{font-size:15px}.opt small{display:block;color:#8A9099;font-size:12.5px;margin-top:2px}.soon{opacity:.45}.pill{margin-left:auto;font-size:11px;background:#2A2E34;border-radius:999px;padding:3px 8px;color:#B4BAC2}
.big{background:#fff;color:#0A0B0D;border-radius:14px;padding:14px;text-align:center;font-weight:700;font-size:16px;margin-top:6px}.hint{color:#7D838C;font-size:12px;margin-top:10px;text-align:center}
.pen{margin-left:auto;color:#8A9099;font-size:15px;align-self:center;padding-left:8px}.ex .pen{margin-top:0}.row .pen{padding-left:10px}
.tip{background:#16181C;border-left:3px solid #E3B341;border-radius:10px;padding:10px 12px;font-size:13px;color:#B4BAC2;margin-bottom:12px}
.ok1{width:72px;height:72px;border-radius:50%;background:#2BB673;color:#0A0B0D;display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:800;margin:30px auto 14px}
.c3{text-align:center}.c3 h2{font-family:"Barlow Condensed","Arial Narrow",sans-serif;font-size:32px;margin-bottom:6px}.c3 p{color:#8A9099;font-size:14px;margin-bottom:16px}
.sum{background:#16181C;border-radius:16px;padding:6px 14px;text-align:left;margin:14px 0}.sum div{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #1C1F24;font-size:14px}.sum div:last-child{border:0}.sum b{font-variant-numeric:tabular-nums}</style>"""
def stepper(n, label):
    dots = "".join(f"<i class='{'done' if i < n else 'on' if i == n else ''}'>{'✓' if i < n else i}</i>" + ("<u></u>" if i < 3 else "") for i in (1, 2, 3))
    return f"<div class=stp>{dots}<span>{label}</span></div>"
SAMPLE = _h.escape("LUNDI PUSH\ndc 4x6 80kg\nincl halt 3x10\ndips lest 4x8 +20\ntriceps poulie 3x12\n\nMARDI PULL\ntractions lestées 4x5 +15\nrowing barre 4x8 85\nface pull 3x15\n\nJEUDI LEGS\nsquat 5x5 120\npresse 4x12\nmollets 5x12")
entry = (STEPS + stepper(1, "Je colle mon programme") + "<div class=top><span class=back>‹ Retour</span><span class=ttl>Ajouter mon programme</span><span style='width:52px'></span></div>"
         "<div class=src style='margin:0 2px 12px'>Colle ton programme tel qu'il est : notes, message du coach, tableau. À l'étape suivante, tu verras ce que l'app a compris avant d'enregistrer quoi que ce soit.</div>"
         f"<div class=card><div class=lab>Colle ton texte ici</div><div class=ta>{SAMPLE}</div><div class=big>Analyser →</div></div>"
         "<div class=opt><div class=ic>📄</div><div><b>Importer un fichier</b><small>Excel (.xlsx) ou CSV depuis ton téléphone</small></div></div>"
         "<div class=opt><div class=ic>🔗</div><div><b>Lien Google Sheet</b><small>Comme le programme de ton coach</small></div></div>"
         "<div class='opt soon'><div class=ic>📷</div><div><b>Photo ou PDF</b><small>Lecture par IA, plus tard</small></div><span class=pill>bientôt</span></div>"
         "<div class=hint>Ton texte reste sur ton téléphone : rien n'est envoyé.</div>")
def prev(variant):
    h = page("P4", "Musculation · push/pull/legs", "tes notes", variant)
    h = h.replace(CSS, STEPS, 1)
    h = h.replace("<div class=top>", stepper(2, "Je vérifie ce que l'app a compris") + "<div class=top>", 1)
    h = h.replace("Aperçu · vérifie avant d'enregistrer", "Voilà ce que j'ai compris de ton texte")
    h = h.replace("<span class=ttl>Importer un programme</span>", "<span class=ttl>Vérifier mon programme</span>")
    h = h.replace("<span class=back>‹ Annuler</span>", "<span class=back>‹ Modifier le texte</span>")
    h = h.replace("Collé depuis : tes notes · rien n'est enregistré tant que tu ne valides pas.", "<div class=tip>Rien n'est enregistré pour l'instant. Touche <b>✎</b> pour corriger un exercice, une série ou une charge.</div>")
    h = h.replace("</span></div></div></div><div class=ex>", "</span></div></div><span class=pen>✎</span></div><div class=ex>")
    import re
    h = re.sub(r"(<div class=raw>.*?</div></div>)(</div>)", r"\1<span class=pen>✎</span>\2", h) if variant == "A" else re.sub(r"(<span class=set>[^<]*</span>)(</div>)", r"\1<span class=pen>✎</span>\2", h)
    h = h.replace("<span class='btn b2'>Enregistrer</span>", "<span class='btn b2'>Enregistrer ✓</span>").replace("<span class='btn b1'>Corriger</span>", "<span class='btn b1'>‹ Retour</span>")
    h = re.sub(r"<div class=btns>.*?</div></div>$", "", h, flags=re.S) if False else h
    i = h.rfind("<div class=btns>"); h = h[:i] if i > 0 else h
    h = h.replace("</style>", ".ex>div:not(.dot){flex:1;min-width:0}.row>.exn{flex:1}.bar{position:fixed;left:0;right:0;bottom:0;padding:14px 16px 40px;background:linear-gradient(180deg,rgba(10,11,13,0),#0A0B0D 35%);display:flex;gap:8px}</style>", 1)
    h += "<div class=bar><span class='btn b1'>‹ Retour</span><span class='btn b2'>Enregistrer ✓</span></div>"
    return h
done = (STEPS + stepper(3, "C'est enregistré") + "<div class=c3><div class=ok1>✓</div><h2>Programme ajouté</h2><p>Tu le retrouves dans l'onglet Prog, comme celui de ton coach.</p></div>"
        "<div class=sum><div><span>Programme</span><b>Push / Pull / Legs</b></div><div><span>Jours</span><b>3</b></div><div><span>Exercices</span><b>22</b></div><div><span>Reconnus</span><b>22 / 22</b></div></div>"
        "<div class=btns><span class='btn b1'>Voir le programme</span><span class='btn b2'>Commencer une séance</span></div>")
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    shots = {}
    for name, h in (("1", entry), ("2A", prev("A")), ("2B", prev("B")), ("3", done)):
        pg.set_content(h); pg.wait_for_timeout(700); f = OUT / f"ecran-{name}.png"
        pg.screenshot(path=str(f), clip={"x": 0, "y": 0, "width": 390, "height": 844}); statusbar(f); shots[name] = f
    br.close()
def flow(second, title, out):
    ims = [Image.open(shots[k]) for k in ("1", second, "3")]; w, h = ims[0].size; pad, gap, top, bot = 50, 110, 150, 150
    B_ = Image.new("RGB", (3 * w + 2 * gap + 2 * pad, h + top + bot), "#1a1b1e"); d = ImageDraw.Draw(B_)
    F = lambda n: ImageFont.truetype(FONT, n)
    d.text((pad, 34), title, fill="white", font=F(40))
    caps = [("① Je colle mon programme", "Tu donnes tes notes, ton Excel ou ton lien."), ("② Je vérifie ce que l'app a compris", "Tu corriges ce qui est faux (✎), puis tu valides."), ("③ C'est enregistré", "Le programme apparaît dans l'onglet Prog.")]
    for i, (im, (t, sub)) in enumerate(zip(ims, caps)):
        x = pad + i * (w + gap); B_.paste(im, (x, top)); d.text((x, top + h + 24), t, fill="white", font=F(30)); d.text((x, top + h + 70), sub, fill="#B4BAC2", font=F(24))
        if i < 2: d.text((x + w + 28, top + h // 2 - 40), "→", fill="#1F5FD0", font=F(80))
    B_.save(out); return out
print(flow("2A", "Option A · l'étape 2 en cartes (une carte par jour)", OUT / "parcours-A.png"))
print(flow("2B", "Option B · l'étape 2 en liste compacte", OUT / "parcours-B.png"))
