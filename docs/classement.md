# Classement automatique : installation (une seule fois, 5 minutes, gratuit)

Le classement tourne sur un petit service Google Apps Script installé sur le compte d'Alane.
Chaque app y envoie ses records à chaque synchro ; le service vérifie auprès de Google qui les envoie
(jeton de connexion de l'app Street Lifting), range la ligne de la personne et renvoie le classement de tout le monde,
sans les adresses e-mail. Personne n'a rien à saisir ni à partager.

1. Sur drive.google.com : Nouveau → Google Sheets. Nomme-le « Street Lifting – Classement ».
2. Dans ce fichier : Extensions → Apps Script. Efface le contenu, colle tout `tools/classement.gs`, puis Enregistrer (icône disquette).
3. Déployer → Nouveau déploiement → roue dentée → « Application Web ».
   - Exécuter en tant que : **Moi**
   - Qui peut accéder : **Tout le monde**
   - Déployer, puis Autoriser l'accès (compte d'Alane ; écran « Google n'a pas validé cette appli » → Paramètres avancés → Accéder au projet).
4. Copie l'URL de l'application Web (elle finit par `/exec`) et envoie-la : elle est inscrite dans l'app (`CLASSEMENT_URL`), et le classement s'active pour tout le monde.

Qui apparaît : toute personne qui ouvre l'app connectée à son compte Google (en phase de test, seuls les comptes ajoutés comme
« utilisateurs test » dans Google Cloud peuvent se connecter). Une personne apparaît dès sa première synchro.
Retirer quelqu'un : supprimer sa ligne dans l'onglet CLASSEMENT du fichier.
Mettre à jour le code plus tard : Déployer → Gérer les déploiements → crayon → Version : nouvelle version (l'URL ne change pas).
