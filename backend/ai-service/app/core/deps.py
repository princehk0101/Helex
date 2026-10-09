from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import sys
import os
import uuid
from app.config import settings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.jwt_utils import verify_token
from helex_common.exceptions import UnauthorizedException

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> uuid.UUID:
    token = credentials.credentials
    payload = verify_token(token, settings.SECRET_KEY)
    if not payload or not payload.get("sub"):
        raise UnauthorizedException("Invalid token")
    return uuid.UUID(payload.get("sub"))

async def verify_project_access(project_id: uuid.UUID, user_id: uuid.UUID):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{settings.PROJECT_SERVICE_URL}/internal/projects/{project_id}/access?user_id={user_id}")
            if resp.status_code == 200 and resp.json().get("allowed") == True:
                return resp.json().get("role")
        except Exception:
            pass
    raise HTTPException(status_code=403, detail="No access to project")
