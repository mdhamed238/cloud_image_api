import json
import logging
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile, status, BackgroundTasks
from sqlalchemy.orm import Session
from io import BytesIO

from app.api import schemas
from app.auth.deps import get_current_user
from app.cache.redis import cache
from app.core.config import settings
from app.db.models import Image, Transformation, User
from app.db.session import get_db
# Switch to R2 storage for production
# from app.storage.local_storage import storage
from app.storage.r2 import storage
from app.utils.image_processor import image_processor

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/images/upload", response_model=schemas.Image, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a new image
    """
    # Validate file size
    content = await file.read()
    if len(content) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_IMAGE_SIZE / (1024 * 1024)}MB"
        )
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1][1:].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file extension. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Get image info
    try:
        image_info = image_processor.get_image_info(content)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )
    
    # Upload to R2
    file_obj = BytesIO(content)
    file_obj.seek(0)
    key, url = storage.upload_file(
        file_obj=file_obj,
        content_type=file.content_type,
        folder=f"users/{current_user.id}/original"
    )
    
    # Create database record
    db_image = Image(
        user_id=current_user.id,
        filename=file.filename,
        original_key=key,
        original_url=url,
        content_type=file.content_type,
        size=len(content),
        width=image_info["width"],
        height=image_info["height"]
    )
    
    # Set metadata using the method instead of property
    db_image.set_metadata({"format": image_info["format"]})
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    
    # Convert the image to a schema response with proper metadata
    return {
        "id": db_image.id,
        "user_id": db_image.user_id,
        "filename": db_image.filename,
        "original_key": db_image.original_key,
        "original_url": db_image.original_url,
        "content_type": db_image.content_type,
        "size": db_image.size,
        "width": db_image.width,
        "height": db_image.height,
        "metadata": db_image.get_metadata(),
        "created_at": db_image.created_at
    }

@router.get("/images", response_model=schemas.ImageList)
def list_images(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List images for the current user
    """
    offset = (page - 1) * limit
    
    # Get total count
    total = db.query(Image).filter(Image.user_id == current_user.id).count()
    
    # Get images for current page
    images = db.query(Image).filter(
        Image.user_id == current_user.id
    ).order_by(
        Image.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    # Convert images to proper schema format with metadata
    formatted_images = []
    for image in images:
        formatted_images.append({
            "id": image.id,
            "user_id": image.user_id,
            "filename": image.filename,
            "original_key": image.original_key,
            "original_url": image.original_url,
            "content_type": image.content_type,
            "size": image.size,
            "width": image.width,
            "height": image.height,
            "metadata": image.get_metadata(),
            "created_at": image.created_at
        })
    
    return {
        "items": formatted_images,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/images/{image_id}", response_model=schemas.Image)
def get_image(
    image_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific image by ID
    """
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Convert the image to a schema response with proper metadata
    return {
        "id": image.id,
        "user_id": image.user_id,
        "filename": image.filename,
        "original_key": image.original_key,
        "original_url": image.original_url,
        "content_type": image.content_type,
        "size": image.size,
        "width": image.width,
        "height": image.height,
        "metadata": image.get_metadata(),
        "created_at": image.created_at
    }

@router.post("/images/{image_id}/transform", response_model=schemas.TransformResponse)
async def transform_image(
    background_tasks: BackgroundTasks,
    transform_request: schemas.TransformRequest,
    image_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transform an image with specified operations
    """
    # Get the image
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Generate a cache key based on image ID and operations
    operations_key = json.dumps(transform_request.operations, sort_keys=True)
    cache_key = f"transform:{image_id}:{operations_key}"
    
    # Check if transformation exists in database
    operations_json = json.dumps(transform_request.operations, sort_keys=True)
    existing_transform = db.query(Transformation).filter(
        Transformation.image_id == image_id,
        Transformation._parameters == operations_json
    ).first()
    
    if existing_transform:
        return {
            "url": existing_transform.cached_url,
            "transformation_id": existing_transform.id
        }
    
    # Check if transformation exists in cache
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Download original image from R2
    import httpx
    try:
        logger.info(f"Attempting to download image from: {image.original_url}")
        
        # For R2, we might need to use the storage client directly instead of HTTP
        if "r2.cloudflarestorage.com" in image.original_url:
            # Extract key from the URL
            key = image.original_key
            logger.info(f"Using R2 storage client to get object with key: {key}")
            
            # Use boto3 client to download the file
            file_obj = BytesIO()
            try:
                storage.s3_client.download_fileobj(
                    storage.bucket_name,
                    key,
                    file_obj
                )
                file_obj.seek(0)
                image_data = file_obj.read()
                logger.info(f"Successfully downloaded image from R2 with key: {key}")
            except Exception as e:
                logger.error(f"Error downloading from R2 directly: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error downloading image from R2: {str(e)}"
                )
        else:
            # Use HTTP for non-R2 URLs
            async with httpx.AsyncClient() as client:
                response = await client.get(image.original_url)
                response.raise_for_status()
                image_data = response.content
    except httpx.HTTPError as e:
        logger.error(f"Error downloading image via HTTP: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error downloading original image"
        )
    
    # Process the image
    try:
        transformed_data = image_processor.process_image(
            image_data=image_data,
            operations=transform_request.operations
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing image"
        )
    
    # Upload transformed image to R2
    file_obj = BytesIO(transformed_data)
    
    # Determine content type based on the last format operation, or use original
    content_type = image.content_type
    for op in reversed(transform_request.operations):
        if op.get("type") == "format":
            format_map = {
                "jpeg": "image/jpeg",
                "jpg": "image/jpeg",
                "png": "image/png",
                "webp": "image/webp",
                "gif": "image/gif"
            }
            output_format = op.get("params", {}).get("output_format")
            if output_format:
                content_type = format_map.get(output_format.lower(), image.content_type)
                break
    
    key, url = storage.upload_file(
        file_obj=file_obj,
        content_type=content_type,
        folder=f"users/{current_user.id}/transformed"
    )
    
    # Create transformation record
    db_transform = Transformation(
        image_id=image.id,
        type="composite",
        cached_key=key,
        cached_url=url
    )
    
    # Set parameters using the method instead of property
    db_transform.set_parameters(transform_request.operations)
    
    db.add(db_transform)
    db.commit()
    db.refresh(db_transform)
    
    result = {
        "url": url,
        "transformation_id": db_transform.id
    }
    
    # Cache the result
    background_tasks.add_task(cache.set, cache_key, result)
    
    return result

@router.get("/transformations", response_model=List[schemas.Transformation])
def list_transformations(
    image_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List transformations for the current user, optionally filtered by image ID
    """
    query = db.query(Transformation).join(Image).filter(Image.user_id == current_user.id)
    
    if image_id is not None:
        query = query.filter(Transformation.image_id == image_id)
    
    transformations = query.order_by(Transformation.created_at.desc()).all()
    
    return transformations

@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an image and all its transformations
    """
    # Get the image
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete all transformations first
    transformations = db.query(Transformation).filter(
        Transformation.image_id == image_id
    ).all()
    
    # Delete files from storage
    try:
        # Delete original image
        if image.original_key:
            storage.delete_file(image.original_key)
        
        # Delete all transformation files
        for transformation in transformations:
            if transformation.cached_key:
                storage.delete_file(transformation.cached_key)
    except Exception as e:
        logger.error(f"Error deleting files from storage: {e}")
        # Continue with database deletion even if storage deletion fails
    
    # Delete from database
    for transformation in transformations:
        db.delete(transformation)
    
    db.delete(image)
    db.commit()
    
    return None

@router.delete("/transformations/{transformation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transformation(
    transformation_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific transformation
    """
    # Get the transformation and verify ownership
    transformation = db.query(Transformation).join(Image).filter(
        Transformation.id == transformation_id,
        Image.user_id == current_user.id
    ).first()
    
    if not transformation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transformation not found"
        )
    
    # Delete file from storage
    try:
        if transformation.cached_key:
            storage.delete_file(transformation.cached_key)
    except Exception as e:
        logger.error(f"Error deleting transformation file from storage: {e}")
        # Continue with database deletion even if storage deletion fails
    
    # Delete from database
    db.delete(transformation)
    db.commit()
    
    return None
