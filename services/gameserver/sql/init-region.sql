-- Regional Database Initialization Script
-- This script sets up individual regional databases

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Regional configuration table
CREATE TABLE IF NOT EXISTS regional_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_name VARCHAR(255) NOT NULL UNIQUE,
    owner_id UUID NOT NULL,
    governance_type VARCHAR(50) DEFAULT 'autocracy',
    economic_specialization VARCHAR(50) DEFAULT 'balanced',
    language_pack JSONB DEFAULT '{}',
    aesthetic_theme JSONB DEFAULT '{}',
    custom_rules JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regional clusters (Federation, Border, Frontier)
CREATE TABLE IF NOT EXISTS regional_clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cluster_name VARCHAR(255) NOT NULL,
    cluster_type VARCHAR(50) NOT NULL, -- federation, border, frontier
    sector_start INTEGER NOT NULL,
    sector_end INTEGER NOT NULL,
    security_level INTEGER DEFAULT 5,
    development_level INTEGER DEFAULT 1, -- 1-10
    special_properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regional events and activities
CREATE TABLE IF NOT EXISTS regional_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    target_clusters VARCHAR(50)[], -- which clusters can participate
    rewards JSONB DEFAULT '{}',
    participation_requirements JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'active',
    created_by UUID, -- Governor or admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regional economy tracking
CREATE TABLE IF NOT EXISTS regional_economy (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_date DATE NOT NULL,
    total_credits_in_circulation DECIMAL(20,2) DEFAULT 0.00,
    trade_volume DECIMAL(20,2) DEFAULT 0.00,
    tax_revenue DECIMAL(20,2) DEFAULT 0.00,
    imports_value DECIMAL(20,2) DEFAULT 0.00,
    exports_value DECIMAL(20,2) DEFAULT 0.00,
    gdp_estimate DECIMAL(20,2) DEFAULT 0.00,
    unemployment_rate DECIMAL(5,4) DEFAULT 0.0000,
    inflation_rate DECIMAL(5,4) DEFAULT 0.0000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date)
);

-- Regional governance tracking
CREATE TABLE IF NOT EXISTS governance_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_type VARCHAR(50) NOT NULL, -- policy, law, regulation, appointment
    title VARCHAR(255) NOT NULL,
    description TEXT,
    proposed_by UUID, -- Player ID
    decision_date TIMESTAMP NOT NULL,
    voting_deadline TIMESTAMP,
    implementation_date TIMESTAMP,
    votes_for INTEGER DEFAULT 0,
    votes_against INTEGER DEFAULT 0,
    votes_abstain INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'proposed', -- proposed, voting, passed, rejected, implemented
    implementation_details JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regional citizen voting records
CREATE TABLE IF NOT EXISTS governance_votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID REFERENCES governance_decisions(id),
    voter_id UUID NOT NULL, -- Player ID
    vote_choice VARCHAR(20) NOT NULL, -- for, against, abstain
    vote_weight DECIMAL(5,4) DEFAULT 1.0000,
    cast_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(decision_id, voter_id)
);

-- Regional cultural developments
CREATE TABLE IF NOT EXISTS cultural_developments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    development_type VARCHAR(50) NOT NULL, -- tradition, festival, landmark, custom
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cultural_impact INTEGER DEFAULT 1, -- 1-10
    player_participation_count INTEGER DEFAULT 0,
    established_date DATE NOT NULL,
    annual_celebration BOOLEAN DEFAULT false,
    cultural_bonus JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regional security incidents
CREATE TABLE IF NOT EXISTS security_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_type VARCHAR(50) NOT NULL, -- piracy, conflict, smuggling, espionage
    sector_id INTEGER NOT NULL,
    severity_level INTEGER DEFAULT 1, -- 1-10
    involved_players UUID[],
    incident_time TIMESTAMP NOT NULL,
    resolution_time TIMESTAMP,
    resolution_method VARCHAR(100),
    impact_assessment JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'investigating',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regional resource deposits (unique to each region)
CREATE TABLE IF NOT EXISTS regional_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type VARCHAR(50) NOT NULL,
    sector_id INTEGER NOT NULL,
    quantity DECIMAL(15,2) NOT NULL,
    quality_rating INTEGER DEFAULT 5, -- 1-10
    extraction_difficulty INTEGER DEFAULT 5, -- 1-10
    ownership_status VARCHAR(50) DEFAULT 'unclaimed', -- unclaimed, claimed, disputed
    owner_id UUID, -- Player ID if claimed
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_extracted_at TIMESTAMP
);

-- Regional infrastructure projects
CREATE TABLE IF NOT EXISTS infrastructure_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_type VARCHAR(50) NOT NULL, -- station, shipyard, research_facility, defense_platform
    name VARCHAR(255) NOT NULL,
    sector_id INTEGER NOT NULL,
    sponsor_id UUID NOT NULL, -- Player or government
    total_cost DECIMAL(15,2) NOT NULL,
    funding_progress DECIMAL(15,2) DEFAULT 0.00,
    construction_progress DECIMAL(5,4) DEFAULT 0.0000, -- 0.0 to 1.0
    estimated_completion TIMESTAMP,
    benefits JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'proposed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default clusters for a 500-sector region
INSERT INTO regional_clusters (cluster_name, cluster_type, sector_start, sector_end, security_level, development_level, special_properties) VALUES
('Federation Core', 'federation', 1, 167, 8, 8, '{"high_security": true, "government_facilities": true, "advanced_infrastructure": true}'),
('Federation Outer', 'federation', 168, 250, 7, 6, '{"established_trade": true, "moderate_security": true}'),
('Border Central', 'border', 251, 334, 5, 4, '{"contested_areas": true, "mixed_governance": true, "trade_opportunities": true}'),
('Border Rim', 'border', 335, 400, 4, 3, '{"frontier_like": true, "low_security": true, "resource_rich": true}'),
('Frontier Inner', 'frontier', 401, 450, 3, 2, '{"unexplored_areas": true, "dangerous": true, "high_rewards": true}'),
('Frontier Outer', 'frontier', 451, 500, 2, 1, '{"wild_space": true, "uncharted": true, "extreme_danger": true, "unknown_resources": true}')
ON CONFLICT (cluster_name) DO NOTHING;

-- Insert sample governance structure
INSERT INTO governance_decisions (decision_type, title, description, proposed_by, decision_date, status) VALUES
('policy', 'Regional Tax Rate Setting', 'Establish the base tax rate for all trade transactions within the region', uuid_generate_v4(), CURRENT_TIMESTAMP, 'implemented'),
('law', 'Player vs Player Combat Regulations', 'Define rules and restrictions for PvP combat within regional space', uuid_generate_v4(), CURRENT_TIMESTAMP, 'implemented'),
('regulation', 'Resource Extraction Licensing', 'Requirements for obtaining licenses to extract regional resources', uuid_generate_v4(), CURRENT_TIMESTAMP, 'implemented')
ON CONFLICT DO NOTHING;

-- Insert sample cultural developments
INSERT INTO cultural_developments (development_type, name, description, established_date, annual_celebration, cultural_bonus) VALUES
('tradition', 'Founders Day', 'Annual celebration of the region''s establishment', CURRENT_DATE, true, '{"trade_bonus": 0.1, "reputation_bonus": 50}'),
('festival', 'Harvest Festival', 'Celebrating successful resource extraction and trade', CURRENT_DATE, true, '{"resource_bonus": 0.15, "community_bonus": 25}'),
('custom', 'Explorer''s Code', 'Unwritten rules for behavior in frontier space', CURRENT_DATE, false, '{"frontier_safety": 0.2, "discovery_bonus": 0.1}')
ON CONFLICT DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_regional_events_time ON regional_events(start_time, end_time);
CREATE INDEX IF NOT EXISTS idx_regional_economy_date ON regional_economy(metric_date);
CREATE INDEX IF NOT EXISTS idx_governance_decisions_status ON governance_decisions(status);
CREATE INDEX IF NOT EXISTS idx_governance_votes_decision ON governance_votes(decision_id);
CREATE INDEX IF NOT EXISTS idx_security_incidents_sector ON security_incidents(sector_id);
CREATE INDEX IF NOT EXISTS idx_security_incidents_time ON security_incidents(incident_time);
CREATE INDEX IF NOT EXISTS idx_regional_resources_sector ON regional_resources(sector_id);
CREATE INDEX IF NOT EXISTS idx_regional_resources_type ON regional_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_infrastructure_projects_sector ON infrastructure_projects(sector_id);
CREATE INDEX IF NOT EXISTS idx_infrastructure_projects_status ON infrastructure_projects(status);

-- Create update triggers
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_regional_config_modtime 
    BEFORE UPDATE ON regional_config 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();