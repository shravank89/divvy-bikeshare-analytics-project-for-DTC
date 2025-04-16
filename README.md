# Divvy Bikeshare Chicago Analytics Project

This project creates a comprehensive analytics platform for Divvy Bikeshare data, using modern data engineering tools to process raw trip data into actionable insights for business stakeholders via Looker Studio dashboards.

# Project Overview
The platform ingests Divvy Bikeshare trip data from the public S3 bucket (https://divvy-tripdata.s3.amazonaws.com/index.html), processes it through a scalable data pipeline, transforms it into analytics-ready models, and serves it to Looker Studio dashboards that help stakeholders understand bike usage patterns, optimize station placement, and improve fleet management.

# Architecture Components
1. Data Ingestion: Airflow orchestrates periodic data downloads from the S3 bucket containing historical trip data
2. Data Processing: Spark jobs process the raw data with help of spark pool in azure synapse and stores in bigquery DWH. 
3. Data Transformation: dbt models transform raw data into consumption models for analytics
4. Infrastructure: Docker containers for local development, Terraform for infrastructure provisioning
5. Dashboarding: Looker Studio connects to Bigquery datawarehouse to visualize buisness insights

# Implementation Details
Infrastructure (Docker + Terraform)
Docker containers would be used for local development, ensuring consistent environments. The cloud infrastructure would be deployed to Azure and GCP using Terraform.

# Data Ingestion (Airflow)
Airflow would orchestrate the entire workflow, starting with downloading files from the S3 bucket:

# Data Processing (Spark)
The Spark code, executed within Azure Synapse spark pool, would process the raw CSV files, lightly transforms it and converts into parquet for efficient storage:

# Datawarehouse Update (Python)
The Python script, upload the data from the parquet file into bigquery datalake.

# Data Transformation (dbt)
dbt would be used to transform the processed data into analytics models:

# Looker Studio Dashboard
The Looker dashboard would connect directly to Bigquery to visualize:

1. User Behaviour Analysis:

2. Peak Usage Time

3. Station Popularity


# Development and Deployment Workflow

1. Local Development:
- Developers use Docker containers with Airflow, dbt and Spark for local testing
- Code versioned in Git


2. CI/CD Pipeline:
- Pull requests trigger automated tests
- Terraform plans validated


3. Infrastructure Deployment:
- Terraform applies infrastructure changes to Azure
- Airflow DAGs deployed to production environment


4. Production Operation:
- Airflow orchestrates monthly data refreshes
- dbt handles data transformations
- Looker Studio reports auto-refresh monthly


# Link for Looker Public dashboard:
https://lookerstudio.google.com/reporting/f2aa8cf5-ca80-4f57-bd25-7fd9d525f242
