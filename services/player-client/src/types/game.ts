// Re-export types from GameContext for easier importing
export type {
  Ship,
  Sector,
  Planet,
  Port,
  MoveOption,
  MarketInfo,
  PlayerState
} from '../contexts/GameContext';

// Additional types for 3D galaxy
export interface Warp {
  target_sector_id: number;
  name: string;
  type: string;
  turn_cost: number;
  can_afford: boolean;
}

export interface Tunnel {
  target_sector_id: number;
  name: string;
  type: string;
  tunnel_type: string;
  stability: number;
  turn_cost: number;
  can_afford: boolean;
}

// Extended Sector interface with additional 3D properties
export interface ExtendedSector extends Sector {
  sector_type: string;
  x_coordinate?: number;
  y_coordinate?: number;
  z_coordinate?: number;
  warps?: Warp[];
  tunnels?: Tunnel[];
  planets?: Planet[];
  ports?: Port[];
}

// Player marker interface for 3D visualization
export interface Player3D {
  user_id: string;
  username: string;
  ship_type?: string;
  sector_id?: number;
  connected_at?: string;
  last_heartbeat?: string;
}