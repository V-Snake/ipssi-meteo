from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'weather-data',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    group_id='debug-group1',  # <-- change à chaque test pour forcer la lecture depuis le début
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Attente de messages sur weather-data...")
for message in consumer:
    print("Reçu :", message.value)