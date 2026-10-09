from sqlalchemy.orm import Session
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
