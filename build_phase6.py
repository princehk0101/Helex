import os

base_dir = r"d:\Helex"

files = {
    "backend/ai-service/.env.example": """SECRET_KEY=default-secret-key-helex-dev-12345
PORT=8006
ALLOWED_ORIGINS=http://localhost:5173
PROJECT_SERVICE_URL=http://localhost:8002
LLM_API_KEY=mock-api-key
""",

    "backend/ai-service/app/config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    PORT: int = 8006
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    PROJECT_SERVICE_URL: str = "http://localhost:8002"
    LLM_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
""",

    "backend/ai-service/app/core/deps.py": """from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import sys
import os
import uuid
from app.config import settings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.jwt_utils import verify_token
from helex_common.exceptions import UnauthorizedException

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> uuid.UUID:
    token = credentials.credentials
    payload = verify_token(token, settings.SECRET_KEY)
    if not payload or not payload.get("sub"):
        raise UnauthorizedException("Invalid token")
    return uuid.UUID(payload.get("sub"))

async def verify_project_access(project_id: uuid.UUID, user_id: uuid.UUID):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{settings.PROJECT_SERVICE_URL}/internal/projects/{project_id}/access?user_id={user_id}")
            if resp.status_code == 200 and resp.json().get("allowed") == True:
                return resp.json().get("role")
        except Exception:
            pass
    raise HTTPException(status_code=403, detail="No access to project")
""",

    "backend/ai-service/app/routers/ai.py": """from fastapi import APIRouter, Depends
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
    suggestion = f"\\n# AI Suggestion based on context\\n# TODO: Implement logic here\\n"
    
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
""",

    "backend/ai-service/app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import settings
from app.routers import ai

app = FastAPI(title="AI Service", version="1.0.0")

origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-service"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
"""
}

for rel_path, content in files.items():
    file_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)

import shutil
shutil.copy(os.path.join(base_dir, "backend/ai-service/.env.example"), os.path.join(base_dir, "backend/ai-service/.env"))

print("Phase 6 AI service scaffolded.")
