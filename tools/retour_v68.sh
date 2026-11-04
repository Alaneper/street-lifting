#!/bin/bash
# Retour arrière en une commande : republie la v68 (commit 27975df, branche origin/v68-prod) sur main avec un NOUVEAU numéro de build.
# Pourquoi rebâtir : le service worker n'installe une version que si son numéro « sl-build » est plus récent ; remettre l'ancien index.html ne remplacerait pas la v69 chez les testeurs.
# Usage : bash tools/retour_v68.sh          (ajouter PUSH=1 pour publier ; sans, tout est préparé en local sur la branche retour-v68)
set -e
main() {
  git fetch origin v68-prod main
  git checkout -B retour-v68 origin/v68-prod
  python3 tools/build.py
  git add -A; git commit -q -m "Retour à la v68 (rebâtie avec un nouveau numéro de build)"
  if [ "$PUSH" = "1" ]; then git push origin retour-v68:main; else echo "Prêt en local (branche retour-v68). Pour publier : PUSH=1 bash tools/retour_v68.sh"; fi
}
main
exit
