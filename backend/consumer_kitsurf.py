from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "kitesurf-data",
    bootstrap_servers="kafka:9092",
    auto_offset_reset="earliest",
    group_id="debug-kitesurf",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

print("Attente de messages sur kitesurf-data...")
for message in consumer:
    print(" Reçu spot kitesurf :", message.value)
