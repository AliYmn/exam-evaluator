# Base image for production
FROM python:3.13.2-slim-bullseye

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copy application files
COPY ./ai_service ./ai_service
COPY ./libs ./libs
COPY ./requirements.txt ./requirements.txt

# Install uv package manager
RUN pip install uv

# Create cache directory
RUN mkdir -p /root/.cache/uv

# Install dependencies with caching
RUN uv pip install --system --cache-dir=/root/.cache/uv -r requirements.txt

# Expose the application port
EXPOSE 8002

# Set default command with gunicorn for production
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "ai_service.main:app", "--bind", "0.0.0.0:8002", "--timeout", "90"]
