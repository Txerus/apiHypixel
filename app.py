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
    {"NOM": "Drill Engine", "Durée HH:MM:SS": "30:00:00"},
    {"NOM": "Golden Plate", "Durée HH:MM:SS": "06:00:00"},
    {"NOM": "Mithril Plate", "Durée HH:MM:SS": "18:00:00"},
    {"NOM": "Gemstone Mixture", "Durée HH:MM:SS": "04:00:00"},
    {"NOM": "Perfect Jasper Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Ruby Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Jade Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Sapphire Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Amber Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Topaz Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Amethyst Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Opal Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Glacite Amalgamation", "Durée HH:MM:SS": "04:00:00"},
    {"NOM": "Refined Tungsten", "Durée HH:MM:SS": "01:00:00"},
    {"NOM": "Refined Umber", "Durée HH:MM:SS": "01:00:00"},
    {"NOM": "Tungsten Plate", "Durée HH:MM:SS": "03:00:00"},
    {"NOM": "Umber Plate", "Durée HH:MM:SS": "03:00:00"},
    {"NOM": "Perfect Onyx Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Citrine Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Aquamarine Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Peridot Gemstone", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Perfect Plate", "Durée HH:MM:SS": "06:00:00"},
    {"NOM": "Mithril Pickaxe", "Durée HH:MM:SS": "00:45:00"},
    {"NOM": "Travel Scroll To The Dwarven Forge", "Durée HH:MM:SS": "05:00:00"},
    {"NOM": "Beacon II", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Titanium Talisman", "Durée HH:MM:SS": "14:00:00"},
    {"NOM": "Diamonite", "Durée HH:MM:SS": "06:00:00"},
    {"NOM": "Power Crystal", "Durée HH:MM:SS": "02:00:00"},
    {"NOM": "Bejeweled Collar", "Durée HH:MM:SS": "02:00:00"},
    {"NOM": "Mithril Gauntlet", "Durée HH:MM:SS": "01:00:00"},
    {"NOM": "Mithril Belt", "Durée HH:MM:SS": "01:00:00"},
    {"NOM": "Mithril Cloak", "Durée HH:MM:SS": "01:00:00"},
    {"NOM": "Mithril Necklace", "Durée HH:MM:SS": "01:00:00"},
    {"NOM": "Refined Mithril Pickaxe", "Durée HH:MM:SS": "22:00:00"},
    {"NOM": "Mithril Drill SX-R226", "Durée HH:MM:SS": "04:00:00"},
    {"NOM": "Mithril-Infused Fuel Tank", "Durée HH:MM:SS": "10:00:00"},
    {"NOM": "Mithril-Plated Drill Engine", "Durée HH:MM:SS": "15:00:00"},
    {"NOM": "Beacon III", "Durée HH:MM:SS": "30:00:00"},
    {"NOM": "Titanium Ring", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Pure Mithril", "Durée HH:MM:SS": "12:00:00"},
    {"NOM": "Rock Gemstone", "Durée HH:MM:SS": "22:00:00"},
    {"NOM": "Petrified Starfall", "Durée HH:MM:SS": "14:00:00"},
    {"NOM": "Ruby Drill TX-15", "Durée HH:MM:SS": "01:00:00"},
    {"NOM": "Pesto Goblin Omelette", "Durée HH:MM:SS": "01:00:00"},
    {"NOM": "Ammonite Pet", "Durée HH:MM:SS": "72:00:00"},
    {"NOM": "Titanium Gauntlet", "Durée HH:MM:SS": "04:30:00"},
    {"NOM": "Titanium Belt", "Durée HH:MM:SS": "04:30:00"},
    {"NOM": "Titanium Cloak", "Durée HH:MM:SS": "04:30:00"},
    {"NOM": "Titanium Necklace", "Durée HH:MM:SS": "04:30:00"},
    {"NOM": "Mole Pet", "Durée HH:MM:SS": "72:00:00"},
    {"NOM": "Mithril Drill SX-R326", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Titanium-Plated Drill Engine", "Durée HH:MM:SS": "30:00:00"},
    {"NOM": "Goblin Omelette", "Durée HH:MM:SS": "18:00:00"},
    {"NOM": "Beacon IV", "Durée HH:MM:SS": "40:00:00"},
    {"NOM": "Titanium Artifact", "Durée HH:MM:SS": "36:00:00"},
    {"NOM": "Hot Stuff", "Durée HH:MM:SS": "00:00:00"},
    {"NOM": "Sunny Side Goblin Omelette", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Gemstone Drill LT-522", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Gleaming Crystal", "Durée HH:MM:SS": "12:00:00"},
    {"NOM": "Titanium Drill DR-X355", "Durée HH:MM:SS": "64:00:00"},
    {"NOM": "Titanium Drill DR-X455", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Titanium Drill DR-X555", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Titanium-Infused Fuel Tank", "Durée HH:MM:SS": "25:00:00"},
    {"NOM": "Beacon V", "Durée HH:MM:SS": "50:00:00"},
    {"NOM": "Titanium Relic", "Durée HH:MM:SS": "72:00:00"},
    {"NOM": "Spicy Goblin Omelette", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Gemstone Chamber", "Durée HH:MM:SS": "04:00:00"},
    {"NOM": "Topaz Drill KGR-12", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Ruby-Polished Drill Engine", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Gemstone Fuel Tank", "Durée HH:MM:SS": "30:00:00"},
    {"NOM": "Amethyst Gauntlet", "Durée HH:MM:SS": "24:00:00"},
    {"NOM": "Jade Belt", "Durée HH:MM:SS": "24:00:00"},
    {"NOM": "Sapphire Cloak", "Durée HH:MM:SS": "24:00:00"},
    {"NOM": "Amber Necklace", "Durée HH:MM:SS": "24:00:00"},
    {"NOM": "Blue Cheese Goblin Omelette", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Titanium Drill DR-X655", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Jasper Drill X", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Sapphire-Polished Drill Engine", "Durée HH:MM:SS": "20:00:00"},
    {"NOM": "Amber Material", "Durée HH:MM:SS": "07:00:00"},
    {"NOM": "Helmet Of Divan", "Durée HH:MM:SS": "23:00:00"},
    {"NOM": "Chestplate Of Divan", "Durée HH:MM:SS": "23:00:00"},
    {"NOM": "Leggings Of Divan", "Durée HH:MM:SS": "23:00:00"},
    {"NOM": "Boots Of Divan", "Durée HH:MM:SS": "23:00:00"},
    {"NOM": "Amber-Polished Drill Engine", "Durée HH:MM:SS": "50:00:00"},
    {"NOM": "Perfectly-Cut Fuel Tank", "Durée HH:MM:SS": "50:00:00"},
    {"NOM": "Divan's Drill", "Durée HH:MM:SS": "60:00:00"},
    {"NOM": "Divan's Powder Coating", "Durée HH:MM:SS": "36:00:00"},
    {"NOM": "Secret Railroad Pass", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Travel Scroll To The Dwarven Base Camp", "Durée HH:MM:SS": "10:00:00"},
    {"NOM": "T-Rex Pet", "Durée HH:MM:SS": "168:00:00"},
    {"NOM": "Spinosaurus Pet", "Durée HH:MM:SS": "168:00:00"},
    {"NOM": "Goblin Pet", "Durée HH:MM:SS": "168:00:00"},
    {"NOM": "Ankylosaurus Pet", "Durée HH:MM:SS": "168:00:00"},
    {"NOM": "Penguin Pet", "Durée HH:MM:SS": "168:00:00"},
    {"NOM": "Mammoth Pet", "Durée HH:MM:SS": "168:00:00"},
    {"NOM": "Chisel", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Tungsten Key", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Umber Key", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Frigid Husk", "Durée HH:MM:SS": "00:00:30"},
    {"NOM": "Dwarven Handwarmers", "Durée HH:MM:SS": "04:00:00"},
    {"NOM": "Reinforced Chisel", "Durée HH:MM:SS": "12:00:00"},
    {"NOM": "Dwarven Metal Talisman", "Durée HH:MM:SS": "24:00:00"},
    {"NOM": "Portable Campfire", "Durée HH:MM:SS": "00:30:00"},
    {"NOM": "Tungsten Regulator", "Durée HH:MM:SS": "06:00:00"},
    {"NOM": "Glacite-Plated Chisel", "Durée HH:MM:SS": "12:00:00"},
    {"NOM": "Perfect Chisel", "Durée HH:MM:SS": "24:00:00"},
    {"NOM": "Pendant Of Divan", "Durée HH:MM:SS": "168:00:00"},
    {"NOM": "Relic Of Power", "Durée HH:MM:SS": "12:00:00"},
    {"NOM": "Skeleton Key", "Durée HH:MM:SS": "00:30:00"}
]

def parse_text_and_time(text):
    # Adapter la regex pour capturer les minutes ainsi que les heures
    match = re.match(r"^(.*?)-\s+(?:ending|coming) in\s+(\d+)\s+(hours|minutes)$", text.strip(), re.IGNORECASE)
    
    if match:
        name = match.group(1).strip()
        value = int(match.group(2))
        unit = match.group(3).lower()
        
        # Conversion en minutes
        if unit == 'hours':
            return name, value * 60  # Convertir les heures en minutes
        elif unit == 'minutes':
            return name, value  # Les minutes sont déjà en minutes
        
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

def calculate_progress(item_name, remaining_minutes):
    for item in table_data:
        if item["NOM"] == item_name:
            total_minutes = convert_time_to_minutes(item["Durée HH:MM:SS"])
            if total_minutes > 0:  # Prévenir la division par zéro
                progress = ((total_minutes - remaining_minutes) / total_minutes) * 100
                return round(progress, 2)  # Retourne le pourcentage arrondi à deux décimales
    return None  # Retourne None si l'item n'est pas trouvé

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
                        "progress": progress
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
