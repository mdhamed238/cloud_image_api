from io import BytesIO
from typing import Dict, Optional, Tuple, Union, List
import logging
from PIL import Image, ImageOps, ImageFilter

logger = logging.getLogger(__name__)

class ImageProcessor:
    @staticmethod
    def get_image_info(image_data: bytes) -> Dict[str, Union[int, str]]:
        """
        Get basic information about an image
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dict with image info (width, height, format)
        """
        try:
            with Image.open(BytesIO(image_data)) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format.lower() if img.format else "unknown"
                }
        except Exception as e:
            logger.error(f"Error getting image info: {e}")
            raise ValueError("Invalid image data")
    
    @staticmethod
    def resize(
        image_data: bytes, 
        width: Optional[int] = None, 
        height: Optional[int] = None,
        maintain_aspect: bool = True
    ) -> bytes:
        """
        Resize an image
        
        Args:
            image_data: Raw image bytes
            width: Target width
            height: Target height
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Transformed image as bytes
        """
        if not width and not height:
            raise ValueError("Either width or height must be specified")
        
        try:
            with Image.open(BytesIO(image_data)) as img:
                original_format = img.format
                
                if maintain_aspect:
                    if width and height:
                        img.thumbnail((width, height), Image.LANCZOS)
                    elif width:
                        ratio = width / img.width
                        height = int(img.height * ratio)
                        img = img.resize((width, height), Image.LANCZOS)
                    else:  # height only
                        ratio = height / img.height
                        width = int(img.width * ratio)
                        img = img.resize((width, height), Image.LANCZOS)
                else:
                    # Force resize to exact dimensions
                    target_width = width or img.width
                    target_height = height or img.height
                    img = img.resize((target_width, target_height), Image.LANCZOS)
                
                output = BytesIO()
                img.save(output, format=original_format)
                return output.getvalue()
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            raise
    
    @staticmethod
    def crop(
        image_data: bytes, 
        x: int, 
        y: int, 
        width: int, 
        height: int
    ) -> bytes:
        """
        Crop an image
        
        Args:
            image_data: Raw image bytes
            x: Left coordinate
            y: Top coordinate
            width: Crop width
            height: Crop height
            
        Returns:
            Transformed image as bytes
        """
        try:
            with Image.open(BytesIO(image_data)) as img:
                original_format = img.format
                
                # Calculate crop box
                right = x + width
                bottom = y + height
                
                # Ensure crop box is within image bounds
                if x < 0 or y < 0 or right > img.width or bottom > img.height:
                    raise ValueError("Crop dimensions are outside image bounds")
                
                # Crop the image
                img = img.crop((x, y, right, bottom))
                
                output = BytesIO()
                img.save(output, format=original_format)
                return output.getvalue()
        except Exception as e:
            logger.error(f"Error cropping image: {e}")
            raise
    
    @staticmethod
    def rotate(
        image_data: bytes, 
        angle: float, 
        expand: bool = False
    ) -> bytes:
        """
        Rotate an image
        
        Args:
            image_data: Raw image bytes
            angle: Rotation angle in degrees
            expand: Whether to expand the output to fit the rotated image
            
        Returns:
            Transformed image as bytes
        """
        try:
            with Image.open(BytesIO(image_data)) as img:
                original_format = img.format
                
                # Rotate the image
                img = img.rotate(angle, expand=expand, resample=Image.BICUBIC)
                
                output = BytesIO()
                img.save(output, format=original_format)
                return output.getvalue()
        except Exception as e:
            logger.error(f"Error rotating image: {e}")
            raise
    
    @staticmethod
    def convert_format(
        image_data: bytes, 
        target_format: str,
        quality: int = 85
    ) -> bytes:
        """
        Convert image format
        
        Args:
            image_data: Raw image bytes
            target_format: Target format (jpeg, png, webp)
            quality: Output quality (1-100, JPEG and WebP only)
            
        Returns:
            Transformed image as bytes
        """
        format_map = {
            "jpeg": "JPEG",
            "jpg": "JPEG",
            "png": "PNG",
            "webp": "WEBP",
            "gif": "GIF"
        }
        
        if target_format.lower() not in format_map:
            raise ValueError(f"Unsupported format: {target_format}")
        
        pil_format = format_map[target_format.lower()]
        
        try:
            with Image.open(BytesIO(image_data)) as img:
                # Convert to RGB if needed (for JPEG)
                if pil_format == "JPEG" and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                output = BytesIO()
                
                # Save with quality for formats that support it
                if pil_format in ("JPEG", "WEBP"):
                    img.save(output, format=pil_format, quality=quality)
                else:
                    img.save(output, format=pil_format)
                
                return output.getvalue()
        except Exception as e:
            logger.error(f"Error converting image format: {e}")
            raise
    
    @staticmethod
    def apply_filter(
        image_data: bytes, 
        filter_type: str
    ) -> bytes:
        """
        Apply a filter to an image
        
        Args:
            image_data: Raw image bytes
            filter_type: Type of filter (grayscale, sepia, blur, sharpen)
            
        Returns:
            Transformed image as bytes
        """
        try:
            with Image.open(BytesIO(image_data)) as img:
                original_format = img.format
                
                if filter_type == "grayscale":
                    img = ImageOps.grayscale(img)
                    # Convert back to RGB if the original was RGB
                    if img.mode != "RGB" and original_format == "JPEG":
                        img = img.convert("RGB")
                
                elif filter_type == "sepia":
                    # Convert to grayscale first
                    gray = ImageOps.grayscale(img)
                    # Apply sepia tone
                    img = Image.merge(
                        "RGB", 
                        (
                            gray.point(lambda x: min(255, x * 1.1)),
                            gray.point(lambda x: min(255, x * 0.9)),
                            gray.point(lambda x: min(255, x * 0.7))
                        )
                    )
                
                elif filter_type == "blur":
                    img = img.filter(ImageFilter.GaussianBlur(radius=2))
                
                elif filter_type == "sharpen":
                    img = img.filter(ImageFilter.SHARPEN)
                
                else:
                    raise ValueError(f"Unsupported filter: {filter_type}")
                
                output = BytesIO()
                img.save(output, format=original_format)
                return output.getvalue()
        except Exception as e:
            logger.error(f"Error applying filter: {e}")
            raise
    
    @staticmethod
    def process_image(
        image_data: bytes,
        operations: List[Dict]
    ) -> bytes:
        """
        Apply multiple operations to an image in sequence
        
        Args:
            image_data: Raw image bytes
            operations: List of operations to apply, each a dict with 'type' and parameters
            
        Returns:
            Transformed image as bytes
        """
        current_data = image_data
        
        for op in operations:
            # Skip invalid operations
            if not op or not isinstance(op, dict):
                logger.warning(f"Skipping invalid operation: {op}")
                continue
                
            op_type = op.get("type")
            
            # Skip operations with missing type
            if not op_type:
                logger.warning(f"Skipping operation with missing type: {op}")
                continue
            
            if op_type == "resize":
                params = op.get("params", {})
                width = params.get("width")
                height = params.get("height")
                maintain_aspect = params.get("maintain_ratio", True)
                
                if width is not None or height is not None:
                    current_data = ImageProcessor.resize(
                        current_data,
                        width=int(width) if width is not None else None,
                        height=int(height) if height is not None else None,
                        maintain_aspect=maintain_aspect
                    )
                else:
                    logger.warning("Skipping resize: missing width and height parameters")
            
            elif op_type == "crop":
                params = op.get("params", {})
                width = params.get("width")
                height = params.get("height")
                x = params.get("x", 0)
                y = params.get("y", 0)
                
                if width is not None and height is not None:
                    current_data = ImageProcessor.crop(
                        current_data,
                        x=int(x),
                        y=int(y),
                        width=int(width),
                        height=int(height)
                    )
                else:
                    logger.warning("Skipping crop: missing width or height parameters")
            
            elif op_type == "rotate":
                angle = op.get("params", {}).get("angle")
                if angle is not None:
                    current_data = ImageProcessor.rotate(
                        current_data,
                        angle=float(angle),
                        expand=op.get("params", {}).get("expand", False)
                    )
                else:
                    logger.warning("Skipping rotation: missing angle parameter")
            
            elif op_type == "format":
                target_format = op.get("params", {}).get("output_format")
                quality = op.get("params", {}).get("quality", 85)
                if target_format:
                    current_data = ImageProcessor.convert_format(
                        current_data,
                        target_format=target_format,
                        quality=quality
                    )
                else:
                    logger.warning("Skipping format conversion: missing output_format parameter")
            
            elif op_type == "filter":
                filter_type = op.get("params", {}).get("filter_type")
                if filter_type:
                    current_data = ImageProcessor.apply_filter(
                        current_data,
                        filter_type=filter_type
                    )
                else:
                    logger.warning("Skipping filter: missing filter_type parameter")
            
            else:
                raise ValueError(f"Unsupported operation: {op_type}")
        
        return current_data

# Create a singleton instance
image_processor = ImageProcessor()
