resource "google_cloud_tasks_queue" "queues" {
  for_each = { for q in var.queues : q.name => q }

  name     = each.key
  location = var.region
  project  = var.project_id

  rate_limits {
    max_dispatches_per_second = each.value.max_dispatches_per_second
    max_concurrent_dispatches = each.value.max_concurrent_dispatches
  }
}
