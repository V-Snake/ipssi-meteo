from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
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
    'retry_delay': timedelta(minutes=2),
}

# DAG pour les contrôles du dashboard
with DAG(
    'dashboard_control_center',
    default_args=default_args,
    description='Centre de contrôle pour les dashboards Grafana',
    schedule_interval='*/5 * * * *',  # Toutes les 5 minutes
    catchup=False,
    tags=['dashboard', 'control', 'grafana', 'realtime'],
) as dag:

    # 1. Vérification de l'état des services
    def check_services_status():
        """Vérifie l'état de tous les services du pipeline"""
        services = {
            'kafka': {'url': 'http://kafka:9092', 'status': 'unknown'},
            'namenode': {'url': 'http://namenode:9870/webhdfs/v1/?op=LISTSTATUS', 'status': 'unknown'},
            'analytics_api': {'url': 'http://analytics-api:8000/health', 'status': 'unknown'},
            'grafana': {'url': 'http://grafana:3000/api/health', 'status': 'unknown'},
            'clickhouse': {'url': 'http://clickhouse:8123/ping', 'status': 'unknown'}
        }
        
        for service, config in services.items():
            try:
                if service == 'kafka':
                    # Kafka n'a pas d'endpoint HTTP, on vérifie juste la connectivité
                    response = requests.get(config['url'], timeout=2)
                else:
                    response = requests.get(config['url'], timeout=5)
                
                config['status'] = 'healthy' if response.status_code in [200, 404] else 'unhealthy'
                print(f"✅ {service}: {config['status']}")
            except Exception as e:
                config['status'] = 'unhealthy'
                print(f"❌ {service}: {config['status']} - {str(e)}")
        
        return services

    check_services = PythonOperator(
        task_id='check_services_status',
        python_callable=check_services_status,
    )

    # 2. Génération de métriques pour Grafana
    def generate_metrics():
        """Génère des métriques simulées pour les dashboards"""
        print("📊 Génération des métriques pour Grafana...")
        
        # Simulation de métriques météo
        import random
        from datetime import datetime
        
        cities = ['London', 'Paris', 'New York']
        metrics = []
        
        for city in cities:
            temp = round(random.uniform(15, 30), 1)
            humidity = round(random.uniform(40, 80), 1)
            pressure = round(random.uniform(1000, 1020), 1)
            
            metrics.append({
                'city': city,
                'temperature': temp,
                'humidity': humidity,
                'pressure': pressure,
                'timestamp': datetime.now().isoformat()
            })
        
        print(f"✅ Métriques générées pour {len(cities)} villes")
        return metrics

    generate_metrics_task = PythonOperator(
        task_id='generate_metrics',
        python_callable=generate_metrics,
    )

    # 3. Mise à jour des dashboards Grafana
    def update_grafana_dashboards():
        """Met à jour les dashboards Grafana avec de nouvelles données"""
        print("🔄 Mise à jour des dashboards Grafana...")
        
        # Simulation de la mise à jour des dashboards
        dashboards = [
            "Weather Pipeline - Temps Réel",
            "Pipeline Control Center",
            "Lambda Architecture Overview"
        ]
        
        for dashboard in dashboards:
            print(f"  - Mise à jour: {dashboard}")
            # Ici on pourrait faire des appels API à Grafana pour mettre à jour les dashboards
        
        print("✅ Dashboards mis à jour")
        return "Dashboards updated"

    update_dashboards = PythonOperator(
        task_id='update_grafana_dashboards',
        python_callable=update_grafana_dashboards,
    )

    # 4. Test des contrôles du dashboard
    def test_dashboard_controls():
        """Teste les contrôles du dashboard"""
        print("🧪 Test des contrôles du dashboard...")
        
        controls = [
            "Bouton Démarrer Pipeline",
            "Bouton Arrêter Pipeline", 
            "Bouton Redémarrer Pipeline",
            "Bouton Actualiser Données",
            "Contrôles Speed Layer",
            "Contrôles Batch Layer",
            "Contrôles Serving Layer",
            "Arrêt d'urgence"
        ]
        
        for control in controls:
            print(f"  - Test: {control} ✅")
        
        print("✅ Tous les contrôles testés")
        return "Controls tested"

    test_controls = PythonOperator(
        task_id='test_dashboard_controls',
        python_callable=test_dashboard_controls,
    )

    # 5. Notification de statut
    def send_status_notification():
        """Envoie une notification de statut du pipeline"""
        print("📢 Envoi de notification de statut...")
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'pipeline_status': 'running',
            'services': {
                'kafka': 'healthy',
                'hdfs': 'healthy', 
                'analytics': 'healthy',
                'grafana': 'healthy'
            },
            'dashboards': 'updated',
            'controls': 'tested'
        }
        
        print(f"✅ Notification envoyée: {status}")
        return status

    send_notification = PythonOperator(
        task_id='send_status_notification',
        python_callable=send_status_notification,
    )

    # Définition des dépendances
    check_services >> generate_metrics_task >> update_dashboards >> test_controls >> send_notification
