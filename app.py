from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import schedule
import threading
import time
import re

app = Flask(__name__)
cached_data = []

def parse_text_and_time(text):
    # Utiliser des expressions régulières pour extraire le nom et le temps restant
    match = re.match(r"^(.*?)-\s+(?:ending|coming) in\s+(\d+)\s+hours$", text.strip(), re.IGNORECASE)
    if match:
        name = match.group(1).strip()  # Le nom de l'élément
        hours = int(match.group(2))  # Le nombre d'heures
        # Convertir les heures en format HH:MM:SS
        time_str = f"{hours:02d}:00:00"
        return name, time_str
    else:
        return text.strip(), "terminé"  # Si pas d'heure, retourne "terminé"

def scrape_data():
    global cached_data
    
    urls = [
        "https://sky.shiiyu.moe/stats/TOLOSA_TXERUS/Pomegranate#Skills",
        "https://sky.shiiyu.moe/stats/Daninho31/Pomegranate#Skills"
    ]
    
    data = []

    try:
        for url in urls:
            # Envoyer une requête GET à la page cible
            response = requests.get(url)
            
            # Vérifier si la requête a réussi
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Sélection des éléments de la forge
                forge_items = soup.find_all(class_="forge-item")
                
                for item in forge_items:
                    info_text = item.find(class_="stat-value").get_text()
                    
                    # Extraire le nom et l'heure depuis le texte récupéré
                    info_name, info_time = parse_text_and_time(info_text)
                    
                    data.append({
                        "info_name": info_name,
                        "info_time": info_time
                    })
            else:
                print(f"Erreur lors de l'accès à la page : {response.status_code}")

        cached_data = data

    except Exception as e:
        print(f"Erreur lors du scraping des données : {e}")

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Actualisation des données toutes les 5 minutes
schedule.every(5).minutes.do(scrape_data)

# Lancer le scheduler dans un thread séparé
t = threading.Thread(target=run_schedule)
t.start()

@app.route('/api/forge', methods=['GET'])
def get_forge_data():
    return jsonify(cached_data)

if __name__ == '__main__':
    # Initialiser les données dès le démarrage
    scrape_data()
    app.run(debug=True)
