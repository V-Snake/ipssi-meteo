#!/usr/bin/env python3
"""
Version simplifiée du writer HDFS utilisant l'API WebHDFS
"""
import os
import json
import time
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, from_unixtime, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, IntegerType

def build_weather_stream_schema() -> StructType:
    """Schema pour le topic weather_stream avec informations de partitionnement HDFS"""
    return StructType([
        StructField("city", StringType(), True),
        StructField("country", StringType(), True),
        StructField("admin1", StringType(), True),  # région/état
        StructField("region", StringType(), True),  # Pour partitionnement HDFS
        StructField("continent", StringType(), True),  # Pour partitionnement HDFS
        StructField("timestamp", LongType(), True),  # epoch seconds
        StructField("date", StringType(), True),  # Format YYYY-MM-DD
        StructField("hour", StringType(), True),  # Format HH
        StructField("weather", StructType([
            StructField("temperature", DoubleType(), True),
            StructField("windspeed", DoubleType(), True),
            StructField("winddirection", DoubleType(), True),
            StructField("weathercode", IntegerType(), True),
            StructField("is_day", IntegerType(), True),
            StructField("time", StringType(), True),
        ]), True),
        StructField("location_info", StructType([
            StructField("timezone", StringType(), True),
            StructField("timezone_abbreviation", StringType(), True),
            StructField("elevation", DoubleType(), True),
        ]), True),
    ])

def is_namenode_in_safemode(namenode_host: str = "namenode", http_port: int = 9870) -> bool:
    """Retourne True si le NameNode est en SafeMode, sinon False.

    S'appuie sur l'endpoint JMX NameNodeInfo.Safemode (string vide s'il est OFF).
    """
    try:
        jmx_url = f"http://{namenode_host}:{http_port}/jmx?get=Hadoop:service=NameNode,name=NameNodeInfo::Safemode"
        resp = requests.get(jmx_url, timeout=3)
        if resp.ok:
            data = resp.json()
            beans = data.get("beans", [])
            if beans:
                safemode_str = beans[0].get("Safemode", "") or ""
                return len(safemode_str.strip()) > 0
    except Exception:
        # En cas d'erreur réseau, être conservateur pendant le démarrage
        return True
    return False

def wait_for_safemode_exit(max_wait_seconds: int = 60) -> None:
    """Attend la sortie du SafeMode (jusqu'à max_wait_seconds)."""
    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        if not is_namenode_in_safemode():
            return
        time.sleep(2)
    # On sort quand même après le délai, au cas où (les écritures auront des retries)

def write_to_hdfs_webhdfs(data, hdfs_namenode, hdfs_path):
    """Écrire des données dans HDFS via l'API WebHDFS"""
    try:
        # Créer le chemin de partitionnement
        city = data.get('city', 'Unknown')
        country = data.get('country', 'Unknown')

        # Extraire la date et l'heure depuis le timestamp ou weather.time
        weather_time = data.get('weather', {}).get('time')
        if weather_time:
            # Format: "2025-09-22T20:30" -> date="2025-09-22", hour="20"
            date = weather_time.split('T')[0]
            hour = weather_time.split('T')[1].split(':')[0]
        else:
            # Fallback sur le timestamp epoch
            timestamp = data.get('timestamp', int(time.time()))
            date = time.strftime("%Y-%m-%d", time.gmtime(timestamp))
            hour = time.strftime("%H", time.gmtime(timestamp))

        partition_path = f"{hdfs_path}/city={city}/country={country}/date={date}/hour={hour}"

        # URL WebHDFS
        create_dir_url = f"http://namenode:9870/webhdfs/v1{partition_path}?op=MKDIRS"
        filename = f"weather_{int(time.time() * 1000)}.json"
        file_path = f"{partition_path}/{filename}"
        write_url = f"http://namenode:9870/webhdfs/v1{file_path}?op=CREATE&overwrite=true"

        # Politique de retry simple sur SafeMode (403/500 avec SafeModeException)
        max_retries = 10
        backoff_seconds = 2

        # S'assurer que le répertoire existe (best-effort)
        try:
            requests.put(create_dir_url, timeout=5)
        except Exception:
            pass

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.put(write_url, data=json.dumps(data, indent=2), timeout=10)
            except Exception as e:
                # Réessayer sur erreurs transitoires réseau
                if attempt == max_retries:
                    print(f"❌ Erreur WebHDFS (réseau): {e}")
                    return False
                time.sleep(backoff_seconds)
                backoff_seconds = min(backoff_seconds * 2, 20)
                continue

            if response.status_code == 201:
                print(f"✅ Écrit dans HDFS: {file_path}")
                return True

            body = (response.text or "").lower()
            is_safemode_error = response.status_code in (403, 500) and ("safemode" in body or "safe mode" in body)
            if is_safemode_error and attempt < max_retries:
                # Attendre sortie du safemode puis retry avec backoff
                wait_for_safemode_exit(max_wait_seconds=30)
                time.sleep(backoff_seconds)
                backoff_seconds = min(backoff_seconds * 2, 20)
                continue

            # Autres erreurs -> pas de retry
            print(f"❌ Erreur écriture HDFS: {response.status_code} - {response.text}")
            return False

        # Épuisement des retries
        print("❌ Abandon après plusieurs tentatives en SafeMode")
        return False

    except Exception as e:
        print(f"❌ Erreur WebHDFS: {e}")
        return False

def main() -> None:
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
    source_topic = os.getenv("SOURCE_TOPIC", "weather_stream")
    hdfs_namenode = os.getenv("HDFS_NAMENODE", "hdfs://namenode:9000")
    hdfs_path = os.getenv("HDFS_PATH", "/weather-data")
    # Optionnel: support d'un topic historique
    history_topic = os.getenv("HISTORY_TOPIC", "weather_history_raw")
    history_base = os.getenv("HISTORY_BASE_PATH", "/hdfs-data")
    checkpoint_dir = os.getenv("CHECKPOINT_DIR", "/tmp/checkpoints/hdfs_writer")

    # Créer la session Spark
    spark = (
        SparkSession.builder
        .appName("weather-hdfs-writer-simple")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .getOrCreate()
    )
    
    spark.sparkContext.setLogLevel("WARN")
    
    # Lire le stream depuis Kafka
    raw_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", kafka_bootstrap)
        .option("subscribe", source_topic)
        .option("startingOffsets", "latest")
        .load()
    )
    
    # Parse JSON data
    stream_schema = build_weather_stream_schema()
    parsed_df = raw_df.select(
        from_json(col("value").cast("string"), stream_schema).alias("data"),
        col("timestamp").alias("kafka_timestamp")
    ).select("data.*")
    
    # Fonction pour écrire dans HDFS
    def write_batch(batch_df, batch_id):
        """Fonction pour écrire chaque batch dans HDFS"""
        print(f"📝 Traitement du batch {batch_id}")
        # Si le NN est en SafeMode, attendre un court instant
        wait_for_safemode_exit(max_wait_seconds=60)
        
        # Itérer en streaming pour éviter de charger tout le batch en mémoire/disque
        for row in batch_df.toLocalIterator():
            data = row.asDict()
            data = {k: v for k, v in data.items() if v is not None}
            write_to_hdfs_webhdfs(data, hdfs_namenode, hdfs_path)
    
    # Écrire dans HDFS avec foreachBatch
    query = (
        parsed_df.writeStream
        .foreachBatch(write_batch)
        .outputMode("append")
        .start()
    )

    # Branche optionnelle: consommer le topic historique et écrire sous /hdfs-data/{country}/{city}/weather_history_raw
    def write_history_batch(batch_df, batch_id):
        print(f"🗃️  Batch historique {batch_id}")
        for row in batch_df.toLocalIterator():
            data = row.asDict()
            data = {k: v for k, v in data.items() if v is not None}
            country = data.get("country", "Unknown")
            city = data.get("city", "Unknown")
            date = data.get("date", time.strftime("%Y-%m-%d", time.gmtime()))
            hour = data.get("hour", time.strftime("%H", time.gmtime()))
            # Chemin dédié historique
            hist_path = f"{history_base}/{country}/{city}/weather_history_raw/date={date}/hour={hour}"
            # Crée dossier
            try:
                requests.put(f"http://namenode:9870/webhdfs/v1{hist_path}?op=MKDIRS", timeout=5)
            except Exception:
                pass
            # Écrit fichier
            fname = f"history_{int(time.time()*1000)}.json"
            file_path = f"{hist_path}/{fname}"
            try:
                r = requests.put(f"http://namenode:9870/webhdfs/v1{file_path}?op=CREATE&overwrite=true", data=json.dumps(data), timeout=10)
                if r.status_code in (200, 201):
                    print(f"✅ Historique écrit: {file_path}")
                else:
                    print(f"❌ Historique erreur {r.status_code}: {r.text}")
            except Exception as e:
                print(f"❌ Historique exception: {e}")

    history_raw = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", kafka_bootstrap)
        .option("subscribe", history_topic)
        .option("startingOffsets", "latest")
        .load()
    )

    hist_parsed = history_raw.select(from_json(col("value").cast("string"), build_weather_stream_schema()).alias("data")).select("data.*")

    hist_query = (
        hist_parsed.writeStream
        .foreachBatch(write_history_batch)
        .outputMode("append")
        .start()
    )
    
    print("🚀 Service HDFS Writer démarré (version simplifiée)")
    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    main()
