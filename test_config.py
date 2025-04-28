import os

# Set environment variables for testing
os.environ["SECRET_KEY"] = "testing-secret-key"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["DATABASE_URL"] = "sqlite:///./app.db"
os.environ["R2_ENDPOINT_URL"] = "https://example.r2.cloudflarestorage.com"
os.environ["R2_ACCESS_KEY_ID"] = "test-access-key"
os.environ["R2_SECRET_ACCESS_KEY"] = "test-secret-key"
os.environ["R2_BUCKET_NAME"] = "test-bucket"
os.environ["R2_PUBLIC_URL"] = "https://test-public-url.com"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["REDIS_CACHE_EXPIRY"] = "86400"
