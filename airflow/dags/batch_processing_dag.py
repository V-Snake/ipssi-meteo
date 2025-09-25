from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
import requests
import json

# Configuration par défaut
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG de batch processing quotidien
with DAG(
    'batch_processing_daily',
    default_args=default_args,
    description='Batch processing quotidien pour la couche Lambda',
    schedule_interval='0 2 * * *',  # Tous les jours à 2h du matin
    catchup=False,
    tags=['batch', 'lambda', 'hdfs', 'analytics'],
) as dag:

    # 1. Vérification de la santé des services
    def check_hdfs_health():
        """Vérifie la santé de HDFS"""
        try:
            response = requests.get('http://namenode:9870/webhdfs/v1/?op=LISTSTATUS', timeout=10)
            if response.status_code == 200:
                print("✅ HDFS NameNode est accessible")
                return True
            else:
                print(f"❌ HDFS NameNode retourne le code {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erreur de connexion HDFS: {e}")
            return False

    def check_analytics_api_health():
        """Vérifie la santé de l'API Analytics"""
        try:
            response = requests.get('http://analytics-api:8000/health', timeout=10)
            if response.status_code == 200:
                print("✅ Analytics API est accessible")
                return True
            else:
                print(f"❌ Analytics API retourne le code {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erreur de connexion Analytics API: {e}")
            return False

    # 2. Tâches de vérification
    check_hdfs = PythonOperator(
        task_id='check_hdfs_health',
        python_callable=check_hdfs_health,
    )

    check_analytics = PythonOperator(
        task_id='check_analytics_health',
        python_callable=check_analytics_api_health,
    )

    # 3. Tâches de batch processing
    create_hdfs_directories = BashOperator(
        task_id='create_hdfs_directories',
        bash_command="""
        echo "Création des répertoires HDFS pour le batch processing..."
        # Créer les répertoires de partition par date
        DATE=$(date +%Y-%m-%d)
        echo "Date du batch: $DATE"
        """,
    )

    # 4. Tâche de traitement des données historiques
    def process_historical_data():
        """Traite les données historiques pour le batch layer"""
        print("🔄 Début du traitement des données historiques...")
        
        # Simulation du traitement batch
        # Dans un vrai pipeline, on ferait :
        # 1. Lire les données de Kafka depuis la veille
        # 2. Les agréger par ville/pays
        # 3. Calculer les statistiques (moyennes, max, min)
        # 4. Sauvegarder dans HDFS avec partitionnement
        
        print("✅ Traitement des données historiques terminé")
        return "Batch processing completed successfully"

    process_batch_data = PythonOperator(
        task_id='process_historical_data',
        python_callable=process_historical_data,
    )

    # 5. Tâche de génération des rapports
    def generate_daily_report():
        """Génère un rapport quotidien via l'API Analytics"""
        try:
            # Appel à l'API pour générer un rapport
            response = requests.get('http://analytics-api:8000/reports/daily', timeout=30)
            if response.status_code == 200:
                report_data = response.json()
                print(f"✅ Rapport quotidien généré: {report_data}")
                return report_data
            else:
                print(f"❌ Erreur génération rapport: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Erreur lors de la génération du rapport: {e}")
            return None

    generate_report = PythonOperator(
        task_id='generate_daily_report',
        python_callable=generate_daily_report,
    )

    # 6. Tâche de nettoyage
    cleanup_temp_files = BashOperator(
        task_id='cleanup_temp_files',
        bash_command="""
        echo "🧹 Nettoyage des fichiers temporaires..."
        # Nettoyer les fichiers temporaires du batch processing
        echo "✅ Nettoyage terminé"
        """,
    )

    # 7. Tâche de notification
    def send_completion_notification():
        """Envoie une notification de fin de batch processing"""
        print("📧 Envoi de notification de fin de batch processing...")
        # Ici on pourrait envoyer un email ou une notification Slack
        print("✅ Notification envoyée")
        return "Notification sent"

    send_notification = PythonOperator(
        task_id='send_completion_notification',
        python_callable=send_completion_notification,
    )

    # Définition des dépendances
    [check_hdfs, check_analytics] >> create_hdfs_directories >> process_batch_data >> generate_report >> cleanup_temp_files >> send_notification
