import json, time, requests, uuid, sys
from datetime import datetime
from confluent_kafka import Producer
from dotenv import load_dotenv
import os

load_dotenv()

TOPIC = os.getenv("KAFKA_TOPIC")
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

# Fix path to cities.json using absolute path resolution
# Script is in /opt/airflow/producers, data is in /opt/airflow/data
current_dir = os.path.dirname(os.path.abspath(__file__))
cities_path = os.path.join(current_dir, '../data/cities.json')

with open(cities_path) as f:
    cities = json.load(f)

p = Producer({'bootstrap.servers': BOOTSTRAP})

def delivery_report(err, msg):
    if err: print(f"Error: {err}")

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,cloud_cover,wind_speed_10m"
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        return r.json()["current"]
    except:
        return None

print("Weather Producer iniciado – Open-Meteo API")
while True:
    for city in cities:
        data = get_weather(city["latitude"], city["longitude"])
        if not data: continue

        event = {
            "event_id": str(uuid.uuid4()),
            "city_id": city["city_id"],
            "city": city["name"],
            "region": city["region"],
            "segment": city["segment"],
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "timestamp": data["time"],
            "temperature_2m": data.get("temperature_2m"),
            "relative_humidity_2m": data.get("relative_humidity_2m"),
            "apparent_temperature": data.get("apparent_temperature"),
            "is_day": bool(data.get("is_day")),
            "precipitation_mm": data.get("precipitation"),
            "weather_code": data.get("weather_code"),
            "cloud_cover": data.get("cloud_cover"),
            "wind_speed_kmh": data.get("wind_speed_10m"),
            "captured_at": datetime.utcnow().isoformat()
        }

        p.produce(TOPIC, key=str(city["city_id"]), value=json.dumps(event).encode(), callback=delivery_report)
        print(f"{city['name']}: {event['temperature_2m']}°C")
    
    p.flush()
    
    # Check for batch mode
    if "--batch" in sys.argv:
        print("Batch mode: Finalizando después de una iteración.")
        break
        
    time.sleep(18)  # cada ~18 segundos todas las ciudades