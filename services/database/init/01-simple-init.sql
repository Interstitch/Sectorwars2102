-- Simple SectorWars 2102 Database Initialization
-- Basic setup for local development

-- Create application user
CREATE USER sectorwars_app WITH 
    ENCRYPTED PASSWORD 'sectorwars_app_password_123'
    CREATEDB
    NOSUPERUSER
    NOCREATEROLE;

-- Grant necessary privileges to application user
GRANT CONNECT ON DATABASE sectorwars_dev TO sectorwars_app;
GRANT CREATE ON DATABASE sectorwars_dev TO sectorwars_app;
GRANT USAGE ON SCHEMA public TO sectorwars_app;
GRANT CREATE ON SCHEMA public TO sectorwars_app;

-- Create essential extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Log successful initialization
SELECT 'Simple database initialization completed successfully' as status;