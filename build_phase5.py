import os

base_dir = r"d:\Helex"

files = {
    # ------------------ CHAT SERVICE ------------------
    "backend/chat-service/.env.example": """DATABASE_URL=postgresql://helex_admin:helex_secret@localhost:5432/chat_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=default-secret-key-helex-dev-12345
PORT=8005
ALLOWED_ORIGINS=http://localhost:5173
PROJECT_SERVICE_URL=http://localhost:8002
""",

    "backend/chat-service/app/config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    PORT: int = 8005
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    PROJECT_SERVICE_URL: str = "http://localhost:8002"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
""",

    "backend/chat-service/app/database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import redis.asyncio as redis

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

redis_client = redis.from_url(settings.REDIS_URL)
""",

    "backend/chat-service/app/models/chat.py": """from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",

    "backend/chat-service/app/schemas/chat.py": """from pydantic import BaseModel
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
""",

    "backend/chat-service/app/core/deps.py": """from fastapi import Depends, Query, WebSocket, WebSocketException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
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
    if not payload or not payload.get("sub"):
        raise UnauthorizedException("Invalid token")
    return uuid.UUID(payload.get("sub"))

async def get_ws_user_id(token: str = Query(...)) -> uuid.UUID:
    payload = verify_token(token, settings.SECRET_KEY)
    if not payload or not payload.get("sub"):
        raise WebSocketException(code=4001, reason="Invalid token")
    return uuid.UUID(payload.get("sub"))

async def verify_project_access(project_id: uuid.UUID, user_id: uuid.UUID):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{settings.PROJECT_SERVICE_URL}/internal/projects/{project_id}/access?user_id={user_id}")
            if resp.status_code == 200 and resp.json().get("allowed") == True:
                return True
        except Exception:
            pass
    return False
""",

    "backend/chat-service/app/routers/chat.py": """from fastapi import APIRouter, Depends, status, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import uuid
import json
import asyncio
from typing import List

from app.database import get_db, redis_client
from app.schemas.chat import MessageCreate, MessageResponse
from app.core.deps import get_current_user_id, get_ws_user_id, verify_project_access
from app.models.chat import Message

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

@router.get("/{project_id}/messages", response_model=List[MessageResponse])
async def get_messages(project_id: uuid.UUID, user_id: uuid.UUID = Depends(get_current_user_id), db: Session = Depends(get_db)):
    if not await verify_project_access(project_id, user_id):
        raise HTTPException(status_code=403, detail="No access to project")
    
    messages = db.query(Message).filter(Message.project_id == project_id).order_by(Message.created_at.desc()).limit(50).all()
    return messages[::-1]  # Return chronologically

@router.websocket("/ws/{project_id}")
async def chat_websocket(websocket: WebSocket, project_id: uuid.UUID, user_id: uuid.UUID = Depends(get_ws_user_id), db: Session = Depends(get_db)):
    await websocket.accept()
    
    if not await verify_project_access(project_id, user_id):
        await websocket.close(code=4003, reason="Forbidden")
        return

    pubsub = redis_client.pubsub()
    channel_name = f"chat_{project_id}"
    await pubsub.subscribe(channel_name)

    async def reader():
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    data = message['data'].decode('utf-8')
                    await websocket.send_text(data)
                await asyncio.sleep(0.01)
        except Exception:
            pass

    task = asyncio.create_task(reader())
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Save to DB
            new_msg = Message(project_id=project_id, user_id=user_id, text=data)
            db.add(new_msg)
            db.commit()
            db.refresh(new_msg)
            
            payload = {
                "id": str(new_msg.id),
                "project_id": str(project_id),
                "user_id": str(user_id),
                "text": data,
                "created_at": new_msg.created_at.isoformat()
            }
            
            # Broadcast via Redis
            await redis_client.publish(channel_name, json.dumps(payload))
            
    except WebSocketDisconnect:
        pass
    finally:
        task.cancel()
        await pubsub.unsubscribe(channel_name)
""",

    "backend/chat-service/app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Chat Service", version="1.0.0", lifespan=lifespan)

origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "chat-service"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
""",


    # ------------------ TERMINAL SERVICE ------------------
    "backend/terminal-service/.env.example": """SECRET_KEY=default-secret-key-helex-dev-12345
PORT=8004
ALLOWED_ORIGINS=http://localhost:5173
PROJECT_SERVICE_URL=http://localhost:8002
""",

    "backend/terminal-service/app/config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    PORT: int = 8004
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    PROJECT_SERVICE_URL: str = "http://localhost:8002"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
""",

    "backend/terminal-service/app/core/deps.py": """from fastapi import Query, WebSocketException
import httpx
import sys
import os
import uuid
from app.config import settings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../shared")))
from helex_common.jwt_utils import verify_token

async def get_ws_user_id(token: str = Query(...)) -> uuid.UUID:
    payload = verify_token(token, settings.SECRET_KEY)
    if not payload or not payload.get("sub"):
        raise WebSocketException(code=4001, reason="Invalid token")
    return uuid.UUID(payload.get("sub"))

async def verify_project_access(project_id: uuid.UUID, user_id: uuid.UUID):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{settings.PROJECT_SERVICE_URL}/internal/projects/{project_id}/access?user_id={user_id}")
            if resp.status_code == 200 and resp.json().get("allowed") == True:
                return resp.json().get("role")
        except Exception:
            pass
    return None
""",

    "backend/terminal-service/app/routers/terminal.py": """from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
import uuid
import docker
import asyncio
import threading
from app.core.deps import get_ws_user_id, verify_project_access

router = APIRouter(prefix="/api/v1/terminal", tags=["Terminal"])

# Keep track of running containers per project
# In a real app, this should be tracked more robustly and cleaned up after inactivity
active_terminals = {}

try:
    client = docker.from_env()
except:
    client = None

@router.websocket("/ws/{project_id}")
async def terminal_websocket(websocket: WebSocket, project_id: uuid.UUID, user_id: uuid.UUID = Depends(get_ws_user_id)):
    await websocket.accept()
    
    role = await verify_project_access(project_id, user_id)
    if not role or role == "VIEWER":
        await websocket.send_text("Error: You do not have permission to use the terminal.\\r\\n")
        await websocket.close(code=4003, reason="Forbidden")
        return

    if client is None:
        await websocket.send_text("Error: Docker daemon not running on the server.\\r\\n")
        await websocket.close(code=1011)
        return

    # For simplicity, create a container per project if not exists
    # Wait, we need to execute bash inside a new container or a running one.
    # Let's run a new isolated python:3.11-slim container for the session.
    try:
        container = client.containers.run(
            "python:3.11-slim",
            command="bash",
            tty=True,
            stdin_open=True,
            detach=True,
            mem_limit="256m"
        )
    except Exception as e:
        await websocket.send_text(f"Error starting container: {str(e)}\\r\\n")
        await websocket.close(code=1011)
        return

    socket = container.attach_socket(params={'stdin': 1, 'stdout': 1, 'stderr': 1, 'stream': 1})
    
    # Thread to read from docker socket and write to websocket
    def docker_to_ws():
        try:
            while True:
                # The socket returns bytes. We read up to 4096 bytes.
                # Use socket._sock for raw reading
                data = socket._sock.recv(4096)
                if not data:
                    break
                # Run the async send_text in the main loop
                asyncio.run_coroutine_threadsafe(websocket.send_text(data.decode('utf-8', errors='replace')), asyncio.get_event_loop())
        except Exception:
            pass

    thread = threading.Thread(target=docker_to_ws, daemon=True)
    thread.start()

    try:
        while True:
            data = await websocket.receive_text()
            # Send data to docker socket
            socket._sock.send(data.encode('utf-8'))
    except WebSocketDisconnect:
        pass
    finally:
        # Cleanup
        try:
            container.stop(timeout=1)
            container.remove(force=True)
        except:
            pass
""",

    "backend/terminal-service/app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import settings
from app.routers import terminal

app = FastAPI(title="Terminal Service", version="1.0.0")

origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(terminal.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "terminal-service"}

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
shutil.copy(os.path.join(base_dir, "backend/chat-service/.env.example"), os.path.join(base_dir, "backend/chat-service/.env"))
shutil.copy(os.path.join(base_dir, "backend/terminal-service/.env.example"), os.path.join(base_dir, "backend/terminal-service/.env"))

print("Phase 5 files built successfully.")
