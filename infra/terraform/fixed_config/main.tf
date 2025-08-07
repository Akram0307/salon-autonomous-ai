module "core" {
  source     = "../modules/core"
  project_id = var.project_id
  region     = var.region
}

module "artifact_registry" {
  source     = "../modules/artifact_registry"
  project_id = var.project_id
  repos      = ["ai-apps", "web", "mobile"]
}

module "iam" {
  source     = "../modules/iam"
  project_id = var.project_id
  services   = ["core-api","payments","notifications","agents-runner","webhook-handler","pricing-optimizer"]
}

module "pubsub" {
  source     = "../modules/pubsub"
  project_id = var.project_id
  topics     = ["booking.events","payment.events","schedule.events","tenant.events","audit.events"]
}

module "firestore" {
  source     = "../modules/firestore"
  project_id = var.project_id
  location   = var.region
}

module "bigquery" {
  source     = "../modules/bigquery"
  project_id = var.project_id
  location   = var.region
  dataset_id = "analytics"
}

module "secrets" {
  source     = "../modules/secret_manager"
  project_id = var.project_id
  secrets    = ["razorpay_api_key","whatsapp_api_token","webhook_secret","payments_provider_secret"]
}

module "workflows" {
  source        = "../modules/workflows"
  project_id    = var.project_id
  location      = var.region
  workflows_def = [
    {
      name            = "booking_orchestrator"
      description     = "Booking orchestrator workflow"
      source_contents = file("${path.module}/../modules/workflows/booking_orchestrator.yaml")
    }
  ]
}

module "tasks" {
  region     = var.region
  source     = "../modules/tasks"
  project_id = var.project_id
  queues     = [
    {
      name                        = "payments-capture"
      max_dispatches_per_second   = 20
      max_concurrent_dispatches   = 100
    },
    {
      name                        = "notifications-send"
      max_dispatches_per_second   = 50
      max_concurrent_dispatches   = 200
    }
  ]
}

module "scheduler" {
  source     = "../modules/scheduler"
  project_id = var.project_id
  location   = var.region
  invoker_sa = module.iam.api_gateway_sa_email
  jobs       = [
    {
      name     = "nightly_exports"
      schedule = "0 2 * * *"
      workflow = "booking_orchestrator"
    }
  ]
}

module "run_services" {
  source = "../modules/run_service"
  project_id = var.project_id
  region     = var.region
  api_gateway_sa = module.iam.api_gateway_sa_email
  services = {
    core-api = { image_repo="ai-apps", memory="512Mi", cpu="1", timeout=60, concurrency=60, env={ SERVICE_NAME="core-api" } }
    payments = { image_repo="ai-apps", memory="512Mi", cpu="1", timeout=60, concurrency=40, env={ SERVICE_NAME="payments" } }
    notifications = { image_repo="ai-apps", memory="512Mi", cpu="1", timeout=60, concurrency=80, env={ SERVICE_NAME="notifications" } }
    agents-runner = { image_repo="ai-apps", memory="1Gi", cpu="1", timeout=120, concurrency=8, env={ SERVICE_NAME="agents-runner", VERTEX_LOCATION=var.region, VERTEX_MODEL="projects/${var.project_id}/locations/${var.region}/publishers/google/models/gemini-2.0-flash-001" } }
    webhook-handler = { image_repo="ai-apps", memory="256Mi", cpu="1", timeout=30, concurrency=80, env={ SERVICE_NAME="webhook-handler" } }
    pricing-optimizer = { image_repo="ai-apps", memory="1Gi", cpu="1", timeout=120, concurrency=8, env={ SERVICE_NAME="pricing-optimizer", VERTEX_LOCATION=var.region, VERTEX_MODEL="projects/${var.project_id}/locations/${var.region}/publishers/google/models/gemini-2.0-pro-001" } }
  }
}

module "api_gateway" {
  source                = "../modules/api_gateway"
  project_id            = var.project_id
  gateway_id            = "salon-gw"
  openapi_spec_path     = "${path.module}/../modules/api_gateway/openapi.yaml"
  firebase_jwt_issuer   = var.firebase_jwt_issuer
  firebase_jwt_audience = var.firebase_jwt_audience
  backends              = module.run_services.service_urls
}

module "monitoring" {
  source     = "../modules/monitoring"
  project_id = var.project_id
}

# Budgets optional unless billing account provided
# module "budgets" { source = "../modules/budgets" project_id = var.project_id billing_account = var.billing_account amount = 200 threshold = var.billing_alert_threshold }
