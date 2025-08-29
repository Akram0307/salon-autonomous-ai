# Booking Service Deployment Guide

## Prerequisites
- Google Cloud Project: salon-autonomous-ai-467811
- Firestore database created in asia-south1 region
- Service account with Firestore access

## Deployment Steps

1. Create service account JSON key and save as secret:
   
   gcloud secrets create booking-service-credentials      --data-file=path/to/service-account.json

2. Deploy to Cloud Run:

   gcloud run deploy booking-service      --image gcr.io/salon-autonomous-ai-467811/booking-service      --region asia-south1      --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/secrets/credentials.json      --update-secrets /secrets/credentials.json=booking-service-credentials:latest      --allow-unauthenticated

## Verification

1. Check service logs:

   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=booking-service" --limit=50

2. Test endpoints:

   curl https://booking-service-fz7fnhwmca-el.a.run.app/health
   curl https://booking-service-fz7fnhwmca-el.a.run.app/api/services
