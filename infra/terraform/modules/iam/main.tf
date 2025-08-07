variable "project_id" { type=string }
variable "services" { type=list(string) }

data "google_project" "proj" {}

resource "google_service_account" "svc" {
  for_each     = toset(var.services)
  account_id   = replace(each.key, "_", "-")
  display_name = "${each.key} service account"
}

resource "google_service_account" "apigw" {
  account_id   = "api-gateway-sa"
  display_name = "API Gateway Invoker SA"
}

# Cloud Build deploy roles
resource "google_project_iam_member" "cloudbuild_deploy" {
  for_each = toset([
    "roles/run.admin","roles/iam.serviceAccountUser","roles/artifactregistry.writer","roles/apigateway.admin","roles/workflows.admin","roles/secretmanager.admin","roles/firestore.indexAdmin"
  ])
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${data.google_project.proj.number}@cloudbuild.gserviceaccount.com"
}

output "api_gateway_sa_email" { value = google_service_account.apigw.email }
output "service_accounts" { value = { for k, v in google_service_account.svc : k => v.email } }
