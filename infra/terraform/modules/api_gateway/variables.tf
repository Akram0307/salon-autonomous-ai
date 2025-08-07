variable "project_id" {
  type = string
}

variable "region" {
  type = string
  default = "us-central1"
}

variable "api_name" {
  type = string
  default = "salon-ai-api"
}

variable "gateway_id" {
  type = string
}

variable "openapi_spec_path" {
  type = string
}

variable "firebase_jwt_issuer" {
  type = string
}

variable "firebase_jwt_audience" {
  type = string
}

variable "backends" {
  type = map(string)
}
