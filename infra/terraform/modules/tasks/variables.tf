variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "queues" {
  type = list(object({
    name                      = string
    max_dispatches_per_second = number
    max_concurrent_dispatches = number
  }))
}
