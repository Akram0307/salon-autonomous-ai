# Booking Service IAM Hardening Checklist

1) Remove public invoker (no change yet)
- gcloud run services remove-iam-policy-binding booking-service \
  --region=asia-south1 \
  --member=allUsers \
  --role=roles/run.invoker

2) Grant API Gateway managed SA invoker
- PROJECT=salon-autonomous-ai-467811
- PROJECT_NUMBER=$(gcloud projects describe $PROJECT --format='value(projectNumber)')
- GW_SA=service-$PROJECT_NUMBER@gateway.gserviceaccount.com
- gcloud run services add-iam-policy-binding booking-service \
  --region=asia-south1 \
  --member=serviceAccount:$GW_SA \
  --role=roles/run.invoker

3) Update Gateway security (choose one; defer enforcement for now)
- API Key: define x-google-api-key in OpenAPI and require key on paths
- JWT (Firebase recommended): add securityDefinitions with issuer https://securetoken.google.com/PROJECT_ID and audiences PROJECT_ID; apply to /api/services

4) Verification steps
- Direct call to Cloud Run should be 403 after removing allUsers:
  curl -i $(gcloud run services describe booking-service --region=asia-south1 --format='value(status.url)')/api/services
- Via API Gateway should be 200 OK (after Gateway deployed and SA bound):
  curl -i https://<gateway-domain>/api/services
