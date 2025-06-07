-- Central Nexus Database Initialization Script
-- This script sets up the central database for the multi-regional platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create specialized Central Nexus tables
CREATE TABLE IF NOT EXISTS nexus_districts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    district_type VARCHAR(50) NOT NULL, -- commerce, diplomatic, industrial, residential, transit
    sector_start INTEGER NOT NULL,
    sector_end INTEGER NOT NULL,
    specialization JSONB DEFAULT '{}',
    regulations JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Central Nexus specific sectors table
CREATE TABLE IF NOT EXISTS nexus_sectors (
    id SERIAL PRIMARY KEY,
    district_id UUID REFERENCES nexus_districts(id),
    sector_number INTEGER NOT NULL UNIQUE,
    sector_type VARCHAR(50) NOT NULL, -- hub, market, embassy, transit, residential
    security_level INTEGER DEFAULT 5, -- 1-10 scale
    traffic_level INTEGER DEFAULT 0,
    special_facilities JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inter-regional warp gates
CREATE TABLE IF NOT EXISTS inter_regional_warp_gates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nexus_sector_id INTEGER REFERENCES nexus_sectors(id),
    destination_region_id UUID,
    gate_type VARCHAR(50) DEFAULT 'standard', -- standard, express, diplomatic
    travel_cost INTEGER DEFAULT 100,
    travel_time_minutes INTEGER DEFAULT 15,
    restrictions JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regional embassies in Central Nexus
CREATE TABLE IF NOT EXISTS regional_embassies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_id UUID NOT NULL,
    nexus_sector_id INTEGER REFERENCES nexus_sectors(id),
    ambassador_id UUID, -- Player ID
    embassy_level INTEGER DEFAULT 1, -- 1-5, affects services offered
    services_offered JSONB DEFAULT '[]',
    diplomatic_status VARCHAR(50) DEFAULT 'neutral',
    established_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Galactic trade routes
CREATE TABLE IF NOT EXISTS galactic_trade_routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    origin_region_id UUID,
    destination_region_id UUID,
    route_efficiency DECIMAL(5,4) DEFAULT 1.0000,
    base_travel_time_hours INTEGER DEFAULT 24,
    security_rating INTEGER DEFAULT 5,
    toll_rate DECIMAL(5,4) DEFAULT 0.0500,
    is_active BOOLEAN DEFAULT true,
    established_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cross-regional events and announcements
CREATE TABLE IF NOT EXISTS galactic_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL, -- tournament, festival, crisis, trade_fair
    title VARCHAR(255) NOT NULL,
    description TEXT,
    participating_regions UUID[],
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    rewards JSONB DEFAULT '{}',
    requirements JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'scheduled',
    created_by UUID, -- Admin or system
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Central Nexus security logs
CREATE TABLE IF NOT EXISTS nexus_security_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_id UUID,
    sector_id INTEGER,
    action_type VARCHAR(50) NOT NULL,
    action_details JSONB DEFAULT '{}',
    security_level_before INTEGER,
    security_level_after INTEGER,
    flagged BOOLEAN DEFAULT false,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regional performance metrics (aggregated)
CREATE TABLE IF NOT EXISTS regional_performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_id UUID NOT NULL,
    metric_date DATE NOT NULL,
    active_players INTEGER DEFAULT 0,
    total_transactions INTEGER DEFAULT 0,
    transaction_volume DECIMAL(20,2) DEFAULT 0.00,
    average_response_time_ms DECIMAL(10,2) DEFAULT 0.00,
    error_count INTEGER DEFAULT 0,
    resource_usage JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(region_id, metric_date)
);

-- Galactic currency exchange rates
CREATE TABLE IF NOT EXISTS galactic_exchange_rates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    base_currency VARCHAR(50) DEFAULT 'galactic_credits',
    regional_currency VARCHAR(50) NOT NULL,
    region_id UUID NOT NULL,
    exchange_rate DECIMAL(10,6) NOT NULL,
    daily_volume DECIMAL(20,2) DEFAULT 0.00,
    rate_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(regional_currency, region_id, rate_date)
);

-- Insert default Central Nexus districts
INSERT INTO nexus_districts (name, district_type, sector_start, sector_end, specialization) VALUES
('Commerce Central', 'commerce', 1, 500, '{"trading_bonus": 1.2, "market_efficiency": 1.5}'),
('Diplomatic Quarter', 'diplomatic', 501, 800, '{"embassy_capacity": 50, "diplomatic_immunity": true}'),
('Industrial Zone', 'industrial', 801, 1200, '{"production_bonus": 1.3, "resource_processing": 1.4}'),
('Residential District', 'residential', 1201, 1600, '{"player_capacity": 2000, "services": ["banking", "medical", "recreation"]}'),
('Transit Hub', 'transit', 1601, 2000, '{"warp_efficiency": 1.5, "travel_time_reduction": 0.3}'),
('High Security Zone', 'commerce', 2001, 2500, '{"security_level": 10, "premium_trading": true}'),
('Cultural Center', 'diplomatic', 2501, 3000, '{"cultural_events": true, "inter_regional_festivals": true}'),
('Research Campus', 'industrial', 3001, 3500, '{"research_bonus": 1.4, "technology_sharing": true}'),
('Free Trade Zone', 'commerce', 3501, 4000, '{"tax_free": true, "unrestricted_trading": true}'),
('Gateway Plaza', 'transit', 4001, 5000, '{"all_region_access": true, "express_travel": true}')
ON CONFLICT (name) DO NOTHING;

-- Insert nexus sectors for each district
DO $$
DECLARE
    district_record RECORD;
    sector_num INTEGER;
BEGIN
    FOR district_record IN SELECT id, sector_start, sector_end, district_type FROM nexus_districts LOOP
        FOR sector_num IN district_record.sector_start..district_record.sector_end LOOP
            INSERT INTO nexus_sectors (district_id, sector_number, sector_type, security_level)
            VALUES (
                district_record.id,
                sector_num,
                CASE 
                    WHEN district_record.district_type = 'commerce' THEN 'market'
                    WHEN district_record.district_type = 'diplomatic' THEN 'embassy'
                    WHEN district_record.district_type = 'industrial' THEN 'industrial'
                    WHEN district_record.district_type = 'residential' THEN 'residential'
                    WHEN district_record.district_type = 'transit' THEN 'transit'
                    ELSE 'hub'
                END,
                CASE 
                    WHEN district_record.district_type = 'diplomatic' THEN 9
                    WHEN sector_num BETWEEN 2001 AND 2500 THEN 10
                    WHEN district_record.district_type = 'transit' THEN 8
                    ELSE 7
                END
            )
            ON CONFLICT (sector_number) DO NOTHING;
        END LOOP;
    END LOOP;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_nexus_sectors_district ON nexus_sectors(district_id);
CREATE INDEX IF NOT EXISTS idx_nexus_sectors_type ON nexus_sectors(sector_type);
CREATE INDEX IF NOT EXISTS idx_warp_gates_active ON inter_regional_warp_gates(is_active);
CREATE INDEX IF NOT EXISTS idx_embassies_region ON regional_embassies(region_id);
CREATE INDEX IF NOT EXISTS idx_trade_routes_regions ON galactic_trade_routes(origin_region_id, destination_region_id);
CREATE INDEX IF NOT EXISTS idx_galactic_events_time ON galactic_events(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_security_logs_player ON nexus_security_logs(player_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_region_date ON regional_performance_metrics(region_id, metric_date);
CREATE INDEX IF NOT EXISTS idx_exchange_rates_region_date ON galactic_exchange_rates(region_id, rate_date);

-- Create update trigger for nexus_districts
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_nexus_districts_modtime 
    BEFORE UPDATE ON nexus_districts 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();