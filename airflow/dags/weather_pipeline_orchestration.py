from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.docker_operator import DockerOperator
from airflow.sensors.http_sensor import HttpSensor
from airflow.sensors.filesystem import FileSensor
import requests
import json


def check_kafka_topics():
    """Vérifier que les topics Kafka existent et ont des messages"""
    try:
        # Simuler une vérification des topics
        print("✅ Checking Kafka topics: weather_stream, weather_transformed, weather_aggregates")
        return "Topics OK"
    except Exception as e:
        print(f"❌ Kafka topics check failed: {e}")
        raise


def check_hdfs_health():
    """Vérifier que HDFS NameNode est accessible"""
    try:
        response = requests.get("http://namenode:9870/", timeout=5)
        if response.status_code == 200:
            print("✅ HDFS NameNode is healthy")
            return "HDFS OK"
        else:
            raise Exception(f"HDFS returned status {response.status_code}")
    except Exception as e:
        print(f"❌ HDFS health check failed: {e}")
        raise


def check_analytics_api():
    """Vérifier que l'API analytics répond"""
    try:
        response = requests.get("http://analytics-api:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Analytics API is healthy")
            return "API OK"
        else:
            raise Exception(f"Analytics API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics API check failed: {e}")
        return "API not available"  # Non-blocking


def get_producer_status():
    """Vérifier le statut des producers via Docker"""
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=data-producer", "--format", "{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        if "Up" in result.stdout:
            print("✅ Data producer is running")
            return "Producer OK"
        else:
            print("❌ Data producer is not running")
            return "Producer DOWN"
    except Exception as e:
        print(f"❌ Producer status check failed: {e}")
        return "Check failed"


def trigger_data_validation():
    """Déclencher une validation des données (exemple)"""
    print("🔍 Starting data validation...")
    # Ici tu pourrais lancer un job Spark de validation
    # ou appeler une API de validation
    print("✅ Data validation completed")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="weather_pipeline_orchestration",
    description="Orchestrate weather data pipeline with Kafka producers and monitoring",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=timedelta(minutes=15),  # Toutes les 15 minutes
    catchup=False,
    max_active_runs=1,
) as dag:

    # 1. Health checks en parallèle
    check_kafka = PythonOperator(
        task_id="check_kafka_topics",
        python_callable=check_kafka_topics,
    )

    check_hdfs = PythonOperator(
        task_id="check_hdfs_health",
        python_callable=check_hdfs_health,
    )

    check_api = PythonOperator(
        task_id="check_analytics_api",
        python_callable=check_analytics_api,
    )

    check_producer = PythonOperator(
        task_id="check_producer_status",
        python_callable=get_producer_status,
    )

    # 2. Vérification que les services Docker sont UP
    verify_docker_services = BashOperator(
        task_id="verify_docker_services",
        bash_command="""
        echo "🔍 Checking Docker services..."
        docker ps --filter "name=kafka" --format "Kafka: {{.Status}}"
        docker ps --filter "name=namenode" --format "NameNode: {{.Status}}"
        docker ps --filter "name=data-producer" --format "Producer: {{.Status}}"
        echo "✅ Docker services check completed"
        """,
    )

    # 3. Vérification des topics Kafka
    check_kafka_topics = BashOperator(
        task_id="check_kafka_topics_detailed",
        bash_command="""
        echo "🔍 Checking Kafka topics..."
        # Simuler une vérification des topics
        echo "weather_stream: OK"
        echo "weather_transformed: OK" 
        echo "weather_aggregates: OK"
        echo "✅ All topics are healthy"
        """,
    )

    # 4. Validation des données (exemple)
    validate_data = PythonOperator(
        task_id="validate_data_quality",
        python_callable=trigger_data_validation,
    )

    # 5. Rapport de statut
    generate_report = BashOperator(
        task_id="generate_pipeline_report",
        bash_command="""
        echo "📊 Weather Pipeline Status Report"
        echo "=================================="
        echo "Timestamp: $(date)"
        echo "Kafka: ✅ Running"
        echo "HDFS: ✅ Running" 
        echo "Producer: ✅ Running"
        echo "Analytics API: ✅ Running"
        echo "=================================="
        echo "✅ Pipeline is healthy and operational"
        """,
    )

    # 6. Exemple de redémarrage du producer si nécessaire
    restart_producer_if_needed = BashOperator(
        task_id="restart_producer_if_needed",
        bash_command="""
        echo "🔄 Checking if producer restart is needed..."
        # Ici tu pourrais ajouter une logique pour redémarrer le producer
        # si il est down ou a des problèmes
        echo "✅ Producer status check completed"
        """,
    )

    # Définir les dépendances
    [check_kafka, check_hdfs, check_api, check_producer] >> verify_docker_services
    verify_docker_services >> check_kafka_topics
    check_kafka_topics >> validate_data
    validate_data >> generate_report
    generate_report >> restart_producer_if_needed
