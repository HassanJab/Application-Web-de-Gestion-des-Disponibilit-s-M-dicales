## _Gestion des Disponibilités Médicales_


[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Cette application Web permet aux médecins de gérer leurs disponibilités et aux patients de consulter ces informations. Elle combine des technologies modernes pour offrir une expérience fluide et intuitive.


### Fonctionnalités principales

1-Authentification des utilisateurs :
-   Inscription et connexion des utilisateurs avec des rôles distincts (médecins ou patients).
-   Gestion sécurisée des sessions pour identifier les utilisateurs.

2-Gestion des disponibilités :
-   Les médecins peuvent ajouter, modifier ou supprimer leurs disponibilités.
-   Les patients peuvent consulter les disponibilités des médecins par spécialité.

3-Notifications en temps réel :
-   Affichage d’alertes lors de l’ajout ou de la modification de disponibilités.

### Fonctionnalités principales

-   **Python** : Langage principal côté serveur.
-   **Flask** : Framework léger pour le développement web.
-   **SQLite** : Base de données pour le stockage des utilisateurs et disponibilités.
-   **Bootstrap** : Framework CSS pour une interface utilisateur réactive et moderne.
-   **Socket IO** : Gestion des notifications en temps réel.
-   **HTML, CSS et JavaScript** : Technologies front-end pour une interface dynamique.

### Installation

1. Cloner le projet.
2. Installer les dépendances.
3. Initialiser la base de données : Utilisez la commande suivante pour créer la base de données SQLite.
4. Lancer l’application.
5. Accéder à l’application : Ouvrez votre navigateur et accédez à : http://127.0.0.1:5000.

```sh
git clone <url_du_dépôt>
cd doctor web
```
```sh
pip install -r requirements.txt
```
```sh
python -c "from app import init_db; init_db()"
```
```sh
python app.py
```

## Notes

Par défaut, l’application utilise database.db comme base de données. Ce fichier peut être réinitialisé si nécessaire.
Les fichiers CSS et JavaScript personnalisés se trouvent dans le dossier static.

