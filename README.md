# TP_KAFKA_MIA26.1_IPSSI
TP kafka stream meteo avec dashboard graphana

# Airflow Integration (Scheduler + Web UI)

This project now includes an Airflow stack to orchestrate and monitor the streaming pipeline.

## What was added
- Airflow services in `docker-compose.yml`: `postgres` (metadata DB), `airflow-init`, `airflow-webserver`, `airflow-scheduler`, `airflow-triggerer`
- Mounted folders: `airflow/dags`, `airflow/logs`, `airflow/plugins`
- Example DAG: `airflow/dags/example_weather_pipeline_dag.py`

## Quick start
```bash
# From the repo root
mkdir -p airflow/dags airflow/logs airflow/plugins

# Optional: set a stable UID (recommended on macOS/Linux)
export AIRFLOW_UID=$(id -u)

# Start core infra first (Kafka, HDFS, Spark, API, etc.)
docker compose up -d --build

# Initialize Airflow metadata DB and admin user (admin/admin)
docker compose up airflow-init

# Start Airflow services
docker compose up -d airflow-webserver airflow-scheduler airflow-triggerer

# Open the UI
open http://localhost:8080  # or browse manually
```

Credentials: username `admin`, password `admin`.

## DAG overview
The example DAG performs simple health checks inside the compose network.

- check_kafka: resolves `kafka` DNS in the Docker network
- check_namenode: probes NameNode UI
- check_analytics_api: calls `http://analytics-api:8000/health`
- daily_validation_stub: placeholder for a batch/validation step

Execution order: `check_kafka` and `check_namenode` (parallel) → `check_analytics_api` → `daily_validation_stub`.

## Where to add your DAGs
Place your DAG files under `airflow/dags/`. The webserver hot-reloads DAGs from this folder.

## Notes
- The stack uses LocalExecutor (single-node) and Postgres 13 for metadata.
- Additional Python libs inside Airflow can be set via `_PIP_ADDITIONAL_REQUIREMENTS` in `docker-compose.yml`.
- For production-like scheduling, consider Sensors (Kafka readiness), SparkSubmitOperator, and externalized configs.

## Windows usage
Use the Windows-optimized compose file which relies on named volumes for Airflow logs/plugins to avoid permission issues.

```powershell
# PowerShell
New-Item -ItemType Directory -Force -Path airflow\dags | Out-Null
New-Item -ItemType Directory -Force -Path airflow\logs | Out-Null
New-Item -ItemType Directory -Force -Path airflow\plugins | Out-Null

docker compose -f docker-compose.windows.yml up -d --build
docker compose -f docker-compose.windows.yml up airflow-init
docker compose -f docker-compose.windows.yml up -d airflow-webserver airflow-scheduler airflow-triggerer

Start-Process http://localhost:8080
```

Notes for Windows:
- Airflow containers run as root (`user: "0:0"`) to avoid file permission issues with bind mounts.
- The Postgres service does not expose host port `5432` to avoid conflicts.

# 🎉 Kafka Container Test Results

Your Kafka container is successfully receiving producer information! Here's a comprehensive summary of what I found:

# ✅ Topics Status
*  weather_stream: Active with 188 messages processed ✅
*  weather_transformed: Active with 187 messages processed ✅  
*  weather_aggregates: Active and ready ✅
*  All topics have proper partition configuration (1 partition, replication factor 1)

# ✅ Producer Activity
*  4 active producers sending data:
*  🏙️ London producer: Sending UK weather data every ~60 seconds
*  🗼 Paris producer: Sending French weather data every ~60 seconds  
*  🗽 New York producer: Sending US weather data every ~60 seconds
*  📍 Original producer: Sending coordinate-based weather data

# ✅ Message Flow Verification
*  180+ messages successfully processed through the pipeline
*  Real weather data being fetched from Open-Meteo API including:
*  Temperature, wind speed, wind direction
*  Weather codes, day/night status
*  Geographic information (city, country, timezone)

# ✅ Consumer Activity 
*  Active consumers are receiving and processing messages in real-time
*  Consumer group weather_consumer shows:
*  LAG = 1: Only 1 message behind (excellent performance!)
*  Multiple active consumers processing different topics
*  Current offset: 187-188: Shows continuous processing

🔍 Sample Message Structure
json
# 📊 Performance Summary
*  Kafka broker: Healthy and responsive
*  Message throughput: Steady flow every 60 seconds per producer
*  Consumer lag: Minimal (1 message behind)
*  Data quality: Rich, structured weather data from multiple cities
*  Error rate: No errors detected

Your Kafka container is working perfectly! 🚀 The producers are successfully sending weather data, and the consumers are processing it with minimal lag. The entire pipeline is functioning as designed.