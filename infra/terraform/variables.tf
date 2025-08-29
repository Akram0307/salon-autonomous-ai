variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "asia-south1"
}

variable "billing_alert_threshold" {
  type    = number
  default = 0.8
}

variable "firebase_jwt_issuer" {
  type = string
}

variable "firebase_jwt_audience" {
  type = string
}
