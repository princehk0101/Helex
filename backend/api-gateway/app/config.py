from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PORT: int = 8000
    SECRET_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    PROJECT_SERVICE_URL: str = "http://localhost:8002"
    COLLAB_SERVICE_URL: str = "http://localhost:8003"
    TERMINAL_SERVICE_URL: str = "http://localhost:8004"
    CHAT_SERVICE_URL: str = "http://localhost:8005"
    AI_SERVICE_URL: str = "http://localhost:8006"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
