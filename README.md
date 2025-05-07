# API de Personnages de Manga

Version: 1.0.0  
Python: 3.8+  
FastAPI: 0.95.0+

Une API REST complète pour gérer des personnages de manga avec leurs compétences, scores et statistiques.

## 🌟 Fonctionnalités

- **Gestion de personnages** : création, récupération et recherche par prénom
- **Système d'évaluation** : ajout et mise à jour des scores pour chaque personnage
- **Statistiques avancées** : distribution par équipe et par position
- **Webhooks** : notifications automatiques pour les événements importants
- **Authentification** : protection des endpoints sensibles par token
- **Documentation interactive** : avec Swagger UI et ReDoc

## 📋 Prérequis

- Python 3.8 ou supérieur
- FastAPI
- Uvicorn (serveur ASGI)

## 🚀 Installation

1. Clonez ce dépôt :

   ```bash
   git clone https://github.com/votre-utilisateur/api-manga.git
   cd api-manga
   ```

2. Créez et activez un environnement virtuel :

   ```bash
   python -m venv venv
   # Sur Windows
   venv\Scripts\activate
   # Sur macOS/Linux
   source venv/bin/activate
   ```

3. Installez les dépendances :
   ```bash
   pip install fastapi uvicorn requests
   ```

## 💻 Utilisation

### Démarrage du serveur

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible à l'adresse `http://localhost:8000`.

### Documentation interactive

- **Swagger UI** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** : [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Interface utilisateur

Un frontend simple est disponible pour interagir avec l'API. Ouvrez le fichier HTML dans votre navigateur et assurez-vous que le serveur API est en cours d'exécution.

## 📁 Structure du projet

```
api-manga/
├── main.py              # Point d'entrée de l'API
├── personnages.json     # Données des personnages
├── scores.json          # Évaluations des personnages
├── webhooks.json        # Configuration des webhooks
├── frontend/            # Interface utilisateur simple
│   └── index.html       # Page HTML du frontend
└── README.md            # Documentation
```

## 🔌 Endpoints API

### Personnages

| Méthode | URL                 | Description                                                  | Auth |
| ------- | ------------------- | ------------------------------------------------------------ | ---- |
| GET     | `/personnages`      | Récupère tous les personnages (filtrage par prénom possible) | Non  |
| GET     | `/personnages/{id}` | Récupère un personnage par ID                                | Non  |
| POST    | `/personnages`      | Crée un nouveau personnage                                   | Oui  |

### Scores

| Méthode | URL                       | Description                       | Auth |
| ------- | ------------------------- | --------------------------------- | ---- |
| GET     | `/personnages/scores`     | Récupère tous les scores          | Oui  |
| GET     | `/personnages/{id}/score` | Récupère le score d'un personnage | Oui  |
| POST    | `/personnages/scores`     | Ajoute/met à jour un score        | Oui  |

### Statistiques

| Méthode | URL                            | Description               | Auth |
| ------- | ------------------------------ | ------------------------- | ---- |
| GET     | `/personnages/stats/equipe`    | Statistiques par équipe   | Oui  |
| GET     | `/personnages/stats/positions` | Statistiques par position | Oui  |

### Webhooks

| Méthode | URL                  | Description                                  | Auth |
| ------- | -------------------- | -------------------------------------------- | ---- |
| POST    | `/subscribe`         | Crée un nouvel abonnement webhook            | Oui  |
| DELETE  | `/unsubscribe`       | Supprime un abonnement webhook               | Oui  |
| GET     | `/webhooks`          | Liste tous les webhooks                      | Oui  |
| POST    | `/simuler-evenement` | Simule un événement pour tester les webhooks | Oui  |

## 🔐 Authentification

L'API utilise un système d'authentification par token. Pour accéder aux endpoints protégés, incluez le token dans le header HTTP :

```bash
curl -X GET http://localhost:8000/personnages/stats/equipe -H "token: manga_api_secret_2025"
```

Le token par défaut est `manga_api_secret_2025` (à des fins de développement uniquement).

## 📊 Modèles de données

### Personnage

```json
{
  "id": 1,
  "prenom": "Tsubasa",
  "nom": "Ozora",
  "equipe": "Nankatsu",
  "position": "Attaquant",
  "description": "Joueur prodige avec un talent naturel",
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
  "avis": "Un joueur exceptionnel avec une technique parfaite",
  "date_evaluation": "2025-05-07",
  "forces": ["Tir puissant", "Vision du jeu", "Leadership"],
  "faiblesses": ["Jeu de tête", "Défense"]
}
```

### Webhook

```json
{
  "url": "https://example.com/webhook",
  "events": ["nouveau_personnage", "nouveau_score", "mise_a_jour_score"],
  "description": "Webhook pour notification des nouveaux personnages et scores"
}
```

## 🚀 Exemples d'utilisation

### Récupérer tous les personnages

```bash
curl -X GET http://localhost:8000/personnages
```

### Créer un nouveau personnage

```bash
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

### Ajouter un score

```bash
curl -X POST http://localhost:8000/personnages/scores \
  -H "Content-Type: application/json" \
  -H "token: manga_api_secret_2025" \
  -d '{
    "personnage_id": 3,
    "nom_complet": "Kojiro Hyuga",
    "equipe": "Toho",
    "position": "Attaquant",
    "score_global": 8.7,
    "avis": "Un attaquant puissant avec un tir dévastateur",
    "date_evaluation": "2025-05-07",
    "forces": ["Puissance", "Tir du tigre", "Détermination"],
    "faiblesses": ["Jeu d'équipe", "Technique pure"]
  }'
```

### Créer un webhook

```bash
curl -X POST http://localhost:8000/subscribe \
  -H "Content-Type: application/json" \
  -H "token: manga_api_secret_2025" \
  -d '{
    "url": "https://example.com/webhook",
    "events": ["nouveau_personnage", "nouveau_score"],
    "description": "Notification pour les nouveaux personnages et scores"
  }'
```

## 📝 Développement

### Structure des fichiers de données

L'API utilise trois fichiers JSON pour stocker les données :

- **personnages.json** : Stocke les informations des personnages
- **scores.json** : Stocke les évaluations des personnages
- **webhooks.json** : Stocke les configurations des webhooks

Ces fichiers sont créés automatiquement s'ils n'existent pas.

### Notifications par webhooks

L'API prend en charge trois types d'événements pour les webhooks :

- `nouveau_personnage` : Déclenché lors de la création d'un personnage
- `nouveau_score` : Déclenché lors de l'ajout d'un score
- `mise_a_jour_score` : Déclenché lors de la mise à jour d'un score existant
