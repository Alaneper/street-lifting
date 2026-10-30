# Corpus de progs sophistiquées (chantier progs, étape 2)

Données 100 % inventées. 40 progs : lot **réglage** (26, sert à corriger le lecteur) et lot **contrôle** (14, gelé, une seule mesure à l'étape 4).

```
python3 tests/corpus_progs/build.py all                       # régénère out/ (artefacts + vérité terrain)
python3 tests/corpus_progs/score.py reglage --detail          # mesure du lecteur (src/prog_import.js) sur le lot réglage
python3 tests/corpus_progs/score.py controle --controle       # UNE fois (étape 4) ; refuse si le lot a changé (CONTROLE.lock)
```

- `lib.py` : modèle de vérité, écriture des .xlsx, lecture des .xlsx **comme l'app** (valeurs brutes : 75 % formaté = 0.75, cellules fusionnées vides sauf la 1re), constructeur de notes.
- `reglage_*.py`, `controle.py` : les progs. `score.py` + `reader_dump.js` : le scoreur.
- Les progs « Sheet » portent les valeurs **formatées** que renvoie l'API Sheets (« 75% », « 62,5 », « 3:00 »).

## Score
« exact » = exercice trouvé à la bonne semaine et au bon jour, avec toutes ses séries (reps + charge) justes. Aussi mesurés : exercice trouvé au bon jour, structure (semaines/jours), extras (RPE, tempo, côté), bruit (lignes lues en trop) et progs importées sans aucune correction.
Un exercice coupé en plusieurs lignes consécutives de même nom (top set + back-off) compte comme un seul.

## Décisions de format (hypothèses de l'étape 2, à valider avant l'étape 3)
1. Si kg **et** % sont présents pour un exercice : on garde le **kg** comme charge (R16).
2. Charges en **lb** : l'unité est conservée dans l'aperçu (« 225 lb ») puis convertie à l'écriture (comme `toGrid`).
3. Maintiens chronométrés : reps = « 45 s » (R03, R04, R06, R14, R25, C06, C13).
4. Pourcentage stocké en fraction (0.75) : lu **75 %**.
5. RPE en fourchette : « 8-9 » (« 8 à 9 » est accepté à la comparaison).
6. Top set + back-off sur plusieurs lignes ou plusieurs groupes = **un seul** exercice.
7. RIR : non évalué dans cette étape (colonne présente en C10, ignorée par la vérité).

## Limites
- Même auteur pour les deux lots (pas un assistant séparé) : le lot contrôle est moins neutre qu'il ne devrait.
- Pas de formules dans les .xlsx (valeurs seulement, comme un fichier enregistré par Excel).
- Les valeurs « Sheet » sont celles que l'API renvoie par défaut ; la locale du Sheet n'a pas pu être vérifiée sur un vrai fichier.
- L'import par lien lit au plus 12 onglets, A1:CZ400 : non couvert ici (limites de l'app, pas du lecteur).
