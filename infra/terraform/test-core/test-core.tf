module "core" {
  source     = "../modules/core"
  project_id = var.project_id
  region     = var.region
}
