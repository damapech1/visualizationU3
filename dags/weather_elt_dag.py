from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'weather_elt_pipeline',
    default_args=default_args,
    description='A simple ELT pipeline for weather data using Kafka and Postgres',
    schedule_interval='@hourly',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['weather', 'elt', 'kafka'],
) as dag:

    # Task 1: Produce data to Kafka (Extract)
    produce_weather = BashOperator(
        task_id='produce_weather_to_kafka',
        bash_command='python /opt/airflow/producers/weather_producer.py --batch',
    )

    # Task 2: Consume data from Kafka to Postgres (Load)
    consume_weather = BashOperator(
        task_id='consume_weather_to_postgres',
        bash_command='python /opt/airflow/consumers/raw_to_postgres.py --batch',
    )

    # Task 3: Transform data in Postgres (Transform)
    transform_weather = PostgresOperator(
        task_id='transform_weather_data',
        postgres_conn_id='postgres_default',
        sql='sql/transform_weather.sql',
    )

    produce_weather >> consume_weather >> transform_weather
