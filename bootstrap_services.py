import os

base_dir = r"d:\Helex\backend"

services = {
    "api-gateway": 8000,
    "auth-service": 8001,
    "project-service": 8002,
    "collab-service": 8003,
    "terminal-service": 8004
}

for service, port in services.items():
    app_dir = os.path.join(base_dir, service, "app")
    
    # Write main.py
    main_content = f"""from fastapi import FastAPI
import uvicorn
from app.config import settings

app = FastAPI(title="{service.replace('-', ' ').title()}", version="1.0.0")

@app.get("/health")
def health_check():
    return {{"status": "ok", "service": "{service}"}}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
"""
    with open(os.path.join(app_dir, "main.py"), "w") as f:
        f.write(main_content)
        
    # Write config.py
    config_content = f"""import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PORT: int = int(os.getenv("PORT", {port}))

settings = Settings()
"""
    with open(os.path.join(app_dir, "config.py"), "w") as f:
        f.write(config_content)
        
    # Write .env.example
    env_content = f"PORT={port}\n"
    with open(os.path.join(base_dir, service, ".env.example"), "w") as f:
        f.write(env_content)

print("Microservices bootstrapped successfully.")
