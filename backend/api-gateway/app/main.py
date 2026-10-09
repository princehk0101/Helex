from fastapi import FastAPI
import uvicorn
from app.config import settings

app = FastAPI(title="Api Gateway", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "api-gateway"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
