import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.db.models import User
from app.auth.security import get_password_hash

def test_register_user(client, db_session):
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    
    # Check that the user was created in the database
    user = db_session.query(User).filter(User.username == "testuser").first()
    assert user is not None
    assert user.email == "test@example.com"

def test_register_existing_username(client, db_session):
    """Test registration with an existing username."""
    # Create a user
    db_session.add(User(
        username="existinguser",
        email="existing@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    ))
    db_session.commit()
    
    # Try to register with the same username
    response = client.post(
        "/api/auth/register",
        json={
            "username": "existinguser",
            "email": "new@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]

def test_login(client, db_session):
    """Test user login."""
    # Create a user
    db_session.add(User(
        username="loginuser",
        email="login@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    ))
    db_session.commit()
    
    # Login with username
    response = client.post(
        "/api/auth/login",
        data={
            "username": "loginuser",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Login with email
    response = client.post(
        "/api/auth/login",
        data={
            "username": "login@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data

def test_login_wrong_password(client, db_session):
    """Test login with wrong password."""
    # Create a user
    db_session.add(User(
        username="wrongpassuser",
        email="wrong@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    ))
    db_session.commit()
    
    # Try to login with wrong password
    response = client.post(
        "/api/auth/login",
        data={
            "username": "wrongpassuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]
