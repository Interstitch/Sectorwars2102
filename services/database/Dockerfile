# PostgreSQL Database Service for SectorWars 2102
# Based on PostgreSQL 15 Alpine for security and performance

FROM postgres:15-alpine

# Install additional utilities for database management
RUN apk add --no-cache \
    curl \
    bash \
    postgresql-contrib

# Set labels for identification
LABEL maintainer="SectorWars 2102 Development Team"
LABEL service="database"
LABEL version="1.0.0"
LABEL description="Local PostgreSQL database for SectorWars 2102"

# Environment variables with defaults
ENV POSTGRES_DB=sectorwars_dev
ENV POSTGRES_USER=postgres
ENV POSTGRES_ENCODING=UTF8
ENV POSTGRES_LOCALE=en_US.UTF-8

# Copy configuration files (optional - will be used if needed)
# COPY config/postgresql.conf /etc/postgresql/postgresql.conf
COPY config/pg_hba.conf /etc/postgresql/pg_hba.conf

# Copy initialization scripts
COPY init/ /docker-entrypoint-initdb.d/

# Create directories for backups and logs
RUN mkdir -p /var/lib/postgresql/backups \
    && mkdir -p /var/log/postgresql \
    && chown -R postgres:postgres /var/lib/postgresql/backups \
    && chown -R postgres:postgres /var/log/postgresql

# Health check script
COPY healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Expose PostgreSQL port
EXPOSE 5432

# Use default PostgreSQL configuration for now
CMD ["postgres"]