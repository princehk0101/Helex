from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
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
        await websocket.send_text("Error: You do not have permission to use the terminal.\r\n")
        await websocket.close(code=4003, reason="Forbidden")
        return

    if client is None:
        await websocket.send_text("Error: Docker daemon not running on the server.\r\n")
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
        await websocket.send_text(f"Error starting container: {str(e)}\r\n")
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
