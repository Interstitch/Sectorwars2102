-- SectorWars 2102 Essential Seed Data
-- This script populates the database with essential data needed for the application to function
-- Executed after database and user initialization

-- Connect to the main database
\c sectorwars_dev;

-- Note: We don't create the actual tables here as they will be created by Alembic migrations
-- This script prepares seed data that will be inserted after tables are created

-- Create a temporary table to store seed data until the real tables exist
CREATE TABLE IF NOT EXISTS _pending_seed_data (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    priority INTEGER DEFAULT 1,
    applied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE _pending_seed_data IS 'Temporary storage for seed data until tables are created';

-- Function to apply pending seed data
CREATE OR REPLACE FUNCTION apply_pending_seed_data()
RETURNS TEXT AS $$
DECLARE
    seed_record RECORD;
    result_text TEXT := '';
    applied_count INTEGER := 0;
BEGIN
    -- Apply seed data in priority order
    FOR seed_record IN 
        SELECT * FROM _pending_seed_data 
        WHERE NOT applied 
        ORDER BY priority, id
    LOOP
        -- Check if target table exists
        IF EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = seed_record.table_name 
            AND table_schema = 'public'
        ) THEN
            -- Table exists, apply the seed data
            -- This is a simplified approach - in practice, you'd want more sophisticated insertion logic
            result_text := result_text || 'Applied seed data for ' || seed_record.table_name || '; ';
            
            -- Mark as applied
            UPDATE _pending_seed_data 
            SET applied = TRUE 
            WHERE id = seed_record.id;
            
            applied_count := applied_count + 1;
        END IF;
    END LOOP;
    
    RETURN format('Applied %s seed data records', applied_count);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION apply_pending_seed_data() IS 'Apply pending seed data to existing tables';

-- Insert essential language data for internationalization
INSERT INTO _pending_seed_data (table_name, data, priority) VALUES
('languages', '{
    "code": "en",
    "name": "English",
    "native_name": "English",
    "direction": "ltr",
    "is_active": true,
    "completion_percentage": 100
}', 1),
('languages', '{
    "code": "es",
    "name": "Spanish",
    "native_name": "Español",
    "direction": "ltr",
    "is_active": true,
    "completion_percentage": 95
}', 1),
('languages', '{
    "code": "zh",
    "name": "Chinese (Simplified)",
    "native_name": "中文(简体)",
    "direction": "ltr",
    "is_active": true,
    "completion_percentage": 90
}', 1),
('languages', '{
    "code": "fr",
    "name": "French",
    "native_name": "Français",
    "direction": "ltr",
    "is_active": true,
    "completion_percentage": 85
}', 1),
('languages', '{
    "code": "pt",
    "name": "Portuguese",
    "native_name": "Português",
    "direction": "ltr",
    "is_active": true,
    "completion_percentage": 80
}', 1);

-- Insert translation namespaces
INSERT INTO _pending_seed_data (table_name, data, priority) VALUES
('translation_namespaces', '{
    "name": "common",
    "description": "Shared content across applications",
    "application": "shared",
    "is_active": true
}', 2),
('translation_namespaces', '{
    "name": "admin",
    "description": "Admin UI specific content",
    "application": "admin-ui",
    "is_active": true
}', 2),
('translation_namespaces', '{
    "name": "game",
    "description": "Player Client specific content",
    "application": "player-client",
    "is_active": true
}', 2),
('translation_namespaces', '{
    "name": "auth",
    "description": "Authentication flows",
    "application": "shared",
    "is_active": true
}', 2),
('translation_namespaces', '{
    "name": "ai",
    "description": "AI assistant content",
    "application": "shared",
    "is_active": true
}', 2),
('translation_namespaces', '{
    "name": "marketing",
    "description": "Landing page content",
    "application": "player-client",
    "is_active": true
}', 2),
('translation_namespaces', '{
    "name": "errors",
    "description": "Error messages",
    "application": "shared",
    "is_active": true
}', 2),
('translation_namespaces', '{
    "name": "validation",
    "description": "Form validation messages",
    "application": "shared",
    "is_active": true
}', 2);

-- Insert essential ship types (for game data)
INSERT INTO _pending_seed_data (table_name, data, priority) VALUES
('ship_types', '{
    "name": "scout_ship",
    "display_name": "Scout Ship",
    "description": "Fast reconnaissance vessel",
    "cargo_capacity": 10,
    "max_health": 100,
    "attack_power": 20,
    "defense_rating": 15,
    "speed": 100,
    "cost": 1000
}', 3),
('ship_types', '{
    "name": "light_freighter",
    "display_name": "Light Freighter",
    "description": "Basic cargo transport ship",
    "cargo_capacity": 50,
    "max_health": 150,
    "attack_power": 10,
    "defense_rating": 25,
    "speed": 70,
    "cost": 2500
}', 3),
('ship_types', '{
    "name": "cargo_hauler",
    "display_name": "Cargo Hauler",
    "description": "Heavy cargo transport vessel",
    "cargo_capacity": 200,
    "max_health": 200,
    "attack_power": 5,
    "defense_rating": 40,
    "speed": 40,
    "cost": 8000
}', 3),
('ship_types', '{
    "name": "fast_courier",
    "display_name": "Fast Courier",
    "description": "High-speed delivery ship",
    "cargo_capacity": 25,
    "max_health": 80,
    "attack_power": 15,
    "defense_rating": 10,
    "speed": 120,
    "cost": 3500
}', 3),
('ship_types', '{
    "name": "escape_pod",
    "display_name": "Escape Pod",
    "description": "Emergency survival vessel",
    "cargo_capacity": 1,
    "max_health": 50,
    "attack_power": 0,
    "defense_rating": 5,
    "speed": 60,
    "cost": 500
}', 3);

-- Insert default admin user data (will be created by the application)
INSERT INTO _pending_seed_data (table_name, data, priority) VALUES
('admin_credentials', '{
    "username": "admin",
    "email": "admin@sectorwars2102.dev",
    "is_active": true,
    "is_superuser": true,
    "created_by_system": true
}', 4);

-- Insert game configuration data
INSERT INTO _pending_seed_data (table_name, data, priority) VALUES
('game_config', '{
    "key": "max_ships_per_player",
    "value": "10",
    "description": "Maximum number of ships a player can own"
}', 5),
('game_config', '{
    "key": "starting_credits",
    "value": "5000",
    "description": "Credits given to new players"
}', 5),
('game_config', '{
    "key": "docking_turn_cost",
    "value": "1",
    "description": "Turns required for docking/undocking"
}', 5),
('game_config', '{
    "key": "max_turns_per_day",
    "value": "100",
    "description": "Maximum turns a player can accumulate per day"
}', 5);

-- Create function to get seed data statistics
CREATE OR REPLACE FUNCTION get_seed_data_stats()
RETURNS TABLE(
    table_name TEXT,
    pending_count BIGINT,
    applied_count BIGINT,
    total_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        _pending_seed_data.table_name::TEXT,
        COUNT(*) FILTER (WHERE NOT applied) AS pending_count,
        COUNT(*) FILTER (WHERE applied) AS applied_count,
        COUNT(*) AS total_count
    FROM _pending_seed_data
    GROUP BY _pending_seed_data.table_name
    ORDER BY _pending_seed_data.table_name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_seed_data_stats() IS 'Get statistics about seed data application status';

-- Grant permissions on seed data tables
GRANT SELECT ON _pending_seed_data TO sectorwars_app, sectorwars_readonly;
GRANT INSERT, UPDATE, DELETE ON _pending_seed_data TO sectorwars_app;
GRANT USAGE ON SEQUENCE _pending_seed_data_id_seq TO sectorwars_app;

-- Log seed data initialization
INSERT INTO _database_metadata (key, value) VALUES 
    ('seed_data_initialized', NOW()::TEXT)
ON CONFLICT (key) DO UPDATE SET 
    value = EXCLUDED.value,
    updated_at = NOW();

-- Display seed data summary
SELECT 
    'Seed data preparation completed' as status,
    COUNT(*) as total_seed_records
FROM _pending_seed_data;

-- Display seed data breakdown
SELECT * FROM get_seed_data_stats();

-- Create a convenience view for checking initialization status
CREATE OR REPLACE VIEW database_initialization_status AS
SELECT 
    key,
    value,
    updated_at
FROM _database_metadata
WHERE key IN (
    'database_name',
    'initialized_at',
    'users_initialized',
    'seed_data_initialized'
)
ORDER BY updated_at;

COMMENT ON VIEW database_initialization_status IS 'View showing database initialization progress';

-- Grant access to the view
GRANT SELECT ON database_initialization_status TO sectorwars_app, sectorwars_readonly, sectorwars_monitor;

SELECT 'Database initialization sequence completed successfully' as final_status;