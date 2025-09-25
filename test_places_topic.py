#!/usr/bin/env python3
import json
from kafka import KafkaConsumer
import os

# Configuration Kafka
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
PLACES_TOPIC = 'place'

print(f"🔍 Test du topic '{PLACES_TOPIC}'")
print(f"📡 Broker: {KAFKA_BROKER}")
print("=" * 50)

try:
    consumer = KafkaConsumer(
        PLACES_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='test-group'
    )
    
    print("✅ Connexion Kafka réussie")
    print("📋 Écoute des messages...")
    
    message_count = 0
    for message in consumer:
        message_count += 1
        print(f"\n📨 Message #{message_count}:")
        print(f"   Topic: {message.topic}")
        print(f"   Partition: {message.partition}")
        print(f"   Offset: {message.offset}")
        print(f"   Data: {json.dumps(message.value, indent=2)}")
        
        if message_count >= 3:  # Limiter à 3 messages
            break
    
    if message_count == 0:
        print("⚠️ Aucun message trouvé dans le topic")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
finally:
    if 'consumer' in locals():
        consumer.close()
        print("🔌 Connexion fermée")
