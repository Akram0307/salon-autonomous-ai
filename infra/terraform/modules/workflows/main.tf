resource "google_workflows_workflow" "workflows" {
  for_each = { for w in var.workflows_def : w.name => w }

  name            = each.key
  project         = var.project_id
  region        = var.location
  description     = each.value.description
  source_contents = each.value.source_contents
}
