# Multi-Regional Migration Plan

*Created: June 1, 2025*  
*Status: PLANNING*  
*Scope: Migrate existing single-galaxy to multi-regional architecture*

## 🎯 Migration Overview

This plan outlines the strategy for migrating the existing SectorWars 2102 single-galaxy implementation to the new multi-regional architecture while maintaining zero downtime and preserving all player data.

## 📊 Current State Analysis

### Existing Data
- **Sectors**: ~500 sectors in single galaxy
- **Players**: All player data in single namespace
- **Assets**: Ships, planets, ports without regional context
- **Economy**: Single unified market
- **Social**: Single communication space

### Migration Challenges
1. Add regional context to all existing data
2. Maintain game state during migration
3. Preserve player experience
4. No data loss or corruption
5. Rollback capability required

## 🔄 Migration Strategy

### Phase 1: Dual-Write Mode (Week 1)
Enable system to write to both old and new schemas simultaneously.

```python
class DualWriteMiddleware:
    """Writes to both legacy and regional schemas"""
    
    async def write_sector_data(self, sector_data: dict):
        # Write to legacy table
        await self.legacy_db.write('sectors', sector_data)
        
        # Write to regional table with default region
        regional_data = {
            **sector_data,
            'region_id': DEFAULT_REGION_ID
        }
        await self.regional_db.write('sectors', regional_data)
        
        # Verify consistency
        await self.verify_write_consistency(sector_data)
```

### Phase 2: Data Migration (Week 2)

#### Step 1: Create Default Region
```sql
-- Create the default region for existing galaxy
INSERT INTO regions (
    id,
    name,
    display_name,
    owner_id,
    status,
    config
) VALUES (
    'default-region-uuid',
    'default',
    'Original Galaxy',
    NULL,  -- Platform owned
    'active',
    '{"is_default": true, "migrated_from": "legacy"}'
);
```

#### Step 2: Migrate Core Game Data
```python
async def migrate_game_data():
    """Migrate all game entities to regional structure"""
    
    migrations = [
        migrate_sectors,
        migrate_planets,
        migrate_ports,
        migrate_warp_tunnels,
        migrate_ships,
        migrate_players
    ]
    
    for migration in migrations:
        logger.info(f"Starting migration: {migration.__name__}")
        
        try:
            await migration(DEFAULT_REGION_ID)
            await verify_migration(migration.__name__)
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            await rollback_migration(migration.__name__)
            raise
```

#### Step 3: Player Migration
```python
async def migrate_players():
    """Special handling for player migration"""
    
    players = await get_all_players()
    
    for player in players:
        # Set regional affiliation
        await db.execute("""
            UPDATE players 
            SET home_region_id = $1,
                current_region_id = $1
            WHERE id = $2
        """, DEFAULT_REGION_ID, player.id)
        
        # Create regional membership
        await db.execute("""
            INSERT INTO region_memberships 
            (player_id, region_id, membership_type, joined_at)
            VALUES ($1, $2, 'citizen', $3)
        """, player.id, DEFAULT_REGION_ID, player.created_at)
        
        # Migrate player assets
        await migrate_player_assets(player.id, DEFAULT_REGION_ID)
```

### Phase 3: Verification & Testing (Week 3)

#### Data Integrity Verification
```python
class MigrationVerifier:
    """Verify migration completeness and accuracy"""
    
    async def verify_complete_migration(self):
        """Run comprehensive verification suite"""
        
        checks = {
            'sector_count': self.verify_sector_count,
            'player_assets': self.verify_player_assets,
            'economic_balance': self.verify_economic_balance,
            'relationship_integrity': self.verify_relationships,
            'game_state': self.verify_game_state
        }
        
        results = {}
        for check_name, check_func in checks.items():
            result = await check_func()
            results[check_name] = result
            
            if not result.passed:
                logger.error(f"Verification failed: {check_name}")
                logger.error(f"Details: {result.details}")
        
        return MigrationVerificationReport(results)
```

### Phase 4: Cutover (Week 4)

#### Cutover Process
1. **Maintenance Mode** (30 minutes)
   ```python
   await enable_maintenance_mode(
       message="Upgrading to Multi-Regional Galaxy! Back in 30 minutes.",
       estimated_duration=1800
   )
   ```

2. **Final Data Sync**
   ```python
   await perform_final_sync()
   await verify_data_consistency()
   ```

3. **Switch to New System**
   ```python
   # Update application configuration
   await update_config('database.schema', 'regional')
   await update_config('features.multi_regional', True)
   
   # Deploy new application version
   await deploy_application('v2.0.0-multi-regional')
   ```

4. **Verification**
   ```python
   await run_smoke_tests()
   await verify_player_access()
   await check_system_health()
   ```

5. **Go Live**
   ```python
   await disable_maintenance_mode()
   await announce_completion(
       "Welcome to the Multi-Regional Galaxy! 
       Your existing progress has been preserved in the Original Galaxy region."
   )
   ```

## 🔒 Rollback Plan

### Automatic Rollback Triggers
- Data corruption detected
- >10% of players unable to access
- Economic calculations incorrect
- Critical functionality broken

### Rollback Procedure
```python
class MigrationRollback:
    """Emergency rollback to legacy system"""
    
    async def execute_rollback(self, reason: str):
        logger.critical(f"Initiating rollback: {reason}")
        
        # 1. Enable maintenance mode
        await enable_maintenance_mode("Technical issues - restoring service")
        
        # 2. Stop new system
        await stop_application_servers()
        
        # 3. Restore database
        await restore_database_backup(self.pre_migration_backup)
        
        # 4. Deploy legacy version
        await deploy_application(self.legacy_version)
        
        # 5. Verify legacy system
        await verify_legacy_system()
        
        # 6. Re-enable access
        await disable_maintenance_mode()
        
        # 7. Communicate
        await notify_players("Service restored. Migration postponed.")
```

## 📋 Migration Checklist

### Pre-Migration (1 Week Before)
- [ ] Full database backup completed
- [ ] Migration scripts tested in staging
- [ ] Rollback procedure tested
- [ ] Support team briefed
- [ ] Player communication sent

### Migration Day
- [ ] Final backup taken
- [ ] Maintenance mode enabled
- [ ] Migration scripts executed
- [ ] Data verification passed
- [ ] New system deployed
- [ ] Smoke tests passed
- [ ] System monitoring active

### Post-Migration (1 Week After)
- [ ] Player feedback collected
- [ ] Performance metrics analyzed
- [ ] Bug reports addressed
- [ ] Documentation updated
- [ ] Lessons learned documented

## 📊 Success Criteria

### Technical Metrics
- Zero data loss
- All players can access their accounts
- Game functionality preserved
- Performance within 10% of legacy

### Business Metrics
- <5% increase in support tickets
- <2% player churn during migration
- Positive community sentiment
- No revenue disruption

## 🔔 Communication Plan

### Pre-Migration
- **T-7 days**: Announcement with benefits explanation
- **T-3 days**: Detailed migration schedule
- **T-1 day**: Final reminder and preparation tips

### During Migration
- Status page updates every 10 minutes
- Social media updates every 15 minutes
- Support team responding to concerns

### Post-Migration
- Success announcement
- Feature highlights
- Thank you to community
- Feedback collection

---

*This migration plan ensures a smooth transition from single-galaxy to multi-regional architecture while protecting player data and experience.*