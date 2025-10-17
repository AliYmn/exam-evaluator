# Base image
FROM python:3.12.8-slim-bullseye

# Set working directory
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Copy requirements files
COPY requirements.txt .

# Install uv package manager
RUN pip install uv

# Install dependencies
RUN uv pip install --no-cache --system -r  requirements.txt

# Copy entrypoint script
COPY ./entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

# Expose Port
EXPOSE 5555

# Set default command
ENTRYPOINT ["/entrypoint"]
