"""DAG for orchestrating dbt transformations on Divvy Bikeshare data.

This DAG performs the following operations:
1. Gets the year and month from execution context
2. Runs dbt debug to verify project setup
3. Executes dbt models with dynamic variables
4. Runs dbt tests to validate transformations
"""

from typing import Dict, Any
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import json


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2020, 4, 1)
}

def get_table_var(**context) -> Dict[str, str]:
    """Extract year and month from the execution contextn and help make table var value.
    
    Args:
        **context: Airflow context containing execution information.
        
    Returns:
        Dict[str, str]: Dictionary containing table_var values which will help make table 
        name in dbt project to work on based on month and year.
    """
    if 'dag_run' in context and context['dag_run'].conf:
        date_str = context['dag_run'].conf.get('execution_date')
        if date_str:
            execution_date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            execution_date = context['execution_date']
    else:
        execution_date = context['execution_date']
            
    table_var = f"{execution_date.strftime('%Y')}{execution_date.strftime('%m')}"

    return {'table_var': table_var}


with DAG(
    'divvy_bikeshare_dbt_pipeline',
    default_args=default_args,
    description='DAG for running dbt transformations',
    schedule_interval=None,
    catchup=False
) as dag:

    # fetch dbt project directory from airflow variables
    dbt_project_dir = '{{ var.value.dbt_project_dir }}'

    get_table_var_values = PythonOperator(
        task_id='get_table_var_value',
        python_callable=get_table_var,
        provide_context=True
    )
    # Install dbt dependencies
    dbt_debug = BashOperator(
        task_id='dbt_debug',
        bash_command=f'cd {dbt_project_dir} && dbt debug',
    )

    # Run dbt models with dynamic variables
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command="cd " +f"{dbt_project_dir}"+" && dbt run --vars '{{ task_instance.xcom_pull(task_ids='get_table_var_value') }}'",
    )

    # Test dbt models
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command="cd " +f"{dbt_project_dir}"+" && dbt run --vars '{{ task_instance.xcom_pull(task_ids='get_table_var_value') }}'",
    )

    # Set task dependencies
    get_table_var_values >> dbt_debug >> dbt_run >> dbt_test