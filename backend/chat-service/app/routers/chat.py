from fastapi import APIRouter, Depends, status, HTTPException, WebSocket, WebSocketDisconnect
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
