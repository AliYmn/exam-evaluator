# Base image for production
FROM python:3.13.2-slim

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copy application files
COPY ./fit_service ./fit_service
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

# Set default command with uvicorn for production with 4 workers
CMD ["uvicorn", "fit_service.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "4"]
