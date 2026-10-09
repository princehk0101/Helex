from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class MessageCreate(BaseModel):
    text: str

class MessageResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    text: str
    created_at: datetime
    model_config = {"from_attributes": True}
