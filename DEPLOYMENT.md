# Deployment Guide

This guide provides instructions for deploying the Cloud Image Processing API to various platforms.

## Prerequisites

Before deploying, make sure you have:

1. A Cloudflare account with R2 storage set up
2. A Redis instance (Redis Cloud free tier or self-hosted)
3. An account on your chosen deployment platform (Railway, Render, or Fly.io)

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
REDIS_URL="redis://username:password@host:port"
REDIS_CACHE_EXPIRY=86400

# Image Processing Settings
MAX_IMAGE_SIZE=10485760
ALLOWED_EXTENSIONS=["jpg", "jpeg", "png", "gif", "webp"]
```

## Deployment Options

### Railway

1. **Create a new project**:
   - Go to [Railway](https://railway.app/) and create a new project
   - Choose "Deploy from GitHub repo"
   - Connect your GitHub repository

2. **Configure environment variables**:
   - In your project settings, add all required environment variables

3. **Add a PostgreSQL database**:
   - Click "New" and select "Database" → "PostgreSQL"
   - Railway will automatically add the database connection variables

4. **Deploy**:
   - Railway will automatically build and deploy your application
   - The deployment URL will be available in the "Settings" tab

### Render

1. **Create a new Web Service**:
   - Go to [Render](https://render.com/) and create a new Web Service
   - Connect your GitHub repository

2. **Configure the service**:
   - Name: `cloud-image-api`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt && alembic upgrade head`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add environment variables**:
   - In the "Environment" section, add all required environment variables

4. **Add a PostgreSQL database**:
   - Go to "New" and select "PostgreSQL"
   - Connect your database by setting the `DATABASE_URL` environment variable

5. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy your application

### Fly.io

1. **Install Flyctl**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Authenticate**:
   ```bash
   flyctl auth login
   ```

3. **Create a fly.toml file**:
   ```bash
   flyctl launch
   ```

4. **Configure the application**:
   - Edit the generated `fly.toml` file to match your requirements
   - Add environment variables using `flyctl secrets set KEY=VALUE`

5. **Add a PostgreSQL database**:
   ```bash
   flyctl postgres create
   ```

6. **Deploy**:
   ```bash
   flyctl deploy
   ```

## CI/CD with GitHub Actions

Create a `.github/workflows/deploy.yml` file in your repository:

```yaml
name: Deploy

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
          python-version: '3.9'
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
      
      # For Railway
      - name: Deploy to Railway
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          
      # For Render (using their API)
      # - name: Deploy to Render
      #   run: |
      #     curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK_URL }}
      
      # For Fly.io
      # - name: Deploy to Fly.io
      #   uses: superfly/flyctl-actions@master
      #   with:
      #     args: "deploy"
      #   env:
      #     FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

## Monitoring and Logging

For production deployments, consider setting up:

1. **Application Monitoring**:
   - Sentry for error tracking
   - Prometheus for metrics
   - Grafana for visualization

2. **Logging**:
   - Configure logging to a service like Datadog or Logz.io
   - Or use the built-in logging of your deployment platform

## Scaling Considerations

1. **Database Scaling**:
   - Consider connection pooling for PostgreSQL
   - Use database indexes for frequently queried fields

2. **Storage Scaling**:
   - Cloudflare R2 scales automatically

3. **Redis Caching**:
   - Implement proper cache invalidation strategies
   - Consider Redis cluster for high availability

4. **Application Scaling**:
   - All recommended platforms support auto-scaling
   - Configure scaling based on CPU/memory usage
