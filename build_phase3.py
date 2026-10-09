import os

base_dir = r"d:\Helex"

files = {
    "backend/project-service/.env.example": """DATABASE_URL=postgresql://helex_admin:helex_secret@localhost:5432/project_db
SECRET_KEY=default-secret-key-helex-dev-12345
PORT=8002
ALLOWED_ORIGINS=http://localhost:5173
""",
    
    "backend/project-service/app/config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    PORT: int = 8002
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
""",
    
    "backend/project-service/app/database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
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
    
    "backend/project-service/app/models/project.py": """from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    language = Column(String, nullable=False, default="python")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Member(Base):
    __tablename__ = "members"
    user_id = Column(UUID(as_uuid=True), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False) # OWNER, EDITOR, VIEWER
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'project_id'),
    )

class File(Base):
    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    path = Column(String, nullable=False)
    is_folder = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('project_id', 'path', name='uix_project_path'),
    )

class Invite(Base):
    __tablename__ = "invites"
    token = Column(String, primary_key=True, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    max_uses = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
""",
    
    "backend/project-service/app/schemas/project.py": """from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.schemas import Role

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    language: str = "python"

class ProjectResponse(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    language: str
    created_at: datetime
    model_config = {"from_attributes": True}

class MemberResponse(BaseModel):
    user_id: UUID
    project_id: UUID
    role: Role
    joined_at: datetime
    model_config = {"from_attributes": True}

class FileCreate(BaseModel):
    path: str
    is_folder: bool = False

class FileResponse(BaseModel):
    id: UUID
    project_id: UUID
    path: str
    is_folder: bool
    updated_at: datetime
    model_config = {"from_attributes": True}

class AccessResponse(BaseModel):
    allowed: bool
    role: Optional[Role] = None
""",
    
    "backend/project-service/app/core/deps.py": """from fastapi import Depends, Request
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
""",
    
    "backend/project-service/app/services/project_service.py": """from sqlalchemy.orm import Session
from app.models.project import Project, Member, File
from app.schemas.project import ProjectCreate, FileCreate
import uuid
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.schemas import Role
from helex_common.exceptions import ForbiddenException, NotFoundException, BadRequestException

def create_project(db: Session, project: ProjectCreate, owner_id: uuid.UUID):
    db_project = Project(name=project.name, owner_id=owner_id, language=project.language)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Add owner as member
    member = Member(user_id=owner_id, project_id=db_project.id, role=Role.OWNER.value)
    db.add(member)
    db.commit()
    
    return db_project

def check_access(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, min_role: Role = None):
    member = db.query(Member).filter(Member.project_id == project_id, Member.user_id == user_id).first()
    if not member:
        raise ForbiddenException("You do not have access to this project")
    
    roles_hierarchy = {Role.VIEWER.value: 1, Role.EDITOR.value: 2, Role.OWNER.value: 3}
    if min_role and roles_hierarchy[member.role] < roles_hierarchy[min_role.value]:
        raise ForbiddenException(f"Requires {min_role.value} access")
    
    return member

def create_file(db: Session, project_id: uuid.UUID, file: FileCreate, user_id: uuid.UUID):
    check_access(db, project_id, user_id, min_role=Role.EDITOR)
    
    # Check duplicate
    existing = db.query(File).filter(File.project_id == project_id, File.path == file.path).first()
    if existing:
        raise BadRequestException("File or folder already exists at this path")
        
    db_file = File(project_id=project_id, path=file.path, is_folder=file.is_folder)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file
""",
    
    "backend/project-service/app/routers/project.py": """from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid
from typing import List

from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, FileCreate, FileResponse
from app.services.project_service import create_project, create_file, check_access
from app.core.deps import get_current_user_id
from app.models.project import Project, File

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_new_project(project: ProjectCreate, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return create_project(db, project, user_id)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: uuid.UUID, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    check_access(db, project_id, user_id)
    project = db.query(Project).filter(Project.id == project_id).first()
    return project

@router.post("/{project_id}/files", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
def add_file(project_id: uuid.UUID, file: FileCreate, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return create_file(db, project_id, file, user_id)

@router.get("/{project_id}/files", response_model=List[FileResponse])
def list_files(project_id: uuid.UUID, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    check_access(db, project_id, user_id)
    return db.query(File).filter(File.project_id == project_id).all()
""",
    
    "backend/project-service/app/routers/internal.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models.project import Member
from app.schemas.project import AccessResponse

router = APIRouter(prefix="/internal/projects", tags=["Internal"])

@router.get("/{project_id}/access", response_model=AccessResponse)
def check_internal_access(project_id: uuid.UUID, user_id: uuid.UUID, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.project_id == project_id, Member.user_id == user_id).first()
    if member:
        return {"allowed": True, "role": member.role}
    return {"allowed": False, "role": None}
""",
    
    "backend/project-service/app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import project, internal

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Project Service", version="1.0.0", lifespan=lifespan)

origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(project.router)
app.include_router(internal.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "project-service"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
""",
    
    "backend/project-service/tests/conftest.py": """import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_project.db"
os.environ["SECRET_KEY"] = "testsecret"

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
    engine.dispose()
    try:
        if os.path.exists("./test_project.db"):
            os.remove("./test_project.db")
    except PermissionError:
        pass

@pytest.fixture
def client():
    return TestClient(app)
""",

    "backend/project-service/tests/test_project.py": """import pytest
import uuid
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.jwt_utils import verify_token
import jwt

# Generate a fake token for testing
def get_fake_token(user_id):
    return jwt.encode({"sub": str(user_id)}, "testsecret", algorithm="HS256")

def test_create_project(client):
    user_id = uuid.uuid4()
    token = get_fake_token(user_id)
    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Test Project"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data
    
    # Store for next test
    os.environ["TEST_PROJECT_ID"] = data["id"]
    os.environ["TEST_USER_ID"] = str(user_id)

def test_get_project(client):
    project_id = os.environ.get("TEST_PROJECT_ID")
    user_id = os.environ.get("TEST_USER_ID")
    token = get_fake_token(user_id)
    
    response = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == project_id

def test_internal_access(client):
    project_id = os.environ.get("TEST_PROJECT_ID")
    user_id = os.environ.get("TEST_USER_ID")
    
    response = client.get(f"/internal/projects/{project_id}/access?user_id={user_id}")
    assert response.status_code == 200
    assert response.json()["allowed"] == True
    assert response.json()["role"] == "OWNER"

def test_add_file_as_owner(client):
    project_id = os.environ.get("TEST_PROJECT_ID")
    user_id = os.environ.get("TEST_USER_ID")
    token = get_fake_token(user_id)
    
    response = client.post(
        f"/api/v1/projects/{project_id}/files",
        headers={"Authorization": f"Bearer {token}"},
        json={"path": "src/main.py", "is_folder": False}
    )
    assert response.status_code == 201
    assert response.json()["path"] == "src/main.py"
"""
}

for rel_path, content in files.items():
    file_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)

import shutil
shutil.copy(os.path.join(base_dir, "backend/project-service/.env.example"), os.path.join(base_dir, "backend/project-service/.env"))

print("Phase 3 files built successfully.")
