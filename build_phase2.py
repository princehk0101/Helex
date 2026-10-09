import os

base_dir = r"d:\Helex"

files = {
    "backend/api-gateway/.env.example": """PORT=8000
SECRET_KEY=default-secret-key-helex-dev-12345
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
AUTH_SERVICE_URL=http://localhost:8001
PROJECT_SERVICE_URL=http://localhost:8002
COLLAB_SERVICE_URL=http://localhost:8003
TERMINAL_SERVICE_URL=http://localhost:8004
CHAT_SERVICE_URL=http://localhost:8005
AI_SERVICE_URL=http://localhost:8006
""",

    "backend/api-gateway/app/config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PORT: int = 8000
    SECRET_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    PROJECT_SERVICE_URL: str = "http://localhost:8002"
    COLLAB_SERVICE_URL: str = "http://localhost:8003"
    TERMINAL_SERVICE_URL: str = "http://localhost:8004"
    CHAT_SERVICE_URL: str = "http://localhost:8005"
    AI_SERVICE_URL: str = "http://localhost:8006"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
""",

    "backend/api-gateway/app/middleware/auth.py": """from fastapi import Request
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.jwt_utils import verify_token
from helex_common.exceptions import UnauthorizedException
from app.config import settings

# Paths that bypass JWT verification
PUBLIC_PATHS = [
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/docs",
    "/openapi.json",
    "/health"
]

async def verify_jwt_middleware(request: Request, call_next):
    # Check if path is public
    for path in PUBLIC_PATHS:
        if request.url.path.startswith(path):
            return await call_next(request)
            
    # For websockets, token might be in query string
    # For REST, token should be in Authorization header
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = request.query_params.get("token")
        
    if not token:
        # Note: Exception in middleware needs to be returned as a JSONResponse if outside routing
        # But we can also use Starlette's exception handling if we raise it
        # Actually it's safer to raise the HTTPException and let FastAPI handle it.
        raise UnauthorizedException("Missing authentication token")
        
    payload = verify_token(token, settings.SECRET_KEY)
    if not payload or not payload.get("sub"):
        raise UnauthorizedException("Invalid or expired token")
        
    # Inject user_id into request state for downstream use if needed
    request.state.user_id = payload.get("sub")
    
    response = await call_next(request)
    return response
""",

    "backend/api-gateway/app/proxy.py": """import httpx
from fastapi import Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)

# Reusable client pool for better performance
client = httpx.AsyncClient()

async def forward_request(request: Request, target_url: str):
    method = request.method
    headers = dict(request.headers)
    # Remove host header to avoid conflicts when forwarding
    headers.pop("host", None)
    
    body = await request.body()
    
    try:
        url = httpx.URL(target_url)
        req = client.build_request(
            method=method,
            url=url,
            headers=headers,
            content=body,
            params=request.query_params,
        )
        
        response = await client.send(req, stream=True)
        
        # We stream the response back to the client to handle large payloads (like SSE) efficiently
        return StreamingResponse(
            response.aiter_raw(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
    except httpx.RequestError as e:
        logger.error(f"Proxy error when calling {target_url}: {e}")
        raise HTTPException(status_code=502, detail="Bad Gateway")
""",

    "backend/api-gateway/app/routes.py": """from fastapi import APIRouter, Request, Depends
from app.proxy import forward_request
from app.config import settings

router = APIRouter()

@router.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_auth(request: Request, path: str):
    target_url = f"{settings.AUTH_SERVICE_URL}/api/v1/auth/{path}"
    return await forward_request(request, target_url)

@router.api_route("/api/v1/projects/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_projects(request: Request, path: str):
    target_url = f"{settings.PROJECT_SERVICE_URL}/api/v1/projects/{path}"
    return await forward_request(request, target_url)

# Add other proxies (collab, terminal, chat, ai) as they are built in later phases.
""",

    "backend/api-gateway/app/main.py": """from fastapi import FastAPI
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
"""
}

for rel_path, content in files.items():
    file_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)

import shutil
shutil.copy(os.path.join(base_dir, "backend/api-gateway/.env.example"), os.path.join(base_dir, "backend/api-gateway/.env"))

print("Phase 2 files built successfully.")
