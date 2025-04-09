# Base image for local development
FROM python:3.13.2-slim-bullseye

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copy application files
COPY ./content_service ./content_service
COPY ./libs ./libs
COPY ./requirements.txt ./requirements.txt

# Install uv package manager
RUN pip install uv

# Create cache directory
RUN mkdir -p /root/.cache/uv

# Install dependencies with caching
RUN uv pip install --system --cache-dir=/root/.cache/uv -r requirements.txt && \
    uv pip install --system --cache-dir=/root/.cache/uv fastapi-cli

# Expose the application port
EXPOSE 8003

# Set default command with FastAPI dev mode for local development
CMD ["uvicorn", "content_service.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
