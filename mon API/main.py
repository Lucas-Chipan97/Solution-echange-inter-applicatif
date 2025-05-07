from fastapi import FastAPI, Header, HTTPException, Body, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import os
import requests
from datetime import datetime

# Initialiser l'application
app = FastAPI(title="API de personnages de manga")

# Configuration CORS - Version très permissive pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise TOUTES les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chemin du fichier de données
chemin_personnages = os.path.join(os.path.dirname(__file__), "personnages.json")
chemin_scores = os.path.join(os.path.dirname(__file__), "scores.json")
chemin_webhooks = os.path.join(os.path.dirname(__file__), "webhooks.json")

# Token d'authentification (dans une application réelle, utilisez un mécanisme plus sécurisé)
TOKEN_SECRET = "manga_api_secret_2025"

# Modèles Pydantic pour la validation des données
class CompetenceModel(BaseModel):
    force: int
    technique: int
    vitesse: int
    endurance: int

class PersonnageModel(BaseModel):
    id: int
    prenom: str
    nom: Optional[str] = None
    equipe: str
    position: str
    description: Optional[str] = None
    competences: CompetenceModel

class ScoreModel(BaseModel):
    personnage_id: int
    nom_complet: str
    equipe: str
    position: str
    score_global: float
    avis: str
    date_evaluation: str
    forces: List[str]
    faiblesses: List[str]

# Modèle pour l'enregistrement des webhooks
class WebhookModel(BaseModel):
    url: str
    events: List[str]  # Types d'événements à notifier ("nouveau_personnage", "nouveau_score", "mise_a_jour_score")
    description: Optional[str] = None

# Fonction pour charger les personnages
def charger_personnages():
    if not os.path.exists(chemin_personnages):
        # Créer un fichier vide avec une liste vide
        with open(chemin_personnages, "w", encoding="utf-8") as fichier:
            json.dump([], fichier)
        return []
    
    with open(chemin_personnages, "r", encoding="utf-8") as fichier:
        return json.load(fichier)

# Fonction pour sauvegarder les personnages
def sauvegarder_personnages(personnages):
    with open(chemin_personnages, "w", encoding="utf-8") as fichier:
        json.dump(personnages, fichier, indent=2, ensure_ascii=False)

# Fonction pour charger les scores
def charger_scores():
    if not os.path.exists(chemin_scores):
        # Créer un fichier vide avec une liste vide
        with open(chemin_scores, "w", encoding="utf-8") as fichier:
            json.dump([], fichier)
        return []
    
    with open(chemin_scores, "r", encoding="utf-8") as fichier:
        return json.load(fichier)

# Fonction pour sauvegarder les scores
def sauvegarder_scores(scores):
    with open(chemin_scores, "w", encoding="utf-8") as fichier:
        json.dump(scores, fichier, indent=2, ensure_ascii=False)

# Fonction pour charger les webhooks
def charger_webhooks():
    if not os.path.exists(chemin_webhooks):
        # Créer un fichier vide avec une liste vide
        with open(chemin_webhooks, "w", encoding="utf-8") as fichier:
            json.dump([], fichier)
        return []
    
    with open(chemin_webhooks, "r", encoding="utf-8") as fichier:
        return json.load(fichier)

# Fonction pour sauvegarder les webhooks
def sauvegarder_webhooks(webhooks):
    with open(chemin_webhooks, "w", encoding="utf-8") as fichier:
        json.dump(webhooks, fichier, indent=2, ensure_ascii=False)

# Fonction pour déclencher les webhooks enregistrés
def declencher_webhooks(event_type: str, payload: Dict):
    webhooks = charger_webhooks()
    for webhook in webhooks:
        if event_type in webhook["events"]:
            try:
                # Envoyer la requête au webhook
                requests.post(
                    webhook["url"],
                    json={
                        "event_type": event_type,
                        "timestamp": datetime.now().isoformat(),
                        "payload": payload
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=5  # Timeout de 5 secondes
                )
            except Exception as e:
                print(f"Erreur lors de l'envoi au webhook {webhook['url']}: {str(e)}")

# Créer un endpoint GET /personnages
@app.get("/personnages")
def get_personnages(prenom: Optional[str] = None):
    """
    Retourne la liste de tous les personnages.
    Peut filtrer par prénom si le paramètre prenom est fourni.
    """
    personnages = charger_personnages()
    
    # Filtrer par prénom si demandé
    if prenom:
        personnages = [p for p in personnages if prenom.lower() in p["prenom"].lower()]
    
    return personnages

# Créer un endpoint GET /personnages/{id}
@app.get("/personnages/{id}")
def get_personnage(id: int):
    """
    Retourne un personnage spécifique par son ID
    """
    personnages = charger_personnages()
    for personnage in personnages:
        if personnage["id"] == id:
            return personnage
    raise HTTPException(status_code=404, detail="Personnage non trouvé")

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

# NOUVEL ENDPOINT POUR L'EXERCICE 3
@app.post("/personnages/scores")
def ajouter_score(score: ScoreModel, background_tasks: BackgroundTasks, token: str = Header(None)):
    """
    Ajoute ou met à jour le score d'un personnage (accès sécurisé)
    """
    # Vérification du token
    if token != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")
    
    # Vérifier si le personnage existe
    personnages = charger_personnages()
    personnage_trouve = None
    
    for personnage in personnages:
        if personnage["id"] == score.personnage_id:
            personnage_trouve = personnage
            break
    
    if not personnage_trouve:
        raise HTTPException(status_code=404, detail=f"Personnage avec l'ID {score.personnage_id} non trouvé")
    
    # Charger les scores existants
    scores = charger_scores()
    
    # Vérifier si un score existe déjà pour ce personnage
    score_existe = False
    event_type = "nouveau_score"
    
    for i, s in enumerate(scores):
        if s["personnage_id"] == score.personnage_id:
            # Mettre à jour le score existant
            scores[i] = score.dict()
            score_existe = True
            event_type = "mise_a_jour_score"
            break
    
    # Si le score n'existe pas, l'ajouter
    if not score_existe:
        scores.append(score.dict())
    
    # Sauvegarder les scores mis à jour
    sauvegarder_scores(scores)
    
    # Préparer la charge utile pour le webhook
    payload = {
        "score": score.dict(),
        "personnage": personnage_trouve
    }
    
    # Déclencher les webhooks en arrière-plan
    background_tasks.add_task(declencher_webhooks, event_type, payload)
    
    return {
        "status": "success",
        "message": "Score ajouté/mis à jour avec succès",
        "score": score,
        "timestamp": datetime.now().isoformat()
    }

# Endpoint pour récupérer tous les scores
@app.get("/personnages/scores")
def get_all_scores(token: str = Header(None)):
    """
    Récupère tous les scores (accès sécurisé)
    """
    # Vérification du token
    if token != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")
    
    scores = charger_scores()
    return scores

# Endpoint pour récupérer le score d'un personnage spécifique
@app.get("/personnages/{id}/score")
def get_personnage_score(id: int, token: str = Header(None)):
    """
    Récupère le score d'un personnage spécifique (accès sécurisé)
    """
    # Vérification du token
    if token != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")
    
    scores = charger_scores()
    for score in scores:
        if score["personnage_id"] == id:
            return score
    
    raise HTTPException(status_code=404, detail=f"Score pour le personnage {id} non trouvé")

# Ajout d'un endpoint pour créer un personnage
@app.post("/personnages")
def create_personnage(personnage: PersonnageModel, background_tasks: BackgroundTasks, token: str = Header(None)):
    """
    Crée un nouveau personnage (accès sécurisé)
    """
    # Vérification du token
    if token != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")
    
    personnages = charger_personnages()
    
    # Vérifier si l'ID existe déjà
    for p in personnages:
        if p["id"] == personnage.id:
            raise HTTPException(status_code=409, detail=f"Un personnage avec l'ID {personnage.id} existe déjà")
    
    # Ajouter le nouveau personnage
    nouveau_personnage = personnage.dict()
    personnages.append(nouveau_personnage)
    sauvegarder_personnages(personnages)
    
    # Déclencher un webhook en arrière-plan
    background_tasks.add_task(declencher_webhooks, "nouveau_personnage", nouveau_personnage)
    
    return {
        "status": "success",
        "message": "Personnage créé avec succès",
        "personnage": personnage
    }

# NOUVEAUX ENDPOINTS POUR LES WEBHOOKS - PARTIE 3

@app.post("/subscribe")
def creer_webhook(webhook: WebhookModel, token: str = Header(None)):
    """
    Crée un nouvel abonnement webhook (accès sécurisé)
    """
    # Vérification du token
    if token != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")
    
    webhooks = charger_webhooks()
    
    # Vérifier si l'URL existe déjà
    for w in webhooks:
        if w["url"] == webhook.url:
            raise HTTPException(status_code=409, detail=f"Un webhook avec l'URL {webhook.url} existe déjà")
    
    # Ajouter le nouveau webhook
    webhooks.append(webhook.dict())
    sauvegarder_webhooks(webhooks)
    
    return {
        "status": "success",
        "message": "Webhook créé avec succès",
        "webhook": webhook
    }

@app.delete("/unsubscribe")
def supprimer_webhook(url: str, token: str = Header(None)):
    """
    Supprime un abonnement webhook (accès sécurisé)
    """
    # Vérification du token
    if token != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")
    
    webhooks = charger_webhooks()
    
    # Chercher et supprimer le webhook
    webhook_trouve = False
    for i, w in enumerate(webhooks):
        if w["url"] == url:
            webhooks.pop(i)
            webhook_trouve = True
            break
    
    if not webhook_trouve:
        raise HTTPException(status_code=404, detail=f"Webhook avec l'URL {url} non trouvé")
    
    sauvegarder_webhooks(webhooks)
    
    return {
        "status": "success",
        "message": f"Webhook {url} supprimé avec succès"
    }

@app.get("/webhooks")
def liste_webhooks(token: str = Header(None)):
    """
    Liste tous les webhooks enregistrés (accès sécurisé)
    """
    # Vérification du token
    if token != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")
    
    webhooks = charger_webhooks()
    return webhooks

# AJOUT D'UN ENDPOINT POUR SIMULER UN ÉVÉNEMENT (POUR TESTER LES WEBHOOKS)
@app.post("/simuler-evenement")
def simuler_evenement(
    event_type: str = Body(..., embed=True),
    payload: dict = Body(..., embed=True),
    background_tasks: BackgroundTasks = None,
    token: str = Header(None)
):
    """
    Simule un événement pour tester les webhooks (accès sécurisé)
    """
    # Vérification du token
    if token != TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Token d'authentification invalide")
    
    # Vérifier que le type d'événement est valide
    types_valides = ["nouveau_personnage", "nouveau_score", "mise_a_jour_score", "test"]
    if event_type not in types_valides:
        raise HTTPException(
            status_code=400, 
            detail=f"Type d'événement non valide. Types valides: {', '.join(types_valides)}"
        )
    
    # Déclencher les webhooks en arrière-plan
    background_tasks.add_task(declencher_webhooks, event_type, payload)
    
    return {
        "status": "success",
        "message": f"Événement {event_type} simulé avec succès",
        "payload": payload
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)