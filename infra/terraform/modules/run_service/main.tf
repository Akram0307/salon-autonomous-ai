variable "project_id" { type=string }
variable "region" { type=string }
variable "services" { type=map(object({ image_repo=string, memory=string, cpu=string, timeout=number, concurrency=number, env=map(string) })) }
variable "api_gateway_sa" { type=string }

data "google_project" "proj" {}

resource "google_cloud_run_v2_service" "svc" {
  for_each = var.services
  name     = each.key
  location = var.region
  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${each.value.image_repo}/${each.key}:latest"
      resources { limits = { cpu = each.value.cpu, memory = each.value.memory } }
      env = [for k, v in each.value.env : { name = k, value = v }]
    }
    scaling { min_instance_count = 0 max_instance_count = 50 }
    timeout = "${each.value.timeout}s"
    max_instance_request_concurrency = each.value.concurrency
    service_account = "${each.key}@${var.project_id}.iam.gserviceaccount.com"
    ingress = "INGRESS_ALL"
  }
}

resource "google_cloud_run_v2_service_iam_member" "invoker_apigw" {
  for_each = google_cloud_run_v2_service.svc
  name     = each.value.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.api_gateway_sa}"
}

output "service_urls" { value = { for k, v in google_cloud_run_v2_service.svc : k => v.uri } }
