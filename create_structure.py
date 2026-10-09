import os
import pathlib

base_dir = r"d:\Helex"

structure = {
    "backend/api-gateway/app/middleware": ["auth.py", "rate_limit.py", "logging.py"],
    "backend/api-gateway/app": ["main.py", "config.py", "routes.py", "proxy.py"],
    "backend/api-gateway/tests": [],
    "backend/api-gateway": ["Dockerfile", "requirements.txt", ".env.example"],
    
    "backend/auth-service/app/models": ["user.py"],
    "backend/auth-service/app/schemas": ["user.py"],
    "backend/auth-service/app/routers": ["auth.py"],
    "backend/auth-service/app/services": ["auth_service.py"],
    "backend/auth-service/app/core": ["security.py", "deps.py"],
    "backend/auth-service/app": ["main.py", "config.py", "database.py"],
    "backend/auth-service/alembic": [],
    "backend/auth-service/tests": [],
    "backend/auth-service": ["alembic.ini", "Dockerfile", "requirements.txt", ".env.example"],
    
    "backend/project-service/app/models": ["project.py", "member.py", "invite.py", "file.py"],
    "backend/project-service/app/schemas": [],
    "backend/project-service/app/routers": ["projects.py", "members.py", "invites.py", "files.py", "internal.py"],
    "backend/project-service/app/services": [],
    "backend/project-service/app/core": ["deps.py", "permissions.py"],
    "backend/project-service/app/clients": ["auth_client.py"],
    "backend/project-service/app": ["main.py", "config.py", "database.py"],
    "backend/project-service/alembic": [],
    "backend/project-service/tests": [],
    "backend/project-service": ["Dockerfile", "requirements.txt", ".env.example"],
    
    "backend/collab-service/app/models": ["document.py"],
    "backend/collab-service/app/ws": ["collab.py", "manager.py", "auth.py"],
    "backend/collab-service/app/services": ["persistence.py", "export.py"],
    "backend/collab-service/app/clients": ["project_client.py"],
    "backend/collab-service/app/core": ["redis.py"],
    "backend/collab-service/app": ["main.py", "config.py", "database.py"],
    "backend/collab-service/tests": [],
    "backend/collab-service": ["Dockerfile", "requirements.txt", ".env.example"],
    
    "backend/terminal-service/app/ws": ["terminal.py"],
    "backend/terminal-service/app/sandbox": ["manager.py", "limits.py", "runner.py"],
    "backend/terminal-service/app/clients": ["project_client.py"],
    "backend/terminal-service/app/core": ["auth.py"],
    "backend/terminal-service/app": ["main.py", "config.py"],
    "backend/terminal-service/sandbox-images": ["python.Dockerfile", "node.Dockerfile"],
    "backend/terminal-service/tests": [],
    "backend/terminal-service": ["Dockerfile", "requirements.txt", ".env.example"],
    
    "backend/chat-service": [],
    
    "backend/shared/helex_common": ["__init__.py", "jwt_utils.py", "schemas.py", "exceptions.py", "logging.py"],
    "backend/shared": ["pyproject.toml"],
    
    "backend/infra/nginx": ["nginx.conf"],
    "backend/infra/postgres": ["init-databases.sql"],
    "backend/infra": ["docker-compose.yml", "docker-compose.dev.yml", ".env.example"],
    
    "frontend": [],
    
    "docs": ["api-contract.md", "architecture.md"],
    
    ".github/workflows": [],
    ".github": ["CODEOWNERS"],
    
    "": [".gitignore", "README.md"]
}

for folder, files in structure.items():
    folder_path = os.path.join(base_dir, folder)
    if folder_path:
        pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        pathlib.Path(file_path).touch()

print("Structure created successfully.")
