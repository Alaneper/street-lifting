"""Construit aliments.json (Ciqual 2025, Anses, Licence Ouverte Etalab 2.0) pour le module alimentation.
Source : conversion JSON de la table officielle (github.com/ar11tehau/food, data/ciqual.json), recoupée avec une 2e conversion
indépendante (github.com/gab22222/mes-apports) : 19 725 valeurs comparées, seuls des arrondis sur des valeurs < 0,001 diffèrent.
Format : [code, nom, kcal, protéines, glucides, lipides, fibres, sucres, sel, portion_g, kcal_calculé(0/1)] pour 100 g."""
import json, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
d = json.load(open(R / "data-src/ciqual-2025.json")); N = d["nutriments"]
por = json.load(open(R / "data-src/portions-inca3.json"))["portions"]
def v(x):
    if x is None: return None
    if isinstance(x, str): return 0.0  # « traces » ou « < seuil » : compté 0
    return float(x)
out = []
for a in d["aliments"]:
    code, nom, vals = a[0], a[1], a[6]
    g = lambda k: v(vals[N.index(k)])
    kcal, p, c, l, f = g("kcal"), g("prot"), g("gluc"), g("lip"), g("fibres")
    est = 0
    if kcal is None:
        if None in (p, c, l): continue
        kcal = 4 * p + 4 * c + 9 * l + 2 * (f or 0) + 7 * (g("alcool") or 0); est = 1  # facteurs du règlement UE 1169/2011
    r = lambda x: None if x is None else round(x, 2)
    out.append([code, nom, round(kcal, 1), r(p), r(c), r(l), r(f), r(g("sucres")), r(g("sel")), (por.get(str(code)) or [0])[0], est])
meta = {"source": "Anses, Table de composition nutritionnelle des aliments Ciqual 2025, Licence Ouverte Etalab 2.0 ; portions : Anses, étude INCA3 (médianes)", "n": len(out)}
(R / "aliments.json").write_text(json.dumps({"meta": meta, "a": out}, ensure_ascii=False, separators=(",", ":")))
print(len(out), "aliments", (R / "aliments.json").stat().st_size // 1024, "Ko")
