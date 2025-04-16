variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The default region for resources"
  type        = string
  default     = "us-central1"
}

variable "location" {
  description = "The location for the BigQuery dataset"
  type        = string
  default     = "US"
}

variable "dataset_id" {
  description = "The ID of the BigQuery dataset"
  type        = string
  default     = "divvy_bikeshare"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}