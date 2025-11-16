# Enhanced Player Analytics - Technical Design

*Created: May 23, 2025*  
*Implementation Week: Week 1*  
*CLAUDE Phase: 2 - Detailed Planning*

## Component Architecture

### Enhanced PlayerAnalytics State
```typescript
interface PlayerAnalyticsState {
  // Data Management
  players: PlayerModel[];
  selectedPlayer: PlayerModel | null;
  totalCount: number;
  currentPage: number;
  
  // UI State
  editMode: boolean;
  unsavedChanges: boolean;
  loading: boolean;
  errors: ValidationError[];
  
  // Filtering & Search
  filters: {
    search: string;
    status: 'all' | 'active' | 'inactive' | 'banned';
    team: string | null;
    minCredits: number | null;
    maxCredits: number | null;
    lastLoginAfter: Date | null;
    lastLoginBefore: Date | null;
    reputationFilter: ReputationFilter | null;
  };
  
  // Sorting & Pagination
  sortBy: 'username' | 'credits' | 'turns' | 'created_at' | 'last_login';
  sortOrder: 'asc' | 'desc';
  pageSize: number;
  
  // Asset Management
  playerAssets: {
    ships: ShipModel[];
    planets: PlanetModel[];
    ports: PortModel[];
    loading: boolean;
  };
  
  // Activity Monitoring
  playerActivity: ActivityLogEntry[];
  realTimeUpdates: boolean;
}
```

### Key Sub-components to Build

#### 1. PlayerSearchAndFilter Component
```typescript
interface PlayerSearchAndFilterProps {
  filters: PlayerFilters;
  onFiltersChange: (filters: PlayerFilters) => void;
  onSearch: (query: string) => void;
  loading?: boolean;
}

// Features:
// - Advanced search with multiple criteria
// - Date range pickers for last login
// - Credit range sliders
// - Team/faction selection
// - Reputation level filtering
// - Real-time search suggestions
```

#### 2. PlayerDetailEditor Component
```typescript
interface PlayerDetailEditorProps {
  player: PlayerModel;
  editMode: boolean;
  onSave: (updates: PlayerUpdates) => Promise<void>;
  onCancel: () => void;
  unsavedChanges: boolean;
}

// Features:
// - Editable fields for all player properties
// - Credit adjustment with reason tracking
// - Turn management (grant/remove)
// - Location teleportation
// - Reputation editing with faction breakdown
// - Account status management
// - Form validation and error handling
```

#### 3. PlayerAssetManager Component
```typescript
interface PlayerAssetManagerProps {
  playerId: string;
  assets: PlayerAssets;
  onAssetTransfer: (transfer: AssetTransfer) => Promise<void>;
  onAssetCreate: (asset: AssetCreation) => Promise<void>;
  onAssetRemove: (assetId: string, type: AssetType) => Promise<void>;
}

// Features:
// - Ship management (assign/remove ships)
// - Planet ownership transfer
// - Port ownership management
// - Asset value calculations
// - Transfer history tracking
```

#### 4. PlayerActivityMonitor Component
```typescript
interface PlayerActivityMonitorProps {
  playerId: string;
  activities: ActivityLogEntry[];
  realTime: boolean;
  onToggleRealTime: (enabled: boolean) => void;
}

// Features:
// - Real-time activity feed
// - Activity filtering and search
// - Activity timeline visualization
// - Suspicious activity alerts
// - Export activity logs
```

#### 5. BulkOperationPanel Component
```typescript
interface BulkOperationPanelProps {
  selectedPlayers: string[];
  onBulkOperation: (operation: BulkOperation) => Promise<void>;
  availableOperations: BulkOperationType[];
}

// Features:
// - Multi-player selection
// - Bulk credit adjustments
// - Bulk turn grants
// - Bulk status changes
// - Bulk reputation adjustments
// - Operation confirmation dialogs
```

#### 6. EmergencyOperationsPanel Component
```typescript
interface EmergencyOperationsPanelProps {
  playerId: string;
  onEmergencyAction: (action: EmergencyAction) => Promise<void>;
}

// Features:
// - Player rescue operations
// - Emergency teleportation
// - Account restoration
// - Compensation management
// - Crisis intervention tools
```

## API Integration Plan

### Enhanced API Endpoints Needed
```typescript
// Enhanced player listing
GET /api/admin/players/enhanced
Query Parameters:
  - page, limit, search, filters (all existing)
  - include_assets: boolean
  - include_activity: boolean
  - real_time: boolean

// Player detail management
GET /api/admin/players/{id}/complete
PUT /api/admin/players/{id}/comprehensive
POST /api/admin/players/{id}/emergency

// Asset management
GET /api/admin/players/{id}/assets
POST /api/admin/players/{id}/assets/transfer
POST /api/admin/players/{id}/assets/create
DELETE /api/admin/players/{id}/assets/{assetId}

// Activity monitoring
GET /api/admin/players/{id}/activity
WS /api/admin/players/{id}/activity/live

// Bulk operations
POST /api/admin/players/bulk-operation
```

### Data Models
```typescript
interface PlayerModel {
  // Core fields (existing)
  id: string;
  username: string;
  email: string;
  credits: number;
  turns: number;
  
  // Enhanced fields
  reputation: FactionReputations;
  currentLocation: {
    sector_id: number;
    sector_name: string;
    is_ported: boolean;
    is_landed: boolean;
    port_id?: string;
    planet_id?: string;
  };
  
  // Asset summary
  assets: {
    ships_count: number;
    planets_count: number;
    ports_count: number;
    total_value: number;
  };
  
  // Activity summary
  activity: {
    last_login: Date;
    session_count_today: number;
    actions_today: number;
    suspicious_activity: boolean;
  };
  
  // Admin metadata
  admin_notes: string;
  last_admin_action: Date;
  created_by_admin: boolean;
}

interface AssetTransfer {
  from_player_id: string;
  to_player_id: string;
  assets: {
    ship_ids?: string[];
    planet_ids?: string[];
    port_ids?: string[];
    credits?: number;
    items?: {
      attack_drones?: number;
      defense_drones?: number;
      mines?: number;
    };
  };
  reason: string;
  notify_players: boolean;
}

interface EmergencyAction {
  type: 'RESCUE' | 'TELEPORT' | 'RESTORE' | 'COMPENSATE';
  parameters: {
    target_sector_id?: number;
    restore_to_date?: Date;
    compensation_amount?: number;
    reason: string;
  };
}

interface BulkOperation {
  player_ids: string[];
  operation: 'CREDIT_ADJUST' | 'TURN_GRANT' | 'STATUS_CHANGE' | 'REPUTATION_ADJUST';
  parameters: {
    amount?: number;
    new_status?: string;
    reputation_changes?: ReputationChange[];
    reason: string;
  };
}
```

## UI/UX Enhancements

### Enhanced Modal System
```typescript
// Multi-tab modal for comprehensive player management
interface PlayerManagementModalTabs {
  'overview': PlayerOverviewTab;
  'edit': PlayerEditTab;
  'assets': PlayerAssetsTab;
  'activity': PlayerActivityTab;
  'emergency': EmergencyOperationsTab;
}

// Each tab has its own component and state management
```

### Real-time Updates
```typescript
// WebSocket integration for live updates
interface RealTimePlayerUpdates {
  player_movement: (playerId: string, newSectorId: number) => void;
  player_action: (playerId: string, action: PlayerAction) => void;
  player_status_change: (playerId: string, newStatus: string) => void;
  admin_action: (adminId: string, targetPlayerId: string, action: string) => void;
}
```

### Advanced Filtering UI
```typescript
// Multi-criteria filtering interface
interface AdvancedFilters {
  searchCriteria: {
    username: string;
    email: string;
    id: string;
  };
  rangeCriteria: {
    credits: [number, number];
    turns: [number, number];
    ships_count: [number, number];
    planets_count: [number, number];
  };
  dateCriteria: {
    created_after: Date;
    created_before: Date;
    last_login_after: Date;
    last_login_before: Date;
  };
  statusCriteria: {
    account_status: string[];
    online_status: boolean;
    team_affiliation: string[];
  };
}
```

## Implementation Priority

### Phase 3 Implementation Order:
1. **Day 1**: Enhanced player listing with advanced filtering
2. **Day 2**: Player detail editor with comprehensive field editing
3. **Day 3**: Asset management system and transfer capabilities
4. **Day 4**: Activity monitoring and real-time updates
5. **Day 5**: Bulk operations and emergency action panels

### Success Criteria for Phase 3:
- [ ] All player database fields editable through UI
- [ ] Asset transfers working between players
- [ ] Real-time activity monitoring functional
- [ ] Bulk operations implemented for common admin tasks
- [ ] Emergency operations available for crisis management
- [ ] Advanced filtering and search working
- [ ] Form validation preventing invalid data entry
- [ ] Comprehensive error handling and user feedback

## Security Considerations
- All operations require admin authentication
- Sensitive operations require additional confirmation
- All actions logged with admin user ID and timestamp
- Asset transfers include reason tracking and notification
- Emergency operations trigger security alerts
- Bulk operations have rate limiting and size restrictions

This design provides a comprehensive foundation for implementing the enhanced Player Analytics component that will give administrators complete control over player management while maintaining security and usability.