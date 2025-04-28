import pytest
from PIL import Image
from app.utils.image_processor import ImageProcessor
from io import BytesIO

@pytest.fixture
def sample_image():
    """Create a sample image for testing."""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def test_get_image_info(sample_image):
    """Test getting image information."""
    info = ImageProcessor.get_image_info(sample_image)
    assert info["width"] == 100
    assert info["height"] == 100
    assert info["format"] == "jpeg"

def test_resize(sample_image):
    """Test image resizing."""
    # Test resize with width only
    resized = ImageProcessor.resize(sample_image, width=50)
    info = ImageProcessor.get_image_info(resized)
    assert info["width"] == 50
    assert info["height"] == 50  # Should maintain aspect ratio
    
    # Test resize with height only
    resized = ImageProcessor.resize(sample_image, height=25)
    info = ImageProcessor.get_image_info(resized)
    assert info["width"] == 25  # Should maintain aspect ratio
    assert info["height"] == 25
    
    # Test resize with both width and height, maintaining aspect ratio
    resized = ImageProcessor.resize(sample_image, width=40, height=20, maintain_aspect=True)
    info = ImageProcessor.get_image_info(resized)
    assert info["width"] <= 40
    assert info["height"] <= 20
    
    # Test resize with both width and height, not maintaining aspect ratio
    resized = ImageProcessor.resize(sample_image, width=40, height=20, maintain_aspect=False)
    info = ImageProcessor.get_image_info(resized)
    assert info["width"] == 40
    assert info["height"] == 20

def test_crop(sample_image):
    """Test image cropping."""
    cropped = ImageProcessor.crop(sample_image, x=25, y=25, width=50, height=50)
    info = ImageProcessor.get_image_info(cropped)
    assert info["width"] == 50
    assert info["height"] == 50

def test_rotate(sample_image):
    """Test image rotation."""
    rotated = ImageProcessor.rotate(sample_image, angle=90)
    # Size should remain the same for 90-degree rotation without expand
    info = ImageProcessor.get_image_info(rotated)
    assert info["width"] == 100
    assert info["height"] == 100
    
    # With expand=True, dimensions might change
    rotated = ImageProcessor.rotate(sample_image, angle=45, expand=True)
    info = ImageProcessor.get_image_info(rotated)
    assert info["width"] > 100
    assert info["height"] > 100

def test_convert_format(sample_image):
    """Test format conversion."""
    # Convert to PNG
    png_data = ImageProcessor.convert_format(sample_image, target_format="png")
    info = ImageProcessor.get_image_info(png_data)
    assert info["format"] == "png"
    
    # Convert to WebP
    webp_data = ImageProcessor.convert_format(sample_image, target_format="webp")
    info = ImageProcessor.get_image_info(webp_data)
    assert info["format"] == "webp"

def test_apply_filter(sample_image):
    """Test applying filters."""
    # Test grayscale
    filtered = ImageProcessor.apply_filter(sample_image, filter_type="grayscale")
    # We can't easily verify the visual effect, but we can check that it returns valid image data
    info = ImageProcessor.get_image_info(filtered)
    assert info["width"] == 100
    assert info["height"] == 100
    
    # Test sepia
    filtered = ImageProcessor.apply_filter(sample_image, filter_type="sepia")
    info = ImageProcessor.get_image_info(filtered)
    assert info["width"] == 100
    assert info["height"] == 100
    
    # Test blur
    filtered = ImageProcessor.apply_filter(sample_image, filter_type="blur")
    info = ImageProcessor.get_image_info(filtered)
    assert info["width"] == 100
    assert info["height"] == 100
    
    # Test sharpen
    filtered = ImageProcessor.apply_filter(sample_image, filter_type="sharpen")
    info = ImageProcessor.get_image_info(filtered)
    assert info["width"] == 100
    assert info["height"] == 100

def test_process_image(sample_image):
    """Test applying multiple operations."""
    operations = [
        {"type": "resize", "params": {"width": 50}},
        {"type": "filter", "params": {"filter_type": "grayscale"}},
        {"type": "rotate", "params": {"angle": 90}}
    ]
    
    processed = ImageProcessor.process_image(sample_image, operations)
    info = ImageProcessor.get_image_info(processed)
    assert info["width"] == 50
    assert info["height"] == 50
