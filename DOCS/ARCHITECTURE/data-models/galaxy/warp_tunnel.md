# Warp Tunnel Data Definition

## Overview

Warp Tunnels in Sector Wars 2102 are special pathways that allow for instantaneous travel between distant sectors. Unlike standard warps that connect adjacent sectors, warp tunnels can span across multiple sectors, clusters, or even regions within the galaxy. They come in two forms: naturally occurring tunnels and artificial tunnels created by players using Warp Jumper ships.

## Position in Galaxy Hierarchy

Warp Tunnels function as connectors between different parts of the galaxy hierarchy:
- They can connect sectors within the same cluster
- They can connect sectors across different clusters
- They can connect sectors across different cosmological zones

## Data Model

```typescript
export enum WarpTunnelType {
  NATURAL = "NATURAL",           // Naturally occurring warp tunnel
  ARTIFICIAL = "ARTIFICIAL"      // Player-created warp tunnel
}

export enum WarpTunnelStability {
  UNSTABLE = "UNSTABLE",         // May collapse or shift
  STABLE = "STABLE"             // Reliable long-term connection
}

export interface WarpTunnelEndpoint {
  sector_id: number;             // Sector ID of endpoint
  cluster_id: string;            // Cluster ID containing sector
  zone_id: string;               // Cosmological zone ID containing cluster
  coordinates: {                 // Galaxy map coordinates
    x: number;
    y: number;
    z: number;
  };
  controlling_faction: string | null; // Faction controlling sector
  is_secured: boolean;           // Whether endpoint has access restrictions
  access_requirements?: {        // Requirements to use endpoint
    reputation: {                // Needed faction reputation
      faction_id: string;
      min_level: number;
    };
    permits?: string[];          // Required permits/passes
  };
}

export interface WarpTunnelProperties {
  length: number;                // Distance in light years
  stability: WarpTunnelStability; // Tunnel stability
  stability_rating: number;      // 0-100 numeric stability
  expected_lifetime?: Date;      // When artificial tunnel may collapse
  age: number;                   // Time since creation in days
  traversal_cost: number;        // Turn cost to use tunnel
  cool_down: number;             // Turns before reuse
  discovered: boolean;           // Whether tunnel is known to players
  discoverer_id?: string;        // Player who discovered tunnel
  discovery_date?: Date;         // When tunnel was discovered
  affected_by_storms: boolean;   // Whether storms can disrupt tunnel
}

export interface WarpTunnelStatus {
  is_active: boolean;            // Whether tunnel is currently usable
  disruption?: {                 // Current disruption details if any
    cause: string;               // Reason for disruption
    severity: number;            // 0-100 severity
    started_at: Date;            // When disruption began
    expected_duration: number;   // Hours until resolution
    estimated_end_time: Date;    // When tunnel should restore
  };
  traffic_level: number;         // 0-100 current usage level
  last_traversal: Date | null;   // When last ship used tunnel
  maintenance_status?: {         // For artificial tunnels
    last_maintenance: Date;      // When last maintained
    condition: number;           // 0-100 condition rating
    needs_repair: boolean;       // Whether repairs needed
  };
}

export interface ArtificialTunnelData {
  creator_id: string;            // Player who created tunnel
  creator_name: string;          // Name of creator
  team_id: string | null;        // Team affiliation if any
  created_at: Date;              // Creation timestamp
  warp_jumper_id: string;        // ID of sacrificed Warp Jumper ship
  construction_cost: number;     // Credits spent on construction
  access_control: {              // Access permissions
    public: boolean;             // Whether open to all players
    team_only: boolean;          // Whether restricted to team
    allowed_players: string[];   // Specific allowed players
    allowed_factions: string[];  // Specific allowed factions
  };
  toll?: {                       // Optional toll system
    enabled: boolean;            // Whether toll is active
    amount: number;              // Credits per use
    total_collected: number;     // Total credits collected
    exempt_players: string[];    // Players exempt from toll
  };
}

export interface WarpTunnelModel {
  id: string;                    // Unique identifier
  name: string;                  // Tunnel name/designation
  type: WarpTunnelType;          // Natural or artificial
  created_at: Date;              // When record was created
  
  // Endpoints
  source: WarpTunnelEndpoint;    // Origin endpoint
  destination: WarpTunnelEndpoint; // Destination endpoint
  bidirectional: boolean;        // Whether travel works both ways
  
  // Properties
  properties: WarpTunnelProperties; // Tunnel characteristics
  status: WarpTunnelStatus;      // Current operational status
  
  // For artificial tunnels only
  artificial_data?: ArtificialTunnelData; // Creation and management data
  
  // Usage statistics
  total_traversals: number;      // Total times tunnel used
  traversal_history: {           // Recent usage
    timestamp: Date;
    player_id: string;
    direction: string;           // "source_to_dest" or "dest_to_source"
  }[];
  
  // Special properties
  special_effects: string[];     // Any unique effects
  description: string;           // Human-readable description
}
```

## Natural Warp Tunnels

Natural warp tunnels are permanent fixtures in the universe that connect distant sectors. They have the following characteristics:

1. **Formation**: Occur naturally in the universe
2. **Stability**: Permanently stable, though can be temporarily disrupted by space storms
3. **Discovery**: Must be discovered by players through exploration
4. **Distribution**: More common in frontier regions, especially around special astronomical features
5. **Access**: Generally open to all players, though endpoints may have faction restrictions

## Artificial Warp Tunnels

Artificial warp tunnels are created by players using Warp Jumper ships, allowing strategic connections between sectors:

1. **Creation Requirements**:
   - Warp Jumper ship (sacrificed in the process)
   - 100,000-500,000 credits for construction
   - Appropriate reputation with local factions
   - No existing tunnel between sectors

2. **Construction Process**:
   - 7-14 real-time days to complete
   - Construction can be disrupted
   - Requires periodic monitoring

3. **Properties**:
   - Generally stable, but less reliable than natural tunnels
   - Can be controlled by creator
   - May eventually collapse (7-30 day lifespan)
   - May require maintenance

## Warp Tunnel Mechanics

1. **Travel**: Instant travel between connected sectors
2. **Turn Cost**: 1-3 turns to use depending on distance
3. **Cooldown**: Some tunnels have reuse cooldown period
4. **Discovery**: Unknown tunnels must be discovered before use
5. **Disruption**: Space storms can temporarily disable tunnels
6. **Access Control**: Some tunnels have factional or player restrictions

## Credit/Time Sink

Artificial warp tunnels represent a significant credit and resource sink:
1. **Creation Cost**: 100,000-500,000 credits
2. **Ship Cost**: Sacrifice of a Warp Jumper ship
3. **Construction Time**: 7-14 real-time days
4. **Maintenance**: Ongoing cost to maintain artificial tunnels