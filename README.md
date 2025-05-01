# Cloud Image Processing API

A backend system for image processing services similar to Cloudinary. This service allows users to upload images, perform various transformations, and retrieve images in different formats.

## Features

- **User Authentication**: Register, login, and secure API endpoints
- **Image Management**: Upload, transform, retrieve, and list images
- **Image Transformations**: Resize, crop, rotate, format conversion, and basic filters
- **Caching System**: Redis-based caching to avoid redundant processing

## Tech Stack

- **Backend Framework**: FastAPI
- **Database**: SQLite (local development) / PostgreSQL (production)
- **Storage**: Cloudflare R2
- **Caching**: Redis
- **Image Processing**: Pillow
- **Authentication**: JWT
- **Deployment**: DigitalOcean App Platform with Docker

## API Endpoints

### Authentication
```
POST /api/auth/register
POST /api/auth/login
```

### Image Operations
```
POST /api/images/upload
GET /api/images?page=1&limit=10
GET /api/images/{image_id}
POST /api/images/{image_id}/transform
```

## User Guide

### Getting Started

1. **Installation and Setup**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/cloud-image-api.git
   cd cloud-image-api
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env.local
   # Edit .env.local with your configuration
   
   # Create database tables
   python setup_db.py
   
   # Start the server
   uvicorn app.main:app --reload
   ```

2. **Access the API Documentation**
   - Open your browser and navigate to `http://localhost:8000/docs` for the Swagger UI
   - Or visit `http://localhost:8000/redoc` for the ReDoc documentation

### Authentication

1. **Register a New User**
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/api/auth/register' \
     -H 'Content-Type: application/json' \
     -d '{
       "username": "testuser",
       "email": "user@example.com",
       "password": "securepassword"
     }'
   ```

2. **Login and Get Access Token**
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/api/auth/login' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'username=testuser&password=securepassword'
   ```
   
   Save the returned access token for use in subsequent requests:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```

### Image Operations

For all image operations, you'll need to include the access token in the Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

1. **Upload an Image**
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/api/images/upload' \
     -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
     -F 'file=@/path/to/your/image.jpg'
   ```
   
   This will return the image metadata including the `id` which you'll need for transformations.

2. **List Your Images**
   ```bash
   curl -X 'GET' \
     'http://localhost:8000/api/images?page=1&limit=10' \
     -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
   ```
   
   Use the `page` and `limit` parameters to paginate through your images.

3. **Get a Specific Image**
   ```bash
   curl -X 'GET' \
     'http://localhost:8000/api/images/1' \
     -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
   ```
   
   Replace `1` with the actual image ID.

4. **Transform an Image**
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/api/images/1/transform' \
     -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
     -H 'Content-Type: application/json' \
     -d '{
       "operations": [
         {
           "type": "resize",
           "width": 500,
           "height": 300,
           "maintain_aspect": true
         },
         {
           "type": "filter",
           "filter": "grayscale"
         }
       ]
     }'
   ```
   
   This will return a URL to the transformed image.

### Transformation Operations

The API supports the following transformation operations:

1. **Resize**
   ```json
   {
     "type": "resize",
     "width": 500,
     "height": 300,
     "maintain_aspect": true
   }
   ```
   
   Parameters:
   - `width`: Target width in pixels
   - `height`: Target height in pixels
   - `maintain_aspect`: Whether to maintain aspect ratio (default: true)

2. **Crop**
   ```json
   {
     "type": "crop",
     "x": 100,
     "y": 100,
     "width": 300,
     "height": 300
   }
   ```
   
   Parameters:
   - `x`: Left coordinate
   - `y`: Top coordinate
   - `width`: Crop width
   - `height`: Crop height

3. **Rotate**
   ```json
   {
     "type": "rotate",
     "angle": 90,
     "expand": true
   }
   ```
   
   Parameters:
   - `angle`: Rotation angle in degrees
   - `expand`: Whether to expand the output to fit the rotated image (default: false)

4. **Format Conversion**
   ```json
   {
     "type": "format",
     "format": "webp",
     "quality": 85
   }
   ```
   
   Parameters:
   - `format`: Target format (jpeg, jpg, png, webp, gif)
   - `quality`: Output quality for JPEG and WebP (1-100, default: 85)

5. **Filters**
   ```json
   {
     "type": "filter",
     "filter": "grayscale"
   }
   ```
   
   Parameters:
   - `filter`: Filter type (grayscale, sepia, blur, sharpen)

### Combining Transformations

You can apply multiple transformations in sequence:

```json
{
  "operations": [
    {
      "type": "resize",
      "width": 500
    },
    {
      "type": "rotate",
      "angle": 90
    },
    {
      "type": "filter",
      "filter": "sepia"
    },
    {
      "type": "format",
      "format": "webp",
      "quality": 90
    }
  ]
}
```

Transformations are applied in the order they are specified.

## Setup and Installation

### Prerequisites
- Python 3.11+
- Redis
- Cloudflare R2 account
- Docker and Docker Compose (for local containerized development)

### Local Development

1. Clone the repository
```bash
git clone https://github.com/yourusername/cloud-image-api.git
cd cloud-image-api
```

2. Create a virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. Run database migrations
```bash
alembic upgrade head
```

5. Start the development server
```bash
uvicorn app.main:app --reload
```

### Docker Development

1. Clone the repository
```bash
git clone https://github.com/yourusername/cloud-image-api.git
cd cloud-image-api
```

2. Set up environment variables
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. Build and start the Docker containers
```bash
docker-compose up -d
```

4. Access the API documentation at http://localhost:8000/docs

## Testing

Run the test suite with:
```bash
pytest
```

## Deployment

Detailed deployment instructions for DigitalOcean App Platform are available in the [DEPLOYMENT.md](DEPLOYMENT.md) file.
