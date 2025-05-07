# API de Personnages de Manga

API REST développée avec FastAPI pour gérer des personnages de manga, leurs scores et statistiques.

## 🌟 Fonctionnalités

- **Personnages**: CRUD, recherche par prénom
- **Scores**: évaluation des personnages
- **Statistiques**: par équipe et position
- **Webhooks**: notifications pour nouveaux personnages/scores

## 🚀 Installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/api-manga.git
cd api-manga

# Installer les dépendances
pip install fastapi uvicorn requests

# Démarrer le serveur
uvicorn main:app --reload
```

## 📋 Endpoints principaux

| Endpoint                       | Méthode      | Description             | Auth |
| ------------------------------ | ------------ | ----------------------- | ---- |
| `/personnages`                 | GET          | Liste des personnages   | Non  |
| `/personnages/{id}`            | GET          | Détails d'un personnage | Non  |
| `/personnages`                 | POST         | Créer un personnage     | Oui  |
| `/personnages/scores`          | GET/POST     | Gérer les scores        | Oui  |
| `/personnages/stats/equipe`    | GET          | Stats par équipe        | Oui  |
| `/personnages/stats/positions` | GET          | Stats par position      | Oui  |
| `/subscribe`, `/unsubscribe`   | POST, DELETE | Gestion des webhooks    | Oui  |

## 🔐 Authentification

Pour les endpoints protégés, incluez le token dans le header HTTP:

```
token: manga_api_secret_2025
```

## 📊 Formats de données

### Personnage

```json
{
  "id": 1,
  "prenom": "Tsubasa",
  "nom": "Ozora",
  "equipe": "Nankatsu",
  "position": "Attaquant",
  "description": "Joueur prodige",
  "competences": {
    "force": 85,
    "technique": 95,
    "vitesse": 90,
    "endurance": 88
  }
}
```

### Score

```json
{
  "personnage_id": 1,
  "nom_complet": "Tsubasa Ozora",
  "equipe": "Nankatsu",
  "position": "Attaquant",
  "score_global": 9.2,
  "avis": "Un joueur exceptionnel",
  "date_evaluation": "2025-05-07",
  "forces": ["Tir puissant", "Vision du jeu"],
  "faiblesses": ["Jeu de tête"]
}
```

## 🔌 Exemple d'utilisation

```bash
# Créer un personnage
curl -X POST http://localhost:8000/personnages \
  -H "Content-Type: application/json" \
  -H "token: manga_api_secret_2025" \
  -d '{
    "id": 3,
    "prenom": "Kojiro",
    "nom": "Hyuga",
    "equipe": "Toho",
    "position": "Attaquant",
    "description": "L'attaquant au tir du tigre",
    "competences": {
      "force": 95,
      "technique": 85,
      "vitesse": 82,
      "endurance": 90
    }
  }'
```

## 📚 Documentation

- Documentation interactive: [http://localhost:8000/docs](http://localhost:8000/docs)
- Interface utilisateur simple incluse pour faciliter les tests

## 💾 Stockage des données

L'API utilise des fichiers JSON pour stocker les données:

- `personnages.json`: informations des personnages
- `scores.json`: évaluations
- `webhooks.json`: configurations des webhooks

Les fichiers sont créés automatiquement au premier lancement.

## 📱 Interface utilisateur

Un frontend HTML/CSS/JS simple est fourni pour interagir avec l'API. Ouvrez le fichier HTML dans votre navigateur après avoir démarré le serveur API.
