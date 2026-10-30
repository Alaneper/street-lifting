"""Mesure du lecteur d'import sur le corpus de progs sophistiquées.
Usage : python3 tests/corpus_progs/score.py reglage [--detail] [--label NOM]
        python3 tests/corpus_progs/score.py controle --controle      (UNE seule fois, étape 4 ; voir CONTROLE.lock)
Score « exact » = exercice trouvé à la bonne semaine ET au bon jour avec TOUTES ses séries (reps + charge) justes."""
import json, pathlib, subprocess, sys, collections, datetime, unicodedata, re
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent
lot = sys.argv[1]; detail = "--detail" in sys.argv
label = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else datetime.date.today().isoformat()
D = HERE / "out" / lot
if lot == "controle":
    if "--controle" not in sys.argv: sys.exit("Le lot « contrôle » ne se lance qu'avec --controle, une seule fois (étape 4 du chantier).")
    lock = HERE / "CONTROLE.lock"
    idx0 = json.loads((D / "index.json").read_text())
    if lock.exists():
        want = json.loads(lock.read_text())
        bad = [m["id"] for m in idx0 if want.get(m["id"]) != m["sha"]]
        if bad: sys.exit("Lot contrôle MODIFIÉ depuis le gel : " + ", ".join(bad) + ". Mesure refusée.")
    with open(HERE / "CONTROLE_RUNS.log", "a") as f: f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} lancé ({label})\n")
idx = json.loads((D / "index.json").read_text())
def strip(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()).strip()
inputs = []
for m in idx:
    if m["kind"] in ("note", "csv"): inputs.append({"id": m["id"], "text": (D / m["file"]).read_text(encoding="utf-8")})
    elif m["kind"] == "xlsx":
        sys.path.insert(0, str(HERE)); import lib
        inputs.append({"id": m["id"], "sheets": lib.read_xlsx_like_app(D / m["file"])})
    else: inputs.append({"id": m["id"], "sheets": json.loads((D / m["file"]).read_text())})
_r = subprocess.run(["node", str(HERE / "reader_dump.js"), str(ROOT / "src/prog_import.js")], input=json.dumps(inputs), capture_output=True, text=True)
if _r.returncode: sys.exit("Le lecteur a planté :\n" + _r.stderr[:1500])
res = json.loads(_r.stdout)
def want_sets(groups): return [f"{r}{'+' if a and r != 'max' else ''}|{l or ''}" for (n, r, l, a) in groups for _ in range(n)]
def nrpe(x): return None if x is None else re.sub(r"\s*(?:à|a|-|–)\s*", "-", str(x).replace(",", ".")).replace(" ", "")
rows = []; tot = collections.Counter(); byp = collections.defaultdict(collections.Counter); det = {}
for m in idx:
    R = res[m["id"]]; T = m["truth"]; c = collections.Counter(); miss = []
    if "error" in R: rows.append((m["id"], "ERREUR " + R["error"])); c["total"] = len(T); c["erreur"] = 1
    else:
        W = [[ [e for e in d["exos"]] for d in w["days"]] for w in R["weeks"]]
        nW = max([t["w"] for t in T] + [0]) + 1
        tw = collections.defaultdict(lambda: collections.defaultdict(int))
        for t in T: tw[t["w"]][t["d"]] += 1
        c["struct_ok"] = int(len(W) == nW and all(len(W[w]) == len(tw[w]) if w < len(W) else False for w in range(nW)))
        c["struct_n"] = 1
        used = set(); matched = 0
        def same(e, t):
            if t["canon"]: return e["canon"] == t["canon"]
            a, b = strip(e["name"]), strip(t["name"]); return a == b or b in a or a in b
        for t in T:
            c["total"] += 1
            pool = W[t["w"]][t["d"]] if t["w"] < len(W) and t["d"] < len(W[t["w"]]) else []
            j = next((j for j, e in enumerate(pool) if (t["w"], t["d"], j) not in used and same(e, t)), None)
            anyw = next(((d, j2) for d, ds in enumerate(W[t["w"]] if t["w"] < len(W) else []) for j2, e in enumerate(ds) if (t["w"], d, j2) not in used and same(e, t)), None)
            if anyw: c["found_week"] += 1
            if j is None:
                miss.append(f"S{t['w']+1} J{t['d']+1} {t['name']} : " + ("rangé dans un autre jour" if anyw else "absent")); continue
            used.add((t["w"], t["d"], j)); matched += 1; c["found_day"] += 1; e = pool[j]
            ws_ = want_sets(t["groups"]); got = list(e["sets"])
            # un exercice coupé en plusieurs lignes consécutives du même nom (top set + back-off) compte comme un seul
            k_ = j + 1
            while got != ws_ and len(got) < len(ws_) and k_ < len(pool) and (t["w"], t["d"], k_) not in used and same(pool[k_], t):
                got += pool[k_]["sets"]; used.add((t["w"], t["d"], k_)); matched += 1; k_ += 1
            e = dict(e, sets=got)
            ok = e["sets"] == ws_
            if ok: c["exact"] += 1
            else: miss.append(f"S{t['w']+1} J{t['d']+1} {t['name']} : attendu {want_sets(t['groups'])[:3]}{'…' if sum(n for n,*_ in t['groups'])>3 else ''}, lu {e['sets'][:3]}{'…' if len(e['sets'])>3 else ''}")
            for k, fn in (("rpe", nrpe), ("tempo", lambda x: x), ("side", lambda x: bool(x))):
                if t.get(k) not in (None, False):
                    c["extra_n"] += 1
                    if fn(e[k]) == fn(t[k]): c["extra_ok"] += 1
                    else: miss.append(f"   {k} de {t['name']} : attendu {t[k]}, lu {e[k]}")
        total_read = sum(len(d) for w in W for d in w)
        c["bruit"] = total_read - matched
        noise_hit = [e["name"] for w in W for d in w for e in d if any(strip(n) and strip(n) in strip(e["name"]) for n in m["noise"])]
        c["bruit_nomme"] = len(noise_hit)
        if noise_hit: miss.append("   bruit nommé lu comme exercice : " + ", ".join(noise_hit[:5]))
        rows.append((m["id"], f"exact {c['exact']:>3}/{c['total']:<3} trouvé(jour) {c['found_day']:>3} structure {'ok' if c['struct_ok'] else 'FAUX'} bruit {c['bruit']}"))
    det[m["id"]] = miss
    for k, v in c.items(): tot[k] += v
    for pi in m["pieges"]:
        for k, v in c.items(): byp[pi][k] += v
        byp[pi]["progs"] += 1
print(f"=== Lot « {lot} » · {len(idx)} progs · étiquette {label}")
for (i, line) in rows:
    m = next(x for x in idx if x["id"] == i); print(f"{i:5} {m['title'][:46]:46} {line}")
    if detail and det[i]: print("      " + "\n      ".join(det[i][:12]))
t = tot
print(f"\nTOTAL : exact {t['exact']}/{t['total']} ({100*t['exact']/max(1,t['total']):.0f} %) · trouvé au bon jour {t['found_day']} ({100*t['found_day']/max(1,t['total']):.0f} %) · trouvé dans la semaine {t['found_week']} · structure juste {t['struct_ok']}/{t['struct_n']} progs · extras (RPE/tempo/côté) {t['extra_ok']}/{t['extra_n']} · bruit (lignes lues en trop) {t['bruit']} dont nommées {t['bruit_nomme']}")
prog_exact = sum(1 for m in idx if "ERREUR" not in dict(rows)[m["id"]] and "exact" in dict(rows)[m["id"]] and re.search(r"exact\s+(\d+)/(\d+)", dict(rows)[m["id"]]) and re.search(r"exact\s+(\d+)/(\d+)", dict(rows)[m["id"]]).group(1) == re.search(r"exact\s+(\d+)/(\d+)", dict(rows)[m["id"]]).group(2) and "structure ok" in dict(rows)[m["id"]] and " bruit 0" in dict(rows)[m["id"]])
print(f"Progs importées SANS AUCUNE correction à faire (tout exact, structure juste, aucun bruit) : {prog_exact}/{len(idx)}")
print("\nPar piège du catalogue (progs concernées · exercices exacts) :")
for k in sorted(byp): v = byp[k]; print(f"  {k:4} {v['progs']:>2} progs · exact {v['exact']}/{v['total']} ({100*v['exact']/max(1,v['total']):.0f} %)")
(D / f"score_{label}.json").write_text(json.dumps(dict(label=label, total=dict(tot), by_piege={k: dict(v) for k, v in byp.items()}, per_prog={r[0]: r[1] for r in rows}, misses=det), ensure_ascii=False, indent=1))
