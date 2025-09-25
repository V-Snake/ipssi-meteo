from fastapi import FastAPI, Query
import requests
from kafka import KafkaProducer, errors
import os
import json
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv(dotenv_path="./config.env")  # Charge les variables d'environnement

app = FastAPI()
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "changeme")

# Boucle pour attendre Kafka si pas prêt
producer = None
for i in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Kafka Producer connecté !")
        break
    except errors.NoBrokersAvailable:
        print(f"Kafka pas prêt, tentative {i+1}/10...")
        time.sleep(2)
if producer is None:
    raise Exception("Impossible de connecter à Kafka après plusieurs tentatives.")

if producer is None:
    raise Exception("Impossible de se connecter à Kafka après plusieurs tentatives.")


# Endpoint supprimé - on utilise maintenant les spots kitesurf via /send-kitesurf

# Endpoint pour récupérer la liste des spots (pour Grafana)
@app.get("/spots")
def get_spots():
    try:
        with open("surfspots-france.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"status": "error", "message": str(e)}

    elements = data.get("elements", [])
    spots = []
    
    for spot in elements:
        if "lat" in spot and "lon" in spot:
            spot_data = {
                "id": spot.get("id"),
                "name": spot.get("tags", {}).get("name", f"Kitesurf Spot {spot.get('id', 'Unknown')}"),
                "latitude": spot["lat"],
                "longitude": spot["lon"],
                "tags": spot.get("tags", {}),
                "country": "France"
            }
            spots.append(spot_data)
    
    return {"status": "ok", "spots": spots, "count": len(spots)}

# Endpoint pour envoyer les données météo d'un spot spécifique
@app.get("/weather/{spot_id}")
def get_weather_for_spot(spot_id: int):
    try:
        with open("surfspots-france.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"status": "error", "message": str(e)}

    elements = data.get("elements", [])
    spot = None
    
    # Trouver le spot par ID
    for element in elements:
        if element.get("id") == spot_id and "lat" in element and "lon" in element:
            spot = element
            break
    
    if not spot:
        return {"status": "error", "message": "Spot not found"}
    
    # Générer des données météo simulées pour ce spot
    import random
    lat = spot["lat"]
    lon = spot["lon"]
    
    # Données météo simulées
    weather_data = {
        "timestamp": datetime.now().isoformat(),
        "spot": {
            "id": spot["id"],
            "name": spot.get("tags", {}).get("name", f"Kitesurf Spot {spot['id']}"),
            "latitude": lat,
            "longitude": lon,
            "country": "France"
        },
        "weather": {
            "temperature": round(random.uniform(15, 25), 1),
            "humidity": round(random.uniform(40, 80), 1),
            "wind_speed": round(random.uniform(15, 35), 1),
            "wind_direction": random.randint(0, 360),
            "condition": random.choice(["sunny", "partly_cloudy", "cloudy"]),
            "kitesurf_rating": random.choice(["excellent", "good", "fair"])
        }
    }
    
    # Envoyer vers weather_stream
    producer.send("weather_stream", weather_data)
    producer.flush()
    
    print(f"🌤️ Weather data sent for spot {spot_id}: {spot.get('tags', {}).get('name', 'Unknown')}")
    return {"status": "ok", "data": weather_data}