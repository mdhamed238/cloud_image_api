from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api import router as api_router
from app.auth import router as auth_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

app = FastAPI(
    title=settings.APP_NAME,
    description="Cloud Image Processing API",
    version="0.1.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(api_router.router, prefix="/api", tags=["api"])

# Mount static files for local storage (development only)
local_storage_path = os.path.join(os.getcwd(), "local_storage")
if os.path.exists(local_storage_path):
    app.mount("/local_storage", StaticFiles(directory=local_storage_path), name="local_storage")

# Create database tables on startup if they don't exist
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the Cloud Image Processing API"}

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicornf
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
