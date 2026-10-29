# Catalogue d'aliments du monde (v54, 29/10/2026)

- **Données** : Google Sheet « Catalogue Street Lifting », onglet `catalogue`, 14 106 produits issus d'Open Food Facts (ODbL 1.0 / DbCL 1.0), colonnes identiques à catalogue-monde-29-10.csv. Sheet non partagé.
- **Service** : `tools/catalogue.gs` (Apps Script, application web, exécuté en tant que le propriétaire, accès « tout le monde », lecture seule). L'adresse /exec est `CAT_URL` dans `src/app.html`.
  - `?a=q&q=nutella&l=fr&n=15` recherche par nom ; `?a=code&ean=<code>` recherche par code-barres ; `?a=flush` vide la mémoire (6 h), à appeler après toute modification du Sheet.
- **App** : nom → catalogue d'abord, puis Open Food Facts sans doublon, incohérents en dernier ; scan → Open Food Facts, puis catalogue, puis liste locale. Si le service ne répond pas (8 s), l'app continue sans lui.

## Pièges
1. Import du CSV : décocher « Convertir le texte en nombres, dates et formules » (sinon « 6.3 » devient une date en réglage français).
2. Le paramètre `c` est refusé par Apps Script (400) : utiliser `ean`.
3. Après un nouvel import : appeler `?a=flush`.

## Limites
Lecture seule ; licence ODbL (partage identique, attribution) à faire valider avant toute publication du fichier ; langue `fr` codée en dur ; mesures de vitesse : 1 à 4,6 s (isolées).
