from fastapi import APIRouter, Depends, status
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
