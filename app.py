import re
from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import schedule
import threading
import time

app = Flask(__name__)
cached_data = []

# Tableau basé sur les données fournies
table_data = [
    {"NOM": "Bejeweled Handle", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Refined Diamond", "Durée HH:MM:SS": "08:00:00"},
    {"NOM": "Refined Mithril", "Durée HH:MM:SS": "06:00:00"},
    {"NOM": "Refined Titanium", "Durée HH:MM:SS": "12:00:00"},
    {"NOM": "Fuel Tank", "Durée HH:MM:SS": "10:00:00"},
    # Ajoutez les autres items ici...
]

def parse_text_and_time(text):
    match = re.match(r"^(.*?)-\s+(?:ending|coming) in\s+(\d+)\s+hours$", text.strip(), re.IGNORECASE)
    
    if match:
        name = match.group(1).strip()
        hours = int(match.group(2))
        return name, hours * 60  # Convert hours to minutes
    else:
        if '-' in text:
            name = text.split('-')[0].strip()
        else:
            name = text.strip()
        return name, 0

def convert_time_to_minutes(time_str):
    hours, minutes, _ = map(int, time_str.split(':'))
    return hours * 60 + minutes

def format_remaining_time(remaining_minutes):
    days, remainder = divmod(remaining_minutes, 1440)  # 1440 minutes in a day
    hours, remainder = divmod(remainder, 60)
    minutes = remainder
    return f"{days:02}:{hours:02}:{minutes:02}:00"

def calculate_progress(item_name, remaining_time):
    for item in table_data:
        if item["NOM"] == item_name:
            total_time = convert_time_to_minutes(item["Durée HH:MM:SS"])
            elapsed_time = total_time - remaining_time
            progress = max(0, min(100, (elapsed_time / total_time) * 100))
            return round(progress, 2)
    return None

def scrape_data():
    global cached_data
    
    urls = [
        "https://sky.shiiyu.moe/stats/TOLOSA_TXERUS/Pomegranate#Skills",
        "https://sky.shiiyu.moe/stats/Daninho31/Pomegranate#Skills"
    ]
    
    data = []

    try:
        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                forge_items = soup.find_all(class_="forge-item")
                
                for item in forge_items:
                    info_text = item.find(class_="stat-value").get_text()
                    item_name, remaining_time = parse_text_and_time(info_text)
                    progress = calculate_progress(item_name, remaining_time)
                    
                    # Convert remaining time to DD:HH:MM:SS format
                    remaining_time_formatted = format_remaining_time(remaining_time)
                    
                    data.append({
                        "item_name": item_name,
                        "remaining_time": remaining_time_formatted,
                        "progress": f'{progress}%'
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

# Schedule to scrape data every 5 minutes
schedule.every(5).minutes.do(scrape_data)

# Run the schedule in a separate thread
t = threading.Thread(target=run_schedule)
t.start()

@app.route('/api/forge', methods=['GET'])
def get_forge_data():
    return jsonify(cached_data)

@app.route('/api/table', methods=['GET'])
def get_table_data():
    return jsonify(table_data)

if __name__ == '__main__':
    scrape_data()  # Initialize data at startup
    app.run(debug=True)
