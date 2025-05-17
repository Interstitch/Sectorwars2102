#!/bin/bash

# Script to connect to Neon PostgreSQL database
# Extracts connection details from .env file if available

# Try to get database URL from .env file
if [ -f .env ]; then
    source <(grep -v '^#' .env | sed -E 's/(.*)=(.*)$/export \1="\2"/')
    echo "Loaded database configuration from .env file"
fi

# Use DATABASE_URL from environment or fall back to default
DB_URL=${DATABASE_URL:-"postgresql://neondb_owner:npg_TNK1MA9qHdXu@ep-lingering-grass-a494zxxb-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"}

echo "Connecting to Neon PostgreSQL database..."
echo "Connection string: ${DB_URL}"

# Connect to the database
psql "${DB_URL}"

# If psql exits with an error, provide some troubleshooting help
if [ $? -ne 0 ]; then
    echo "Connection failed. Please check:"
    echo "1. Your .env file has the correct DATABASE_URL"
    echo "2. Your network connection is stable"
    echo "3. The database server is running"
    echo "4. The credentials are correct"
    echo ""
    echo "You can also try connecting using pgAdmin 4."
fi 