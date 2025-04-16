"""Master DAG for orchestrating the complete Divvy Bikeshare data pipeline.

This DAG coordinates the execution of the following sub-DAGs in sequence:
1. Data Extraction: Downloads raw data from Divvy Bikeshare
2. Data Transformation: Processes data using Azure Spark
3. BigQuery Loading: Loads transformed data into BigQuery
4. DBT Transformation: Applies business logic transformations
"""

from airflow import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from datetime import datetime

# Default configuration
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 4, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1
}

with DAG(
    dag_id='divvy_bikeshare_master_pipeline',
    schedule_interval="@monthly",
    start_date=datetime(2020, 4, 1),
    catchup=False,
) as dag:

    extract = TriggerDagRunOperator(
        task_id='extract_from_source',
        trigger_dag_id='divvy_bikeshare_data_extract',
        conf={"execution_date": "{{ ds }}"},
        wait_for_completion=True
    )

    transform = TriggerDagRunOperator(
        task_id='transformation_azure_spark_pool',
        trigger_dag_id='divvy_bikeshare_pyspark_transformation',
        conf={"execution_date": "{{ ds }}"},
        wait_for_completion=True
    )

    load = TriggerDagRunOperator(
        task_id='load_to_bigquery',
        trigger_dag_id='divvy_bikeshare_bigquery_feed',
        conf={"execution_date": "{{ ds }}"},
        wait_for_completion=True
    )

    dbt = TriggerDagRunOperator(
        task_id='dbt_transformation',
        trigger_dag_id='divvy_bikeshare_dbt_pipeline',
        conf={"execution_date": "{{ ds }}"},
    )
    
    extract >> transform >> load >> dbt