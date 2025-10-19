# Custom PostgreSQL Dockerfile to handle Fly.io volume mount points
FROM postgres:16.2-alpine

# Set custom PGDATA location
ENV PGDATA=/data/pgdata

# Create data directory and set ownership
RUN mkdir -p /data/pgdata && \
    chown -R postgres:postgres /data

# Create custom initialization script
RUN mkdir -p /docker-entrypoint-initdb.d

# Expose PostgreSQL port
EXPOSE 5432

# Use the default PostgreSQL entrypoint
CMD ["postgres"]
