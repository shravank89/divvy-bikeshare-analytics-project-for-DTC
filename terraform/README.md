# Terraform Infrastructure

This folder contains the Terraform configuration and supporting scripts for provisioning and managing cloud infrastructure for the Divvy Bikeshare Analytics project. The infrastructure is deployed across Azure and Google Cloud Platform (GCP) using Terraform.

## Directory Structure

- **azure/**: Contains Terraform configurations for provisioning resources in Azure that includes resource group, storage account, azure synapse and spark pool.
- **gcp-bigquery/**: Contains Terraform configurations for provisioning BigQuery dataset in GCP.
- **bash-scripts/**: Contains bash scripts for automating the deployment of Terraform configurations.

---

## Azure Directory

The `azure/` directory includes Terraform configurations for provisioning Azure resources such as Azure Synapse Spark pools and other required infrastructure.

### Key Files:
- `main.tf`: Defines the Azure resources to be provisioned.
- `variables.tf`: Contains variables for configuring the Azure infrastructure.
- `outputs.tf`: Specifies the outputs of the Terraform configuration.

### Deployment:
Use the `deploy_azure.sh` script in the `bash-scripts/` directory to deploy the Azure infrastructure.

---

## GCP BigQuery Directory

The `gcp-bigquery/` directory includes Terraform configurations for provisioning BigQuery datasets and tables.

### Key Files:
- `main.tf`: Defines the BigQuery datasets and tables to be provisioned.
- `variables.tf`: Contains variables for configuring the BigQuery resources.
- `terraform.tfstate` and `terraform.tfstate.backup`: State files that track the current state of the infrastructure.

### Deployment:
Use the `deploy_gcp.sh` script in the `bash-scripts/` directory to deploy the GCP BigQuery infrastructure.

---

## Bash Scripts Directory

The `bash-scripts/` directory contains scripts to automate the deployment of Terraform configurations for both Azure and GCP.

### Key Scripts:
- `deploy_azure.sh`: Automates the deployment of Azure infrastructure.
  - Checks for required environment variables: `ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, `ARM_SUBSCRIPTION_ID`, `ARM_TENANT_ID`.
  - Initializes, validates, plans, and applies the Terraform configuration.

- `deploy_gcp.sh`: Automates the deployment of GCP BigQuery infrastructure.
  - Checks for required environment variables: `GOOGLE_CREDENTIALS`, `GOOGLE_PROJECT`.
  - Initializes, validates, plans, and applies the Terraform configuration.

---

## Deployment Workflow

1. **Set Environment Variables**:
   - For Azure: Export `ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, `ARM_SUBSCRIPTION_ID`, and `ARM_TENANT_ID`.
   - For GCP: Export `GOOGLE_CREDENTIALS` and `GOOGLE_PROJECT`.

2. **Run Deployment Scripts**:
   - For Azure: Execute `bash-scripts/deploy_azure.sh`.
   - For GCP: Execute `bash-scripts/deploy_gcp.sh`.

3. **Monitor Deployment**:
   - Terraform will initialize, validate, plan, and apply the infrastructure changes.
   - Logs will be displayed in the terminal for each step.

---

## Notes

- Ensure that the required environment variables are set before running the deployment scripts.
- The Terraform state files (`terraform.tfstate` and `terraform.tfstate.backup`) should be stored securely to avoid accidental loss or corruption.
- Modify the `variables.tf` files in each directory to customize the infrastructure for different environments (e.g., dev, staging, prod).

---