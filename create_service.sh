#!/bin/bash

SERVICE_NAME=$1

mkdir -p /root/salon-autonomous-ai/services/$SERVICE_NAME/app
touch /root/salon-autonomous-ai/services/$SERVICE_NAME/app/main.py /root/salon-autonomous-ai/services/$SERVICE_NAME/requirements.txt /root/salon-autonomous-ai/services/$SERVICE_NAME/Dockerfile

cat > /root/salon-autonomous-ai/services/$SERVICE_NAME/app/main.py << 'EOT'
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
EOT

cat > /root/salon-autonomous-ai/services/$SERVICE_NAME/requirements.txt << 'EOT'
fastapi>=0.68.0
uvicorn>=0.15.0
google-cloud-pubsub>=2.13.0
google-cloud-secret-manager>=2.10.0
EOT

cat > /root/salon-autonomous-ai/services/$SERVICE_NAME/Dockerfile << 'EOT'
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOT
