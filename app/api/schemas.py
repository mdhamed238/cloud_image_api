from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator

class ImageBase(BaseModel):
    filename: str

class ImageCreate(ImageBase):
    pass

class ImageInDB(ImageBase):
    id: int
    user_id: int
    original_key: str
    original_url: str
    content_type: str
    size: int
    width: int
    height: int
    metadata: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True

class Image(ImageInDB):
    pass

class ImageList(BaseModel):
    items: List[Image]
    total: int
    page: int
    limit: int

class TransformationBase(BaseModel):
    type: str
    parameters: Dict[str, Any] = {}

class TransformationCreate(TransformationBase):
    pass

class TransformationInDB(TransformationBase):
    id: int
    image_id: int
    cached_key: str
    cached_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Transformation(TransformationInDB):
    pass

class ResizeParams(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    maintain_aspect: bool = True
    
    @field_validator('width', 'height')
    def validate_dimensions(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Dimensions must be positive")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "width": 800,
                "height": 600,
                "maintain_aspect": True
            }
        }

class CropParams(BaseModel):
    x: int
    y: int
    width: int
    height: int
    
    @field_validator('width', 'height')
    def validate_dimensions(cls, v):
        if v <= 0:
            raise ValueError("Dimensions must be positive")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "x": 100,
                "y": 100,
                "width": 500,
                "height": 500
            }
        }

class RotateParams(BaseModel):
    angle: float
    expand: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "angle": 90,
                "expand": True
            }
        }

class FormatParams(BaseModel):
    format: str
    quality: int = 85
    
    @field_validator('format')
    def validate_format(cls, v):
        valid_formats = ["jpeg", "jpg", "png", "webp", "gif"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Format must be one of: {', '.join(valid_formats)}")
        return v.lower()
    
    @field_validator('quality')
    def validate_quality(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Quality must be between 1 and 100")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "format": "webp",
                "quality": 85
            }
        }

class FilterParams(BaseModel):
    filter: str
    
    @field_validator('filter')
    def validate_filter(cls, v):
        valid_filters = ["grayscale", "sepia", "blur", "sharpen"]
        if v.lower() not in valid_filters:
            raise ValueError(f"Filter must be one of: {', '.join(valid_filters)}")
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "filter": "grayscale"
            }
        }

class TransformRequest(BaseModel):
    operations: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "operations": [
                    {
                        "type": "resize",
                        "width": 800,
                        "height": 600,
                        "maintain_aspect": True
                    },
                    {
                        "type": "filter",
                        "filter": "grayscale"
                    }
                ]
            }
        }

class TransformResponse(BaseModel):
    url: str
    transformation_id: int
