# Multi-Regional Data Models

## Overview

This document defines the comprehensive data models for the Multi-Regional System in SectorWars 2102. These models support regional governance, Central Nexus management, diplomatic relations, and inter-regional functionality.

## Core Regional Models

### Region

The primary model representing a player-owned regional territory.

```sql
CREATE TABLE regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    owner_id UUID REFERENCES users(id),
    
    -- Subscription Management
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'standard',
    paypal_subscription_id VARCHAR(255),
    subscription_status VARCHAR(50),
    subscription_started_at TIMESTAMP,
    subscription_expires_at TIMESTAMP,
    last_payment_at TIMESTAMP,
    next_billing_at TIMESTAMP,
    
    -- Regional Status
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Governance Configuration
    governance_type VARCHAR(50) NOT NULL DEFAULT 'autocracy',
    voting_threshold DECIMAL(3,2) NOT NULL DEFAULT 0.51,
    election_frequency_days INTEGER NOT NULL DEFAULT 90,
    constitutional_text TEXT,
    
    -- Economic Configuration
    tax_rate DECIMAL(5,4) NOT NULL DEFAULT 0.10,
    trade_bonuses JSONB NOT NULL DEFAULT '{}',
    economic_specialization VARCHAR(50),
    starting_credits INTEGER NOT NULL DEFAULT 1000,
    starting_ship VARCHAR(50) NOT NULL DEFAULT 'scout',
    
    -- Cultural Identity
    language_pack JSONB NOT NULL DEFAULT '{}',
    aesthetic_theme JSONB NOT NULL DEFAULT '{}',
    traditions JSONB NOT NULL DEFAULT '{}',
    social_hierarchy JSONB NOT NULL DEFAULT '{}',
    
    -- Infrastructure
    nexus_warp_gate_sector INTEGER,
    total_sectors INTEGER NOT NULL DEFAULT 500,
    active_players_30d INTEGER NOT NULL DEFAULT 0,
    total_trade_volume DECIMAL(20,2) NOT NULL DEFAULT 0.0,
    
    -- Constraints
    CONSTRAINT valid_voting_threshold CHECK (voting_threshold >= 0.1 AND voting_threshold <= 0.9),
    CONSTRAINT valid_tax_rate CHECK (tax_rate >= 0.05 AND tax_rate <= 0.25),
    CONSTRAINT valid_election_frequency CHECK (election_frequency_days >= 30 AND election_frequency_days <= 365),
    CONSTRAINT valid_starting_credits CHECK (starting_credits >= 100),
    CONSTRAINT valid_sector_count CHECK (total_sectors >= 100 AND total_sectors <= 1000)
);

CREATE INDEX idx_regions_owner_id ON regions(owner_id);
CREATE INDEX idx_regions_status ON regions(status);
CREATE INDEX idx_regions_subscription_status ON regions(subscription_status);
```

#### TypeScript Interface

```typescript
interface Region {
  id: string
  name: string
  displayName: string
  ownerId: string
  
  // Subscription
  subscriptionTier: 'standard' | 'premium' | 'enterprise'
  paypalSubscriptionId?: string
  subscriptionStatus?: 'active' | 'cancelled' | 'suspended' | 'expired'
  subscriptionStartedAt?: Date
  subscriptionExpiresAt?: Date
  lastPaymentAt?: Date
  nextBillingAt?: Date
  
  // Status
  status: 'active' | 'suspended' | 'terminated' | 'pending'
  createdAt: Date
  updatedAt: Date
  
  // Governance
  governanceType: 'autocracy' | 'democracy' | 'council'
  votingThreshold: number // 0.1 - 0.9
  electionFrequencyDays: number // 30 - 365
  constitutionalText?: string
  
  // Economics
  taxRate: number // 0.05 - 0.25
  tradeBonuses: Record<string, number> // 1.0 - 3.0
  economicSpecialization?: string
  startingCredits: number // 100+
  startingShip: string
  
  // Culture
  languagePack: Record<string, string>
  aestheticTheme: Record<string, any>
  traditions: Record<string, any>
  socialHierarchy: Record<string, any>
  
  // Infrastructure
  nexusWarpGateSector?: number
  totalSectors: number
  activePlayers30d: number
  totalTradeVolume: number
}
```

### Regional Membership

Represents player membership and citizenship within regions.

```sql
CREATE TABLE regional_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id),
    region_id UUID NOT NULL REFERENCES regions(id),
    
    -- Membership Details
    membership_type VARCHAR(50) NOT NULL DEFAULT 'visitor',
    reputation_score INTEGER NOT NULL DEFAULT 0,
    local_rank VARCHAR(50),
    voting_power DECIMAL(5,4) NOT NULL DEFAULT 1.0,
    
    -- Activity Tracking
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_visit TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_visits INTEGER NOT NULL DEFAULT 0,
    
    -- Constraints
    CONSTRAINT unique_membership UNIQUE(player_id, region_id),
    CONSTRAINT valid_voting_power CHECK (voting_power >= 0.0 AND voting_power <= 5.0),
    CONSTRAINT valid_reputation CHECK (reputation_score >= -1000 AND reputation_score <= 1000)
);

CREATE INDEX idx_regional_memberships_player_id ON regional_memberships(player_id);
CREATE INDEX idx_regional_memberships_region_id ON regional_memberships(region_id);
CREATE INDEX idx_regional_memberships_type ON regional_memberships(membership_type);
```

#### TypeScript Interface

```typescript
interface RegionalMembership {
  id: string
  playerId: string
  regionId: string
  
  // Membership
  membershipType: 'visitor' | 'resident' | 'citizen'
  reputationScore: number // -1000 to 1000
  localRank?: string
  votingPower: number // 0.0 - 5.0
  
  // Activity
  joinedAt: Date
  lastVisit: Date
  totalVisits: number
  
  // Computed properties
  isCitizen: boolean
  canVote: boolean
}
```

## Governance Models

### Regional Policy

Democratic policy proposals and referendums.

```sql
CREATE TABLE regional_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL REFERENCES regions(id),
    
    -- Policy Details
    policy_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    proposed_changes JSONB NOT NULL,
    
    -- Proposal Tracking
    proposed_by UUID NOT NULL REFERENCES players(id),
    proposed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    voting_closes_at TIMESTAMP NOT NULL,
    
    -- Voting Results
    votes_for INTEGER NOT NULL DEFAULT 0,
    votes_against INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'voting',
    
    -- Constraints
    CONSTRAINT valid_voting_period CHECK (voting_closes_at > proposed_at),
    CONSTRAINT non_negative_votes_for CHECK (votes_for >= 0),
    CONSTRAINT non_negative_votes_against CHECK (votes_against >= 0)
);

CREATE INDEX idx_regional_policies_region_id ON regional_policies(region_id);
CREATE INDEX idx_regional_policies_status ON regional_policies(status);
CREATE INDEX idx_regional_policies_proposed_at ON regional_policies(proposed_at);
```

#### TypeScript Interface

```typescript
interface RegionalPolicy {
  id: string
  regionId: string
  
  // Policy Details
  policyType: 'tax_rate' | 'pvp_rules' | 'trade_policy' | 'immigration' | 'defense' | 'cultural'
  title: string
  description?: string
  proposedChanges: Record<string, any>
  
  // Tracking
  proposedBy: string
  proposedAt: Date
  votingClosesAt: Date
  
  // Results
  votesFor: number
  votesAgainst: number
  status: 'voting' | 'passed' | 'rejected' | 'implemented'
  
  // Computed properties
  totalVotes: number
  approvalPercentage: number
  isPassing: boolean
}
```

### Regional Election

Elections for regional positions and leadership.

```sql
CREATE TABLE regional_elections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL REFERENCES regions(id),
    
    -- Election Details
    position VARCHAR(50) NOT NULL,
    candidates JSONB NOT NULL,
    voting_opens_at TIMESTAMP NOT NULL,
    voting_closes_at TIMESTAMP NOT NULL,
    results JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    
    -- Constraints
    CONSTRAINT valid_election_period CHECK (voting_closes_at > voting_opens_at)
);

CREATE INDEX idx_regional_elections_region_id ON regional_elections(region_id);
CREATE INDEX idx_regional_elections_status ON regional_elections(status);
CREATE INDEX idx_regional_elections_position ON regional_elections(position);
```

#### TypeScript Interface

```typescript
interface RegionalElection {
  id: string
  regionId: string
  
  // Election Details
  position: 'governor' | 'council_member' | 'ambassador' | 'trade_commissioner'
  candidates: Array<{
    playerId: string
    playerName: string
    platform: string
    voteCount?: number
  }>
  votingOpensAt: Date
  votingClosesAt: Date
  results?: Record<string, any>
  status: 'pending' | 'active' | 'completed' | 'cancelled'
  
  // Computed properties
  isActive: boolean
}
```

### Regional Vote

Individual votes cast in elections.

```sql
CREATE TABLE regional_votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    election_id UUID NOT NULL REFERENCES regional_elections(id),
    voter_id UUID NOT NULL REFERENCES players(id),
    candidate_id UUID NOT NULL REFERENCES players(id),
    
    -- Vote Details
    weight DECIMAL(5,4) NOT NULL DEFAULT 1.0,
    cast_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT one_vote_per_election UNIQUE(election_id, voter_id),
    CONSTRAINT valid_vote_weight CHECK (weight >= 0.0 AND weight <= 5.0)
);

CREATE INDEX idx_regional_votes_election_id ON regional_votes(election_id);
CREATE INDEX idx_regional_votes_voter_id ON regional_votes(voter_id);
```

## Diplomatic Models

### Regional Treaty

Treaties and agreements between regions.

```sql
CREATE TABLE regional_treaties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_a_id UUID NOT NULL REFERENCES regions(id),
    region_b_id UUID NOT NULL REFERENCES regions(id),
    
    -- Treaty Details
    treaty_type VARCHAR(50) NOT NULL,
    terms JSONB NOT NULL,
    signed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    
    -- Constraints
    CONSTRAINT unique_treaty UNIQUE(region_a_id, region_b_id, treaty_type),
    CONSTRAINT different_treaty_regions CHECK (region_a_id != region_b_id)
);

CREATE INDEX idx_regional_treaties_region_a ON regional_treaties(region_a_id);
CREATE INDEX idx_regional_treaties_region_b ON regional_treaties(region_b_id);
CREATE INDEX idx_regional_treaties_type ON regional_treaties(treaty_type);
```

#### TypeScript Interface

```typescript
interface RegionalTreaty {
  id: string
  regionAId: string
  regionBId: string
  
  // Treaty Details
  treatyType: 'trade_agreement' | 'defense_pact' | 'non_aggression' | 'cultural_exchange'
  terms: Record<string, any>
  signedAt: Date
  expiresAt?: Date
  status: 'active' | 'suspended' | 'terminated' | 'expired'
  
  // Computed properties
  isActive: boolean
  isExpired: boolean
}
```

## Travel & Communication Models

### Inter-Regional Travel

Tracks player movement between regions.

```sql
CREATE TABLE inter_regional_travels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id),
    source_region_id UUID NOT NULL REFERENCES regions(id),
    destination_region_id UUID NOT NULL REFERENCES regions(id),
    
    -- Travel Details
    travel_method VARCHAR(50) NOT NULL,
    travel_cost INTEGER NOT NULL DEFAULT 0,
    assets_transferred JSONB NOT NULL DEFAULT '{}',
    
    -- Status Tracking
    initiated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'in_transit',
    
    -- Constraints
    CONSTRAINT different_regions CHECK (source_region_id != destination_region_id),
    CONSTRAINT non_negative_cost CHECK (travel_cost >= 0)
);

CREATE INDEX idx_inter_regional_travels_player_id ON inter_regional_travels(player_id);
CREATE INDEX idx_inter_regional_travels_source ON inter_regional_travels(source_region_id);
CREATE INDEX idx_inter_regional_travels_destination ON inter_regional_travels(destination_region_id);
CREATE INDEX idx_inter_regional_travels_status ON inter_regional_travels(status);
```

#### TypeScript Interface

```typescript
interface InterRegionalTravel {
  id: string
  playerId: string
  sourceRegionId: string
  destinationRegionId: string
  
  // Travel Details
  travelMethod: 'platform_gate' | 'player_gate' | 'warp_jumper'
  travelCost: number
  assetsTransferred: Record<string, any>
  
  // Status
  initiatedAt: Date
  completedAt?: Date
  status: 'in_transit' | 'completed' | 'failed' | 'cancelled'
  
  // Computed properties
  isCompleted: boolean
  durationMinutes?: number
}
```

## Central Nexus Models

### Enhanced Sector Model

Extended sector model for multi-regional support and Central Nexus districts.

```sql
ALTER TABLE sectors ADD COLUMN sector_number INTEGER;
ALTER TABLE sectors ADD COLUMN region_id UUID REFERENCES regions(id);
ALTER TABLE sectors ADD COLUMN district VARCHAR(50);
ALTER TABLE sectors ADD COLUMN security_level INTEGER DEFAULT 5;
ALTER TABLE sectors ADD COLUMN development_level INTEGER DEFAULT 1;
ALTER TABLE sectors ADD COLUMN traffic_level INTEGER DEFAULT 1;

CREATE INDEX idx_sectors_sector_number ON sectors(sector_number);
CREATE INDEX idx_sectors_region_id ON sectors(region_id);
CREATE INDEX idx_sectors_district ON sectors(district);
CREATE INDEX idx_sectors_security_level ON sectors(security_level);
CREATE UNIQUE INDEX idx_sectors_region_sector_number ON sectors(region_id, sector_number);
```

#### TypeScript Interface

```typescript
interface Sector {
  id: string
  sectorId: number // Legacy identifier
  sectorNumber: number // Multi-regional identifier
  name: string
  
  // Regional Assignment
  regionId?: string
  district?: string // Central Nexus district type
  
  // Multi-regional Properties
  securityLevel: number // 1-10
  developmentLevel: number // 1-10
  trafficLevel: number // 1-10
  
  // Existing properties...
  clusterId: string
  type: SectorType
  isDiscovered: boolean
  discoveredById?: string
  discoveryDate?: Date
  
  // Physical properties
  xCoord: number
  yCoord: number
  zCoord: number
  radiationLevel: number
  hazardLevel: number
  
  // Resources and occupancy
  resources: Record<string, any>
  playersPresent: string[]
  shipsPresent: string[]
  defenses: Record<string, any>
  
  // Relationships
  region?: Region
  planets: Planet[]
  ports: Port[]
  ships: Ship[]
}
```

## Validation & Business Rules

### Regional Configuration Constraints

```typescript
interface RegionalConfigConstraints {
  taxRate: {
    min: 0.05
    max: 0.25
    description: "Regional tax rate percentage"
  }
  
  votingThreshold: {
    min: 0.1
    max: 0.9
    description: "Democratic voting threshold"
  }
  
  electionFrequencyDays: {
    min: 30
    max: 365
    description: "Days between elections"
  }
  
  startingCredits: {
    min: 100
    max: 10000
    description: "Credits given to new citizens"
  }
  
  tradeBonuses: {
    min: 1.0
    max: 3.0
    description: "Trade bonus multiplier per resource"
  }
  
  totalSectors: {
    min: 100
    max: 1000
    default: 500
    description: "Total sectors in region"
  }
  
  reputationScore: {
    min: -1000
    max: 1000
    description: "Player reputation within region"
  }
  
  votingPower: {
    min: 0.0
    max: 5.0
    description: "Voting weight for elections"
  }
}
```

### Central Nexus Districts Configuration

```typescript
interface DistrictConfiguration {
  commerce_central: {
    sectors: 500
    securityRange: [7, 9]
    developmentRange: [8, 10]
    trafficRange: [8, 10]
    characteristics: ['premium_markets', 'trade_hubs', 'financial_centers']
  }
  
  diplomatic_quarter: {
    sectors: 300
    securityRange: [8, 10]
    developmentRange: [7, 9]
    trafficRange: [4, 7]
    characteristics: ['embassies', 'negotiation_chambers', 'cultural_centers']
  }
  
  industrial_zone: {
    sectors: 600
    securityRange: [4, 7]
    developmentRange: [6, 9]
    trafficRange: [6, 9]
    characteristics: ['manufacturing', 'shipyards', 'industrial_complexes']
  }
  
  residential_district: {
    sectors: 800
    securityRange: [5, 8]
    developmentRange: [5, 8]
    trafficRange: [3, 6]
    characteristics: ['housing', 'services', 'entertainment']
  }
  
  transit_hub: {
    sectors: 400
    securityRange: [6, 8]
    developmentRange: [7, 10]
    trafficRange: [8, 10]
    characteristics: ['warp_gates', 'transportation', 'logistics']
  }
  
  high_security_zone: {
    sectors: 200
    securityRange: [9, 10]
    developmentRange: [8, 10]
    trafficRange: [1, 3]
    characteristics: ['restricted_access', 'high_value', 'premium_services']
  }
  
  cultural_center: {
    sectors: 350
    securityRange: [6, 8]
    developmentRange: [6, 9]
    trafficRange: [5, 8]
    characteristics: ['events', 'festivals', 'cultural_exchange']
  }
  
  research_campus: {
    sectors: 450
    securityRange: [7, 9]
    developmentRange: [8, 10]
    trafficRange: [3, 6]
    characteristics: ['technology', 'innovation', 'research_facilities']
  }
  
  free_trade_zone: {
    sectors: 600
    securityRange: [3, 6]
    developmentRange: [5, 8]
    trafficRange: [7, 10]
    characteristics: ['unrestricted_trade', 'black_market', 'smuggling']
  }
  
  gateway_plaza: {
    sectors: 800
    securityRange: [6, 8]
    developmentRange: [6, 8]
    trafficRange: [8, 10]
    characteristics: ['welcome_center', 'orientation', 'first_contact']
  }
}
```

## Performance Considerations

### Database Indexing Strategy

```sql
-- Regional queries optimization
CREATE INDEX idx_regions_active_subscription ON regions(status, subscription_status);
CREATE INDEX idx_regions_governance_type ON regions(governance_type);
CREATE INDEX idx_regions_economic_specialization ON regions(economic_specialization);

-- Membership queries optimization
CREATE INDEX idx_memberships_region_type ON regional_memberships(region_id, membership_type);
CREATE INDEX idx_memberships_player_active ON regional_memberships(player_id, last_visit);

-- Policy and election queries
CREATE INDEX idx_policies_region_status ON regional_policies(region_id, status);
CREATE INDEX idx_elections_region_active ON regional_elections(region_id, status);

-- Central Nexus queries optimization
CREATE INDEX idx_sectors_nexus_district ON sectors(region_id, district) WHERE region_id IS NOT NULL;
CREATE INDEX idx_sectors_development_traffic ON sectors(development_level, traffic_level);

-- Performance monitoring
CREATE INDEX idx_inter_regional_travels_active ON inter_regional_travels(status, initiated_at);
```

### Query Optimization Patterns

```sql
-- Regional statistics aggregation
WITH regional_stats AS (
  SELECT 
    r.id,
    COUNT(rm.id) as total_members,
    COUNT(rm.id) FILTER (WHERE rm.membership_type = 'citizen') as citizens,
    COUNT(rm.id) FILTER (WHERE rm.membership_type = 'resident') as residents,
    COUNT(rm.id) FILTER (WHERE rm.membership_type = 'visitor') as visitors,
    AVG(rm.reputation_score) as avg_reputation,
    COUNT(rp.id) FILTER (WHERE rp.status = 'voting') as pending_policies,
    COUNT(re.id) FILTER (WHERE re.status = 'active') as active_elections
  FROM regions r
  LEFT JOIN regional_memberships rm ON r.id = rm.region_id
  LEFT JOIN regional_policies rp ON r.id = rp.region_id
  LEFT JOIN regional_elections re ON r.id = re.region_id
  WHERE r.owner_id = $1
  GROUP BY r.id
)
SELECT * FROM regional_stats;

-- Central Nexus district aggregation
SELECT 
  district,
  COUNT(*) as sector_count,
  AVG(security_level) as avg_security,
  AVG(development_level) as avg_development,
  AVG(traffic_level) as avg_traffic,
  MIN(sector_number) as sector_start,
  MAX(sector_number) as sector_end
FROM sectors 
WHERE region_id = (SELECT id FROM regions WHERE name = 'central-nexus')
GROUP BY district
ORDER BY MIN(sector_number);
```

## Migration Scripts

### Regional System Migration

```sql
-- Add multi-regional columns to existing tables
ALTER TABLE players ADD COLUMN current_region_id UUID REFERENCES regions(id);
ALTER TABLE ships ADD COLUMN home_region_id UUID REFERENCES regions(id);

-- Create default Central Nexus region
INSERT INTO regions (name, display_name, governance_type, economic_specialization, total_sectors)
VALUES ('central-nexus', 'Central Nexus', 'galactic_council', 'universal_hub', 5000);

-- Migrate existing players to Central Nexus citizenship
INSERT INTO regional_memberships (player_id, region_id, membership_type)
SELECT p.id, r.id, 'citizen'
FROM players p
CROSS JOIN regions r
WHERE r.name = 'central-nexus';

-- Update existing sectors to belong to Central Nexus
UPDATE sectors 
SET region_id = (SELECT id FROM regions WHERE name = 'central-nexus'),
    sector_number = sector_id
WHERE region_id IS NULL;
```

---

**Data Model Version:** 2.0.0  
**Last Updated:** June 1, 2025  
**Schema Compatibility:** PostgreSQL 14+  
**Total Tables:** 12 (7 new, 5 enhanced)  