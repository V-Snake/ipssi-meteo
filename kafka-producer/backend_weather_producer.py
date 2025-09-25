import json
import time
import sys
import os
import random
import requests
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

# Configuration Kafka
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
PLACES_TOPIC = os.getenv('PLACES_TOPIC', 'place')
WEATHER_TOPIC = os.getenv('WEATHER_TOPIC', 'weather_stream')
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://backend-api:8000')

print(f"🌍 Backend Weather Producer v1.0")
print(f"📡 Reading places from topic: {PLACES_TOPIC}")
print(f"📤 Sending weather to topic: {WEATHER_TOPIC}")
print(f"🔗 Backend API: {BACKEND_API_URL}")
print("=" * 60)

# Retry until Kafka is available
producer = None
consumer = None

while producer is None or consumer is None:
    try:
        print("⏳ Trying to connect to Kafka...")
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        consumer = KafkaConsumer(
            PLACES_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='backend-weather-producer-group'
        )
        print("✅ Kafka producer and consumer connected.")
    except Exception as e:
        print(f"❌ Kafka not ready yet: {e}")
        time.sleep(2)

def get_region_from_coordinates(lat, lon):
    """Détermine la région géographique basée sur les coordonnées"""
    if 35 <= lat <= 70 and -25 <= lon <= 40:
        return "Europe"
    elif 25 <= lat <= 70 and -170 <= lon <= -50:
        return "North America"
    elif -60 <= lat <= 15 and -85 <= lon <= -30:
        return "South America"
    elif 10 <= lat <= 70 and 70 <= lon <= 180:
        return "Asia"
    elif -50 <= lat <= -10 and 110 <= lon <= 180:
        return "Oceania"
    else:
        return "Other"

def get_weather_from_backend(lat, lon):
    """Récupère les données météo depuis le backend API"""
    try:
        response = requests.get(f"{BACKEND_API_URL}/weather", params={"lat": lat, "lon": lon}, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error calling backend API: {e}")
        return None

def generate_simulated_weather_data(place_data):
    """Génère des données météo simulées réalistes basées sur les coordonnées"""
    
    lat = place_data.get('latitude', 0)
    lon = place_data.get('longitude', 0)
    name = place_data.get('name', 'Unknown')
    country = place_data.get('country', 'Unknown')
    
    # Génération de données météo réalistes basées sur la latitude
    base_temp = 30 - (abs(lat) * 0.7)  # Température décroît avec la latitude
    
    # Variation de température selon l'heure et la saison
    hour = datetime.now().hour
    temp_variation = random.uniform(-8, 8)
    temperature = base_temp + temp_variation + (hour - 12) * 0.3
    
    # Ajustement pour l'hémisphère sud
    if lat < 0:
        temperature += random.uniform(-5, 5)  # Variation saisonnière
    
    # Génération d'autres métriques
    humidity = random.uniform(30, 90)
    pressure = random.uniform(980, 1030)
    wind_speed = random.uniform(0, 30)
    wind_direction = random.randint(0, 360)
    
    # Conditions météo (plus réalistes selon la latitude)
    if abs(lat) > 60:  # Zones polaires
        conditions = ["snowy", "cloudy", "partly_cloudy"]
    elif abs(lat) > 30:  # Zones tempérées
        conditions = ["sunny", "partly_cloudy", "cloudy", "rainy"]
    else:  # Zones tropicales
        conditions = ["sunny", "partly_cloudy", "rainy"]
    
    weather_code = random.choice(conditions)
    
    # Données simulées
    weather_data = {
        "timestamp": datetime.now().isoformat(),
        "place": {
            "name": name,
            "country": country,
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            },
            "region": get_region_from_coordinates(lat, lon)
        },
        "weather": {
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "pressure": round(pressure, 1),
            "wind_speed": round(wind_speed, 1),
            "wind_direction": wind_direction,
            "condition": weather_code,
            "visibility": round(random.uniform(5, 20), 1),
            "uv_index": random.randint(0, 11)
        },
        "source": "backend_simulated",
        "version": "1.0"
    }
    
    return weather_data

def process_places_message(places_data):
    """Traite un message contenant une liste de lieux"""
    try:
        if isinstance(places_data, dict) and 'places' in places_data:
            places = places_data['places']
        elif isinstance(places_data, list):
            places = places_data
        else:
            print(f"⚠️ Format de message non reconnu: {type(places_data)}")
            return
        
        print(f"📍 Processing {len(places)} places...")
        
        for i, place in enumerate(places):
            try:
                # Vérifier que le lieu a les coordonnées nécessaires
                if 'latitude' not in place or 'longitude' not in place:
                    print(f"⚠️ Place {i+1} missing coordinates, skipping...")
                    continue
                
                lat = place['latitude']
                lon = place['longitude']
                name = place.get('name', 'Unknown')
                
                # Essayer d'abord l'API backend, sinon simulation
                print(f"🌤️ Getting weather for {name} ({lat}, {lon})...")
                
                # Pour l'instant, on utilise la simulation (l'API backend nécessite une clé API)
                weather_data = generate_simulated_weather_data(place)
                
                # Envoyer les données météo
                producer.send(WEATHER_TOPIC, weather_data)
                print(f"🚀 Weather data sent for {name}")
                
                # Petite pause entre les envois
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error processing place {i+1}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error processing places message: {e}")

print("🔄 Starting backend weather producer...")
print("📋 Waiting for places data from topic 'place'...")

try:
    for message in consumer:
        try:
            places_data = message.value
            print(f"\n📨 Received places data: {json.dumps(places_data, indent=2)}")
            
            # Traiter les lieux
            process_places_message(places_data)
            
            print(f"✅ Processed message from topic '{PLACES_TOPIC}'")
            print("⏳ Waiting for next places data...")
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            continue

except KeyboardInterrupt:
    print("\n🛑 Producer stopped by user")
except Exception as e:
    print(f"❌ Producer failed: {e}")
finally:
    if producer:
        producer.close()
        print("🔌 Producer connection closed.")
    if consumer:
        consumer.close()
        print("🔌 Consumer connection closed.")
