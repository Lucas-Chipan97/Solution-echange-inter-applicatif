# API de Personnages de Manga

Version: 1.0.0
Python: 3.8+
FastAPI: 0.95.0+

Une API REST sécurisée pour gérer et exposer des personnages fictifs de manga, inspirée de "Olive et Tom" (Captain Tsubasa).

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Endpoints](#endpoints)
- [Sécurité](#sécurité)
- [Tests](#tests)
- [Contribution](#contribution)
- [Licence](#licence)

## Fonctionnalités

- Récupération de la liste complète des personnages
- Récupération des détails d'un personnage par ID
- Authentification par token pour les endpoints sécurisés
- Documentation interactive avec Swagger UI
- Mise à jour automatique en développement avec `--reload`

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/api-manga.git
   cd api-manga
   ```

2. Créez et activez un environnement virtuel (recommandé) :
   ```bash
   python -m venv venv
   # Sur Windows
   venv\Scripts\activate
   # Sur macOS/Linux
   source venv/bin/activate
   ```

3. Installez les dépendances :
   ```bash
   pip install fastapi uvicorn
   ```

## 💻 Utilisation

### Démarrage du serveur

```bash
uvicorn main:app --reload
```

Le serveur sera accessible à l'adresse `http://localhost:8000`.

### Documentation interactive

- **Swagger UI** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** : [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📁 Structure du projet

```
mon_api/
├── main.py              # Point d'entrée de l'API
├── personnages.json     # Données statiques des personnages
├── .gitignore           # Fichiers à ignorer pour Git
└── README.md            # Ce fichier que vous lisez actuellement
```

## 🔌 Endpoints

| Méthode | URL | Description | Authentification |
|---------|-----|-------------|-----------------|
| GET | `/personnages` | Récupère tous les personnages | Non |
| GET | `/personnages/{id}` | Récupère un personnage par ID | Non |
| GET | `/personnages/stats` | Récupère des statistiques avancées | Oui |

### Exemples d'utilisation

#### Récupérer tous les personnages

```bash
curl -X GET http://localhost:8000/personnages
```

Réponse :
```json
[
  {
    "id": 1,
    "nom": "Olive",
    "equipe": "New Team",
    "position": "Attaquant",
    "competence": "Coup du faucon"
  },
  {
    "id": 2,
    "nom": "Tom",
    "equipe": "New Team",
    "position": "Gardien",
    "competence": "Arrêt stellaire"
  }
]
```

#### Récupérer un personnage spécifique

```bash
curl -X GET http://localhost:8000/personnages/1
```

Réponse :
```json
{
  "id": 1,
  "nom": "Olive",
  "equipe": "New Team",
  "position": "Attaquant",
  "competence": "Coup du faucon"
}
```

## 🔒 Sécurité

### Authentification par token

Pour accéder aux endpoints sécurisés, vous devez inclure un token d'authentification dans les headers HTTP :

```bash
curl -X GET http://localhost:8000/personnages/stats -H "token: MON_TOKEN_SECRET"
```

## 🧪 Tests

Pour exécuter les tests (si implémentés) :

```bash
pytest
```
