#!/bin/bash

# Set error handling
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function for logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%dT%H:%M:%S%z')] ERROR: $1${NC}" >&2
}

# Change to the GCP Terraform directory
cd "$(dirname "$0")/../gcp-bigquery"

# Check if required environment variables are set
required_vars=("GOOGLE_CREDENTIALS" "GOOGLE_PROJECT")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        error "$var is not set. Please export $var before running this script."
        exit 1
    fi
done

# Initialize Terraform
log "Initializing Terraform..."
terraform init

# Validate the Terraform configuration
log "Validating Terraform configuration..."
terraform validate

# Plan the changes
log "Planning Terraform changes..."
terraform plan -out=tfplan

# Apply the changes
log "Applying Terraform changes..."
terraform apply -auto-approve tfplan

# Clean up the plan file
rm -f tfplan

log "Deployment completed successfully!"