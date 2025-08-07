resource "google_storage_bucket" "core" {
  name     = "${var.project_id}-core-bucket"
  project  = var.project_id
  location = var.region

  uniform_bucket_level_access = true
}
