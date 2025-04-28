from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    images = relationship("Image", back_populates="user")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    original_key = Column(String)  # Storage key in R2
    original_url = Column(String)  # Public URL
    content_type = Column(String)
    size = Column(Integer)  # Size in bytes
    width = Column(Integer)
    height = Column(Integer)
    _metadata_json = Column(Text)  # JSON serialized metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="images")
    transformations = relationship("Transformation", back_populates="image")

    def get_metadata(self):
        """Get the metadata as a dictionary"""
        if self._metadata_json and isinstance(self._metadata_json, str):
            return json.loads(self._metadata_json)
        return {}

    def set_metadata(self, value):
        """Set the metadata from a dictionary"""
        if value is not None:
            self._metadata_json = json.dumps(value)
        else:
            self._metadata_json = None

class Transformation(Base):
    __tablename__ = "transformations"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"))
    type = Column(String)  # resize, crop, rotate, etc.
    _parameters = Column(Text)  # JSON serialized parameters
    cached_key = Column(String)  # Storage key in R2
    cached_url = Column(String)  # Public URL
    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("Image", back_populates="transformations")

    def get_parameters(self):
        """Get the parameters as a dictionary"""
        if self._parameters and isinstance(self._parameters, str):
            return json.loads(self._parameters)
        return {}

    def set_parameters(self, value):
        """Set the parameters from a dictionary"""
        if value is not None:
            self._parameters = json.dumps(value)
        else:
            self._parameters = None
