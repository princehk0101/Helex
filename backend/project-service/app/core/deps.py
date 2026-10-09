from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
import sys
import os
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.jwt_utils import verify_token
from helex_common.exceptions import UnauthorizedException

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> uuid.UUID:
    token = credentials.credentials
    payload = verify_token(token, settings.SECRET_KEY)
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")
        
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise UnauthorizedException("Invalid token payload")
        
    try:
        user_id = uuid.UUID(user_id_str)
        return user_id
    except ValueError:
        raise UnauthorizedException("Invalid user ID format")
