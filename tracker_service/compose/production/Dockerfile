# Base image for production
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
RUN mkdir -p ${UV_CACHE_DIR} && \
    uv pip install --system -r requirements.txt

# Copy application files after dependencies are installed
COPY ./tracker_service ./tracker_service
COPY ./libs ./libs

# Expose the application port
EXPOSE 8003

# Set default command with uvicorn for production with 4 workers
CMD ["uvicorn", "tracker_service.main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "4"]
