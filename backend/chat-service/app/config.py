from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    PORT: int = 8005
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    PROJECT_SERVICE_URL: str = "http://localhost:8002"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
