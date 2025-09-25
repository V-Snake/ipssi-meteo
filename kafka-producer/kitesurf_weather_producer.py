import json
import time
import sys
import os
import random
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

# Configuration Kafka
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
PLACES_TOPIC = os.getenv('PLACES_TOPIC', 'place')
WEATHER_TOPIC = os.getenv('WEATHER_TOPIC', 'weather_stream')

print(f"🏄 Kitesurf Weather Producer v1.0")
print(f"📡 Reading places from topic: {PLACES_TOPIC}")
print(f"📤 Sending weather to topic: {WEATHER_TOPIC}")
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
            group_id='kitesurf-weather-producer-group'
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

def get_wind_conditions_for_kitesurf(lat, lon):
    """Génère des conditions de vent spécifiques au kitesurf"""
    # Conditions de vent plus réalistes pour le kitesurf
    base_wind_speed = random.uniform(15, 35)  # 15-35 km/h idéal pour kitesurf
    
    # Variation selon la latitude (plus de vent près des côtes)
    if abs(lat) < 30:  # Zones tropicales
        base_wind_speed += random.uniform(5, 15)
    elif abs(lat) > 60:  # Zones polaires
        base_wind_speed += random.uniform(-5, 10)
    
    wind_direction = random.randint(0, 360)
    
    # Conditions météo adaptées au kitesurf
    conditions = ["sunny", "partly_cloudy", "cloudy"]
    weather_code = random.choice(conditions)
    
    return {
        "wind_speed": round(base_wind_speed, 1),
        "wind_direction": wind_direction,
        "condition": weather_code,
        "kitesurf_rating": "excellent" if base_wind_speed > 25 else "good" if base_wind_speed > 20 else "fair"
    }

def generate_kitesurf_weather_data(place_data):
    """Génère des données météo spécialisées pour le kitesurf"""
    
    lat = place_data.get('latitude', 0)
    lon = place_data.get('longitude', 0)
    name = place_data.get('name', 'Unknown')
    country = place_data.get('country', 'Unknown')
    spot_type = place_data.get('type', 'unknown')
    
    # Génération de données météo réalistes basées sur la latitude
    base_temp = 30 - (abs(lat) * 0.7)  # Température décroît avec la latitude
    
    # Variation de température selon l'heure
    hour = datetime.now().hour
    temp_variation = random.uniform(-8, 8)
    temperature = base_temp + temp_variation + (hour - 12) * 0.3
    
    # Ajustement pour l'hémisphère sud
    if lat < 0:
        temperature += random.uniform(-5, 5)
    
    # Conditions de vent spécialisées kitesurf
    wind_conditions = get_wind_conditions_for_kitesurf(lat, lon)
    
    # Génération d'autres métriques
    humidity = random.uniform(40, 85)
    pressure = random.uniform(980, 1030)
    visibility = random.uniform(8, 20)
    
    # Données météo spécialisées kitesurf
    weather_data = {
        "timestamp": datetime.now().isoformat(),
        "place": {
            "name": name,
            "country": country,
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            },
            "region": get_region_from_coordinates(lat, lon),
            "type": spot_type,
            "osm_id": place_data.get('osm_id'),
            "tags": place_data.get('tags', {})
        },
        "weather": {
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "pressure": round(pressure, 1),
            "visibility": round(visibility, 1),
            "uv_index": random.randint(0, 11),
            **wind_conditions  # Inclut wind_speed, wind_direction, condition, kitesurf_rating
        },
        "kitesurf": {
            "spot_quality": random.choice(["excellent", "good", "fair", "poor"]),
            "crowd_level": random.choice(["low", "medium", "high"]),
            "water_temperature": round(temperature - random.uniform(2, 8), 1),
            "wave_height": round(random.uniform(0.5, 3.0), 1),
            "tide_condition": random.choice(["low", "rising", "high", "falling"])
        },
        "source": "kitesurf_simulated",
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
                
                # Générer les données météo spécialisées kitesurf
                weather_data = generate_kitesurf_weather_data(place)
                
                # Envoyer les données météo
                producer.send(WEATHER_TOPIC, weather_data)
                print(f"🏄 Kitesurf weather data sent for {place.get('name', 'Unknown')} ({place.get('latitude')}, {place.get('longitude')})")
                
                # Petite pause entre les envois
                time.sleep(0.2)
                
            except Exception as e:
                print(f"❌ Error processing place {i+1}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error processing places message: {e}")

print("🔄 Starting kitesurf weather producer...")
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
