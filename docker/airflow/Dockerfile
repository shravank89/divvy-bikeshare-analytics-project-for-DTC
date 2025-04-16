FROM apache/airflow:2.5.0

USER root
# Create all required directories with correct permissions
RUN mkdir -p /opt/airflow/logs/scheduler && \
    mkdir -p /opt/airflow/logs/webserver && \
    mkdir -p /opt/airflow/dags && \
    mkdir -p /opt/airflow/plugins && \
    chown -R airflow:0 /opt/airflow && \
    chmod -R 775 /opt/airflow


# Install wget
RUN apt-get update && apt-get install -y wget unzip && rm -rf /var/lib/apt/lists/*


# Install Azure CLI
RUN apt-get update && apt-get install -y ca-certificates curl apt-transport-https lsb-release gnupg
RUN curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null
RUN echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/azure-cli.list
RUN apt-get update && apt-get install -y azure-cli


RUN apt-get update && \
apt-get install -y git wget unzip && \
rm -rf /var/lib/apt/lists/*

USER airflow

# Install dbt
RUN pip install apache-airflow-providers-microsoft-mssql \
    dbt-core==1.4.5 \
    dbt-bigquery==1.4 \
    "protobuf<=3.20.0"
# Add local bin to PATH
ENV PATH="/home/airflow/.local/bin:${PATH}"