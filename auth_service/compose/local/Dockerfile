# Base image for local development
FROM python:3.13.2-slim

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_CACHE_DIR=/root/.cache/uv

# Install uv package manager
RUN pip install uv

# Copy only requirements first to leverage Docker cache
COPY ./requirements.txt ./requirements.txt

# Install dependencies with caching
# Cache directory will be mounted as a volume in docker-compose
RUN mkdir -p ${UV_CACHE_DIR} && \
    uv pip install --system -r requirements.txt && \
    uv pip install --system fastapi-cli

# Copy application files after dependencies are installed
COPY ./auth_service ./auth_service
COPY ./libs ./libs

# Expose the application port
EXPOSE 8004

# Set default command with FastAPI dev mode for local development
CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8004", "--reload"]
