# Deployment Guide

This guide provides instructions for deploying the Cloud Image Processing API to DigitalOcean App Platform using Docker.

## Prerequisites

Before deploying, make sure you have:

1. A Cloudflare account with R2 storage set up
2. A DigitalOcean account
3. The DigitalOcean CLI (`doctl`) installed and authenticated

## Environment Variables

Ensure all required environment variables are set up on your deployment platform:

```
APP_NAME="Cloud Image API"
ENVIRONMENT="production"
DEBUG=false
SECRET_KEY="your-secure-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Settings (PostgreSQL for production)
DATABASE_URL="postgresql://user:password@host/dbname"

# Cloudflare R2 Settings
R2_ENDPOINT_URL="https://your-account-id.r2.cloudflarestorage.com"
R2_ACCESS_KEY_ID="your-access-key-id"
R2_SECRET_ACCESS_KEY="your-secret-access-key"
R2_BUCKET_NAME="your-bucket-name"
R2_PUBLIC_URL="https://your-public-bucket-url.com"

# Redis Settings
REDIS_URL="redis://localhost:6379/0"
REDIS_CACHE_EXPIRY=86400

# Image Processing Settings
MAX_IMAGE_SIZE=10485760
ALLOWED_EXTENSIONS=["jpg", "jpeg", "png", "gif", "webp"]
```

## Deployment to DigitalOcean App Platform

### 1. Prepare Your Application

Ensure your application has the following files:

- `Dockerfile`: Defines how to build your application container
- `.dockerignore`: Specifies files to exclude from the Docker build
- `.do/app-docker.yaml`: DigitalOcean App Platform specification
- `init_db.sql`: SQL script to initialize the database schema

### 2. Understanding the Deployment Architecture

The deployment architecture consists of:

- **FastAPI Application**: Runs your API endpoints
- **Redis**: Runs in the same container as FastAPI for caching
- **PostgreSQL**: Managed database provided by DigitalOcean

Both FastAPI and Redis run in the same container, managed by Supervisor.

### 3. Deploy Using the DigitalOcean CLI

```bash
# Create a new app
doctl apps create --spec .do/app-docker.yaml

# Or update an existing app
doctl apps update YOUR_APP_ID --spec .do/app-docker.yaml
```

### 4. Deploy Using the DigitalOcean Web Interface

1. Go to the [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Choose "GitHub" as the source
4. Select your repository
5. Choose the branch to deploy from
6. Configure your app settings:
   - Select "Dockerfile" as the build method
   - Configure environment variables
   - Add a managed PostgreSQL database
7. Click "Create Resources"

## Common Issues and Solutions

### PostgreSQL Permission Issues

When deploying to DigitalOcean's managed PostgreSQL, you might encounter permission errors:

```
psycopg2.errors.InsufficientPrivilege: permission denied for schema public
```

**Solution:**

1. **Remove automatic table creation in FastAPI startup:**
   - Comment out or remove `Base.metadata.create_all(bind=engine)` in your app's startup event

2. **Use SQL initialization script:**
   - Create an `init_db.sql` file with your schema definition
   - Use the PostgreSQL client in your container startup script to execute this file

3. **Wait for PostgreSQL to be ready:**
   - Use `pg_isready` to check if PostgreSQL is available before attempting to connect
   - Add appropriate retry logic in your container startup script

### Database URL Format

DigitalOcean provides the database URL in the format:

```
${db.DATABASE_URL}
```

This is automatically expanded to the actual connection string at runtime.

## Monitoring Your Deployment

Monitor your deployment using the DigitalOcean CLI:

```bash
# List your apps
doctl apps list

# Get app details
doctl apps get YOUR_APP_ID

# List deployments
doctl apps list-deployments YOUR_APP_ID

# View logs
doctl apps logs YOUR_APP_ID
```

## CI/CD with GitHub Actions

Create a `.github/workflows/deploy.yml` file in your repository:

```yaml
name: Deploy to DigitalOcean

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
      - name: Deploy to DigitalOcean App Platform
        run: doctl apps update ${{ secrets.DIGITALOCEAN_APP_ID }} --spec .do/app-docker.yaml
```

Remember to add your DigitalOcean access token and app ID as secrets in your GitHub repository.
