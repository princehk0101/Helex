from fastapi import Request
from fastapi.responses import JSONResponse
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.jwt_utils import verify_token
from app.config import settings

# Paths that bypass JWT verification
PUBLIC_PATHS = [
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/docs",
    "/openapi.json",
    "/health"
]

def unauthorized_response(message: str):
    return JSONResponse(
        status_code=401,
        content={"detail": {"detail": message, "code": "UNAUTHORIZED"}},
        headers={"WWW-Authenticate": "Bearer"}
    )

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
        return unauthorized_response("Missing authentication token")
        
    payload = verify_token(token, settings.SECRET_KEY)
    if not payload or not payload.get("sub"):
        return unauthorized_response("Invalid or expired token")
        
    # Inject user_id into request state for downstream use if needed
    request.state.user_id = payload.get("sub")
    
    response = await call_next(request)
    return response
