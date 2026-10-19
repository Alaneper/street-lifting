# Street Lifting

Web app de suivi de street lifting : PR, total, RIS, prog du coach (Google Sheets), poids de corps et compétitions.

App : https://alaneper.github.io/street-lifting/

## Organisation

- `src/app.html` : l'application (interface, calculs, lecture de la prog du coach).
- `src/pwa_layer.js` : connexion Google, accès à l'API Sheets, création du carnet.
- `tools/build.py` : assemble `index.html`, la page publiée sur GitHub Pages.
- `tests/unit.js` : tests sur des cas réels de la prog (`node tests/unit.js`).
- `tests/e2e.py` : parcours complet dans un navigateur, sur des données simulées.

Les données ne sont jamais dans ce dépôt : elles restent dans le Google Sheet de chaque utilisateur.
