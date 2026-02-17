# Django API for AWS Lambda via Mangum (ASGI adapter for API Gateway).
# Build: docker build -f Dockerfile .
# Lambda handler: handler.handler (Mangum wraps Django ASGI).

ARG PYTHON_VERSION=3.12
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

# Install libpq for psycopg2 (Lambda base is Amazon Linux)
RUN yum install -y postgresql-libs && yum clean all

# Install Python dependencies into Lambda task root
COPY mindpump/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -t "${LAMBDA_TASK_ROOT}"

# Copy Lambda handler and Django project
COPY handler.py .
COPY mindpump/ mindpump/

# Build-time args (e.g. from GitHub Actions); override in Lambda function env if needed
ARG DB_NAME=postgres
ARG DB_USER=postgres
ARG DB_PASSWORD=
ARG DB_HOST=
ARG DB_PORT=5432
ARG API_BASIC_AUTH_USERNAME=
ARG API_BASIC_AUTH_PASSWORD=

ENV DJANGO_SETTINGS_MODULE=mindpump.settings \
    DB_NAME=${DB_NAME} \
    DB_USER=${DB_USER} \
    DB_PASSWORD=${DB_PASSWORD} \
    DB_HOST=${DB_HOST} \
    DB_PORT=${DB_PORT} \
    API_BASIC_AUTH_USERNAME=${API_BASIC_AUTH_USERNAME} \
    API_BASIC_AUTH_PASSWORD=${API_BASIC_AUTH_PASSWORD}

# Mangum handler: receives API Gateway events and forwards to Django ASGI
CMD ["handler.handler"]
