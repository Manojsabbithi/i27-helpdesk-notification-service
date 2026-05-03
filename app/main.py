from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load .env ONLY for local dev
load_dotenv(".env")
load_dotenv(".env.local", override=True)

from app.routes.notification_routes import router as notification_router

app = FastAPI(title="Notification Service")

@app.get("/healthz")
def health():
    return {"status": "UP"}

@app.get("/readyz")
def ready():
    return {"status": "READY"}

app.include_router(notification_router)
