import os
import shutil
import uuid
import logging
from typing import BinaryIO, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class LocalStorage:
    """
    A local file system storage implementation for development purposes.
    This class mimics the interface of the R2Storage class but stores files locally.
    """
    
    def __init__(self):
        # Create a directory for storing uploaded files
        self.storage_dir = Path("./local_storage")
        self.storage_dir.mkdir(exist_ok=True)
        
        # Base URL for accessing files (for development)
        self.base_url = "http://localhost:8000/local_storage"
    
    def upload_file(
        self, 
        file_obj: BinaryIO, 
        content_type: str, 
        folder: str = "uploads"
    ) -> Tuple[str, str]:
        """
        Upload a file to local storage
        
        Args:
            file_obj: File-like object to upload
            content_type: MIME type of the file
            folder: Folder to store the file in
            
        Returns:
            Tuple of (storage_key, public_url)
        """
        # Create folder if it doesn't exist
        folder_path = self.storage_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Generate a unique filename
        file_id = str(uuid.uuid4())
        extension = self._get_extension_from_content_type(content_type)
        filename = f"{file_id}{extension}"
        
        # Full path to the file
        file_path = folder_path / filename
        
        # Storage key (relative path)
        key = f"{folder}/{filename}"
        
        try:
            # Save the file
            file_obj.seek(0)
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file_obj, f)
            
            # Construct the public URL
            public_url = f"{self.base_url}/{key}"
            
            logger.info(f"File saved locally at {file_path}")
            return key, public_url
        except Exception as e:
            logger.error(f"Error saving file locally: {e}")
            raise
    
    def delete_file(self, key: str) -> bool:
        """
        Delete a file from local storage
        
        Args:
            key: Storage key of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.storage_dir / key
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted locally: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file locally: {e}")
            return False
    
    def get_file_url(self, key: str) -> str:
        """
        Get the public URL for a file
        
        Args:
            key: Storage key of the file
            
        Returns:
            Public URL for the file
        """
        return f"{self.base_url}/{key}"
    
    def check_file_exists(self, key: str) -> bool:
        """
        Check if a file exists in local storage
        
        Args:
            key: Storage key of the file
            
        Returns:
            True if the file exists, False otherwise
        """
        file_path = self.storage_dir / key
        return file_path.exists()
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """
        Get file extension from content type
        
        Args:
            content_type: MIME type
            
        Returns:
            File extension with dot
        """
        content_type_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
        }
        
        return content_type_map.get(content_type, '.bin')

# Create a singleton instance
storage = LocalStorage()
