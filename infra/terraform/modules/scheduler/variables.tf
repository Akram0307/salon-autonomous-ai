variable "project_id" {
  type = string
}

variable "location" {
  type = string
}

variable "invoker_sa" {
  type = string
}

variable "jobs" {
  type = list(object({
    name     = string
    schedule = string
    workflow = string
  }))
}
