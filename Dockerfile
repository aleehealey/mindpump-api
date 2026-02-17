# Django API image for AWS Lambda (container image support).
# Build with args: docker build -f api/Dockerfile --build-arg DB_PASSWORD=... api/
# Lambda Web Adapter forwards requests to port 8080 by default.

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=mindpump.settings

WORKDIR /app

# Install runtime deps (optional, for psycopg2 etc. if you add DB later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY mindpump/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project (mindpump = project package + api app)
COPY mindpump/ .

# Build-time args (e.g. from GitHub Actions); can also override at runtime via -e
ARG DB_NAME=postgres
ARG DB_USER=postgres
ARG DB_PASSWORD=
ARG DB_HOST=
ARG DB_PORT=5432
ARG API_BASIC_AUTH_USERNAME=
ARG API_BASIC_AUTH_PASSWORD=

ENV DB_NAME=${DB_NAME} \
    DB_USER=${DB_USER} \
    DB_PASSWORD=${DB_PASSWORD} \
    DB_HOST=${DB_HOST} \
    DB_PORT=${DB_PORT} \
    API_BASIC_AUTH_USERNAME=${API_BASIC_AUTH_USERNAME} \
    API_BASIC_AUTH_PASSWORD=${API_BASIC_AUTH_PASSWORD}

# Lambda Web Adapter expects the app to listen on 8080
EXPOSE 8080

# Run gunicorn; 1 worker is typical for Lambda (one invocation at a time per instance)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "2", "--timeout", "30", "mindpump.wsgi:application"]
