"""Génère les images de démarrage iOS (apple-touch-startup-image) dans splash/ : fond de l'app + logo B² + « BE TOO STRONG »,
à la même place que l'écran de lancement de l'app (même HTML, mêmes polices), barre et libellé masqués.
Usage : python3 tools/make_startup_images.py   (nécessite Playwright + Chromium)"""
import pathlib, re
from playwright.sync_api import sync_playwright
P = pathlib.Path(__file__).resolve().parent.parent
app = (P / "src" / "app.html").read_text(encoding="utf-8")
svg = re.search(r'<div id="splash"[^>]*>(<svg.*?</svg>)', app, re.S).group(1)
# (largeur CSS, hauteur CSS, ratio) : tous les iPhone récents en portrait
DEVICES = [(440, 956, 3), (430, 932, 3), (428, 926, 3), (402, 874, 3), (393, 852, 3), (390, 844, 3), (414, 896, 3), (414, 896, 2), (375, 812, 3), (414, 736, 3), (375, 667, 2)]
HTML = """<!doctype html><meta charset=utf-8><style>
@font-face{font-family:"B2 Display";src:url(FONTS/bs.woff2) format("woff2");font-weight:100 900}
:root{--floor:#0C0B0A;--chalk:#F5F2EC;--acc:#FF4A2B;--faint:#8A857D;--deck3:#363330;--f-show:"B2 Display","Arial Narrow",sans-serif;--f-text:sans-serif}
html,body{margin:0;height:100%;background:var(--floor)}
.splash{position:fixed;inset:0;background:var(--floor);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;text-align:center}
.splash b{font:800 26px var(--f-show);letter-spacing:.06em;color:var(--chalk)}.splash svg{width:120px;height:auto}
.lbar{width:168px;height:3px;margin-top:6px;visibility:hidden}.llab{font:500 12px/1 var(--f-text);min-height:12px;visibility:hidden}
</style><div class="splash">SVG<b>BE TOO STRONG</b><div class="lbar"></div><div class="llab">.</div></div>""".replace("SVG", svg).replace("FONTS", (P / "fonts").as_uri())
out = P / "splash"; out.mkdir(exist_ok=True)
import tempfile
page = pathlib.Path(tempfile.mkdtemp()) / "splash.html"; page.write_text(HTML, encoding="utf-8")
tags = []
with sync_playwright() as p:
    br = p.chromium.launch()
    for w, h, r in DEVICES:
        c = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=r); pg = c.new_page()
        pg.goto(page.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        name = f"splash-{w * r}x{h * r}.png"; pg.screenshot(path=str(out / name)); c.close()
        tags.append(f'<link rel="apple-touch-startup-image" media="(device-width:{w}px) and (device-height:{h}px) and (-webkit-device-pixel-ratio:{r}) and (orientation:portrait)" href="splash/{name}">')
    br.close()
try:
    from PIL import Image   # palette réduite : fichiers plus petits, fond exact conservé
    for f in out.glob("*.png"): Image.open(f).convert("RGB").quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(f, optimize=True)
except ImportError: pass
(out / "tags.html").write_text("\n".join(tags) + "\n", encoding="utf-8")
print(len(tags), "images")
