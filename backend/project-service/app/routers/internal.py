from fastapi import APIRouter, Depends
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
