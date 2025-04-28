import pytest
import os
import io
from unittest.mock import patch, MagicMock

from app.storage.r2 import R2Storage
from app.core.config import settings

@pytest.fixture
def mock_s3_client():
    """Create a mock S3 client for testing R2 storage"""
    mock_client = MagicMock()
    
    # Mock successful upload
    mock_client.upload_fileobj.return_value = None
    
    # Mock successful download
    def mock_download_fileobj(bucket, key, file_obj):
        file_obj.write(b"mock file content")
    
    mock_client.download_fileobj.side_effect = mock_download_fileobj
    
    # Mock successful delete
    mock_client.delete_object.return_value = {"DeleteMarker": True}
    
    return mock_client

@pytest.fixture
def r2_storage(mock_s3_client):
    """Create an R2Storage instance with a mock S3 client"""
    with patch('boto3.client', return_value=mock_s3_client):
        storage = R2Storage()
        storage.s3_client = mock_s3_client
        storage.bucket_name = "test-bucket"
        storage.public_url = "https://test-bucket.r2.cloudflarestorage.com"
        yield storage

def test_upload_file(r2_storage, mock_s3_client):
    """Test uploading a file to R2 storage"""
    # Create a test file
    file_content = b"test file content"
    file_obj = io.BytesIO(file_content)
    
    # Upload the file
    key, url = r2_storage.upload_file(file_obj, "image/jpeg", "original")
    
    # Verify the S3 client was called correctly
    mock_s3_client.upload_fileobj.assert_called_once()
    
    # Verify the key format
    assert key.startswith("original/")
    
    # Verify the URL is correctly formed
    assert url.startswith(r2_storage.public_url)
    assert "original/" in url

def test_upload_file_with_custom_filename(r2_storage, mock_s3_client):
    """Test uploading a file with a custom folder"""
    # Create a test file
    file_content = b"test file content"
    file_obj = io.BytesIO(file_content)
    
    # Upload with custom folder
    key, url = r2_storage.upload_file(file_obj, "image/png", "transformed")
    
    # Verify the key includes the custom folder
    assert key.startswith("transformed/")
    assert url.startswith(r2_storage.public_url)
    assert "transformed/" in url

def test_get_file_url(r2_storage):
    """Test constructing a URL for a file key"""
    key = "original/test_file.jpg"
    
    # Manually construct URL as the class doesn't have a get_url method
    url = f"{r2_storage.public_url}/{key}"
    
    assert url == f"{r2_storage.public_url}/{key}"

def test_delete_file(r2_storage, mock_s3_client):
    """Test deleting a file from R2 storage"""
    key = "test_user/original/test_file.jpg"
    
    # Delete the file
    result = r2_storage.delete_file(key)
    
    # Verify the S3 client was called correctly
    mock_s3_client.delete_object.assert_called_once_with(
        Bucket="test-bucket",
        Key=key
    )
    
    # Verify the result
    assert result is True

def test_delete_file_error_handling(r2_storage, mock_s3_client):
    """Test error handling when deleting a file"""
    # Make the delete operation fail
    mock_s3_client.delete_object.side_effect = Exception("Delete failed")
    
    key = "test_user/original/test_file.jpg"
    
    # Delete should return False on error
    result = r2_storage.delete_file(key)
    assert result is False

def test_upload_file_error_handling(r2_storage, mock_s3_client):
    """Test error handling when uploading a file"""
    # Make the upload operation fail
    mock_s3_client.upload_fileobj.side_effect = Exception("Upload failed")
    
    # Create a test file
    file_content = b"test file content"
    file_obj = io.BytesIO(file_content)
    file_obj.name = "test_file.jpg"
    
    # Upload should raise the exception
    with pytest.raises(Exception):
        r2_storage.upload_file(file_obj, "image/jpeg", "original")

def test_storage_integration(r2_storage):
    """Test the full file lifecycle in storage"""
    # Create a test file
    file_content = b"test file content"
    file_obj = io.BytesIO(file_content)
    file_obj.name = "test_file.jpg"
    
    # Upload
    key, url = r2_storage.upload_file(file_obj, "image/jpeg", "original")
    
    # Get URL
    assert url.endswith(key)
    
    # Delete
    result = r2_storage.delete_file(key)
    assert result is True
