provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

module "core" {
  source     = "./modules/core"
  project_id = var.project_id
  region     = var.region
}

module "artifact_registry" {
  source     = "./modules/artifact_registry"
  project_id = var.project_id
  region     = var.region
  repos      = ["ai-apps", "web", "mobile"]
}

module "iam" {
  source     = "./modules/iam"
  project_id = var.project_id
  services   = ["core-api", "booking", "payments", "notifications", "agents-runner", "webhook-handler", "pricing-optimizer"]
}

module "pubsub" {
  source     = "./modules/pubsub"
  project_id = var.project_id
  topics     = ["booking-created", "booking-cancelled", "booking-updated"]
}

module "firestore" {
  source     = "./modules/firestore"
  project_id = var.project_id
  location   = var.region
}

module "bigquery" {
  source     = "./modules/bigquery"
  project_id = var.project_id
  location   = var.region
  dataset_id = "analytics"
}

module "secrets" {
  source     = "./modules/secret_manager"
  project_id = var.project_id
  secrets    = ["razorpay_api_key", "whatsapp_api_token", "webhook_secret", "payments_provider_secret"]
}

module "workflows" {
  source         = "./modules/workflows"
  project_id     = var.project_id
  location       = var.region
  workflows_def  = {
    booking_orchestrator = file("${path.module}/modules/workflows/booking_orchestrator.yaml")
  }
}

module "tasks" {
  source     = "./modules/tasks"
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
  source     = "./modules/scheduler"
  project_id = var.project_id
  jobs       = [
    {
      name     = "nightly_exports"
      schedule = "0 2 * * *"
      http_target = null
      workflow = "booking_orchestrator"
    },
    {
      name     = "reminders"
      schedule = "*/15 * * * *"
      http_target = null
      workflow = "booking_orchestrator"
    },
    {
      name     = "rebuild_availability"
      schedule = "0 * * * *"
      http_target = null
      workflow = "booking_orchestrator"
    }
  ]
}

module "run_services" {
  source     = "./modules/run_service"
  project_id = var.project_id
  region     = var.region
  services   = {
    core-api = {
      image_repo    = "ai-apps"
      memory        = "512Mi"
      cpu           = "1"
      timeout       = 60
      concurrency   = 80
      env           = {
        SERVICE_NAME = "core-api"
      }
      invokers      = []
      vpc_connector = null
    }
    booking = {
      image_repo    = "ai-apps"
      memory        = "512Mi"
      cpu           = "1"
      timeout       = 60
      concurrency   = 80
      env           = {
        SERVICE_NAME = "booking"
      }
      invokers      = []
      vpc_connector = null
    }
    payments = {
      image_repo    = "ai-apps"
      memory        = "512Mi"
      cpu           = "1"
      timeout       = 60
      concurrency   = 80
      env           = {
        SERVICE_NAME = "payments"
      }
      invokers      = []
      vpc_connector = null
    }
    notifications = {
      image_repo    = "ai-apps"
      memory        = "512Mi"
      cpu           = "1"
      timeout       = 60
      concurrency   = 80
      env           = {
        SERVICE_NAME = "notifications"
      }
      invokers      = []
      vpc_connector = null
    }
    agents-runner = {
      image_repo    = "ai-apps"
      memory        = "1Gi"
      cpu           = "1"
      timeout       = 120
      concurrency   = 40
      env           = {
        SERVICE_NAME     = "agents-runner"
        VERTEX_LOCATION  = var.region
        VERTEX_MODEL     = "projects/${var.project_id}/locations/${var.region}/publishers/google/models/gemini-1.5-pro-001"
      }
      invokers      = []
      vpc_connector = null
    }
    webhook-handler = {
      image_repo    = "ai-apps"
      memory        = "256Mi"
      cpu           = "1"
      timeout       = 30
      concurrency   = 80
      env           = {
        SERVICE_NAME = "webhook-handler"
      }
      invokers      = []
      vpc_connector = null
    }
    pricing-optimizer = {
      image_repo    = "ai-apps"
      memory        = "1Gi"
      cpu           = "1"
      timeout       = 120
      concurrency   = 40
      env           = {
        SERVICE_NAME     = "pricing-optimizer"
        VERTEX_LOCATION  = var.region
        VERTEX_MODEL     = "projects/${var.project_id}/locations/${var.region}/publishers/google/models/gemini-1.5-pro-001"
      }
      invokers      = []
      vpc_connector = null
    }
  }
}

module "api_gateway" {
  source                = "./modules/api_gateway"
  project_id            = var.project_id
  region                = var.region
  gateway_id            = "salon-gw"
  openapi_spec_path     = "${path.module}/modules/api_gateway/openapi.yaml"
  firebase_jwt_issuer   = var.firebase_jwt_issuer
  firebase_jwt_aud      = var.firebase_jwt_audience
  invoker_service_acct  = module.iam.api_gateway_sa_email
  backends              = module.run_services.service_urls
}

module "monitoring" {
  source     = "./modules/monitoring"
  project_id = var.project_id
}

module "budgets" {
  source     = "./modules/budgets"
  project_id = var.project_id
  amount     = 200
  threshold  = var.billing_alert_threshold
}
