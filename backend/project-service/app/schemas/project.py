from pydantic import BaseModel, Field
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
