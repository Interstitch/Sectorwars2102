# API Contract Coordination
**Purpose**: Define API endpoints before implementation to ensure compatibility  
**Process**: Define → Review → Implement

**REMINDER: All three main components of our game is DOCKER based and running in a container.**

## Contract Status Legend
- 📝 **Proposed**: Initial definition, needs review
- ✅ **Approved**: Ready for implementation
- 🚧 **In Progress**: Currently being implemented
- ✔️ **Completed**: Implemented and tested
- ⚠️ **Modified**: Changed after initial approval (requires re-review)

---

## Phase 1 API Contracts (Weeks 1-4)

### Security Enhancements (Gameserver)
```typescript
// Security Headers Middleware
📝 Middleware: SecurityHeaders
   - Adds OWASP-compliant security headers
   - No API endpoint, internal middleware

// Audit Logging
✔️ POST /api/admin/audit/log
   Request: { action: string, resource: string, details: object }
   Response: { success: boolean, auditId: string }

✔️ GET /api/admin/audit/logs
   Query: { page: number, limit: number, userId?: string, action?: string }
   Response: { logs: AuditLog[], total: number }
```

### Message System (Gameserver → Player UI + Admin UI)
```typescript
// Player Messaging
✔️ POST /api/messages/send
   Request: { recipientId: string, subject?: string, content: string }
   Response: { messageId: string, sentAt: string }

✔️ GET /api/messages/inbox
   Query: { page: number, unreadOnly?: boolean }
   Response: { messages: Message[], unreadCount: number, total: number }

✔️ PUT /api/messages/{messageId}/read
   Response: { success: boolean }

✔️ DELETE /api/messages/{messageId}
   Response: { success: boolean }

// Team Messaging  
✔️ GET /api/messages/team/{teamId}
   Query: { page: number }
   Response: { messages: Message[], total: number }

// Admin Message Management
✔️ GET /api/admin/messages/all
   Query: { page: number, flagged?: boolean }
   Response: { messages: Message[], total: number }

✔️ POST /api/admin/messages/{messageId}/moderate
   Request: { action: 'delete' | 'flag' | 'unflag', reason?: string }
   Response: { success: boolean }
```

### Combat System (Gameserver → Player UI)
```typescript
// Combat Engagement
✔️ POST /api/combat/engage
   Request: { targetType: 'ship' | 'planet' | 'port', targetId: string }
   Response: { combatId: string, status: 'initiated' | 'error', message?: string }

✔️ GET /api/combat/{combatId}/status
   Response: { status: 'ongoing' | 'completed', rounds: CombatRound[], winner?: string }

// Drone Management
✔️ POST /api/drones/deploy
   Request: { sectorId: string, droneCount: number }
   Response: { deploymentId: string, dronesDeployed: number }

✔️ GET /api/drones/deployed
   Response: { deployments: DroneDeployment[] }

✔️ DELETE /api/drones/{deploymentId}/recall
   Response: { dronesRecalled: number }
```

### Economy Dashboard (Gameserver → Admin UI)
```typescript
// Market Monitoring
✔️ GET /api/v1/admin/economy/market-data
   Query: { commodities?: string[], sectors?: string[] }
   Response: { 
     marketData: Array<{
       portId: string,
       portName: string,
       sectorId: string,
       commodities: Array<{
         name: string,
         buyPrice: number,
         sellPrice: number,
         inventory: number,
         demand: 'low' | 'medium' | 'high',
         priceChange24h: number
       }>,
       lastUpdate: string
     }>,
     timestamp: string 
   }

✔️ GET /api/v1/admin/economy/metrics
   Response: { 
     creditCirculation: number,
     inflationRate: number,
     marketStability: number,
     totalTrades24h: number,
     totalVolume24h: number,
     alerts: Array<{
       id: string,
       type: 'price_spike' | 'market_crash' | 'supply_shortage' | 'unusual_activity',
       severity: 'info' | 'warning' | 'critical',
       message: string,
       affectedCommodity?: string,
       affectedPort?: string,
       timestamp: string
     }>
   }

// Market Intervention
✔️ POST /api/v1/admin/economy/intervention
   Request: { 
     type: 'price_cap' | 'price_floor' | 'supply_injection',
     commodity: string,
     value: number,
     duration?: number
   }
   Response: { 
     interventionId: string, 
     estimatedImpact: {
       affectedPorts: number,
       priceChange: number,
       marketStabilityChange: number,
       estimatedDuration: number
     }
   }

✔️ GET /api/v1/admin/economy/price-alerts
   Query: { threshold_percent?: number }
   Response: Array<{
     id: string,
     timestamp: string,
     alert_type: string,
     severity: string,
     port_id?: string,
     port_name?: string,
     resource_type?: string,
     recommended_action: string
   }>
```

### Combat Overview (Gameserver → Admin UI)
```typescript
// Combat Monitoring
✔️ GET /api/v1/admin/combat/live
   Query: { limit?: number, combat_type?: string, sector_id?: string, active_only?: boolean }
   Response: Array<{
     id: string,
     combat_type: string,
     status: string,
     started_at: string,
     ended_at?: string,
     duration_seconds: number,
     current_round: number,
     sector: { id: string, coordinates: string, name: string },
     attacker: { id: string, type: string, name: string, level?: number },
     defender: { id: string, type: string, name: string, level?: number },
     combat_stats: {
       attacker_damage_dealt: number,
       defender_damage_dealt: number,
       attacker_shields_remaining: number,
       defender_shields_remaining: number
     },
     victor_id?: string,
     is_active: boolean,
     needs_intervention: boolean
   }>

✔️ POST /api/v1/admin/combat/{id}/intervene
   Request: {
     intervention_type: 'stop_combat' | 'adjust_damage' | 'restore_shields' | 'declare_winner',
     parameters: object
   }
   Response: {
     intervention_id: string,
     combat_id: string,
     type: string,
     status: string,
     timestamp: string,
     result: object,
     message: string
   }

✔️ GET /api/v1/admin/combat/balance
   Query: { timeframe?: string, group_by?: string }
   Response: {
     timeframe: string,
     total_combats: number,
     group_by: string,
     analytics: object,
     balance_metrics: {
       balance_score: number,
       variance: number,
       min_win_rate: number,
       max_win_rate: number
     },
     outliers: Array<{
       entity: string,
       type: 'overpowered' | 'underpowered',
       win_rate: number,
       severity: string
     }>,
     recommendations: string[]
   }

✔️ GET /api/v1/admin/combat/disputes
   Query: { status?: string, limit?: number }
   Response: Array<{
     id: string,
     combat_id?: string,
     type: string,
     severity: string,
     timestamp: string,
     description: string,
     participants: object,
     status: string,
     recommended_action: string
   }>
```

### Fleet Management (Gameserver → Admin UI)
```typescript
// Ship Administration
✔️ GET /api/v1/admin/ships
   Query: { page?: number, limit?: number, status?: string, type?: string, ownerId?: string, sectorId?: string }
   Response: { 
     ships: Array<{
       id: string,
       name: string,
       type: string,
       ownerId: string,
       ownerName: string,
       sectorId: string,
       sectorName: string,
       status: 'active' | 'destroyed' | 'maintenance' | 'docked',
       health: number,
       fuel: number,
       maintenanceLevel: number,
       insuranceStatus: 'active' | 'expired' | 'none',
       cargo: {
         capacity: number,
         used: number,
         items: Array<{ name: string, quantity: number }>
       },
       location: { x: number, y: number, z: number, docked?: string },
       lastActive: string
     }>,
     total: number,
     page: number,
     totalPages: number
   }

✔️ POST /api/v1/admin/ships/{shipId}/emergency
   Request: { 
     action: 'repair' | 'refuel' | 'teleport',
     targetSectorId?: string
   }
   Response: { 
     success: boolean, 
     shipId: string,
     action: string,
     newStatus: Partial<Ship>,
     message: string
   }

✔️ GET /api/v1/admin/ships/health-report
   Response: { 
     totalShips: number,
     byStatus: {
       active: number,
       destroyed: number,
       maintenance: number,
       docked: number
     },
     byCondition: {
       excellent: number,
       good: number,
       fair: number,
       poor: number,
       critical: number
     },
     maintenanceNeeded: number,
     criticalIssues: Array<{
       shipId: string,
       shipName: string,
       issue: 'low_fuel' | 'damaged' | 'stranded' | 'no_insurance',
       severity: 'low' | 'medium' | 'high' | 'critical',
       description: string,
       recommendedAction: string
     }>
   }

✔️ POST /api/v1/admin/ships/create
   Request: {
     type: string,
     ownerId: string,
     sectorId: string,
     name?: string
   }
   Response: { ship: Ship }

✔️ DELETE /api/v1/admin/ships/{shipId}
   Response: { success: boolean }
```

### Enhanced Security (Admin UI → Gameserver)
```typescript
// Multi-Factor Authentication
📝 POST /api/v1/auth/login/direct
   Request: { username: string, password: string }
   Response: { 
     // If MFA is required:
     requires_mfa: true,
     session_token: string
     // If MFA is not required:
     access_token: string,
     refresh_token: string,
     user_id: string
   }

📝 POST /api/v1/auth/mfa/verify
   Request: { code: string, session_token: string }
   Response: { 
     access_token: string,
     refresh_token: string,
     user_id: string
   }

📝 POST /api/v1/auth/mfa/generate
   Headers: { Authorization: Bearer <token> }
   Response: { 
     secret: string,
     qr_code_url: string,
     backup_codes: string[]
   }

📝 POST /api/v1/auth/mfa/confirm
   Headers: { Authorization: Bearer <token> }
   Request: { code: string, secret: string }
   Response: { success: boolean }

📝 GET /api/v1/auth/me
   Headers: { Authorization: Bearer <token> }
   Response: { 
     id: string,
     username: string,
     email: string,
     is_admin: boolean,
     is_active: boolean,
     last_login: string | null,
     mfaEnabled: boolean
   }
// Audit Logging
📝 POST /api/v1/admin/audit/events
   Request: { 
     action: string,
     resourceType: string,
     resourceId: string,
     details: object
   }
   Response: { success: boolean, eventId: string }

📝 GET /api/v1/admin/audit/events
   Query: { 
     page?: number,
     limit?: number,
     userId?: string,
     action?: string,
     startDate?: string,
     endDate?: string
   }
   Response: { 
     events: AuditEvent[],
     total: number,
     page: number,
     pages: number
   }
   Request: { code: string }
   Response: { success: boolean }

📝 POST /api/auth/mfa/validate
   Request: { code: string }
   Response: { valid: boolean, userId: string }

// Security Metrics
📝 GET /api/admin/security/metrics
   Query: { timeRange: '1h' | '24h' | '7d' | '30d' }
   Response: {
     totalLogins24h: number,
     failedLogins24h: number,
     activeUsers: number,
     mfaEnabledUsers: number,
     totalUsers: number,
     suspiciousActivities: number,
     blockedIPs: number,
     recentThreats: Array<{
       id: string,
       timestamp: string,
       type: string,
       severity: 'low' | 'medium' | 'high' | 'critical',
       description: string,
       status: 'detected' | 'mitigated' | 'investigating'
     }>
   }

// IP Management
📝 GET /api/admin/security/blocked-ips
   Response: { 
     ips: Array<{
       ip: string,
       reason: string,
       blockedAt: string,
       blockedBy: string,
       expiresAt?: string
     }>
   }

📝 POST /api/admin/security/block-ip
   Request: { ip: string, reason: string, duration?: number }
   Response: { success: boolean }

📝 DELETE /api/admin/security/blocked-ips/{ip}
   Response: { success: boolean }

// Security Policies
📝 GET /api/admin/security/policies
   Response: {
     passwordPolicy: {
       minLength: number,
       requireUppercase: boolean,
       requireNumbers: boolean,
       requireSpecialChars: boolean,
       expirationDays: number
     },
     sessionPolicy: {
       timeout: number,
       maxConcurrent: number,
       rememberMeDuration: number
     },
     mfaPolicy: {
       required: boolean,
       allowedMethods: string[]
     }
   }

📝 PUT /api/admin/security/policies
   Request: { /* partial policy updates */ }
   Response: { success: boolean, policies: /* updated policies */ }
```

---

## Phase 2 API Contracts (Weeks 5-8)

### Faction System (Gameserver → All UIs)
```typescript
// Player Faction Endpoints
✔️ GET /api/factions/
   Response: Array<{
     id: string,
     name: string,
     faction_type: string,
     description?: string,
     color_primary?: string,
     color_secondary?: string,
     logo_url?: string,
     territory_count: number
   }>

✔️ GET /api/factions/reputation
   Response: Array<{
     faction_id: string,
     faction_name: string,
     faction_type: string,
     current_value: number,
     current_level: string,
     title: string,
     trade_modifier: number,
     port_access_level: number,
     combat_response: string
   }>

✔️ GET /api/factions/{factionId}/reputation
   Response: { /* same as above */ }

✔️ GET /api/factions/missions
   Query: { faction_id?: string }
   Response: Array<{
     id: string,
     faction_id: string,
     faction_name: string,
     title: string,
     description?: string,
     mission_type: string,
     credit_reward: number,
     reputation_reward: number,
     item_rewards: string[],
     target_sector_id?: string,
     cargo_type?: string,
     cargo_quantity?: number,
     expires_at?: string
   }>

✔️ GET /api/factions/{factionId}/territory
   Response: {
     faction_id: string,
     faction_name: string,
     sectors: string[],
     home_sector_id?: string
   }

✔️ GET /api/factions/{factionId}/pricing-modifier
   Response: {
     faction_id: string,
     faction_name: string,
     base_modifier: number,
     player_modifier: number,
     description: string
   }

// Admin Faction Management
✔️ GET /api/admin/factions/
   Response: Array<{ /* detailed faction data */ }>

✔️ POST /api/admin/factions/
   Request: {
     name: string,
     faction_type: 'Federation' | 'Independents' | 'Pirates' | 'Merchants' | 'Explorers' | 'Military',
     description?: string,
     base_pricing_modifier: number,
     trade_specialties: string[],
     aggression_level: number,
     diplomacy_stance: string,
     color_primary?: string,
     color_secondary?: string,
     logo_url?: string
   }

✔️ PUT /api/admin/factions/{factionId}
   Request: { /* partial faction data */ }

✔️ DELETE /api/admin/factions/{factionId}
   Response: { success: boolean, message: string }

✔️ PUT /api/admin/factions/{factionId}/territory
   Request: { sector_ids: string[], home_sector_id?: string }

✔️ POST /api/admin/factions/{factionId}/missions
   Request: { /* mission data */ }

✔️ PUT /api/admin/factions/{factionId}/reputation
   Request: { player_id: string, change: number, reason: string }
```

### Drone Combat System (Gameserver → All UIs)
```typescript
// To be defined when Phase 2 begins
```

### Planetary Management (Gameserver → Player UI)
```typescript
// Planet Data
✔️ GET /api/planets/owned
   Response: { 
     planets: Array<{
       id: string,
       name: string,
       sectorId: string,
       sectorName: string,
       planetType: string,
       colonists: number,
       maxColonists: number,
       productionRates: {
         fuel: number,
         organics: number,
         equipment: number,
         colonists: number
       },
       allocations: {
         fuel: number,
         organics: number,
         equipment: number,
         unused: number
       },
       buildings: Array<{
         type: string,
         level: number,
         upgrading: boolean,
         completionTime?: string
       }>,
       defenses: {
         turrets: number,
         shields: number,
         fighters: number
       },
       underSiege: boolean,
       siegeDetails?: {
         attackerId: string,
         attackerName: string,
         phase: 'orbital' | 'bombardment' | 'invasion',
         startTime: string
       }
     }>,
     totalPlanets: number
   }

✔️ GET /api/planets/{planetId}
   Response: { /* detailed planet data as above */ }

// Colonist Management
✔️ PUT /api/planets/{planetId}/allocate
   Request: { 
     fuel: number,
     organics: number,
     equipment: number
   }
   Response: { 
     success: boolean,
     allocations: { fuel: number, organics: number, equipment: number, unused: number },
     productionRates: { fuel: number, organics: number, equipment: number, colonists: number }
   }

// Building Management
✔️ POST /api/planets/{planetId}/buildings/upgrade
   Request: { 
     buildingType: 'factory' | 'farm' | 'mine' | 'defense' | 'research',
     targetLevel: number
   }
   Response: { 
     success: boolean,
     buildingType: string,
     newLevel: number,
     completionTime: string,
     cost: { credits: number, resources: object }
   }

// Defense Configuration
✔️ PUT /api/planets/{planetId}/defenses
   Request: { 
     turrets?: number,
     shields?: number,
     fighters?: number
   }
   Response: { 
     success: boolean,
     defenses: { turrets: number, shields: number, fighters: number },
     defensePower: number
   }

// Genesis Device Deployment
✔️ POST /api/planets/genesis/deploy
   Request: { 
     sectorId: string,
     planetName: string,
     planetType: 'terran' | 'oceanic' | 'mountainous' | 'desert' | 'frozen'
   }
   Response: { 
     success: boolean,
     planetId: string,
     deploymentTime: number,
     genesisDevicesRemaining: number
   }

// Colony Specialization
✔️ PUT /api/planets/{planetId}/specialize
   Request: { 
     specialization: 'agricultural' | 'industrial' | 'military' | 'research' | 'balanced'
   }
   Response: { 
     success: boolean,
     specialization: string,
     bonuses: { production: object, defense: number, research: number }
   }

// Siege Status
✔️ GET /api/planets/{planetId}/siege-status
   Response: { 
     underSiege: boolean,
     siegeDetails?: {
       attackerId: string,
       attackerName: string,
       phase: string,
       startTime: string,
       estimatedPhaseCompletion: string,
       defenseEffectiveness: number,
       casualties: { colonists: number, fighters: number }
     }
   }
```

### Team Management (Gameserver → All UIs)
```typescript
// Team Operations
✔️ GET /api/teams/{teamId}
   Response: {
     id: string,
     name: string,
     tag: string,
     description: string,
     leaderId: string,
     leaderName: string,
     memberCount: number,
     maxMembers: number,
     reputation: number,
     founded: string,
     isPublic: boolean,
     recruitmentStatus: 'open' | 'invite-only' | 'closed',
     treasury: {
       credits: number,
       fuel: number,
       organics: number,
       equipment: number
     }
   }

✔️ POST /api/teams/create
   Request: {
     name: string,
     tag: string,
     description: string,
     isPublic: boolean,
     recruitmentStatus: 'open' | 'invite-only' | 'closed'
   }
   Response: { team: Team }

✔️ PUT /api/teams/{teamId}
   Request: { /* partial team updates */ }
   Response: { team: Team }

✔️ DELETE /api/teams/{teamId}
   Response: { success: boolean }

// Member Management
✔️ GET /api/teams/{teamId}/members
   Response: {
     members: Array<{
       id: string,
       playerId: string,
       playerName: string,
       role: 'leader' | 'officer' | 'member',
       joinedAt: string,
       contributions: {
         credits: number,
         resources: number,
         combatKills: number
       },
       online: boolean,
       location: { sectorId: string, sectorName: string },
       shipType: string,
       combatRating: number
     }>
   }

✔️ POST /api/teams/{teamId}/invite
   Request: { playerId: string, message?: string }
   Response: { invitationId: string }

✔️ DELETE /api/teams/{teamId}/members/{memberId}
   Request: { reason?: string }
   Response: { success: boolean }

✔️ PUT /api/teams/{teamId}/members/{memberId}/role
   Request: { role: 'officer' | 'member' }
   Response: { success: boolean }

// Team Chat
✔️ GET /api/teams/{teamId}/messages
   Query: { limit?: number, before?: string }
   Response: { messages: TeamMessage[] }

✔️ POST /api/teams/{teamId}/messages
   Request: { content: string }
   Response: { message: TeamMessage }

// Resource Management
✔️ POST /api/teams/{teamId}/treasury/deposit
   Request: {
     credits?: number,
     fuel?: number,
     organics?: number,
     equipment?: number
   }
   Response: { success: boolean, newTreasury: Treasury }

✔️ POST /api/teams/{teamId}/treasury/withdraw
   Request: {
     credits?: number,
     fuel?: number,
     organics?: number,
     equipment?: number
   }
   Response: { success: boolean, newTreasury: Treasury }

✔️ POST /api/teams/{teamId}/transfer
   Request: {
     toPlayerId: string,
     resources: {
       credits?: number,
       fuel?: number,
       organics?: number,
       equipment?: number
     },
     reason?: string
   }
   Response: { transferId: string }

// Mission Management
✔️ GET /api/teams/{teamId}/missions
   Response: { missions: TeamMission[] }

✔️ POST /api/teams/{teamId}/missions
   Request: {
     name: string,
     description: string,
     type: 'combat' | 'trading' | 'exploration' | 'defense' | 'siege',
     objectives: Array<{
       description: string,
       type: string,
       targetId?: string,
       requiredAmount?: number
     }>
   }
   Response: { mission: TeamMission }

✔️ PUT /api/teams/{teamId}/missions/{missionId}
   Request: { /* partial mission updates */ }
   Response: { mission: TeamMission }

📝 POST /api/teams/{teamId}/missions/{missionId}/join
   Response: { success: boolean }

📝 DELETE /api/teams/{teamId}/missions/{missionId}/leave
   Response: { success: boolean }

// Alliance & Diplomacy (PHASE 3 - DEFERRED)
📝 GET /api/teams/{teamId}/alliances
   Response: { alliances: Alliance[] }

📝 GET /api/teams/{teamId}/relations
   Response: { relations: DiplomaticRelation[] }

📝 POST /api/teams/{teamId}/alliances/propose
   Request: {
     targetTeamIds: string[],
     name: string,
     type: 'mutual-defense' | 'trade' | 'non-aggression',
     terms: string[],
     duration?: number
   }
   Response: { proposalId: string }

📝 POST /api/teams/{teamId}/treaties/propose
   Request: {
     targetTeamId: string,
     type: 'peace' | 'trade' | 'defense' | 'non-aggression',
     terms: string[],
     duration?: number
   }
   Response: { proposalId: string }

📝 PUT /api/teams/{teamId}/relations/{targetTeamId}
   Request: { type: 'ally' | 'neutral' | 'hostile' | 'war' }
   Response: { success: boolean }

📝 DELETE /api/teams/{teamId}/alliances/{allianceId}
   Response: { success: boolean }

// Analytics
✔️ GET /api/teams/{teamId}/analytics
   Query: { period: 'day' | 'week' | 'month' | 'all-time' }
   Response: {
     metrics: {
       combatStats: {
         kills: number,
         deaths: number,
         kdRatio: number,
         damageDealt: number,
         damageTaken: number
       },
       economicStats: {
         creditsEarned: number,
         creditsSpent: number,
         resourcesGathered: number,
         resourcesTraded: number,
         profitMargin: number
       },
       territoryStats: {
         sectorsControlled: number,
         planetsOwned: number,
         portsVisited: number,
         territoriesLost: number,
         territoriesGained: number
       },
       memberStats: {
         averageOnlineTime: number,
         activeMembers: number,
         newRecruits: number,
         membersLost: number
       }
     },
     topPerformers: {
       combat: TeamMember[],
       trading: TeamMember[],
       exploration: TeamMember[]
     }
   }

// Permissions
✔️ GET /api/teams/{teamId}/permissions
   Response: {
     canInvite: boolean,
     canKick: boolean,
     canPromote: boolean,
     canManageTreasury: boolean,
     canStartMissions: boolean,
     canEditTeamInfo: boolean,
     canManageAlliances: boolean,
     canDeclareWar: boolean
   }
```

**Note: Team Management Phase 1 & 2 endpoints (15 total) have been completed. Phase 3 endpoints (missions join/leave, alliances, diplomacy) are deferred to a future iteration.**

### Fleet Battle System (Gameserver → Player UI)
```typescript
// Fleet Management
✔️ POST /api/fleets
   Request: { name: string, formation?: string, commander_id?: string }
   Response: { id: string, team_id: string, name: string, status: string, total_ships: number }

✔️ GET /api/fleets
   Response: Array<Fleet>

✔️ GET /api/fleets/{fleetId}
   Response: Fleet

✔️ POST /api/fleets/{fleetId}/add-ship
   Request: { ship_id: string, role?: string }
   Response: FleetMember

✔️ DELETE /api/fleets/{fleetId}/remove-ship/{shipId}
   Response: { message: string }

✔️ PATCH /api/fleets/{fleetId}/formation
   Query: { formation: 'standard' | 'aggressive' | 'defensive' | 'flanking' | 'turtle' }
   Response: { message: string }

✔️ DELETE /api/fleets/{fleetId}
   Response: { message: string }

// Fleet Battles
✔️ POST /api/fleets/{fleetId}/initiate-battle
   Request: { defender_fleet_id: string }
   Response: { battle_id: string, phase: string, attacker_fleet_id: string, defender_fleet_id: string }

✔️ POST /api/fleets/battles/{battleId}/simulate-round
   Response: { status: string, round: number, round_results: object, battle_ongoing: boolean }

✔️ GET /api/fleets/battles
   Query: { active_only?: boolean }
   Response: Array<FleetBattle>
```

---

## Phase 3 API Contracts (Weeks 9-12)

### Market Intelligence Enhancement (Gameserver → Player UI)
```typescript
// Market Data Analysis
📝 POST /api/trading/market-data
   Request: { 
     sectorId: number | null,
     range: number  // radius in sectors
   }
   Response: {
     marketData: Array<{
       portId: string,
       portName: string,
       sectorId: number,
       prices: {
         fuel: { buy: number, sell: number, stock: number },
         organics: { buy: number, sell: number, stock: number },
         equipment: { buy: number, sell: number, stock: number }
       },
       lastUpdate: string,
       volume24h: number,
       priceChange24h: {
         fuel: number,
         organics: number,
         equipment: number
       }
     }>,
     opportunities: Array<{
       type: 'arbitrage' | 'shortage' | 'surplus',
       resource: string,
       portA: string,
       portB?: string,
       potentialProfit: number,
       confidence: number
     }>
   }

// Price Predictions
📝 POST /api/trading/predictions
   Request: {
     resources: string[],
     portIds?: string[],
     timeframes: ['1h', '6h', '24h', '7d']
   }
   Response: {
     predictions: Array<{
       resource: string,
       portId: string,
       portName: string,
       currentPrice: number,
       predictions: {
         '1h': { price: number, confidence: number, direction: 'up' | 'down' | 'stable' },
         '6h': { price: number, confidence: number, direction: 'up' | 'down' | 'stable' },
         '24h': { price: number, confidence: number, direction: 'up' | 'down' | 'stable' },
         '7d': { price: number, confidence: number, direction: 'up' | 'down' | 'stable' }
       },
       factors: string[]
     }>
   }

// Route Optimization
📝 POST /api/trading/optimize-routes
   Request: {
     startSectorId: string,
     constraints: {
       maxStops: number,
       maxTurns: number,
       maxTime: number,
       minProfit: number
     },
     preferredResources?: string[]
   }
   Response: {
     routes: Array<{
       id: string,
       name: string,
       totalProfit: number,
       totalTime: number,
       totalTurns: number,
       stops: Array<{
         sectorId: string,
         portId: string,
         action: 'buy' | 'sell',
         resource: string,
         quantity: number,
         profit: number
       }>,
       efficiency: number,
       riskLevel: 'low' | 'medium' | 'high'
     }>
   }

// Competition Analysis
📝 POST /api/trading/competition
   Request: {
     sectorRange: number,
     timeframe: '24h' | '7d' | '30d'
   }
   Response: {
     competitors: Array<{
       playerId: string,
       username: string,
       tradingStats: {
         profitLast24h: number,
         tradesLast24h: number,
         avgProfitPerTrade: number,
         favoriteResource: string
       },
       competitionScore: number,
       threatLevel: 'low' | 'medium' | 'high'
     }>,
     marketDominance: {
       fuel: { playerId: string, share: number },
       organics: { playerId: string, share: number },
       equipment: { playerId: string, share: number }
     }
   }
```

### Player Analytics System (Gameserver → Player UI)
```typescript
// Performance Analytics
📝 POST /api/players/{playerId}/analytics
   Request: {
     categories: ['overall', 'combat', 'trading', 'exploration', 'social'],
     timeRange: '24h' | '7d' | '30d' | '90d' | 'all'
   }
   Response: {
     overall: {
       totalPlaytime: number,
       creditsEarned: number,
       netWorth: number,
       rank: number,
       percentile: number
     },
     combat: {
       totalBattles: number,
       victories: number,
       winRate: number,
       damageDealt: number,
       damageTaken: number,
       favoriteTarget: string,
       kdRatio: number
     },
     trading: {
       totalTrades: number,
       totalProfit: number,
       avgProfitPerTrade: number,
       favoriteResource: string,
       bestRoute: string,
       efficiency: number
     },
     exploration: {
       sectorsVisited: number,
       planetsDiscovered: number,
       wormholesFound: number,
       mapCompletion: number,
       uniqueFinds: number
     },
     social: {
       messagesReceived: number,
       messagesSent: number,
       teamContributions: number,
       reputation: number,
       alliesCount: number
     },
     timeSeriesData: Array<{
       timestamp: string,
       metric: string,
       value: number
     }>
   }

// Achievement System
📝 GET /api/players/{playerId}/achievements
   Response: {
     achievements: Array<{
       id: string,
       name: string,
       description: string,
       category: 'combat' | 'trading' | 'exploration' | 'social' | 'special',
       tier: 'bronze' | 'silver' | 'gold' | 'platinum' | 'legendary',
       progress: number,
       maxProgress: number,
       completed: boolean,
       completedAt?: string,
       rewards: {
         credits?: number,
         experience?: number,
         title?: string,
         shipSkin?: string
       },
       hidden: boolean
     }>,
     stats: {
       totalAchievements: number,
       completedAchievements: number,
       totalPoints: number,
       completionRate: number,
       rarest: string
     }
   }

// Progress Tracking
📝 GET /api/players/{playerId}/progress
   Query: { timeRange: string }
   Response: {
     timeline: Array<{
       date: string,
       event: string,
       category: 'combat' | 'trading' | 'exploration' | 'social' | 'achievement',
       significance: 'minor' | 'moderate' | 'major' | 'legendary',
       details?: string
     }>,
     milestones: Array<{
       id: string,
       name: string,
       description: string,
       achieved: boolean,
       achievedDate?: string,
       nextTarget?: string,
       progress: number,
       icon: string
     }>,
     trends: Array<{
       category: string,
       data: Array<{ timestamp: string, value: number, label?: string }>,
       improvement: number,
       projection: number
     }>,
     comparisons: Array<{
       metric: string,
       personal: number,
       average: number,
       top10: number,
       percentile: number
     }>
   }

// Goal Management
📝 GET /api/players/{playerId}/goals
   Response: {
     goals: Array<{
       id: string,
       title: string,
       description: string,
       category: 'combat' | 'trading' | 'exploration' | 'social' | 'personal',
       type: 'daily' | 'weekly' | 'monthly' | 'custom',
       status: 'active' | 'completed' | 'failed' | 'paused',
       priority: 'low' | 'medium' | 'high' | 'critical',
       progress: number,
       target: number,
       unit: string,
       deadline: string,
       rewards: {
         credits?: number,
         experience?: number,
         achievement?: string,
         customReward?: string
       },
       milestones: Array<{
         threshold: number,
         description: string,
         completed: boolean
       }>,
       createdAt: string,
       updatedAt: string,
       completedAt?: string
     }>,
     stats: {
       totalGoals: number,
       completedGoals: number,
       failedGoals: number,
       successRate: number,
       currentStreak: number,
       bestStreak: number,
       averageCompletionTime: number,
       categoryBreakdown: object
     }
   }

📝 GET /api/players/goal-templates
   Response: Array<{
     id: string,
     title: string,
     description: string,
     category: string,
     suggestedTarget: number,
     unit: string,
     difficulty: 'easy' | 'medium' | 'hard' | 'extreme',
     estimatedTime: string,
     tips: string[]
   }>

📝 POST /api/players/{playerId}/goals
   Request: {
     title: string,
     description: string,
     category: string,
     type: string,
     priority: string,
     target: number,
     unit: string,
     deadline: string,
     rewards?: object,
     milestones?: Array<object>
   }
   Response: { goal: Goal }

📝 PUT /api/players/{playerId}/goals/{goalId}
   Request: { /* partial goal updates */ }
   Response: { goal: Goal }

📝 DELETE /api/players/{playerId}/goals/{goalId}
   Response: { success: boolean }

// Leaderboards
📝 GET /api/leaderboards/{category}
   Query: {
     subcategory?: string,
     timeRange: 'daily' | 'weekly' | 'monthly' | 'all',
     friends?: boolean,
     team?: boolean,
     region?: boolean
   }
   Response: {
     category: string,
     subcategory?: string,
     timeRange: string,
     entries: Array<{
       rank: number,
       playerId: string,
       username: string,
       avatar?: string,
       value: number,
       secondaryValue?: number,
       change: number,
       trend: 'up' | 'down' | 'stable',
       isCurrentPlayer: boolean,
       teamId?: string,
       teamName?: string,
       additionalInfo?: object
     }>,
     lastUpdated: string,
     totalPlayers: number,
     currentPlayerRank?: number
   }
```

### Social Features Foundation (Gameserver → Player UI)
```typescript
// Player Profiles
📝 GET /api/players/{playerId}/profile
   Response: {
     profile: {
       playerId: string,
       username: string,
       avatar?: string,
       bio?: string,
       joinDate: string,
       lastSeen: string,
       isOnline: boolean,
       level: number,
       experience: number,
       title?: string,
       badges: string[],
       favoriteShip?: string,
       homePort?: string
     },
     stats: {
       rank: number,
       netWorth: number,
       combatRating: number,
       tradingRating: number,
       explorationRating: number
     },
     achievements: {
       recent: Achievement[],
       showcased: Achievement[],
       totalPoints: number
     },
     social: {
       friendCount: number,
       teamId?: string,
       teamName?: string,
       teamRole?: string,
       reputation: object
     }
   }

📝 PUT /api/players/{playerId}/profile
   Request: {
     bio?: string,
     avatar?: string,
     showcasedAchievements?: string[],
     privacy?: {
       showStats: boolean,
       showLocation: boolean,
       showOnlineStatus: boolean
     }
   }
   Response: { success: boolean, profile: Profile }

// Friend System
📝 GET /api/players/{playerId}/friends
   Response: {
     friends: Array<{
       friendId: string,
       username: string,
       avatar?: string,
       isOnline: boolean,
       lastSeen: string,
       location?: { sectorId: string, sectorName: string },
       mutualFriends: number,
       friendSince: string
     }>,
     pendingRequests: Array<{
       requestId: string,
       fromPlayerId: string,
       fromUsername: string,
       sentAt: string,
       message?: string
     }>
   }

📝 POST /api/players/{playerId}/friends/request
   Request: { targetPlayerId: string, message?: string }
   Response: { requestId: string }

📝 PUT /api/players/{playerId}/friends/request/{requestId}
   Request: { action: 'accept' | 'reject' }
   Response: { success: boolean }

📝 DELETE /api/players/{playerId}/friends/{friendId}
   Response: { success: boolean }

// Private Messaging Enhancement
📝 POST /api/messages/private
   Request: {
     recipientId: string,
     content: string,
     subject?: string,
     priority?: 'normal' | 'high',
     attachments?: Array<{
       type: 'coordinates' | 'route' | 'screenshot',
       data: object
     }>
   }
   Response: { messageId: string, sentAt: string }

📝 GET /api/messages/conversations
   Response: {
     conversations: Array<{
       participantId: string,
       participantName: string,
       lastMessage: {
         id: string,
         content: string,
         sentAt: string,
         isRead: boolean
       },
       unreadCount: number,
       totalMessages: number
     }>
   }

// Community Features
📝 GET /api/community/events
   Query: { type?: string, upcoming?: boolean }
   Response: {
     events: Array<{
       id: string,
       name: string,
       description: string,
       type: 'tournament' | 'race' | 'hunt' | 'market' | 'social',
       startTime: string,
       endTime: string,
       requirements?: object,
       rewards: object,
       participants: number,
       maxParticipants?: number,
       isRegistered: boolean
     }>
   }

📝 POST /api/community/events/{eventId}/register
   Response: { success: boolean, registrationId: string }

📝 GET /api/community/news
   Response: {
     articles: Array<{
       id: string,
       title: string,
       summary: string,
       content: string,
       author: string,
       publishedAt: string,
       category: 'update' | 'event' | 'story' | 'guide',
       tags: string[],
       viewCount: number,
       likeCount: number
     }>
   }
```

---

## WebSocket Events

### Real-time Events (All Instances)
```typescript
// Message Notifications
📝 Event: "new_message"
   Payload: { messageId: string, senderId: string, preview: string }

// Combat Updates
📝 Event: "combat_update"
   Payload: { combatId: string, round: number, status: string }

// Economic Alerts
📝 Event: "economy_alert"
   Payload: { type: string, severity: string, message: string }

// Fleet Status Changes
📝 Event: "ship_status_change"
   Payload: { shipId: string, oldStatus: string, newStatus: string }
```

---

## API Versioning Strategy

All APIs follow the pattern: `/api/v1/[resource]/[action]`

Version changes will be documented here with migration guides.

---

## Review Process

1. **Propose**: Add endpoint definition with 📝 status
2. **Review**: Other instances check compatibility
3. **Approve**: Change status to ✅ when all agree
4. **Implement**: Update to 🚧 when coding begins
5. **Complete**: Mark as ✔️ when tested and working

---

**Note**: This is a living document. Update immediately when proposing new endpoints or modifying existing ones.