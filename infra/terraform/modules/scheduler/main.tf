resource "google_cloud_scheduler_job" "jobs" {
  for_each = { for j in var.jobs : j.name => j }

  name      = each.key
  schedule  = each.value.schedule
  time_zone = "Asia/Kolkata"
  region    = var.location
  project   = var.project_id

  http_target {
    http_method = "POST"
    uri         = "https://workflowexecutions.googleapis.com/v1/projects/${var.project_id}/locations/${var.location}/workflows/${each.value.workflow}:execute"
    oidc_token { service_account_email = var.invoker_sa }
    body = base64encode(jsonencode({ job: each.key }))
  }
}
