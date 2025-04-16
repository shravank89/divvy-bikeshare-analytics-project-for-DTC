"""DAG for extracting Divvy Bikeshare data from source and uploading to Azure Blob Storage.

This DAG performs the following operations:
1. Downloads monthly Divvy Bikeshare data from S3
2. Extracts the downloaded zip file
3. Uploads the CSV data to Azure Blob Storage with standardized naming
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from airflow import DAG
from airflow.operators.python import PythonOperator, get_current_context
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
import requests
import os
import zipfile
import glob
import shutil

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 4, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,   
    'retry_delay': timedelta(minutes=5),
}

def download_bikeshare_data(**context) -> None:
    """Download Divvy Bikeshare data from S3 and upload to Azure Blob Storage.
    
    Args:
        **context: Airflow context containing execution information.
        
    Raises:
        requests.exceptions.HTTPError: If the download request fails.
        zipfile.BadZipFile: If the downloaded file is not a valid zip file.
    """
    base_url = "https://divvy-tripdata.s3.amazonaws.com/"
    # Get date from trigger configuration or fallback to logical date
    if 'dag_run' in context and context['dag_run'].conf:
        date_str = context['dag_run'].conf.get('execution_date')
        print(date_str)
        if date_str:
            run_date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            run_date = context['logical_date']
    else:
        run_date = context['logical_date']
    
    year = run_date.year
    month = run_date.month
    
    wasb_hook = WasbHook(wasb_conn_id='azure_processed_blob_storage')
    
    filename = f"{year}{month:02d}-divvy-tripdata.zip"
    url = f"{base_url}{filename}"
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Define paths
        local_file_path = os.path.join("/tmp", f"bikeshare-data-{year}-{month}.zip")
        extract_path = os.path.join("/tmp", f"bikeshare-extracted-{year}-{month}")
        
        # Clean up any existing files/directories
        if os.path.exists(local_file_path):
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)
            else:
                shutil.rmtree(local_file_path)
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        
        # Create extraction directory
        os.makedirs(extract_path, exist_ok=True)
        
        # Download and write zip file
        with open(local_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

        

        # Extract zip file
        with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # Upload extracted CSV files to Azure Data Lake with new naming format
        csv_files = glob.glob(f"{extract_path}/*.csv")
        for csv_file in csv_files:
            csv_filename = f"divvy_bikshare_chicago_data_{year}{month:02d}.csv"
            wasb_hook.load_file(
                file_path=csv_file,
                container_name='bikeshare',
                blob_name=f"divvy-raw-csv-data/{year}/{month:02d}/{csv_filename}",
                overwrite=True
            )
            
        # Clean up temporary files
        os.remove(local_file_path)
        shutil.rmtree(extract_path)
        
        context['ti'].xcom_push(key=f"file_{year}{month}", value=csv_filename)
    except requests.exceptions.HTTPError:
        print("http error")
    except zipfile.BadZipFile:
        print(f"Error: Bad zip file for {filename}")

with DAG(
    'divvy_bikeshare_data_extract',
    default_args=default_args,
    description='ETL pipeline for extraction of divvy Bikeshare raw data',
    schedule_interval=None,
    catchup=False,
    params={
        'execution_date': None
    },
) as dag:

    download_task = PythonOperator(
        task_id='download_bikeshare_data',
        python_callable=download_bikeshare_data,
        provide_context=True
    )