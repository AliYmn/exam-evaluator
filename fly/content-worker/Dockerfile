# Base image for production
FROM python:3.13.2-slim-bullseye

# Set working directory
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create a non-root user and give appropriate permissions
RUN groupadd -r celerygroup && useradd -r -g celerygroup celeryuser
RUN mkdir -p /app/.ipython && chown -R celeryuser:celerygroup /app

# Install uv package manager
RUN pip install uv

# Copy only requirements first to leverage Docker cache
COPY backend/requirements.txt ./requirements.txt

# Create cache directory
RUN mkdir -p /root/.cache/uv

# Install dependencies with caching
RUN uv pip install --system --cache-dir=/root/.cache/uv -r requirements.txt

# Copy application files
COPY backend/content_service ./content_service
COPY backend/libs ./libs

# Copy entrypoint script
COPY backend/content_service/compose/production/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh && chmod +x /entrypoint.sh

# Make sure celeryuser can access necessary files
RUN chown -R celeryuser:celerygroup /app

# Switch to non-root user
USER celeryuser

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
