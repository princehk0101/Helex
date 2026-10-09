from fastapi import APIRouter, Depends
import uuid
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from app.core.deps import get_current_user_id, verify_project_access
from app.config import settings

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

class CompletionRequest(BaseModel):
    project_id: uuid.UUID
    file_path: str
    prefix: str
    suffix: str

class ChatRequest(BaseModel):
    project_id: uuid.UUID
    messages: List[dict] # {"role": "user", "content": "..."}
    context_files: Optional[List[str]] = []

@router.post("/complete")
async def generate_completion(request: CompletionRequest, user_id: uuid.UUID = Depends(get_current_user_id)):
    await verify_project_access(request.project_id, user_id)
    
    # Mocking AI delay
    await asyncio.sleep(1)
    
    # In a real app, call LLM (e.g., Gemini or Claude) with prefix and suffix.
    suggestion = f"\n# AI Suggestion based on context\n# TODO: Implement logic here\n"
    
    return {"suggestion": suggestion}

@router.post("/chat")
async def ai_chat(request: ChatRequest, user_id: uuid.UUID = Depends(get_current_user_id)):
    await verify_project_access(request.project_id, user_id)
    
    # Mocking AI delay
    await asyncio.sleep(1.5)
    
    last_message = request.messages[-1].get("content", "")
    
    return {
        "reply": f"Antigravity Assistant: I see you are asking about '{last_message}'. Since this is a mock endpoint, I recommend checking the workspace files {request.context_files} for more details."
    }
