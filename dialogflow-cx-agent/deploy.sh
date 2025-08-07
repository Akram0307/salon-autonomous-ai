#!/bin/bash

# Set environment variables
export GOOGLE_CLOUD_PROJECT_ID="salon-autonomous-ai-467811"
export LOCATION_ID="asia-south1"

# Create temp directory if it doesn't exist
mkdir -p temp

# Process configuration files and replace placeholders
for file in intents/*.json entities/*.json webhooks/*.json flows/*.json; do
  if [ -f "$file" ]; then
    echo "Processing $file..."
    sed -e "s/\${GOOGLE_CLOUD_PROJECT_ID}/$GOOGLE_CLOUD_PROJECT_ID/g" \
        -e "s/\${LOCATION_ID}/$LOCATION_ID/g" \
        "$file" > "temp/$(basename "$file")"
  fi
done

echo "Configuration files processed. Please update the AGENT_ID and API_KEY in the processed files before importing."
