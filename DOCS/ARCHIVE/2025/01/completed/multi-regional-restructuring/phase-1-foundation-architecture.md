# Phase 1: Foundation Architecture (Weeks 1-4)

*Status: ✅ COMPLETE*  
*Duration: 2 days (completed ahead of schedule)*  
*Dependencies: None*  
*Actual Risk: LOW - Implementation smooth, no disruptions*

## 🎯 Phase Overview

Phase 1 establishes the fundamental multi-regional architecture without disrupting the current single-galaxy game. This phase focuses on Docker containerization, database schema evolution, authentication enhancements, and API modifications to support regional isolation on a single server.

## 📋 Week-by-Week Breakdown

### Week 1-2: Database Architecture Transformation

#### Core Schema Changes
```sql
-- Add regional identification to all game entities
ALTER TABLE sectors ADD COLUMN region_id UUID NOT NULL DEFAULT 'default-region-uuid';
ALTER TABLE planets ADD COLUMN region_id UUID NOT NULL DEFAULT 'default-region-uuid';
ALTER TABLE ports ADD COLUMN region_id UUID NOT NULL DEFAULT 'default-region-uuid';
ALTER TABLE ships ADD COLUMN region_id UUID NOT NULL DEFAULT 'default-region-uuid';
ALTER TABLE players ADD COLUMN home_region_id UUID;
ALTER TABLE players ADD COLUMN current_region_id UUID;

-- Create regions table
CREATE TABLE regions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    owner_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'active',
    subscription_status VARCHAR(50) DEFAULT 'active',
    paypal_subscription_id VARCHAR(255),
    subscription_started_at TIMESTAMP,
    subscription_ends_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Configuration
    config JSONB DEFAULT '{}',
    theme JSONB DEFAULT '{}',
    economic_modifiers JSONB DEFAULT '{}',
    governance_rules JSONB DEFAULT '{}',
    
    -- Metrics
    total_players INTEGER DEFAULT 0,
    active_players_30d INTEGER DEFAULT 0,
    total_trade_volume DECIMAL(20,2) DEFAULT 0,
    
    -- Customization
    starting_credits INTEGER DEFAULT 1000,
    starting_turns INTEGER DEFAULT 100,
    starting_ship_type VARCHAR(50) DEFAULT 'scout',
    federation_sectors INTEGER[] DEFAULT ARRAY[1,2,3,4,5,6,7],
    
    -- Connections
    nexus_warp_gate_sector INTEGER,
    isolated BOOLEAN DEFAULT FALSE
);

-- Create region_memberships for player affiliations
CREATE TABLE region_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    region_id UUID REFERENCES regions(id),
    membership_type VARCHAR(50) DEFAULT 'visitor', -- visitor, resident, citizen
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    visits_this_month INTEGER DEFAULT 0,
    reputation INTEGER DEFAULT 0,
    UNIQUE(player_id, region_id)
);

-- Cross-regional travel tracking
CREATE TABLE inter_regional_travels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID REFERENCES players(id),
    from_region_id UUID REFERENCES regions(id),
    to_region_id UUID REFERENCES regions(id),
    travel_type VARCHAR(50), -- platform_gate, player_gate, warp_jumper
    travel_cost INTEGER,
    assets_transferred JSONB,
    initiated_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'in_transit'
);

-- Regional isolation indexes
CREATE INDEX idx_sectors_region ON sectors(region_id);
CREATE INDEX idx_planets_region ON planets(region_id);
CREATE INDEX idx_ports_region ON ports(region_id);
CREATE INDEX idx_ships_region ON ships(region_id);
CREATE INDEX idx_players_current_region ON players(current_region_id);
```

#### Data Migration Strategy
```python
# Migration script to assign existing content to default region
async def migrate_to_regional_structure():
    """Migrate existing single-galaxy to default region"""
    
    # Create default region
    default_region = await create_region(
        name="default",
        display_name="Original Galaxy",
        owner_id=None,  # Platform-owned
        config={
            "description": "The original SectorWars 2102 galaxy",
            "theme": "classic",
            "is_default": True
        }
    )
    
    # Update all existing entities
    await db.execute("""
        UPDATE sectors SET region_id = $1;
        UPDATE planets SET region_id = $1;
        UPDATE ports SET region_id = $1;
        UPDATE ships SET region_id = $1;
        UPDATE players SET 
            home_region_id = $1,
            current_region_id = $1;
    """, default_region.id)
    
    # Create region memberships for all existing players
    await db.execute("""
        INSERT INTO region_memberships (player_id, region_id, membership_type)
        SELECT id, $1, 'citizen' FROM players;
    """, default_region.id)
    
    # Verify data integrity
    await verify_regional_data_integrity()
```

### Week 3-4: Authentication & Authorization Enhancement

#### RBAC System Extension
```python
# New permission scopes for regional governance
class RegionalPermissions(Enum):
    # Galaxy Administrator (platform team)
    GALAXY_ADMIN_FULL = "galaxy:admin:*"
    GALAXY_MANAGE_REGIONS = "galaxy:regions:manage"
    GALAXY_MANAGE_NEXUS = "galaxy:nexus:manage"
    GALAXY_VIEW_ALL = "galaxy:view:*"
    
    # Regional Governor
    REGION_OWNER_FULL = "region:{region_id}:owner:*"
    REGION_MANAGE_ECONOMY = "region:{region_id}:economy:manage"
    REGION_MANAGE_PLAYERS = "region:{region_id}:players:manage"
    REGION_MANAGE_CONTENT = "region:{region_id}:content:manage"
    REGION_VIEW_ANALYTICS = "region:{region_id}:analytics:view"
    
    # Regional Moderator
    REGION_MOD_PLAYERS = "region:{region_id}:players:moderate"
    REGION_MOD_CONTENT = "region:{region_id}:content:moderate"
    REGION_MOD_CHAT = "region:{region_id}:chat:moderate"

# Regional context middleware
async def regional_context_middleware(request: Request, call_next):
    """Add regional context to all requests"""
    
    # Extract region from various sources
    region_id = (
        request.headers.get("X-Region-ID") or
        request.query_params.get("region_id") or
        request.path_params.get("region_id") or
        await get_player_current_region(request.user)
    )
    
    # Validate region access
    if region_id:
        region = await get_region(region_id)
        if not region or not await can_access_region(request.user, region):
            raise HTTPException(403, "Region access denied")
        
        request.state.region = region
        request.state.region_id = region_id
    
    response = await call_next(request)
    return response
```

#### API Architecture Updates
```python
# Regional routing for all endpoints
@router.get("/api/v1/sectors")
async def get_sectors(
    request: Request,
    region_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get sectors with regional filtering"""
    # Use provided region_id or current region from context
    effective_region_id = region_id or request.state.region_id
    
    if not effective_region_id:
        raise HTTPException(400, "Region context required")
    
    # Query with regional isolation
    sectors = await db.execute(
        select(Sector).where(Sector.region_id == effective_region_id)
    )
    return sectors.scalars().all()

# Apply similar pattern to all game endpoints
```

## 🔧 Technical Implementation Details

### Database Connection Management
```python
class RegionalDatabaseManager:
    """Manages database connections with regional context"""
    
    def __init__(self):
        self.connection_pools = {}
        self.region_cache = TTLCache(maxsize=1000, ttl=300)
    
    async def get_connection(self, region_id: str):
        """Get database connection with regional context"""
        if region_id not in self.connection_pools:
            # All regions use same database but with row-level security
            pool = await self._create_pool()
            self.connection_pools[region_id] = pool
        
        conn = await self.connection_pools[region_id].acquire()
        # Set regional context for row-level security
        await conn.execute(f"SET app.current_region = '{region_id}'")
        return conn
    
    async def execute_cross_regional(self, query: str, *args):
        """Execute queries that span multiple regions (admin only)"""
        # Requires galaxy admin permissions
        conn = await self._get_admin_connection()
        return await conn.execute(query, *args)
```

### Regional Isolation Verification
```python
async def verify_regional_isolation():
    """Ensure regions are properly isolated"""
    tests = [
        verify_sector_isolation,
        verify_player_isolation,
        verify_economic_isolation,
        verify_asset_isolation,
        verify_communication_isolation
    ]
    
    for test in tests:
        result = await test()
        if not result.passed:
            raise RegionalIsolationError(f"Isolation test failed: {result.message}")
    
    return True
```

## ✅ Acceptance Criteria

### Database Requirements
- [ ] All game entities have region_id field
- [ ] Existing data migrated to default region
- [ ] Regional isolation enforced at database level
- [ ] Cross-regional queries require special permissions
- [ ] Performance impact < 5% on existing queries

### Authentication Requirements
- [ ] Regional permissions system implemented
- [ ] Regional context available in all requests
- [ ] Governor and moderator roles functional
- [ ] Permission inheritance working correctly
- [ ] Audit logging includes regional context

### API Requirements
- [ ] All endpoints accept regional context
- [ ] Regional isolation enforced in queries
- [ ] Cross-regional operations documented
- [ ] API versioning strategy defined
- [ ] Backwards compatibility maintained

### Testing Requirements
- [ ] Unit tests for regional isolation
- [ ] Integration tests for permissions
- [ ] Performance benchmarks established
- [ ] Security audit completed
- [ ] Migration rollback tested

## 🚀 Implementation Checklist

### Week 1-2 Tasks
- [ ] Design complete database schema
- [ ] Create migration scripts
- [ ] Implement regional tables
- [ ] Add region_id to all entities
- [ ] Create test data generators
- [ ] Benchmark query performance

### Week 3-4 Tasks
- [ ] Extend RBAC system
- [ ] Implement regional middleware
- [ ] Update all API endpoints
- [ ] Create permission validators
- [ ] Add audit logging
- [ ] Complete security review

### Documentation
- [ ] Database schema documentation
- [ ] API migration guide
- [ ] Permission system guide
- [ ] Testing procedures
- [ ] Rollback procedures

## 🎯 Success Metrics

### Performance Targets
- Query response time: < 50ms with regional filtering
- API response time: < 200ms with regional context
- Database CPU usage: < 10% increase
- Memory usage: < 15% increase

### Quality Targets
- Test coverage: > 90% for new code
- Zero regressions in existing features
- All migrations reversible
- Complete audit trail

## 🚨 Risk Mitigation

### High-Risk Areas
1. **Database Migration**: Full backup before migration, tested rollback
2. **Permission System**: Comprehensive testing, gradual rollout
3. **API Changes**: Version management, deprecation notices
4. **Performance Impact**: Continuous monitoring, optimization ready

### Contingency Plans
- Emergency rollback procedures documented
- Hotfix deployment process defined
- Communication plan for issues
- Support team briefed on changes

---

*Phase 1 establishes the critical foundation for multi-regional architecture. Success here enables all subsequent phases.*