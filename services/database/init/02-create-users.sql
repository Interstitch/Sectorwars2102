-- SectorWars 2102 User Management and Security Setup
-- This script creates additional users and sets up security policies
-- Executed after database initialization

-- Connect to the main database
\c sectorwars_dev;

-- Create backup user for automated backups
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'sectorwars_backup') THEN
        -- Create backup user with replication privileges
        CREATE USER sectorwars_backup WITH 
            ENCRYPTED PASSWORD 'sectorwars_backup_password_123'
            REPLICATION
            NOCREATEDB
            NOSUPERUSER
            NOCREATEROLE;
        
        -- Grant necessary privileges for backup operations
        GRANT CONNECT ON DATABASE sectorwars_dev TO sectorwars_backup;
        GRANT USAGE ON SCHEMA public TO sectorwars_backup;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO sectorwars_backup;
        
        -- Grant permissions on future tables
        ALTER DEFAULT PRIVILEGES IN SCHEMA public 
            GRANT SELECT ON TABLES TO sectorwars_backup;
        
        RAISE NOTICE 'Created backup user: sectorwars_backup';
    ELSE
        RAISE NOTICE 'Backup user sectorwars_backup already exists';
    END IF;
END
$$;

-- Create monitoring user for database monitoring tools
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'sectorwars_monitor') THEN
        -- Create monitoring user with limited privileges
        CREATE USER sectorwars_monitor WITH 
            ENCRYPTED PASSWORD 'sectorwars_monitor_password_123'
            NOCREATEDB
            NOSUPERUSER
            NOCREATEROLE;
        
        -- Grant necessary privileges for monitoring
        GRANT CONNECT ON DATABASE sectorwars_dev TO sectorwars_monitor;
        GRANT USAGE ON SCHEMA public TO sectorwars_monitor;
        
        -- Grant access to system views for monitoring
        GRANT SELECT ON pg_stat_database TO sectorwars_monitor;
        GRANT SELECT ON pg_stat_user_tables TO sectorwars_monitor;
        GRANT SELECT ON pg_stat_user_indexes TO sectorwars_monitor;
        GRANT SELECT ON pg_statio_user_tables TO sectorwars_monitor;
        GRANT SELECT ON pg_statio_user_indexes TO sectorwars_monitor;
        GRANT SELECT ON pg_stat_activity TO sectorwars_monitor;
        
        RAISE NOTICE 'Created monitoring user: sectorwars_monitor';
    ELSE
        RAISE NOTICE 'Monitoring user sectorwars_monitor already exists';
    END IF;
END
$$;

-- Set up row-level security (RLS) preparation
-- This creates the foundation for RLS policies that may be added later

-- Create security context function
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS INTEGER AS $$
BEGIN
    -- This function will be used by RLS policies
    -- For now, it returns NULL, but can be extended to extract user ID from JWT or session
    RETURN NULLIF(current_setting('app.current_user_id', true), '')::INTEGER;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_current_user_id() IS 'Get current application user ID for RLS policies';

-- Create security audit table for tracking security events
CREATE TABLE IF NOT EXISTS _security_audit_log (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    username VARCHAR(100),
    table_name VARCHAR(100),
    action VARCHAR(20),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE _security_audit_log IS 'Audit log for security-sensitive operations';

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_security_audit_created_at ON _security_audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_security_audit_event_type ON _security_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_security_audit_username ON _security_audit_log(username);

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    -- Only audit specific operations on sensitive tables
    IF TG_TABLE_NAME IN ('users', 'admin_credentials', 'oauth_accounts', 'user_language_preferences') THEN
        INSERT INTO _security_audit_log (
            event_type,
            username,
            table_name,
            action,
            old_values,
            new_values,
            created_at
        ) VALUES (
            'table_modification',
            current_user,
            TG_TABLE_NAME,
            TG_OP,
            CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN to_jsonb(OLD) ELSE NULL END,
            CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
            NOW()
        );
    END IF;
    
    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION audit_trigger_function() IS 'Trigger function for auditing table modifications';

-- Set up database activity logging
-- Create function to log user connections
CREATE OR REPLACE FUNCTION log_user_connection()
RETURNS EVENT_TRIGGER AS $$
BEGIN
    -- Log connection events for monitoring
    INSERT INTO _security_audit_log (
        event_type,
        username,
        created_at
    ) VALUES (
        'user_connection',
        current_user,
        NOW()
    );
EXCEPTION WHEN OTHERS THEN
    -- Don't fail the connection if logging fails
    NULL;
END;
$$ LANGUAGE plpgsql;

-- Create database configuration table
CREATE TABLE IF NOT EXISTS _database_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    is_sensitive BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE _database_config IS 'Database configuration settings';

-- Add trigger for updated_at
CREATE TRIGGER update_database_config_updated_at
    BEFORE UPDATE ON _database_config
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default configuration
INSERT INTO _database_config (config_key, config_value, description) VALUES 
    ('security_audit_enabled', 'true', 'Enable security audit logging'),
    ('connection_logging_enabled', 'true', 'Enable connection logging'),
    ('max_connections_per_user', '10', 'Maximum connections per user'),
    ('session_timeout_minutes', '60', 'Session timeout in minutes'),
    ('password_min_length', '12', 'Minimum password length'),
    ('failed_login_attempts_limit', '5', 'Maximum failed login attempts before lockout')
ON CONFLICT (config_key) DO NOTHING;

-- Grant appropriate permissions
GRANT SELECT ON _security_audit_log TO sectorwars_app, sectorwars_monitor;
GRANT INSERT ON _security_audit_log TO sectorwars_app;
GRANT USAGE ON SEQUENCE _security_audit_log_id_seq TO sectorwars_app;

GRANT SELECT ON _database_config TO sectorwars_app, sectorwars_readonly;
GRANT INSERT, UPDATE ON _database_config TO sectorwars_app;
GRANT USAGE ON SEQUENCE _database_config_id_seq TO sectorwars_app;

-- Create security helper functions
CREATE OR REPLACE FUNCTION check_password_strength(password TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check password meets minimum requirements
    IF length(password) < 12 THEN
        RETURN FALSE;
    END IF;
    
    -- Check for at least one digit, one letter, and one special character
    IF NOT (password ~ '[0-9]' AND password ~ '[a-zA-Z]' AND password ~ '[^a-zA-Z0-9]') THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION check_password_strength(TEXT) IS 'Check if password meets security requirements';

-- Create function to hash passwords securely
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
BEGIN
    -- Use bcrypt for secure password hashing
    RETURN crypt(password, gen_salt('bf', 12));
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION hash_password(TEXT) IS 'Hash password securely using bcrypt';

-- Create function to verify passwords
CREATE OR REPLACE FUNCTION verify_password(password TEXT, hash TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN hash = crypt(password, hash);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION verify_password(TEXT, TEXT) IS 'Verify password against bcrypt hash';

-- Log user creation completion
INSERT INTO _database_metadata (key, value) VALUES 
    ('users_initialized', NOW()::TEXT)
ON CONFLICT (key) DO UPDATE SET 
    value = EXCLUDED.value,
    updated_at = NOW();

-- Display user creation summary
SELECT 
    'User creation and security setup completed' as status,
    COUNT(*) as total_users
FROM pg_user 
WHERE usename LIKE 'sectorwars_%' OR usename = 'postgres';

-- Display security features summary
SELECT 
    'Security features initialized' as status,
    'Audit logging, password hashing, and monitoring ready' as features;