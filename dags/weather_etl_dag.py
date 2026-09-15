from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="weather_etl",
    start_date=datetime(2026, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["weather", "etl"],
) as dag:

    extract = BashOperator(
        task_id="extract_weather_data",
        bash_command="python /opt/airflow/src/extract.py",
    )

    transform = BashOperator(
        task_id="transform_weather_data",
        bash_command="python /opt/airflow/src/transform.py",
    )

    load = BashOperator(
        task_id="load_weather_data",
        bash_command="python /opt/airflow/src/load.py",
    )

    extract >> transform >> load
