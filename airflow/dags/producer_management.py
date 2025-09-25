from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import subprocess
import time


def start_producer():
    """Démarrer le data-producer via Docker Compose"""
    try:
        result = subprocess.run(
            ["docker", "compose", "up", "-d", "data-producer"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("✅ Data producer started successfully")
            return "Producer started"
        else:
            print(f"❌ Failed to start producer: {result.stderr}")
            raise Exception(f"Producer start failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error starting producer: {e}")
        raise


def stop_producer():
    """Arrêter le data-producer"""
    try:
        result = subprocess.run(
            ["docker", "compose", "stop", "data-producer"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("✅ Data producer stopped successfully")
            return "Producer stopped"
        else:
            print(f"❌ Failed to stop producer: {result.stderr}")
            raise Exception(f"Producer stop failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error stopping producer: {e}")
        raise


def restart_producer():
    """Redémarrer le data-producer"""
    try:
        print("🔄 Restarting data producer...")
        # Arrêter d'abord
        stop_result = subprocess.run(
            ["docker", "compose", "stop", "data-producer"],
            capture_output=True, text=True, timeout=30
        )
        
        # Attendre un peu
        time.sleep(5)
        
        # Redémarrer
        start_result = subprocess.run(
            ["docker", "compose", "up", "-d", "data-producer"],
            capture_output=True, text=True, timeout=30
        )
        
        if start_result.returncode == 0:
            print("✅ Data producer restarted successfully")
            return "Producer restarted"
        else:
            raise Exception(f"Producer restart failed: {start_result.stderr}")
    except Exception as e:
        print(f"❌ Error restarting producer: {e}")
        raise


def check_producer_logs():
    """Vérifier les logs du producer"""
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", "10", "data-producer"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("📋 Recent producer logs:")
            print(result.stdout)
            return "Logs retrieved"
        else:
            print(f"❌ Failed to get logs: {result.stderr}")
            return "Logs unavailable"
    except Exception as e:
        print(f"❌ Error getting logs: {e}")
        return "Logs error"


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


# DAG pour démarrer le producer
with DAG(
    dag_id="start_weather_producer",
    description="Start the weather data producer",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manuel uniquement
    catchup=False,
) as dag:

    start_producer_task = PythonOperator(
        task_id="start_data_producer",
        python_callable=start_producer,
    )

    check_logs_task = PythonOperator(
        task_id="check_producer_logs",
        python_callable=check_producer_logs,
    )

    start_producer_task >> check_logs_task


# DAG pour arrêter le producer
with DAG(
    dag_id="stop_weather_producer",
    description="Stop the weather data producer",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manuel uniquement
    catchup=False,
) as dag:

    stop_producer_task = PythonOperator(
        task_id="stop_data_producer",
        python_callable=stop_producer,
    )


# DAG pour redémarrer le producer
with DAG(
    dag_id="restart_weather_producer",
    description="Restart the weather data producer",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manuel uniquement
    catchup=False,
) as dag:

    restart_producer_task = PythonOperator(
        task_id="restart_data_producer",
        python_callable=restart_producer,
    )

    check_logs_after_restart = PythonOperator(
        task_id="check_logs_after_restart",
        python_callable=check_producer_logs,
    )

    restart_producer_task >> check_logs_after_restart
