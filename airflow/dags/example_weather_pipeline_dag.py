from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


with DAG(
    dag_id="example_weather_pipeline",
    description="Orchestrate weather streaming pipeline healthchecks and batch triggers",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=timedelta(minutes=10),
    catchup=False,
) as dag:

    # Simple health check to ensure Kafka and NameNode are reachable from the compose network
    check_kafka = BashOperator(
        task_id="check_kafka",
        bash_command="bash -c 'getent hosts kafka && echo OK'",
    )

    check_namenode = BashOperator(
        task_id="check_namenode",
        bash_command="bash -c 'curl -sf http://namenode:9870/ | head -n1 && echo OK'",
    )

    # Trigger a lightweight read via analytics API to validate HDFS contents path wiring
    check_analytics_api = BashOperator(
        task_id="check_analytics_api",
        bash_command="bash -c 'curl -sf http://analytics-api:8000/health || true'",
    )

    # Example of a daily compaction or validation stub (to be replaced by Spark submit if needed)
    daily_stub = BashOperator(
        task_id="daily_validation_stub",
        bash_command="echo 'Run daily validation or compaction here'",
    )

    [check_kafka, check_namenode] >> check_analytics_api >> daily_stub


