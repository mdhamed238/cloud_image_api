import json
import logging
from typing import Any, Optional, Union
import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        self.redis_enabled = True
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            self.default_expiry = settings.REDIS_CACHE_EXPIRY
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis cache disabled: {e}")
            self.redis_enabled = False
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.redis_enabled:
            return None
            
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting value from Redis: {e}")
            return None
    
    def set(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        """
        Set a value in the cache
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            expiry: Expiry time in seconds (defaults to REDIS_CACHE_EXPIRY)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_enabled:
            return False
            
        try:
            expiry = expiry or self.default_expiry
            serialized = json.dumps(value)
            self.redis_client.setex(key, expiry, serialized)
            return True
        except Exception as e:
            logger.error(f"Error setting value in Redis: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_enabled:
            return False
            
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting value from Redis: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache
        
        Args:
            key: Cache key
            
        Returns:
            True if the key exists, False otherwise
        """
        if not self.redis_enabled:
            return False
            
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking if key exists in Redis: {e}")
            return False
    
    def get_transformation_key(self, image_id: int, transform_type: str, params: dict) -> str:
        """
        Generate a cache key for an image transformation
        
        Args:
            image_id: ID of the image
            transform_type: Type of transformation
            params: Transformation parameters
            
        Returns:
            Cache key
        """
        # Sort params to ensure consistent keys
        sorted_params = json.dumps(params, sort_keys=True)
        return f"transform:{image_id}:{transform_type}:{sorted_params}"

# Create a singleton instance
cache = RedisCache()
