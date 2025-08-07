variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "service_account_email" {
  description = "The email of the service account that needs Firestore access."
  type        = string
}
