from fastapi import FastAPI, Header, HTTPException
import json
import os

# Initialiser l'application
app = FastAPI(title="API de personnages de manga")

# Chemin du fichier de données
chemin_fichier = os.path.join(os.path.dirname(__file__), "personnages.json")

# Token d'authentification (dans une application réelle, utilisez un mécanisme plus sécurisé)
TOKEN_SECRET = "manga_api_secret_2025"

# Fonction pour charger les données
def charger_personnages():
    with open(chemin_fichier, "r", encoding="utf-8") as fichier:
        return json.load(fichier)

# Créer un endpoint GET /personnages
@app.get("/personnages")
def get_personnages():
    """
    Retourne la liste de tous les personnages (accès public)
    """
    personnages = charger_personnages()
    return personnages

# Créer un endpoint GET /personnages/{id}
@app.get("/personnages/{id}")
def get_personnage(id: int):
    """
    Retourne un personnage spécifique par son ID (accès public)
    """
    personnages = charger_personnages()
    for personnage in personnages:
        if personnage["id"] == id:
            return personnage
    return {"erreur": "Personnage non trouvé"}

# Endpoint sécurisé - nécessite un token d'authentification
@app.get("/personnages/stats/equipe")
def get_stats_equipe(token: str = Header(None)):
    """
    Retourne des statistiques sur les équipes (accès sécurisé)
    """
    # Vérification du token
    if token != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")
    
    # Calcul des statistiques
    personnages = charger_personnages()
    equipes = {}
    
    for personnage in personnages:
        equipe = personnage["equipe"]
        if equipe in equipes:
            equipes[equipe] += 1
        else:
            equipes[equipe] = 1
    
    return {
        "statistiques": "équipes",
        "total_personnages": len(personnages),
        "distribution_equipes": equipes
    }

# Autre endpoint sécurisé
@app.get("/personnages/stats/positions")
def get_stats_positions(token: str = Header(None)):
    """
    Retourne des statistiques sur les positions des joueurs (accès sécurisé)
    """
    # Vérification du token
    if token != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")
    
    # Calcul des statistiques
    personnages = charger_personnages()
    positions = {}
    
    for personnage in personnages:
        position = personnage["position"]
        if position in positions:
            positions[position] += 1
        else:
            positions[position] = 1
    
    return {
        "statistiques": "positions",
        "total_personnages": len(personnages),
        "distribution_positions": positions
    }