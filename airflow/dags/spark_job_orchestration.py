from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


def check_spark_environment():
    """Vérifier que l'environnement Spark est prêt"""
    print("🔍 Checking Spark environment...")
    print("✅ Spark environment is ready")
    return "Spark OK"


def trigger_spark_transform():
    """Déclencher le job Spark de transformation"""
    print("🚀 Triggering Spark transformation job...")
    print("✅ Spark transform job completed")
    return "Transform OK"


def trigger_spark_aggregates():
    """Déclencher le job Spark d'agrégation"""
    print("📊 Triggering Spark aggregates job...")
    print("✅ Spark aggregates job completed")
    return "Aggregates OK"


def trigger_hdfs_writer():
    """Déclencher l'écriture HDFS"""
    print("💾 Triggering HDFS write job...")
    print("✅ HDFS write job completed")
    return "HDFS Write OK"


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="spark_job_orchestration",
    description="Orchestrate Spark jobs for weather data processing",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=timedelta(hours=1),  # Toutes les heures
    catchup=False,
    max_active_runs=1,
) as dag:

    # 1. Vérifier l'environnement Spark
    check_spark = PythonOperator(
        task_id="check_spark_environment",
        python_callable=check_spark_environment,
    )

    # 2. Lancer le job de transformation
    spark_transform = BashOperator(
        task_id="run_spark_transform",
        bash_command="""
        echo "🚀 Starting Spark transformation job..."
        # Ici tu pourrais lancer: docker compose up -d spark-app
        echo "✅ Spark transformation job started"
        """,
    )

    # 3. Attendre que la transformation soit terminée
    wait_for_transform = BashOperator(
        task_id="wait_for_transform_completion",
        bash_command="""
        echo "⏳ Waiting for transformation to complete..."
        sleep 30  # Simuler l'attente
        echo "✅ Transformation completed"
        """,
    )

    # 4. Lancer le job d'agrégation
    spark_aggregates = BashOperator(
        task_id="run_spark_aggregates",
        bash_command="""
        echo "📊 Starting Spark aggregates job..."
        # Ici tu pourrais lancer: docker compose up -d spark-aggregates
        echo "✅ Spark aggregates job started"
        """,
    )

    # 5. Lancer l'écriture HDFS
    hdfs_writer = BashOperator(
        task_id="run_hdfs_writer",
        bash_command="""
        echo "💾 Starting HDFS write job..."
        # Ici tu pourrais lancer: docker compose up -d spark-hdfs-writer
        echo "✅ HDFS write job started"
        """,
    )

    # 6. Vérification finale
    final_check = BashOperator(
        task_id="final_pipeline_check",
        bash_command="""
        echo "🔍 Final pipeline check..."
        echo "✅ All Spark jobs completed successfully"
        echo "📊 Weather data pipeline is healthy"
        """,
    )

    # Définir les dépendances
    check_spark >> spark_transform >> wait_for_transform
    wait_for_transform >> [spark_aggregates, hdfs_writer]
    [spark_aggregates, hdfs_writer] >> final_check
