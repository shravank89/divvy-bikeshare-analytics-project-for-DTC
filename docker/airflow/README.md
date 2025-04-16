# Airflow Docker Setup

This directory contains the Docker configuration for running Apache Airflow in a containerized environment. The setup includes a webserver, scheduler, and PostgreSQL database.

## Components

### Dockerfile
Builds a custom Airflow image with:
- Base image: apache/airflow:2.5.0
- Additional tools: wget, unzip, git
- Azure CLI for cloud interactions
- DBT installation for data transformations

### docker-compose.yml
Orchestrates three main services:
1. **PostgreSQL Database**
   - Stores Airflow metadata
   - Persists data using named volumes

2. **Airflow Webserver**
   - Provides web UI interface (port 8080)
   - Initializes database and creates admin user
   - Mounts necessary volumes for DAGs, logs, and configurations

3. **Airflow Scheduler**
   - Monitors and triggers DAG runs
   - Shares volume mounts with webserver

### requirements.txt
Manages Python dependencies including:
- Airflow core and provider packages
- Cloud provider SDKs (Azure, Google)
- Data processing libraries (pandas, pyarrow)
- DBT for data transformations

## Volume Mounts
- DAGs directory: `/opt/airflow/dags`
- Logs directory: `/opt/airflow/logs`
- Plugins directory: `/opt/airflow/plugins`
- DBT project directory: `/opt/airflow/dbt-project`
- DBT profiles: `/home/airflow/.dbt`
- Keys directory: `/opt/airflow/keys`

## Getting Started

1. Build and start the containers:
```bash
docker-compose up -d
```

2. Access the Airflow UI:
- URL: http://localhost:8080
- Username: admin
- Password: admin

3. Monitor logs:
```bash
docker-compose logs -f
```

4. Shut down:
```bash
docker-compose down
```

## Environment Configuration
Key environment variables are set in docker-compose.yml:
- Database connection
- Executor type (LocalExecutor)
- Logging configuration
- User permissions (UID/GID)

## Security Notes
- Default admin credentials should be changed in production scenarios.
- Sensitive information is managed through Airflow's secrets backend
