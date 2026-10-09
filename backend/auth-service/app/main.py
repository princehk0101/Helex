from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables for now, real migration needs Alembic
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Auth Service", version="1.0.0", lifespan=lifespan)

origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth-service"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
