import requests
import json
import os

# API endpoint
base_url = "http://localhost:8000"
login_url = f"{base_url}/api/auth/login"
upload_url = f"{base_url}/api/images/upload"

# Test user credentials - replace with valid credentials
user_credentials = {
    "username": "testuser",
    "password": "password123"
}

# Path to test image - replace with a valid image path
test_image_path = "test_image.jpg"

def create_test_image():
    """Create a simple test image if it doesn't exist"""
    if not os.path.exists(test_image_path):
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color = 'red')
            img.save(test_image_path)
            print(f"Created test image: {test_image_path}")
        except ImportError:
            print("PIL not installed. Please provide a test image manually.")
            return False
    return True

def login():
    """Login to get access token"""
    # Make sure to use form data for login, not JSON
    response = requests.post(
        login_url, 
        data=user_credentials,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        token_data = response.json()
        print("Login successful")
        return token_data.get("access_token")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def upload_image(token):
    """Upload an image to test R2 storage"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(test_image_path, "rb") as image_file:
        files = {"file": (os.path.basename(test_image_path), image_file, "image/jpeg")}
        response = requests.post(upload_url, headers=headers, files=files)
    
    if response.status_code == 201:
        print("Image upload successful!")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print(f"Image upload failed: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    # Create test image if needed
    if not create_test_image():
        print("Failed to create or find test image. Exiting.")
        exit(1)
    
    # Login to get token
    token = login()
    if not token:
        print("Failed to get authentication token. Exiting.")
        exit(1)
    
    # Upload test image
    success = upload_image(token)
    if success:
        print("R2 integration test completed successfully!")
    else:
        print("R2 integration test failed.")
