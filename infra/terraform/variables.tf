variable "project_id" { type = string }
variable "region" { type = string default = "asia-south1" }
variable "firebase_jwt_issuer" { type = string default = "" }
variable "firebase_jwt_audience" { type = string default = "" }
variable "billing_account" { type = string default = "" }
variable "billing_alert_threshold" { type = number default = 0.8 }
