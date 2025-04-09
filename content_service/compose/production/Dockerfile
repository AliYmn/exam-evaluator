# Base image for production - Multi-stage build
FROM python:3.13.2-slim as builder

# Set working directory
WORKDIR /app

# Environment variables for builder stage
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_CACHE_DIR=/root/.cache/uv

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy only requirements first to leverage Docker cache
COPY ./requirements.txt ./requirements.txt

# Install dependencies with caching
RUN mkdir -p ${UV_CACHE_DIR} && \
    uv pip install --system -r requirements.txt

# Final stage
FROM python:3.13.2-slim

# Set working directory
WORKDIR /app

# Environment variables for runtime (without cache-related vars)
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY ./content_service ./content_service
COPY ./libs ./libs

# Expose the application port
EXPOSE 8001

# Set default command with uvicorn for production with 4 workers
CMD ["uvicorn", "content_service.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]
