from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import logging

from app.config import settings
from app.routes import router
from app.middleware.auth import verify_jwt_middleware
import sys
import os

# To ensure the common exceptions are accessible when handling HTTP errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Helex API Gateway", version="1.0.0")

# CORS middleware
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth middleware for verifying JWT token on protected routes
app.add_middleware(BaseHTTPMiddleware, dispatch=verify_jwt_middleware)

# Register routes
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "api-gateway"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
