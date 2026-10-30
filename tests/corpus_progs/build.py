"""Construit les lots du corpus : python3 tests/corpus_progs/build.py [reglage|controle|neutre|all]"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import lib
which = sys.argv[1] if len(sys.argv) > 1 else "all"
if which in ("reglage", "all"):
    import reglage_notes, reglage_xlsx, reglage_sheets
    progs = [f() for m in (reglage_notes, reglage_xlsx, reglage_sheets) for f in m.ALL]
    idx = lib.build(progs, "reglage"); print("réglage :", len(idx), "progs,", sum(len(m["truth"]) for m in idx), "exercices attendus")
if which in ("controle", "all"):
    import controle
    progs = [f() for f in controle.ALL]
    idx = lib.build(progs, "controle"); print("contrôle :", len(idx), "progs,", sum(len(m["truth"]) for m in idx), "exercices attendus")
if which in ("neutre", "all"):
    import neutre
    idx = lib.build(neutre.PROGS, "neutre"); print("neutre :", len(idx), "progs,", sum(len(m["truth"]) for m in idx), "entrées de vérité")
