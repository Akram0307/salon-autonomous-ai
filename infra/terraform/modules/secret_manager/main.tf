resource "google_secret_manager_secret" "secret" {
  for_each = toset(var.secrets)
  
  secret_id = each.key
  project   = var.project_id
  
  replication {
    auto {}
  }
  
  labels = {
    environment = "dev"
  }
}
