from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


def print_hello():
    print("Hello from Airflow!")
    return "Hello World!"


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="simple_test_dag",
    description="Simple test DAG to verify Airflow is working",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=timedelta(minutes=5),
    catchup=False,
) as dag:

    # Simple Python task
    hello_task = PythonOperator(
        task_id="hello_world",
        python_callable=print_hello,
    )

    # Simple bash task
    bash_task = BashOperator(
        task_id="bash_hello",
        bash_command="echo 'Hello from Bash!' && date",
    )

    # List files task
    list_files = BashOperator(
        task_id="list_files",
        bash_command="ls -la /opt/airflow/dags/",
    )

    # Task dependencies
    hello_task >> bash_task >> list_files
