# Divvy Bikeshare Airflow Pipeline

This directory contains the Airflow DAGs that orchestrate the complete Divvy Bikeshare data pipeline. The pipeline processes monthly bikeshare data through multiple stages of transformation and loading.

## Pipeline Overview

The data pipeline is orchestrated by a master DAG that coordinates the execution of several sub-DAGs in sequence:

1. **Data Extraction** (`divvy_bikeshare_data_extract`)
   - Downloads monthly Divvy Bikeshare data from S3
   - Extracts ZIP files and standardizes naming
   - Uploads raw CSV data to Azure Blob Storage

2. **Spark Transformation** (`divvy_bikeshare_pyspark_transformation`)
   - Processes raw data using Azure Synapse Analytics
   - Executes PySpark jobs for data transformation
   - Outputs processed data in Parquet format

3. **BigQuery Loading** (`divvy_bikeshare_bigquery_feed`)
   - Renames processed Parquet files with standardized naming
   - Downloads data from Azure Blob Storage
   - Loads transformed data into BigQuery

4. **DBT Transformation** (`divvy_bikeshare_dbt_pipeline`)
   - Runs dbt models with dynamic variables
   - Applies business logic transformations
   - Validates data quality through tests

## DAG Dependencies

```
extract >> transform >> load >> dbt
```

## Configuration Requirements

### Airflow Connections
- `azure_processed_blob_storage`: Azure Blob Storage connection
- `azure_synapse_connection`: Azure Synapse Analytics connection

### Airflow Variables
- `dbt_project_dir`: Path to dbt project directory
- `pyspark_script_file_path`: Path to PySpark transformation script
- `base_path`: Base storage path for data
- `input_directory`: Directory containing raw data
- `output_directory`: Directory for transformed data

## Scheduling

The master pipeline is configured for manual triggering (schedule_interval=None) with the ability to process historical data from April 2020 onwards. Each sub-DAG inherits this configuration and can also be triggered independently if needed.

## Error Handling

- All DAGs include retry mechanisms for transient failures
- Email notifications on task failures
- Comprehensive logging and error reporting

## Development Guidelines

1. Follow the existing DAG structure and naming conventions
2. Ensure proper error handling and logging
3. Test changes thoroughly in development environment
4. Document any new variables or connections required
5. Maintain backward compatibility when possible