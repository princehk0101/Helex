from fastapi import APIRouter, Request, Depends
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
