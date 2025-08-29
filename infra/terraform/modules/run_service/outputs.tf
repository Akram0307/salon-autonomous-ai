output "service_urls" {
  description = "The URLs of the Cloud Run services."
  value       = { for k, v in google_cloud_run_v2_service.svc : k => v.uri }
}

output "service_account_emails" {
  description = "The emails of the service accounts created for the Cloud Run services."
  value       = { for k, v in google_cloud_run_v2_service.svc : k => "${k}@${var.project_id}.iam.gserviceaccount.com" }
}
