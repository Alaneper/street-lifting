# Corpus de progs sophistiquées (chantier progs, étape 2)

Données 100 % inventées. 40 progs : lot **réglage** (26, sert à corriger le lecteur) et lot **contrôle** (14, gelé, une seule mesure à l'étape 4).

```
python3 tests/corpus_progs/build.py all                       # régénère out/ (artefacts + vérité terrain)
python3 tests/corpus_progs/score.py reglage --detail          # mesure du lecteur (src/prog_import.js) sur le lot réglage
python3 tests/corpus_progs/score.py controle --controle       # UNE fois (étape 4) ; refuse si le lot a changé (CONTROLE.lock)
python3 tests/corpus_progs/score.py neutre --controle         # lot écrit par un assistant séparé (neutre.py, NEUTRE.lock) ; mesuré à l'aveugle le 30/10 : 153/212
```

- `lib.py` : modèle de vérité, écriture des .xlsx, lecture des .xlsx **comme l'app** (valeurs brutes : 75 % formaté = 0.75, cellules fusionnées vides sauf la 1re), constructeur de notes.
- `reglage_*.py`, `controle.py` : les progs. `score.py` + `reader_dump.js` : le scoreur.
- Les progs « Sheet » portent les valeurs **formatées** que renvoie l'API Sheets (« 75% », « 62,5 », « 3:00 »).

## Score
« exact » = exercice trouvé à la bonne semaine et au bon jour, avec toutes ses séries (reps + charge) justes. Aussi mesurés : exercice trouvé au bon jour, structure (semaines/jours), extras (RPE, tempo, côté), bruit (lignes lues en trop) et progs importées sans aucune correction.
Un exercice coupé en plusieurs lignes consécutives de même nom (top set + back-off) compte comme un seul.

## Décisions de format (validées par Alane le 30/10/2026)
1. Si kg **et** % sont présents pour un exercice : les **deux** sont lus et transcrits (vérité « 140 kg · 78 % » en R16 et R20).
2. Charges en **lb** : l'unité est conservée dans l'aperçu (« 225 lb »), puis convertie à l'écriture avec le facteur exact 0,45359237, kg stockés à **2 décimales** (aller-retour lb→kg→lb sans perte, testé sur 1999 valeurs). À vérifier par des essais à l'étape 3.
3. Maintiens chronométrés : reps = « 45 s » (R03, R04, R06, R14, R25, C06, C13). Validé.
4. Pourcentage stocké en fraction par Excel (0.75) : lu **75 %**. Validé après explication.
5. RPE en fourchette : « 8-9 » (« 8 à 9 » est accepté à la comparaison). Validé.
6. Top set et back-off = **deux entrées séparées** (deux fiches dans l'app, poids différents) : R03, R09, R16 et R20 ont été réécrits en ce sens ; le scoreur ne tolère plus la fusion de lignes.
7. RIR : traité plus tard ; formule à vérifier avant usage (RIR = 10 − RPE d'après Zourdos et al., 2016 pour 10 → 0 RIR et 9 → 1 RIR ; demi-points non vérifiés). Colonne présente en C10, ignorée par la vérité.

## Limites
- Lots réglage et contrôle : même auteur (pas un assistant séparé). Le lot **neutre** (12 progs, 212 exercices) a été écrit par un assistant séparé qui n'a jamais vu le lecteur ; il n'est plus à l'aveugle depuis les corrections de la v65. Pas de cardio ni d'EMOM dans ce lot.
- Pas de formules dans les .xlsx (valeurs seulement, comme un fichier enregistré par Excel).
- Les valeurs « Sheet » sont celles que l'API renvoie par défaut ; la locale du Sheet n'a pas pu être vérifiée sur un vrai fichier.
- L'import par lien lit au plus 12 onglets, A1:CZ400 : non couvert ici (limites de l'app, pas du lecteur).
