"""Maquettes du parcours « Ajouter mon programme » (écran d'ajout + aperçu A + aperçu B), rendues avec le vrai résultat de src/prog_import.js,
dans le cadre d'un iPhone (barre d'état simulée). Usage : python3 tests/maquettes_import.py <dossier de sortie>"""
import sys, pathlib, html as _h
H = pathlib.Path(__file__).resolve().parent
src = (H / "apercu_import.py").read_text()
exec(src[:src.index("with sync_playwright()")])           # définit data, page, CSS, COL, CASES, OUT
from PIL import Image, ImageDraw, ImageFont
m = (H / "mockups.py").read_text()
exec(m[m.index("FONT ="):m.index("def board")])             # définit FONT, statusbar

ENTRY = CSS + """<style>.card{background:#16181C;border-radius:16px;padding:14px;margin-bottom:12px}.lab{font-size:13px;color:#8A9099;margin-bottom:8px;font-weight:600}
.ta{background:#0F1114;border:1px solid #2A2E34;border-radius:12px;padding:12px;font-size:13.5px;line-height:1.45;color:#B4BAC2;height:230px;overflow:hidden;white-space:pre-wrap;font-family:Barlow,sans-serif}
.opt{display:flex;align-items:center;gap:12px;background:#16181C;border-radius:16px;padding:14px;margin-bottom:10px}.ic{width:40px;height:40px;border-radius:12px;background:#1F2227;display:flex;align-items:center;justify-content:center;font-size:18px}
.opt b{font-size:15px}.opt small{display:block;color:#8A9099;font-size:12.5px;margin-top:2px}.soon{opacity:.45}.pill{margin-left:auto;font-size:11px;background:#2A2E34;border-radius:999px;padding:3px 8px;color:#B4BAC2}
.big{background:#fff;color:#0A0B0D;border-radius:14px;padding:14px;text-align:center;font-weight:700;font-size:16px;margin-top:6px}.hint{color:#7D838C;font-size:12px;margin-top:10px;text-align:center}</style>"""
SAMPLE = _h.escape("LUNDI PUSH\ndc 4x6 80kg\nincl halt 3x10\ndips lest 4x8 +20\ntriceps poulie 3x12\n\nMARDI PULL\ntractions lestées 4x5 +15\nrowing barre 4x8 85\nface pull 3x15\n\nJEUDI LEGS\nsquat 5x5 120\npresse 4x12\nmollets 5x12")
entry = (ENTRY + "<div class=top><span class=back>‹ Retour</span><span class=ttl>Ajouter mon programme</span><span style='width:52px'></span></div>"
         "<div class=src style='margin:0 2px 12px'>Colle ton programme tel qu'il est : notes, message du coach, tableau. L'app te montre ce qu'elle a compris avant d'enregistrer quoi que ce soit.</div>"
         f"<div class=card><div class=lab>Colle ton texte ici</div><div class=ta>{SAMPLE}</div><div class=big>Analyser</div></div>"
         "<div class=opt><div class=ic>📄</div><div><b>Importer un fichier</b><small>Excel (.xlsx) ou CSV depuis ton téléphone</small></div></div>"
         "<div class=opt><div class=ic>🔗</div><div><b>Lien Google Sheet</b><small>Comme le programme de ton coach</small></div></div>"
         "<div class='opt soon'><div class=ic>📷</div><div><b>Photo ou PDF</b><small>Lecture par IA, plus tard</small></div><span class=pill>bientôt</span></div>"
         "<div class=hint>Ton texte reste sur ton téléphone : rien n'est envoyé.</div>")
pa, pb = page("P4", CASES[0][2], CASES[0][3], "A"), page("P4", CASES[0][2], CASES[0][3], "B")
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    files = []
    for name, h in (("1-ajout", entry), ("2A-apercu", pa), ("2B-apercu", pb)):
        pg.set_content(h); pg.wait_for_timeout(700); f = OUT / f"maquette-{name}.png"
        pg.screenshot(path=str(f), clip={"x": 0, "y": 0, "width": 390, "height": 844}); statusbar(f); files.append(f)
    br.close()
ims = [Image.open(f) for f in files]; w, h = ims[0].size; pad, top = 40, 120
B_ = Image.new("RGB", (3 * w + 4 * pad, h + top + pad), "#1a1b1e"); d = ImageDraw.Draw(B_)
d.text((pad, 30), "Ajouter mon programme · 1 écran d'ajout, 2 aperçus au choix", fill="white", font=ImageFont.truetype(FONT, 34))
for i, (im, lab) in enumerate(zip(ims, ["1 · Ajout (commun)", "A · Cartes par jour", "B · Liste compacte"])):
    x = pad + i * (w + pad); d.text((x, 80), lab, fill="#B4BAC2", font=ImageFont.truetype(FONT, 28)); B_.paste(im, (x, top))
B_.save(OUT / "maquette-ajout-programme.png"); print(OUT / "maquette-ajout-programme.png")
