variable "project_id" {
  type = string
}

variable "location" {
  type = string
}

variable "workflows_def" {
  type = list(object({
    name = string
    description = string
    source_contents = string
  }))
}
