variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "services" {
  type = map(object({
    image_repo    = string
    memory        = string
    cpu           = string
    timeout       = number
    concurrency   = number
    env           = map(string)
  }))
}

variable "api_gateway_sa" {
  type = string
}

data "google_project" "proj" {
  project_id = var.project_id
}

resource "google_cloud_run_v2_service" "svc" {
  for_each = var.services
  name     = each.key
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"
  deletion_protection = false
  
  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${each.value.image_repo}/${each.key}:latest"
      resources {
        limits = {
          cpu    = each.value.cpu
          memory = each.value.memory
        }
      }
      
      dynamic "env" {
        for_each = each.value.env
        content {
          name  = env.key
          value = env.value
        }
      }
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    
    timeout                        = "${each.value.timeout}s"
    max_instance_request_concurrency = each.value.concurrency
    service_account                = "${each.key}@${var.project_id}.iam.gserviceaccount.com"
  }
}

resource "google_cloud_run_v2_service_iam_member" "invoker_apigw" {
  for_each = google_cloud_run_v2_service.svc
  name     = each.value.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${var.api_gateway_sa}"
}
