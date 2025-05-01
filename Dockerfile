FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies including Redis and PostgreSQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    redis-server \
    supervisor \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create supervisor configuration directory
RUN mkdir -p /etc/supervisor/conf.d

# Create startup script to initialize database, then start services
RUN echo '#!/bin/bash\n\
\n\
# Extract host and port from DATABASE_URL\n\
if [[ $DATABASE_URL =~ postgres://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then\n\
  DB_USER="${BASH_REMATCH[1]}"\n\
  DB_PASS="${BASH_REMATCH[2]}"\n\
  DB_HOST="${BASH_REMATCH[3]}"\n\
  DB_PORT="${BASH_REMATCH[4]}"\n\
  DB_NAME="${BASH_REMATCH[5]}"\n\
  echo "Extracted database connection info: Host=$DB_HOST, Port=$DB_PORT, Name=$DB_NAME"\n\
\n\
  # Wait for PostgreSQL to be ready\n\
  echo "Waiting for PostgreSQL to be ready..."\n\
  max_attempts=30\n\
  attempt=0\n\
  until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME || [ $attempt -eq $max_attempts ]; do\n\
    attempt=$((attempt+1))\n\
    echo "Waiting for PostgreSQL to be ready... ($attempt/$max_attempts)"\n\
    sleep 2\n\
  done\n\
\n\
  if [ $attempt -eq $max_attempts ]; then\n\
    echo "PostgreSQL did not become ready in time, but will try to initialize anyway"\n\
  else\n\
    echo "PostgreSQL is ready!"\n\
  fi\n\
\n\
  # Initialize database with our SQL script\n\
  echo "Initializing database schema..."\n\
  export PGPASSWORD=$DB_PASS\n\
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f /app/init_db.sql || echo "Database initialization failed, but continuing..."\n\
  unset PGPASSWORD\n\
else\n\
  echo "Could not parse DATABASE_URL, skipping database initialization"\n\
fi\n\
\n\
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

# Command to run the startup script which will initialize the database and then start supervisor
CMD ["/app/start.sh"]
