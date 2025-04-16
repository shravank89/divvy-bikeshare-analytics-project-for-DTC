"""Azure Synapse Spark Transformation DAG for Divvy Bikeshare Data.

This DAG orchestrates the transformation of Divvy Bikeshare data using Azure Synapse Analytics
PySpark jobs. It handles the execution of Spark batch jobs for processing monthly bikeshare data.

Dependencies:
    - Azure Synapse workspace with configured Spark pool
    - Airflow connection 'azure_synapse_connection' configured
    - Required Airflow variables:
        - pyspark_script_file_path: Path to the PySpark transformation script
        - base_path: Base storage path for data
        - input_directory: Directory containing raw data
        - output_directory: Directory for transformed data
        - input_file_name_base: Base name pattern for input files

The DAG performs the following steps:
    1. Extracts year and month from execution context
    2. Submits a Spark batch job to transform the corresponding monthly data

The Spark job configuration includes memory settings and other parameters optimized for
the transformation workload.
"""


from typing import Dict, Any
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.microsoft.azure.operators.synapse import AzureSynapseRunSparkBatchOperator
from airflow.exceptions import AirflowException
from airflow.models import Variable

# Constants
DAG_ID = 'divvy_bikeshare_pyspark_transformation'
SPARK_POOL = 'pyspark'
DATE_FORMAT = '%Y-%m-%d'

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email_on_retry': False
}

def get_year_month(**context) -> Dict[str, Any]:
    """Extract year and month from the execution context.

    This function retrieves the execution date either from the DAG run configuration
    or falls back to the logical date. It then extracts the year and month values.

    Args:
        **context: The Airflow task context containing execution information.

    Returns:
        Dict[str, Any]: A dictionary containing 'year' and 'month' keys.

    Raises:
        AirflowException: If year or month extraction fails.
    """
    try:
        # Get date from trigger configuration or fallback to logical date
        if 'dag_run' in context and context['dag_run'].conf:
            date_str = context['dag_run'].conf.get('execution_date')
            run_date = datetime.strptime(date_str, DATE_FORMAT) if date_str else context['logical_date']
        else:
            run_date = context['logical_date']
            
        year = run_date.year
        month = run_date.month
        if not year or not month:
            raise ValueError("Invalid year or month values")
        return {'year': year, 'month': f"{month:02d}"}
    except Exception as e:
        raise AirflowException(f"Failed to get year and month: {str(e)}")


class CustomAzureSynapseRunSparkBatchOperator(AzureSynapseRunSparkBatchOperator):
    """Custom Synapse operator that extends templating capabilities.

    This operator adds the 'payload' field to the template_fields to enable
    Jinja templating for the entire Spark job configuration.
    """
    template_fields = AzureSynapseRunSparkBatchOperator.template_fields + ('payload', )


with DAG(
    DAG_ID,
    default_args=default_args,
    description='Run a Synapse Spark notebook for Divvy Bikeshare data transformation',
    schedule_interval=None,
    catchup=False,
    params={
        'execution_date': None
    },
    tags=['azure', 'synapse', 'spark']
) as dag:
    # Task to get year and month
    get_date = PythonOperator(
        task_id='get_date',
        python_callable=get_year_month,
        provide_context=True,
        doc_md="""### Get Date Task
Extracts year and month from execution context for data processing."""
    )
    
    # Configure and run Spark job
    run_spark_job = CustomAzureSynapseRunSparkBatchOperator(
        task_id="execute_spark_job",
        azure_synapse_conn_id="azure_synapse_connection",
        spark_pool=SPARK_POOL,
        wait_for_termination=True,
        check_interval=60,
        doc_md="""### Execute Spark Job Task Runs the PySpark transformation job on Azure Synapse.""",
        payload={
            "name": "SparkJobFromAirflow",
            "file": "{{ var.value.pyspark_script_file_path }}",
            "language": "python",
            "className": "",
            "args": [
                "--input_path", 
                "{{ var.value.base_path }}/{{ var.value.input_directory }}/{{ ti.xcom_pull(task_ids='get_date')['year'] }}/{{ ti.xcom_pull(task_ids='get_date')['month'] }}/{{ var.value.input_file_name_base }}{{ ti.xcom_pull(task_ids='get_date')['year'] }}{{ ti.xcom_pull(task_ids='get_date')['month'] }}.csv",
                "--output_path", 
                "{{ var.value.base_path }}/{{ var.value.output_directory }}"
            ],
            "driverMemory": "4g",
            "driverCores": 1,
            "executorMemory": "4g",
            "executorCores": 1,
            "numExecutors": 2,
            "conf": {
                "spark.dynamicAllocation.enabled": "false",
                "spark.shuffle.service.enabled": "false"
            },
            "executorSize": "Small",
            "executorCount": 2,
        }
    )

    # Set task dependencies
    get_date >> run_spark_job