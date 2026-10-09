from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, UniqueConstraint, PrimaryKeyConstraint
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
