from sqlalchemy.orm import Session
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
