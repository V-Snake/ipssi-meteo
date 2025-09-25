from fastapi import FastAPI, Query
import requests
from kafka import KafkaProducer, errors
import os
import json
from dotenv import load_dotenv
import time

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


@app.get("/weather")
def get_weather(lat: float, lon: float):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={lat},{lon}"
    res = requests.get(url)
    data = res.json()
    producer.send("weather-data", data)
    producer.flush()
    print("Message publié dans Kafka :", data)  
    return {"status": "ok", "data": data}