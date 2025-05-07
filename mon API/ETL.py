import requests
import json
import time
import logging
import os
from datetime import datetime
from tqdm import tqdm  # Pour la barre de progression (pip install tqdm)

# Configuration
# Exercice 2 - API source (paginée)
SOURCE_API_URL = "https://projects.propublica.org/nonprofits/api/v2/search.json"
SEARCH_TERM = "anime"  # Terme de recherche adapté au thème manga
MAX_PAGES = 5  # Limiter le nombre de pages
TIMEOUT = 5  # Timeout en secondes
INTERMEDIATE_FILE = "data_intermediaire.json"

# Exercice 3 - API cible pour le POST
TARGET_API_URL = "http://localhost:8000/personnages/scores"  # Adapter selon votre endpoint
API_TOKEN = "manga_api_secret_2025"  # Utiliser le même token que dans votre API

# Configuration des fichiers
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_FILE = os.path.join(OUTPUT_DIR, f"manga_etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "api_post_results.json")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# --- FONCTIONS POUR L'ÉTAPE EXTRACT (EXERCICE 2) ---

def extract_data(query_term, max_pages=5):
    """
    Fonction pour extraire les données de l'API paginée
    """
    logger.info(f"Extraction des données pour le terme '{query_term}'...")
    all_organizations = []
    current_page = 0
    total_pages = None
    
    # Utilisation de tqdm pour afficher une barre de progression
    with tqdm(total=max_pages, desc="Pages récupérées") as progress_bar:
        while (total_pages is None or current_page < total_pages) and current_page < max_pages:
            try:
                # Construction de l'URL avec les paramètres de pagination
                params = {
                    'q': query_term,
                    'page': current_page
                }
                
                # Appel à l'API avec retry pattern
                for attempt in range(3):  # 3 tentatives maximum
                    try:
                        response = requests.get(
                            SOURCE_API_URL, 
                            params=params,
                            timeout=TIMEOUT
                        )
                        response.raise_for_status()
                        break
                    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                        if attempt == 2:  # Dernière tentative
                            raise
                        logger.warning(f"Tentative {attempt+1} échouée, nouvelle tentative dans 2 secondes...")
                        time.sleep(2)
                
                data = response.json()
                
                # Déterminer le nombre total de pages si pas encore connu
                if total_pages is None and 'num_pages' in data:
                    total_pages = min(data.get('num_pages', max_pages), max_pages)
                    progress_bar.total = total_pages
                    progress_bar.refresh()
                
                # Récupérer les organisations de la page courante
                if 'organizations' in data:
                    all_organizations.extend(data['organizations'])
                else:
                    logger.warning(f"Pas d'organisations trouvées à la page {current_page}")
                    break
                
                # Vérifier s'il y a encore des données
                if not data.get('organizations', []):
                    logger.info("Plus de données disponibles.")
                    break
                
                # Passer à la page suivante
                current_page += 1
                progress_bar.update(1)
                
                # Pause pour éviter de surcharger l'API
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la récupération de la page {current_page}: {e}")
                break
    
    logger.info(f"Extraction terminée. {len(all_organizations)} organisations extraites au total.")
    return all_organizations

# --- FONCTIONS POUR L'ÉTAPE TRANSFORM (EXERCICE 2) ---

def transform_organizations_to_characters(organizations):
    """
    Transformer les données d'organisations en personnages de manga
    """
    logger.info("Transformation des données en personnages de manga...")
    characters = []
    
    # Types de personnages pour une diversité
    positions = ["attaquant", "défenseur", "milieu", "gardien", "coach"]
    equipes = ["Nankatsu SC", "Toho Academy", "Meiwa FC", "Furano FC", "FC Tokyo"]
    
    for i, org in enumerate(organizations):
        # Ne garder que les organisations avec une ville et un nom
        if 'city' in org and org['city'] and 'name' in org and org['name']:
            # Extraire le prénom et le nom à partir du nom de l'organisation
            org_name = org['name']
            name_parts = org_name.split()
            
            if len(name_parts) >= 2:
                prenom = name_parts[0]
                nom = ' '.join(name_parts[1:3])  # Limiter à 2 mots max pour le nom
            else:
                prenom = org_name
                nom = ""
            
            # Calculer des attributs basés sur les données de l'organisation
            force = min(99, max(50, int((org.get('totrevenue', 0) or 0) / 20000) + 50))
            technique = min(99, max(50, (i % 50) + 50))  # Varier entre 50 et 99
            vitesse = min(99, max(50, ((i * 7) % 50) + 50))  # Différent de technique
            
            # Créer un personnage
            character = {
                "id": i + 1,
                "prenom": prenom[:20],  # Limiter la longueur
                "nom": nom[:30],
                "equipe": equipes[i % len(equipes)],
                "position": positions[i % len(positions)],
                "description": f"Originaire de {org.get('city', 'une ville inconnue')}, {org.get('state', '')}",
                "competences": {
                    "force": force,
                    "technique": technique,
                    "vitesse": vitesse,
                    "endurance": min(99, max(50, ((i * 13) % 50) + 50))
                }
            }
            characters.append(character)
    
    logger.info(f"Transformation terminée. {len(characters)} personnages créés.")
    return characters

# --- FONCTIONS POUR L'ÉTAPE LOAD DE L'EXERCICE 2 ---

def save_to_file(data, filename):
    """
    Sauvegarder les données dans un fichier JSON
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    logger.info(f"Sauvegarde des données dans {filepath}...")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Sauvegarde terminée. {len(data)} éléments sauvegardés.")
    return filepath

# --- FONCTIONS POUR L'EXERCICE 3 ---

def load_from_file(filename):
    """
    Charger les données depuis un fichier JSON
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Erreur lors du chargement du fichier {filepath}: {e}")
        return None

def transform_for_scores(characters):
    """
    Transformer les personnages pour le format de scores attendu par l'API
    """
    logger.info("Préparation des données de scores pour le POST...")
    scores_data = []
    
    for character in characters:
        # Calculer un score global basé sur les compétences
        competences = character.get("competences", {})
        if isinstance(competences, dict):
            score_global = sum(competences.values()) / len(competences) if competences else 70
        else:
            # Si les compétences ne sont pas un dictionnaire, utiliser une valeur par défaut
            score_global = 70
        
        # Générer un avis basé sur le score
        avis = generate_avis(score_global)
        
        # Créer l'objet de score
        score_item = {
            "personnage_id": character.get("id"),
            "nom_complet": f"{character.get('prenom', '')} {character.get('nom', '')}".strip(),
            "equipe": character.get("equipe", "Équipe inconnue"),
            "position": character.get("position", "Position inconnue"),
            "score_global": round(score_global, 1),
            "avis": avis,
            "date_evaluation": datetime.now().strftime("%Y-%m-%d"),
            "forces": [],
            "faiblesses": []
        }
        
        # Identifier les forces et faiblesses
        if isinstance(competences, dict):
            for comp, valeur in competences.items():
                if valeur >= 80:
                    score_item["forces"].append(comp)
                elif valeur <= 65:
                    score_item["faiblesses"].append(comp)
        
        scores_data.append(score_item)
    
    logger.info(f"Transformation pour scores terminée. {len(scores_data)} scores préparés.")
    return scores_data

def generate_avis(score):
    """
    Générer un avis basé sur le score global
    """
    if score >= 90:
        return "Joueur exceptionnel de classe mondiale"
    elif score >= 80:
        return "Excellent joueur de premier plan"
    elif score >= 70:
        return "Bon joueur fiable"
    elif score >= 60:
        return "Joueur moyen avec du potentiel"
    else:
        return "Joueur en développement"

def post_to_api(scores_data):
    """
    Envoyer les scores à l'API
    """
    headers = {
        "token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    success_count = 0
    error_count = 0
    results = []
    
    logger.info(f"Envoi de {len(scores_data)} scores à l'API...")
    
    # Utiliser tqdm pour afficher une barre de progression
    for score in tqdm(scores_data, desc="Envoi des scores"):
        try:
            # Envoi avec retry pattern
            for attempt in range(3):  # 3 tentatives maximum
                try:
                    response = requests.post(
                        TARGET_API_URL, 
                        json=score,
                        headers=headers,
                        timeout=TIMEOUT
                    )
                    
                    # Vérifier les codes de statut
                    if response.status_code in [200, 201]:
                        success_count += 1
                        result = {
                            "status": "success",
                            "status_code": response.status_code,
                            "personnage": score["nom_complet"],
                            "response": response.json() if response.text else None
                        }
                        logger.info(f"Succès pour {score['nom_complet']}: {response.status_code}")
                        break
                    elif response.status_code == 409:  # Conflit (déjà existant)
                        result = {
                            "status": "conflit",
                            "status_code": response.status_code,
                            "personnage": score["nom_complet"],
                            "response": response.json() if response.text else None
                        }
                        logger.warning(f"Conflit pour {score['nom_complet']}: {response.status_code}")
                        break
                    else:
                        if attempt == 2:  # Dernière tentative
                            raise requests.exceptions.RequestException(
                                f"Code HTTP inattendu: {response.status_code} - {response.text}"
                            )
                        logger.warning(f"Tentative {attempt+1} échouée pour {score['nom_complet']}, nouvelle tentative...")
                        time.sleep(1)
                
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                    if attempt == 2:  # Dernière tentative
                        raise
                    logger.warning(f"Tentative {attempt+1} échouée pour {score['nom_complet']}, erreur: {e}")
                    time.sleep(2)
            
        except Exception as e:
            error_count += 1
            result = {
                "status": "error",
                "personnage": score["nom_complet"],
                "error": str(e)
            }
            logger.error(f"Erreur pour {score['nom_complet']}: {e}")
        
        results.append(result)
        time.sleep(0.5)  # Pause pour éviter de surcharger l'API
    
    logger.info(f"Envoi terminé. Succès: {success_count}, Erreurs: {error_count}")
    return results

# --- TESTS UNITAIRES ---

def run_tests():
    """
    Exécuter des tests unitaires simples
    """
    logger.info("Exécution des tests unitaires...")
    
    # Test 1: Génération d'avis
    assert generate_avis(95) == "Joueur exceptionnel de classe mondiale"
    assert generate_avis(85) == "Excellent joueur de premier plan"
    assert generate_avis(75) == "Bon joueur fiable"
    assert generate_avis(65) == "Joueur moyen avec du potentiel"
    assert generate_avis(55) == "Joueur en développement"
    
    # Test 2: Transformation pour scores
    test_character = {
        "id": 1,
        "prenom": "Test",
        "nom": "Character",
        "equipe": "Test Team",
        "position": "attaquant",
        "competences": {
            "force": 90,
            "technique": 60,
            "vitesse": 80,
            "endurance": 70
        }
    }
    
    transformed = transform_for_scores([test_character])
    
    # Vérifier que le champ 'avis' a bien été ajouté
    assert "avis" in transformed[0], "Le champ 'avis' n'a pas été ajouté"
    
    # Vérifier le score global
    assert "score_global" in transformed[0], "Le champ 'score_global' n'a pas été ajouté"
    assert 0 <= transformed[0]["score_global"] <= 100, "Le score n'est pas dans la plage 0-100"
    
    # Vérifier les forces et faiblesses
    assert "forces" in transformed[0], "Le champ 'forces' n'a pas été ajouté"
    assert "faiblesses" in transformed[0], "Le champ 'faiblesses' n'a pas été ajouté"
    assert "force" in transformed[0]["forces"], "La force devrait être une force"
    assert "technique" in transformed[0]["faiblesses"], "La technique devrait être une faiblesse"
    
    logger.info("Tous les tests unitaires ont réussi!")

# --- FONCTION PRINCIPALE ---

def run_etl():
    """
    Fonction principale qui exécute le processus ETL complet
    """
    logger.info("=== DÉMARRAGE DU PROCESSUS ETL ===")
    
    # Exécuter les tests
    run_tests()
    
    # PARTIE EXERCICE 2: EXTRACT & TRANSFORM
    # Extraction depuis l'API source
    organizations = extract_data(SEARCH_TERM, MAX_PAGES)
    
    if not organizations:
        logger.error("Aucune donnée extraite. Abandon du processus.")
        return
    
    # Transformation des organisations en personnages
    characters = transform_organizations_to_characters(organizations)
    
    # Sauvegarde intermédiaire
    save_to_file(characters, INTERMEDIATE_FILE)
    
    # PARTIE EXERCICE 3: TRANSFORM & LOAD (POST)
    # Préparation des scores pour l'API
    scores_data = transform_for_scores(characters)
    
    # Envoi des scores à l'API
    api_results = post_to_api(scores_data)
    
    # Sauvegarde des résultats
    save_to_file(api_results, "api_post_results.json")
    
    logger.info("=== PROCESSUS ETL TERMINÉ ===")
    
    # Analyser les résultats
    success_count = sum(1 for r in api_results if r.get("status") == "success")
    error_count = sum(1 for r in api_results if r.get("status") == "error")
    conflict_count = sum(1 for r in api_results if r.get("status") == "conflit")
    
    logger.info(f"Résumé: {len(api_results)} éléments traités")
    logger.info(f"  - Succès: {success_count}")
    logger.info(f"  - Erreurs: {error_count}")
    logger.info(f"  - Conflits: {conflict_count}")
    
    return {
        "characters_generated": len(characters),
        "scores_posted": len(scores_data),
        "success_count": success_count,
        "error_count": error_count,
        "conflict_count": conflict_count
    }

# Point d'entrée
if __name__ == "__main__":
    results = run_etl()
    print("\nRésultats du processus ETL:")
    for key, value in results.items():
        print(f"  {key}: {value}")