FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies including Redis
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    redis-server \
    supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create supervisor configuration directory
RUN mkdir -p /etc/supervisor/conf.d

# Create startup script to run migrations before starting services
RUN echo '#!/bin/bash\n\
echo "Running database migrations..."\n\
python -m alembic upgrade head\n\
echo "Starting services..."\n\
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf\n\
' > /app/start.sh && chmod +x /app/start.sh

# Create supervisor configuration file
RUN echo "[supervisord]\n\
nodaemon=true\n\
\n\
[program:redis]\n\
command=redis-server\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
\n\
[program:api]\n\
command=uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
directory=/app\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0" > /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 8000

# Command to run the startup script which will run migrations and then start supervisor
CMD ["/app/start.sh"]
