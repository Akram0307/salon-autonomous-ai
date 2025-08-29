variable "project_id" {
  type = string
}

variable "region" {
  type = string
  default = "asia-south1"
}

variable "repos" {
  type = list(string)
}
