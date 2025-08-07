variable "project_id" { type=string }
variable "location" { type=string }
variable "dataset_id" { type=string }
resource "google_bigquery_dataset" "analytics" { project=var.project_id dataset_id=var.dataset_id location=var.location }
