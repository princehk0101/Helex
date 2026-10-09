import os
import pathlib

base_dir = r"d:\Helex"

files = {
    # SHARED LIB
    "backend/shared/helex_common/__init__.py": "",
    "backend/shared/helex_common/schemas.py": """from enum import Enum

class Role(str, Enum):
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"
""",
    "backend/shared/helex_common/exceptions.py": """from fastapi import HTTPException

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail={"detail": detail, "code": "NOT_FOUND"})

class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail={"detail": detail, "code": "FORBIDDEN"})

class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail={"detail": detail, "code": "UNAUTHORIZED"}, headers={"WWW-Authenticate": "Bearer"})

class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=400, detail={"detail": detail, "code": "BAD_REQUEST"})
""",
    "backend/shared/helex_common/jwt_utils.py": """import jwt
from jwt.exceptions import InvalidTokenError
from typing import Optional

ALGORITHM = "HS256"

def verify_token(token: str, secret_key: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        return None
""",

    # AUTH SERVICE
    "backend/auth-service/.env.example": """DATABASE_URL=postgresql://helex_admin:helex_secret@localhost:5432/auth_db
SECRET_KEY=default-secret-key-helex-dev-12345
ACCESS_TOKEN_EXPIRE_MINUTES=60
PORT=8001
ALLOWED_ORIGINS=http://localhost:5173
""",
    "backend/auth-service/app/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PORT: int = 8001
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

settings = Settings()
""",
    "backend/auth-service/app/database.py": """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "backend/auth-service/app/models/user.py": """from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    color = Column(String, nullable=False) # e.g., hex code
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "backend/auth-service/app/schemas/user.py": """from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    color: str = Field(..., min_length=4, max_length=9)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    color: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
""",
    "backend/auth-service/app/core/security.py": """from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
""",
    "backend/auth-service/app/core/deps.py": """from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
import sys
import os

# Add shared library to path (temporary hack for direct running, better to use package install)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.jwt_utils import verify_token
from helex_common.exceptions import UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token, settings.SECRET_KEY)
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")
        
    user = db.query(User).filter(str(User.id) == user_id).first()
    if user is None:
        raise UnauthorizedException("User not found")
    return user
""",
    "backend/auth-service/app/services/auth_service.py": """from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.exceptions import BadRequestException

def create_user(db: Session, user: UserCreate):
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise BadRequestException("Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        color=user.color
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
""",
    "backend/auth-service/app/routers/auth.py": """from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import create_user
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.exceptions import UnauthorizedException

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user or not verify_password(user_login.password, user.password_hash):
        raise UnauthorizedException("Incorrect email or password")
        
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
""",
    "backend/auth-service/app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables for now, real migration needs Alembic
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Auth Service", version="1.0.0", lifespan=lifespan)

origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth-service"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
""",
    "backend/auth-service/tests/conftest.py": """import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Set testing env before importing app
os.environ["DATABASE_URL"] = "sqlite:///./test_auth.db"
os.environ["SECRET_KEY"] = "testsecret"

# We must ensure check_same_thread is False for SQLite
from app.database import Base, get_db
from app.main import app

engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_auth.db"):
        os.remove("./test_auth.db")

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "backend/auth-service/tests/test_auth.py": """def test_register(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password123", "color": "#FF0000"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_me(client):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
"""
}

for rel_path, content in files.items():
    file_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)

# create .env for auth-service
import shutil
shutil.copy(os.path.join(base_dir, "backend/auth-service/.env.example"), os.path.join(base_dir, "backend/auth-service/.env"))

print("Phase 1 files built successfully.")
