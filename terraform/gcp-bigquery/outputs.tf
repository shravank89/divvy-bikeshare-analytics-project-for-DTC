output "dataset_id" {
  description = "The ID of the created BigQuery dataset"
  value       = google_bigquery_dataset.divvy_monthly_raw_data.dataset_id
}

output "dataset_location" {
  description = "The location of the created BigQuery dataset"
  value       = google_bigquery_dataset.divvy_monthly_raw_data.location
}

output "dataset_link" {
  description = "Link to the BigQuery dataset in Google Cloud Console"
  value       = "https://console.cloud.google.com/bigquery?project=${var.project_id}&d=${google_bigquery_dataset.divvy_monthly_raw_data.dataset_id}&p=${var.project_id}&page=dataset"
}