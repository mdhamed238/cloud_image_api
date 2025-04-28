import os
from typing import List, Union, Optional
from pydantic import validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Cloud Image API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    
    # Cloudflare R2
    R2_ENDPOINT_URL: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str
    R2_PUBLIC_URL: str
    
    # Redis
    REDIS_URL: str
    REDIS_CACHE_EXPIRY: int = 86400  # 24 hours in seconds
    
    # Image Processing
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: Optional[str], values: dict) -> str:
        if values.get("ENVIRONMENT") == "test":
            return "sqlite:///./test.db"
        return v
    
    class Config:
        env_file = [".env", ".env.local"]
        case_sensitive = True

settings = Settings()
