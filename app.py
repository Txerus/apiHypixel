from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import schedule
import threading
import time

app = Flask(__name__)
cached_data = []

def scrape_data():
    global cached_data
    
    try:
        # Liste des URL à scraper
        urls = [
            "https://sky.shiiyu.moe/stats/TOLOSA_TXERUS/Pomegranate#Skills",
            "https://sky.shiiyu.moe/stats/Daninho31/Pomegranate#Skills"
        ]
        
        combined_data = []
        
        for url in urls:
            response = requests.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remplacez ceci par la manière correcte de sélectionner les éléments que vous souhaitez récupérer
                forge_items = soup.find_all(class_="forge-item")
                
                for item in forge_items:
                    slot = item.find(class_="forge-slot").get_text()
                    info = item.find(class_="stat-value").get_text()
                    combined_data.append({"slot": slot, "info": info, "url": url})
            else:
                print(f"Erreur lors de l'accès à la page {url} : {response.status_code}")
        
        cached_data = combined_data

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
