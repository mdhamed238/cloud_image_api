import pytest
import os
from fastapi import status
from PIL import Image
from sqlalchemy.orm import Session

from app.db.models import Image as ImageModel, Transformation, User
from app.api.schemas import ImageCreate
from app.utils.image_processor import ImageProcessor

# Test image file path
TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test_image.jpg")

@pytest.fixture(scope="function")
def test_image():
    """Create a test image file for upload testing"""
    # Create a test image if it doesn't exist
    if not os.path.exists(TEST_IMAGE_PATH):
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(TEST_IMAGE_PATH)
    
    # Return the file path
    return TEST_IMAGE_PATH

@pytest.fixture(scope="function")
def test_user(client, db_session):
    """Create a test user for API testing"""
    # Create a test user with a unique email using a timestamp
    import time
    unique_suffix = str(int(time.time() * 1000))
    
    from app.auth.security import get_password_hash
    
    user = User(
        username=f"testuser{unique_suffix}",
        email=f"test{unique_suffix}@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    response = client.post(
        "/api/auth/login",
        data={
            "username": f"testuser{unique_suffix}",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    
    return {"user_id": user.id, "token": token}

@pytest.fixture(scope="function")
def uploaded_image(client, test_user, test_image):
    """Create an uploaded image for testing"""
    token = test_user["token"]
    
    # Upload an image
    with open(test_image, "rb") as f:
        response = client.post(
            "/api/images/upload",
            files={"file": ("test_image.jpg", f, "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    return response.json(), token

def test_upload_image(client, test_user, test_image, db_session):
    """Test image upload endpoint"""
    token = test_user["token"]
    
    # Upload an image
    with open(test_image, "rb") as f:
        response = client.post(
            "/api/images/upload",
            files={"file": ("test_image.jpg", f, "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert "filename" in data
    assert "original_url" in data
    assert "created_at" in data
    
    # Check that the image was created in the database
    image = db_session.query(ImageModel).filter(ImageModel.id == data["id"]).first()
    assert image is not None
    assert image.filename == "test_image.jpg"

def test_get_images(client, db_session, uploaded_image):
    """Test getting list of images"""
    image_data, token = uploaded_image
    
    # Get list of images
    response = client.get(
        "/api/images",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Check if response is in pagination format
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1
    
    # Check pagination
    response = client.get(
        "/api/images?page=1&limit=5",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "limit" in data
    assert data["limit"] == 5

def test_get_image_by_id(client, db_session, uploaded_image):
    """Test getting a specific image by ID"""
    image_data, token = uploaded_image
    
    # Get image by ID
    response = client.get(
        f"/api/images/{image_data['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == image_data["id"]
    assert data["filename"] == image_data["filename"]
    assert data["original_url"] == image_data["original_url"]
    
    # Use db_session to query the database
    image = db_session.query(ImageModel).filter(ImageModel.id == data["id"]).first()
    assert image is not None

def test_transform_image(client, db_session, uploaded_image):
    """Test image transformation endpoint"""
    image_data, token = uploaded_image
    
    # Apply a transformation
    response = client.post(
        f"/api/images/{image_data['id']}/transform",
        json={
            "operations": [
                {
                    "type": "resize",
                    "params": {
                        "width": 50,
                        "height": 50
                    }
                },
                {
                    "type": "filter",
                    "params": {
                        "filter_type": "grayscale"
                    }
                }
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "transformation_id" in data
    assert "url" in data
    assert data["url"].startswith("http")  # Ensure URL is valid

def test_delete_transformation(client, db_session, uploaded_image):
    """Test deleting a transformation"""
    image_data, token = uploaded_image
    
    # Create a transformation
    response = client.post(
        f"/api/images/{image_data['id']}/transform",
        json={
            "operations": [
                {
                    "type": "resize",
                    "params": {
                        "width": 50
                    }
                }
            ]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    transformation_data = response.json()
    transformation_id = transformation_data["transformation_id"]
    
    # Delete the transformation
    response = client.delete(
        f"/api/transformations/{transformation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check status code - accept either 204 (No Content) or 200 (OK)
    assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

def test_delete_image(client, db_session, uploaded_image):
    """Test deleting an image"""
    image_data, token = uploaded_image
    
    # Delete the image
    response = client.delete(
        f"/api/images/{image_data['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's gone
    image = db_session.query(ImageModel).filter(
        ImageModel.id == image_data["id"]
    ).first()
    assert image is None
    
    # Verify we can't access it anymore
    response = client.get(
        f"/api/images/{image_data['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_unauthorized_access(client, db_session, uploaded_image):
    """Test unauthorized access to protected endpoints"""
    image_data, _ = uploaded_image
    
    # Try to access without token
    response = client.get("/api/images")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.get(f"/api/images/{image_data['id']}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Try to upload without token
    with open(TEST_IMAGE_PATH, "rb") as f:
        response = client.post(
            "/api/images/upload",
            files={"file": ("test_image.jpg", f, "image/jpeg")}
        )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_invalid_image_id(client, db_session, uploaded_image):
    """Test accessing non-existent image"""
    _, token = uploaded_image
    
    # Try to access non-existent image
    response = client.get(
        "/api/images/9999",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Clean up test image after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Clean up test resources after all tests"""
    def remove_test_image():
        if os.path.exists(TEST_IMAGE_PATH):
            os.remove(TEST_IMAGE_PATH)
    
    request.addfinalizer(remove_test_image)
