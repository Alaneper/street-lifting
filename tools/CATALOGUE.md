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

## v56 — Produits proposés par les utilisateurs

- L'app envoie (`a=submit`) tout produit créé à la main ou après un scan introuvable, sauf si la case « Partager » est décochée ou si les valeurs sont incohérentes (`foodCheck`). Hors ligne : file d'attente locale `sl4-subq`, renvoyée au retour du réseau.
- Identité : un identifiant d'appareil aléatoire (`sl4-dev`), aucun compte ni donnée personnelle. Il sera remplacé par l'identifiant utilisateur au passage au vrai serveur.
- Onglet `proposes` (créé tout seul). Clé : code-barres sans zéros de tête, sinon nom+marque normalisés. Un produit est `prive` tant qu'un seul appareil l'a envoyé ; il passe à `partage` quand un 2e appareil différent envoie des valeurs proches (±10 % ou 10 kcal / 1 g). Valeurs très différentes = proposition séparée.
- Les produits `partage` sont servis avec `comm:1` par `a=code` et `a=q`. Déjà au catalogue ou déjà partagé : rien n'est créé, l'existant est renvoyé.
- Garde-fous : verrou (LockService), 30 envois par appareil et par jour, contrôle de cohérence côté serveur.
- Test de la logique serveur : `node tests/gs_submit.js` ; côté app : `python3 tests/e2e_v56.py`.
- Migration : l'onglet `proposes` devient une table (cle, code, nom, marque, k, p, g, l, appareils, statut) ; `appareils` devient une liste d'identifiants utilisateurs.
- À faire avant ouverture au public : mention dans la politique RGPD / conditions (le produit partagé ne contient aucune donnée personnelle), et choix éventuel d'une modération manuelle.
