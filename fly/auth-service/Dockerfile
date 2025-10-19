# Base image for production
FROM python:3.13.2-slim

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install uv package manager
RUN pip install uv

# Copy only requirements first to leverage Docker cache
COPY ./backend/requirements.txt ./requirements.txt

# Create cache directory
RUN mkdir -p /root/.cache/uv

# Install dependencies with caching
RUN uv pip install --system --cache-dir=/root/.cache/uv -r requirements.txt

# Copy application files
COPY ./backend/auth_service ./auth_service
COPY ./backend/libs ./libs

# Expose the application port
EXPOSE 8004

# Set default command with uvicorn for production with 4 workers
CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8004", "--workers", "4"]
