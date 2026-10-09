from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    PORT: int = 8006
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    PROJECT_SERVICE_URL: str = "http://localhost:8002"
    LLM_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
