import json
import requests
import time
import logging
from tqdm import tqdm
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/scores"  # À adapter selon votre configuration
API_TOKEN = "manga_api_secret_2025"  # À remplacer par votre token
INPUT_FILE = "nonprofits_data.json"  # Fichier généré dans l'exercice 2
LOG_FILE = f"api_post_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
TIMEOUT = 5  # Timeout en secondes

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

def load_data(filename):
    """
    Charger les données depuis le fichier JSON
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Erreur lors du chargement du fichier {filename}: {e}")
        return None

def transform_data(data):
    """
    Transformer les données pour le format attendu par l'API
    """
    transformed_data = []
    
    for item in data:
        # Créer un nouvel objet avec les champs adaptés pour l'API
        transformed_item = {
            "nom_organisation": item["nom"],
            "localisation": f"{item['ville']}, {item['etat']}",
            "score": calculate_score(item),
            "avis": generate_avis(item),
            "date_evaluation": datetime.now().strftime("%Y-%m-%d"),
            "categorie": item["categorie_revenu"]
        }
        # Supprimer les champs non utilisés
        transformed_data.append(transformed_item)
    
    return transformed_data

def calculate_score(item):
    """
    Calculer un score basé sur les revenus (exemple simple)
    """
    try:
        # Score entre 0 et 100 basé sur le revenu
        revenu = item.get("revenu_total", 0)
        if revenu <= 0:
            return 0
        elif revenu < 100000:
            return int(revenu / 1000)  # 0-99
        elif revenu < 1000000:
            return min(60 + int(revenu / 20000), 99)  # 60-99
        else:
            return 100  # Maximum pour les grands revenus
    except (TypeError, ValueError):
        return 50  # Valeur par défaut en cas d'erreur

def generate_avis(item):
    """
    Générer un avis basé sur les données
    """
    score = calculate_score(item)
    if score >= 90:
        return "Excellent"
    elif score >= 70:
        return "Très bon"
    elif score >= 50:
        return "Bon"
    elif score >= 30:
        return "Moyen"
    else:
        return "À améliorer"

def post_data_to_api(data_items):
    """
    Envoyer les données à l'API
    """
    headers = {
        "token": API_TOKEN,
        "Content-Type": "application/json"
    }
    
    success_count = 0
    error_count = 0
    results = []
    
    # Utiliser tqdm pour afficher une barre de progression
    for item in tqdm(data_items, desc="Envoi des données à l'API"):
        try:
            # Envoi avec retry pattern
            for attempt in range(3):  # 3 tentatives maximum
                try:
                    response = requests.post(
                        API_URL, 
                        json=item,
                        headers=headers,
                        timeout=TIMEOUT
                    )
                    
                    # Vérifier les codes de statut
                    if response.status_code == 200 or response.status_code == 201:
                        success_count += 1
                        result = {
                            "status": "success",
                            "status_code": response.status_code,
                            "item": item["nom_organisation"],
                            "response": response.json() if response.text else None
                        }
                        logger.info(f"Succès pour {item['nom_organisation']}: {response.status_code}")
                        break
                    elif response.status_code == 409:  # Conflit (déjà existant)
                        result = {
                            "status": "conflit",
                            "status_code": response.status_code,
                            "item": item["nom_organisation"],
                            "response": response.json() if response.text else None
                        }
                        logger.warning(f"Conflit pour {item['nom_organisation']}: {response.status_code}")
                        break
                    else:
                        if attempt == 2:  # Dernière tentative
                            raise requests.exceptions.RequestException(
                                f"Code HTTP inattendu: {response.status_code} - {response.text}"
                            )
                        logger.warning(f"Tentative {attempt+1} échouée pour {item['nom_organisation']}, nouvelle tentative...")
                        time.sleep(1)  # Attendre 1 seconde avant de réessayer
                
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                    if attempt == 2:  # Dernière tentative
                        raise
                    logger.warning(f"Tentative {attempt+1} échouée pour {item['nom_organisation']}, erreur: {e}")
                    time.sleep(2)  # Attendre 2 secondes avant de réessayer
            
        except Exception as e:
            error_count += 1
            result = {
                "status": "error",
                "item": item["nom_organisation"],
                "error": str(e)
            }
            logger.error(f"Erreur pour {item['nom_organisation']}: {e}")
        
        results.append(result)
        time.sleep(0.5)  # Pause pour éviter de surcharger l'API
    
    logger.info(f"Traitement terminé. Succès: {success_count}, Erreurs: {error_count}")
    return results

def save_results(results, filename="api_post_results.json"):
    """
    Sauvegarder les résultats dans un fichier JSON
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"Résultats sauvegardés dans {filename}")

def test_transformation():
    """
    Test unitaire simple pour vérifier que le champ 'avis' est bien ajouté
    """
    test_data = [{
        "nom": "Test Org",
        "ville": "Paris",
        "etat": "IDF",
        "revenu_total": 50000,
        "categorie_revenu": "Petit (<100K)"
    }]
    
    transformed = transform_data(test_data)
    
    # Vérifier que le champ 'avis' a bien été ajouté
    assert "avis" in transformed[0], "Le champ 'avis' n'a pas été ajouté"
    assert transformed[0]["avis"] in ["Excellent", "Très bon", "Bon", "Moyen", "À améliorer"], \
        "L'avis n'a pas une valeur correcte"
    
    # Vérifier le score
    assert "score" in transformed[0], "Le champ 'score' n'a pas été ajouté"
    assert 0 <= transformed[0]["score"] <= 100, "Le score n'est pas dans la plage 0-100"
    
    print("Le test de transformation a réussi!")

def main():
    """
    Fonction principale exécutant tout le processus
    """
    logger.info("Démarrage du traitement")
    
    # Exécuter les tests unitaires
    test_transformation()
    
    # Charger les données depuis le fichier généré dans l'exercice 2
    logger.info(f"Chargement des données depuis {INPUT_FILE}...")
    raw_data = load_data(INPUT_FILE)
    
    if not raw_data:
        logger.error("Aucune donnée n'a pu être chargée. Fin du traitement.")
        return
    
    # Transformer les données
    logger.info("Transformation des données...")
    transformed_data = transform_data(raw_data)
    
    # Afficher un aperçu
    logger.info(f"{len(transformed_data)} éléments transformés.")
    if transformed_data:
        logger.info(f"Exemple d'élément transformé: {json.dumps(transformed_data[0], indent=2)}")
    
    # Envoyer les données à l'API
    logger.info(f"Envoi des données à l'API {API_URL}...")
    results = post_data_to_api(transformed_data)
    
    # Sauvegarder les résultats
    save_results(results)
    
    logger.info("Traitement terminé.")

if __name__ == "__main__":
    main()
