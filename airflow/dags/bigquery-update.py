"""DAG for loading processed Divvy Bikeshare data from Azure Blob Storage to BigQuery.

This DAG performs the following operations:
1. Renames the processed parquet file with standardized naming convention
2. Downloads the parquet file from Azure Blob Storage
3. Loads the data into BigQuery with appropriate schema handling
"""

from typing import Dict, Any, Optional
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from datetime import datetime, timedelta
import pandas as pd
import pyarrow.parquet as pq
import io
from google.cloud import bigquery

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 4, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def rename_processed_parquet_file(**context) -> str:
    """Rename the processed parquet file to include the year and month.
    
    Args:
        **context: Airflow context containing execution information.
        
    Returns:
        str: The new blob name after renaming.
        
    Raises:
        Exception: If no parquet file is found in the specified directory.
    """
    """Rename the processed parquet file to include the year and month"""
    # Get date from trigger configuration or fallback to logical date
    if 'dag_run' in context and context['dag_run'].conf:
        date_str = context['dag_run'].conf.get('execution_date')
        if date_str:
            execution_date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            execution_date = context['logical_date']
    else:
        execution_date = context['logical_date']
        
    year = execution_date.strftime('%Y')
    month = execution_date.strftime('%m')

    # Get file from blob storage
    wasb_hook = WasbHook(wasb_conn_id='azure_processed_blob_storage')
    
    # List blobs in the directory to find the part file
    blob_service_client = wasb_hook.get_conn()
    container_client = blob_service_client.get_container_client('bikeshare')
    blob_list = container_client.list_blobs(name_starts_with=f'processed_data/divvy_bikeshare_data_parquet/{year}/{month}/')
    
    # Find the part file
    for blob in blob_list:
        if blob.name.endswith('.parquet') and 'part-' in blob.name:
            # Construct new blob name
            new_blob_name = f'processed_data/divvy_bikeshare_data_parquet/{year}/{month}/divvy_bikeshare_chicago_data_{year}{month}.parquet'
            
            # Copy blob to new name
            source_blob = container_client.get_blob_client(blob.name)
            dest_blob = container_client.get_blob_client(new_blob_name)
            dest_blob.start_copy_from_url(source_blob.url)
            
            # Delete original blob after copy
            source_blob.delete_blob()
            
            return new_blob_name
    
    raise Exception(f"No parquet file found in processed_data/divvy_bikeshare_data_parquet/{year}/{month}/")



def parquet_file_to_bigquery(**context) -> None:
    """Process a parquet file and load it to BigQuery.
    
    Args:
        **context: Airflow context containing execution information.
        
    Raises:
        Exception: If there are any errors during file processing or BigQuery loading.
    """
    """Process a single parquet file and load to BigQuery"""
    file = rename_processed_parquet_file(**context)
    # Get file from blob storage
    wasb_hook = WasbHook(wasb_conn_id='azure_processed_blob_storage')
    blob_data = wasb_hook.download(container_name='bikeshare', blob_name=file, offset=0, length=None).readall()
    
    # Read parquet data
    parquet_file = io.BytesIO(blob_data)
    df = pq.read_table(parquet_file).to_pandas()

    df["start_date"] = df["start_date"].astype(str)
    df["end_date"] = df["end_date"].astype(str)
    # Clean numeric columns
    for col in df.select_dtypes(include=['float', 'int']).columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # Replace invalid values with NaN
    
    try:
        # Get BigQuery connection
        bq_hook = BigQueryHook(gcp_conn_id='google_cloud_connection')
        client = bq_hook.get_client()
        
        # Extract table name from the standardized file name
        # The file name is already in the format: divvy_bikeshare_chicago_data_YYYYMM.parquet
        table_name = file.split('/')[-1].replace('.parquet', '')
        
        # Get dataset from connection (or use default)
        dataset_id = bq_hook.project_id + '.divvy_monthly_raw_data'
        
        # Create dataset if it doesn't exist
        try:
            client.get_dataset(dataset_id)
        except Exception:
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = 'US'
            client.create_dataset(dataset, exists_ok=True)
        
        # Construct table reference
        table_ref = f"{dataset_id}.{table_name}"
        
        # Automatically detect schema from DataFrame
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION]
        )
        
        # Load data to BigQuery
        df.to_gbq(
            destination_table=table_ref,
            project_id=bq_hook.project_id,
            if_exists='replace',
            table_schema=None,  # Auto-detect schema
            credentials=bq_hook.get_credentials()
        )
        
    except Exception as e:
        error_msg = f"Error processing file {file}: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

with DAG(
    'divvy_bikeshare_bigquery_feed',
    default_args=default_args,
    description='Load current month parquet file from Azure Blob to BigQuery',
    schedule_interval=None,  
    catchup=False,
    params={
        'execution_date': None
    }
) as dag:

    # Single task to process current month's file
    process_current_month = PythonOperator(
        task_id='process_current_month',
        python_callable=parquet_file_to_bigquery,
        provide_context=True
    )