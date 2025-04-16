# Configure the Google Cloud provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Create a BigQuery dataset
resource "google_bigquery_dataset" "divvy_monthly_raw_data" {
  dataset_id                  = "divvy_monthly_raw_data"
  friendly_name              = "divvy_monthly_raw_data"
  description                = "Dataset for Divvy Bikeshare Analytics"
  location                   = var.location
  delete_contents_on_destroy = false

  labels = {
    environment = var.environment
  }

  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }

  access {
    role          = "READER"
    special_group = "projectReaders"
  }

  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }
}