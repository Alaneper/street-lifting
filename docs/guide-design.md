# Street Lifting · mini guide de design (v21, 21/10/2026)

Références : l'épuré de Whoop, le logo de Hevy, la rigueur de Garmin. Ambiance compétitive et puissante, jamais « jeu vidéo ».
Règle d'or : un chiffre héros par écran, le reste en retrait.

## 1. Couleurs (tokens CSS, fichier `src/app.html`)

| Token | Valeur | Usage | Contraste mesuré |
|---|---|---|---|
| `--floor` | #0A0B0D | fond de l'app | — |
| `--deck` / `--deck2` / `--deck3` | #16181C / #1F2227 / #2A2E34 | cartes, champs, bordures fortes | — |
| `--chalk` | #FFFFFF | texte principal, bouton principal (fond blanc, texte noir) | 19:1 sur le fond |
| `--dust` | #8A9099 | texte secondaire, onglets inactifs | 6,1:1 sur le fond, 5,0:1 sur `--deck2` |
| `--faint` | #7D838C | texte effacé (séance faite, jours hors du mois) | 5,2:1 sur le fond, 4,7:1 sur `--deck` |
| placeholder | #848A93 | texte d'exemple des champs | 4,6:1 sur `--deck2` |
| `--brand` | #1F5FD0 | héros principal (J−X, total), compétitions | texte blanc 5,8:1 |
| `--mu` `--pull` `--dip` `--squat` | #E3B341 #4C8DF6 #2BB673 #F0524A | **uniquement** pour désigner un mouvement | sur fond sombre : 10,1 / 6,1 / 7,5 / 5,6:1 |

Règles :
- une couleur de mouvement ne sert qu'à désigner ce mouvement. Les états sont neutres : hausse et « Monte la charge » en blanc, baisse en gris avec « − », séance faite en gris clair, fin du repos en bleu marque. Seule exception : le rouge `--bad` pour une vraie alerte (au-dessus de la limite de poids, échec de synchro) ;
- jamais de texte blanc sur jaune MU (1,95:1), vert dips (2,61:1), bleu tractions (3,26:1) ou rouge squat (3,49:1).

## 2. Typographie

- Texte : Barlow 400/500/600/700. Chiffres et titres d'écran : Barlow Condensed 700/800, chiffres tabulaires.
- Échelle : 11 (onglets) · 12 · 13 · 15 (corps) · 16–18 (titres de section) · 22/30/44/76 (chiffres héros).
- Champs de saisie : 16 px minimum (sinon iOS zoome au toucher).
- Nombres : virgule décimale, espace insécable fine pour les milliers dans les graphiques (« 20 000 kg »), unité toujours affichée.

## 3. Grille et espacements

- Multiples de 4 : 4 · 8 · 12 · 16 · 24. Marges latérales : 16 px (iPhone), 32 px (iPad, ≥ 760 px).
- Rayons : 12 (champs, petits boutons) · 16 (cartes de liste) · 24 (cartes et héros).
- iPad : accueil sur deux colonnes (1,15 / 1), autres onglets centrés à 720 px.
- Zones de sécurité : `env(safe-area-inset-*)` en haut (barre d'état translucide), en bas (barre d'onglets) et sur les côtés.

## 4. Composants

- **Héros** : 24 px de rayon, 20 px de marge interne, ligne du haut 15 px, chiffre 76 px, ligne du bas 15 px.
  - Héros principal (J−X, total, calories) : fond bleu marque plein, texte blanc (5,8:1).
  - Héros d'un mouvement (séance, fiche, séance en direct) : carte sombre `--deck`, halo et filet de la couleur du mouvement, **chiffre dans la couleur du mouvement** (MU 9,1 / tractions 5,5 / dips 6,8 / squat 5,1:1), textes en `--steel-hi` et `--dust` (choix 2B du 21/10).
- **En-tête** : reste en haut (sticky), fond `--floor` à 86 % flouté derrière l'heure et l'îlot ; au défilement, filet et nom de l'onglet (« Street Lifting · Progrès ») (choix 1B).
- **Carte Pesée** : sous le héros d'Aujourd'hui tant qu'on ne s'est pas pesé ; stepper 56 px, bouton « Noter 74,9 kg » et marge sur la catégorie mis à jour en direct ; disparaît une fois la pesée notée (choix 3A).
- **Bouton principal** : blanc, texte noir, 54 px de haut, pleine largeur. Un seul par écran.
- **Bouton secondaire** : `--deck2`. **Bouton-lien** : souligné discret, zone tactile de 44 px sans changer la mise en page.
- **Puces** (blocs, semaines, périodes) : 36 px visibles, 44 px au toucher (`::after`), rangée qui défile horizontalement.
- **Segments** (Alimentation / Poids) : 38 px visibles, 44 px au toucher.
- **Champs** : 44 px de haut minimum ; le champ date d'iOS est neutralisé (`appearance:none`, `min-width:0`, texte à gauche).

## 5. Cibles tactiles et usage à une main

- Toute cible ≥ 44 × 44 px (Apple), aucune < 24 px (WCAG 2.5.8). Contrôle automatique : `python3 tests/qa.py <étiquette>`.
- Séance en direct : valider la série = un toucher sur la case de droite (44 px) ; le repos démarre seul ; le minuteur flotte en bas, à portée du pouce.

## 6. États

- Chargement : squelettes (`.skel`), jamais d'écran vide ; l'app s'affiche d'abord avec les dernières données du téléphone, puis se met à jour.
- Vide : une phrase qui dit quoi faire (« Rien de noté pour l'instant »), pas de « 0 » seul.
- Erreur et hors connexion : message en français clair + bouton « Réessayer » ; ce qui est saisi en séance reste sur le téléphone.
- Synchro : rien quand tout est à jour, pastille blanche qui pulse pendant la synchro, rouge si pas synchronisé ; libellé lu par VoiceOver.
- Mise à jour de l'app : installée tout de suite si rien n'a été touché, sinon bandeau « Nouvelle version prête » en bas (jamais pendant une séance).

## 7. Mouvement

- Transitions 150 à 300 ms, courbe `cubic-bezier(.2,.8,.2,1)`. Retour au toucher : léger `scale(.97)` sur les boutons.
- Tout est coupé si l'iPhone demande de réduire les animations (`prefers-reduced-motion`).

## 8. Comportements validés (21/10/2026)

- 1RM estimé : à partir de la série la plus lourde (à charge égale, la meilleure estimation).
- Séance en cours : rouverte automatiquement à l'ouverture si elle date de moins de 3 h et n'a pas été fermée avec ×.
- Corps s'ouvre sur Poids avant midi tant qu'on ne s'est pas pesé (sauf choix manuel pendant la session).

## 9. Textes

- Français, tutoiement, phrases courtes, pas de jargon sans explication (RIR, e1RM expliqués dans « Méthodes et sources »).
- Aucune donnée inventée : chaque chiffre vient du carnet, de la prog du coach ou d'une source citée (Official Streetlifting, Ciqual, Open Food Facts, RTS).

## 10. Contrôle qualité avant chaque publication

`python3 tools/build.py` puis : `tests/e2e*.py`, `tests/unit.js`, `tests/qa.py` (captures 390 et 834 px, contrastes, cibles, débordements), `tests/perf.py` (ouverture), `tests/lh.py` (Lighthouse), `tests/apercu.py` (captures avec barre d'état d'iPhone). Numéro de version visible dans Réglages ; numéro de build dans `<meta name="sl-build">` (le service worker n'installe que des builds plus récents).
