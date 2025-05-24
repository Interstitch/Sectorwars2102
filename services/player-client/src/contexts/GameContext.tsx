import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

// Types for game state
export interface Ship {
  id: string;
  name: string;
  type: string;
  sector_id: number;
  cargo: Record<string, number>;
  cargo_capacity: number;
  current_speed: number;
  base_speed: number;
  combat: any;
  maintenance: any;
  is_flagship: boolean;
  purchase_value: number;
  current_value: number;
}

export interface Sector {
  id: number;
  name: string;
  type: string;
  hazard_level: number;
  radiation_level: number;
  resources: Record<string, any>;
  players_present: any[];
  special_features: string[];
  description?: string;
}

export interface Planet {
  id: string;
  name: string;
  type: string;
  status: string;
  sector_id: number;
  owner?: any;
  resources: Record<string, any>;
  population: number;
  max_population: number;
  habitability_score: number;
}

export interface Port {
  id: string;
  name: string;
  type: string;
  status: string;
  sector_id: number;
  owner?: any;
  services: Record<string, any>;
  faction_affiliation?: string;
}

export interface MoveOption {
  sector_id: number;
  name: string;
  type: string;
  turn_cost: number;
  can_afford: boolean;
  tunnel_type?: string;
  stability?: number;
}

export interface MarketInfo {
  resources: Record<string, {
    quantity: number;
    buy_price: number;
    sell_price: number;
  }>;
  port: {
    id: string;
    name: string;
    type: string;
    faction: string | null;
    tax_rate: number;
  };
}

export interface PlayerState {
  id: string;
  username: string;
  credits: number;
  turns: number;
  current_sector_id: number;
  is_ported: boolean;
  is_landed: boolean;
  defense_drones: number;
  attack_drones: number;
  current_ship_id?: string;
  team_id?: string;
}

interface GameContextType {
  // Player info
  playerState: PlayerState | null;
  refreshPlayerState: () => Promise<void>;
  
  // Player ships
  ships: Ship[];
  currentShip: Ship | null;
  loadShips: () => Promise<void>;
  setCurrentShip: (shipId: string) => Promise<void>;
  
  // Current location info
  currentSector: Sector | null;
  availableMoves: {
    warps: MoveOption[];
    tunnels: MoveOption[];
  };
  planetsInSector: Planet[];
  portsInSector: Port[];
  
  // Movement
  moveToSector: (sectorId: number) => Promise<any>;
  getAvailableMoves: () => Promise<void>;
  
  // Port interactions
  dockAtPort: (portId: string) => Promise<any>;
  marketInfo: MarketInfo | null;
  getMarketInfo: (portId: string) => Promise<void>;
  buyResource: (portId: string, resourceType: string, quantity: number) => Promise<any>;
  sellResource: (portId: string, resourceType: string, quantity: number) => Promise<any>;
  
  // Planet interactions
  landOnPlanet: (planetId: string) => Promise<any>;
  
  // Combat
  attackPlayer: (playerId: string) => Promise<any>;
  attackDrones: () => Promise<any>;
  
  // Loading states
  isLoading: boolean;
  error: string | null;
  
  // General methods
  exploreCurrentLocation: () => Promise<void>;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

export const GameProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Player state
  const [playerState, setPlayerState] = useState<PlayerState | null>(null);
  
  // Ships
  const [ships, setShips] = useState<Ship[]>([]);
  const [currentShip, setCurrentShip] = useState<Ship | null>(null);
  
  // Location
  const [currentSector, setCurrentSector] = useState<Sector | null>(null);
  const [availableMoves, setAvailableMoves] = useState<{ warps: MoveOption[], tunnels: MoveOption[] }>({
    warps: [],
    tunnels: []
  });
  const [planetsInSector, setPlanetsInSector] = useState<Planet[]>([]);
  const [portsInSector, setPortsInSector] = useState<Port[]>([]);
  
  // Market
  const [marketInfo, setMarketInfo] = useState<MarketInfo | null>(null);
  
  // Get API URL using the same logic as AuthContext
  const getApiUrl = () => {
    // If an environment variable is explicitly set, use it
    if (import.meta.env.VITE_API_URL) {
      return import.meta.env.VITE_API_URL;
    }

    const windowUrl = window.location.origin;

    // For GitHub Codespaces, use proxy to avoid authentication issues with external URLs
    if (windowUrl.includes('.app.github.dev')) {
      return '';  // Use proxy through Vite dev server
    }

    // Local development
    if (windowUrl.includes('localhost')) {
      return 'http://localhost:8080';
    }

    // For other environments - use proxy
    return '';
  };

  // Set up axios with authorization header
  const api = axios.create({
    baseURL: getApiUrl(),
  });
  
  // Use token from localStorage directly instead of from context
  api.interceptors.request.use(config => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
  
  // Initialize game state when user logs in
  useEffect(() => {
    console.log('GameContext: User changed:', user);
    if (user) {
      console.log('GameContext: Initializing for user:', user.username);
      refreshPlayerState();
      loadShips();
    } else {
      console.log('GameContext: No user, clearing state');
      setPlayerState(null);
      setCurrentShip(null);
      setShips([]);
    }
  }, [user]);
  
  // Update current location info when sector changes
  useEffect(() => {
    if (playerState?.current_sector_id) {
      exploreCurrentLocation();
      getAvailableMoves();
    }
  }, [playerState?.current_sector_id]);
  
  // Refresh player state
  const refreshPlayerState = async () => {
    if (!user) {
      console.log('GameContext: No user for refreshPlayerState');
      return;
    }
    
    console.log('GameContext: Refreshing player state for user:', user.username);
    console.log('GameContext: API base URL:', getApiUrl());
    
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('GameContext: Calling /api/v1/player/state');
      const response = await api.get('/api/v1/player/state');
      console.log('GameContext: Player state response:', response.data);
      setPlayerState(response.data);
      
      // If player has a current ship, load its details
      if (response.data.current_ship_id) {
        console.log('GameContext: Loading current ship details');
        const shipResponse = await api.get('/api/v1/player/current-ship');
        console.log('GameContext: Current ship response:', shipResponse.data);
        setCurrentShip(shipResponse.data);
      }
    } catch (error) {
      console.error('GameContext: Error fetching player state:', error);
      setError('Failed to load player state');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load player's ships
  const loadShips = async () => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/api/v1/player/ships');
      setShips(response.data || []);
      
      // If there's a current ship, update it
      if (playerState?.current_ship_id) {
        const currentShip = response.data.find((ship: Ship) => ship.id === playerState.current_ship_id);
        if (currentShip) {
          setCurrentShip(currentShip);
        }
      }
    } catch (error) {
      console.error('Error loading ships:', error);
      setError('Failed to load ships');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Set current ship
  const setActiveShip = async (shipId: string) => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      await api.post(`/api/v1/ships/${shipId}/set-active`);
      
      // Update player state and ships
      await refreshPlayerState();
      await loadShips();
    } catch (error) {
      console.error('Error setting active ship:', error);
      setError('Failed to set active ship');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Move to another sector
  const moveToSector = async (sectorId: number) => {
    if (!user || !playerState) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post(`/api/v1/player/move/${sectorId}`);
      
      // Update player state after movement
      await refreshPlayerState();
      
      return response.data;
    } catch (error: any) {
      console.error('Error moving to sector:', error);
      setError(error.response?.data?.message || 'Failed to move to sector');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Get available moves from current sector
  const getAvailableMoves = async () => {
    if (!user || !playerState) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/api/v1/player/available-moves');
      setAvailableMoves(response.data);
    } catch (error) {
      console.error('Error getting available moves:', error);
      setError('Failed to get available moves');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Explore current location (sector, planets, ports)
  const exploreCurrentLocation = async () => {
    if (!user || !playerState) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Get sector info
      const sectorResponse = await api.get('/api/v1/player/current-sector');
      setCurrentSector(sectorResponse.data);
      
      // Get planets in sector
      const planetsResponse = await api.get(`/api/v1/sectors/${playerState.current_sector_id}/planets`);
      setPlanetsInSector(planetsResponse.data.planets || []);
      
      // Get ports in sector
      const portsResponse = await api.get(`/api/v1/sectors/${playerState.current_sector_id}/ports`);
      setPortsInSector(portsResponse.data.ports || []);
    } catch (error) {
      console.error('Error exploring location:', error);
      setError('Failed to explore current location');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Dock at a port
  const dockAtPort = async (portId: string) => {
    if (!user || !playerState) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/trading/dock', { port_id: portId });
      
      // Update player state after docking
      await refreshPlayerState();
      
      return response.data;
    } catch (error: any) {
      console.error('Error docking at port:', error);
      setError(error.response?.data?.message || 'Failed to dock at port');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Get market info for a port
  const getMarketInfo = async (portId: string) => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/api/v1/trading/market/${portId}`);
      setMarketInfo(response.data);
    } catch (error) {
      console.error('Error getting market info:', error);
      setError('Failed to get market info');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Buy resource from a port
  const buyResource = async (portId: string, resourceType: string, quantity: number) => {
    if (!user || !playerState) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/trading/buy', {
        port_id: portId,
        resource_type: resourceType,
        quantity: quantity
      });
      
      // Update player state and market info after purchase
      await refreshPlayerState();
      await getMarketInfo(portId);
      
      return response.data;
    } catch (error: any) {
      console.error('Error buying resource:', error);
      setError(error.response?.data?.message || 'Failed to buy resource');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Sell resource to a port
  const sellResource = async (portId: string, resourceType: string, quantity: number) => {
    if (!user || !playerState) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/trading/sell', {
        port_id: portId,
        resource_type: resourceType,
        quantity: quantity
      });
      
      // Update player state and market info after sale
      await refreshPlayerState();
      await getMarketInfo(portId);
      
      return response.data;
    } catch (error: any) {
      console.error('Error selling resource:', error);
      setError(error.response?.data?.message || 'Failed to sell resource');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Land on a planet
  const landOnPlanet = async (planetId: string) => {
    if (!user || !playerState) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/planets/land', { planet_id: planetId });
      
      // Update player state after landing
      await refreshPlayerState();
      
      return response.data;
    } catch (error: any) {
      console.error('Error landing on planet:', error);
      setError(error.response?.data?.message || 'Failed to land on planet');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Attack another player
  const attackPlayer = async (playerId: string) => {
    if (!user || !playerState) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/combat/attack-player', { defender_id: playerId });
      
      // Update player state after combat
      await refreshPlayerState();
      
      return response.data;
    } catch (error: any) {
      console.error('Error attacking player:', error);
      setError(error.response?.data?.message || 'Failed to attack player');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Attack sector drones
  const attackDrones = async () => {
    if (!user || !playerState) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/combat/attack-drones', { 
        sector_id: playerState.current_sector_id 
      });
      
      // Update player state after combat
      await refreshPlayerState();
      
      return response.data;
    } catch (error: any) {
      console.error('Error attacking drones:', error);
      setError(error.response?.data?.message || 'Failed to attack drones');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  const value = {
    // Player info
    playerState,
    refreshPlayerState,
    
    // Player ships
    ships,
    currentShip,
    loadShips,
    setCurrentShip: setActiveShip,
    
    // Current location info
    currentSector,
    availableMoves,
    planetsInSector,
    portsInSector,
    
    // Movement
    moveToSector,
    getAvailableMoves,
    
    // Port interactions
    dockAtPort,
    marketInfo,
    getMarketInfo,
    buyResource,
    sellResource,
    
    // Planet interactions
    landOnPlanet,
    
    // Combat
    attackPlayer,
    attackDrones,
    
    // Loading states
    isLoading,
    error,
    
    // General methods
    exploreCurrentLocation
  };
  
  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
};

// Hook for using the game context
export const useGame = () => {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
};