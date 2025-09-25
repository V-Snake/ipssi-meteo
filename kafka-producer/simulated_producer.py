import json
import time
import sys
import os
import random
from datetime import datetime
from kafka import KafkaProducer

# Configuration Kafka
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC = os.getenv('TOPIC', 'weather_stream')

# Configuration Ville/Pays depuis variables d'environnement ou arguments
if len(sys.argv) >= 3:
    CITY = sys.argv[1]
    COUNTRY = sys.argv[2]
    print(f"📍 Arguments utilisés: {CITY}, {COUNTRY}")
else:
    CITY = os.getenv('CITY', 'Paris')
    COUNTRY = os.getenv('COUNTRY', 'France')
    print(f"🌍 Variables d'environnement utilisées: {CITY}, {COUNTRY}")

# Retry until Kafka is available
producer = None
while producer is None:
    try:
        print("⏳ Trying to connect to Kafka...")
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("✅ Kafka producer connected.")
    except Exception as e:
        print(f"❌ Kafka not ready yet: {e}")
        time.sleep(2)

def get_region_from_country(country):
    """Détermine la région géographique pour le partitionnement HDFS"""
    region_mapping = {
        "France": "Europe",
        "United Kingdom": "Europe", 
        "Germany": "Europe",
        "Spain": "Europe",
        "Italy": "Europe",
        "United States": "North America",
        "Canada": "North America",
        "Mexico": "North America",
        "Brazil": "South America",
        "Argentina": "South America",
        "China": "Asia",
        "Japan": "Asia",
        "India": "Asia",
        "Australia": "Oceania",
        "New Zealand": "Oceania"
    }
    return region_mapping.get(country, "Other")

def generate_simulated_weather_data(city, country):
    """Génère des données météo simulées réalistes"""
    
    # Coordonnées simulées basées sur la ville
    coordinates = {
        "Paris": {"lat": 48.8566, "lon": 2.3522},
        "London": {"lat": 51.5074, "lon": -0.1278},
        "New York": {"lat": 40.7128, "lon": -74.0060},
        "Tokyo": {"lat": 35.6762, "lon": 139.6503},
        "Sydney": {"lat": -33.8688, "lon": 151.2093}
    }
    
    coords = coordinates.get(city, {"lat": 48.8566, "lon": 2.3522})
    
    # Génération de données météo réalistes
    base_temp = {
        "Paris": 15,
        "London": 12,
        "New York": 18,
        "Tokyo": 20,
        "Sydney": 22
    }.get(city, 15)
    
    # Variation de température selon l'heure
    hour = datetime.now().hour
    temp_variation = random.uniform(-5, 5)
    temperature = base_temp + temp_variation + (hour - 12) * 0.5
    
    # Génération d'autres métriques
    humidity = random.uniform(40, 80)
    pressure = random.uniform(1000, 1020)
    wind_speed = random.uniform(5, 25)
    wind_direction = random.randint(0, 360)
    
    # Conditions météo
    conditions = ["sunny", "partly_cloudy", "cloudy", "rainy", "snowy"]
    weather_code = random.choice(conditions)
    
    # Données simulées
    weather_data = {
        "timestamp": datetime.now().isoformat(),
        "city": city,
        "country": country,
        "region": get_region_from_country(country),
        "coordinates": {
            "latitude": coords["lat"],
            "longitude": coords["lon"]
        },
        "weather": {
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "pressure": round(pressure, 1),
            "wind_speed": round(wind_speed, 1),
            "wind_direction": wind_direction,
            "condition": weather_code,
            "visibility": random.uniform(5, 15)
        },
        "source": "simulated",
        "version": "2.0"
    }
    
    return weather_data

print(f"🌤️  Starting simulated weather data producer...")
print(f"📍 Location: {CITY}, {COUNTRY}")
print(f"📡 Sending to topic: {TOPIC}")
print("=" * 50)

try:
    while True:
        try:
            # Générer des données météo simulées
            data = generate_simulated_weather_data(CITY, COUNTRY)
            
            if data:
                # Envoyer les données au topic Kafka
                producer.send(TOPIC, data)
                print(f"🚀 Simulated weather data sent: {json.dumps(data, indent=2)}")
            else:
                print("⚠️  No weather data generated, skipping this cycle")
            
            # Attendre 30 secondes avant la prochaine requête
            print("⏳ Waiting 30 seconds before next update...")
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n🛑 Producer stopped by user")
            break
        except Exception as e:
            print(f"❌ Failed to send data: {e}")
            print("⏳ Retrying in 10 seconds...")
            time.sleep(10)

except Exception as e:
    print(f"❌ Producer failed: {e}")
finally:
    if producer:
        producer.close()
        print("🔌 Producer connection closed.")
