import boto3
from botocore.exceptions import ClientError
import logging
from typing import BinaryIO, Tuple
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)

class R2Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        )
        self.bucket_name = settings.R2_BUCKET_NAME
        self.public_url = settings.R2_PUBLIC_URL

    def upload_file(
        self, 
        file_obj: BinaryIO, 
        content_type: str, 
        folder: str = "uploads"
    ) -> Tuple[str, str]:
        """
        Upload a file to R2 storage
        
        Args:
            file_obj: File-like object to upload
            content_type: MIME type of the file
            folder: Folder to store the file in
            
        Returns:
            Tuple of (storage_key, public_url)
        """
        # Generate a unique filename
        file_id = str(uuid.uuid4())
        key = f"{folder}/{file_id}"
        
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read',
                }
            )
            
            # Construct the public URL
            public_url = f"{self.public_url}/{key}"
            
            return key, public_url
        except ClientError as e:
            logger.error(f"Error uploading file to R2: {e}")
            raise
    
    def delete_file(self, key: str) -> bool:
        """
        Delete a file from R2 storage
        
        Args:
            key: The key of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            logger.info(f"Successfully deleted file from R2: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file from R2: {e}")
            return False
    
    def get_file_url(self, key: str) -> str:
        """
        Get the public URL for a file
        
        Args:
            key: Storage key of the file
            
        Returns:
            Public URL for the file
        """
        return f"{self.public_url}/{key}"
    
    def check_file_exists(self, key: str) -> bool:
        """
        Check if a file exists in R2 storage
        
        Args:
            key: Storage key of the file
            
        Returns:
            True if the file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except ClientError:
            return False

# Create a singleton instance
storage = R2Storage()
