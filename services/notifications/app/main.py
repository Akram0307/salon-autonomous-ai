from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
app = FastAPI()
@app.get('/health')
def health():
    return {"status": "ok", "service": os.getenv("SERVICE_NAME","unknown")}
