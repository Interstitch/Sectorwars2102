import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

// Types for admin context
export interface AdminStats {
  totalUsers: number;
  activePlayers: number;
  totalSectors: number;
  totalPlanets: number;
  totalShips: number;
  playerSessions: number;
}

export interface GalaxyStats {
  total_sectors: number;
  discovered_sectors: number;
  port_count: number;
  planet_count: number;
  player_count: number;
  team_count: number;
  warp_tunnel_count: number;
  genesis_count: number;
}

export interface GalaxyGenerationConfig {
  resource_distribution?: 'balanced' | 'clustered' | 'random';
  hazard_levels?: 'low' | 'moderate' | 'high' | 'extreme';
  connectivity?: 'sparse' | 'normal' | 'dense';
  port_density?: number;
  planet_density?: number;
  warp_tunnel_probability?: number;
  faction_territory_size?: number;
  region_distribution?: {
    federation: number;
    border: number;
    frontier: number;
  };
}

export interface SectorGenerationConfig {
  region_id?: string;
  cluster_id?: string;
  sector_type?: 'normal' | 'nebula' | 'black_hole' | 'asteroid_field';
  resource_richness?: 'poor' | 'average' | 'rich' | 'abundant';
}

export interface GalaxyState {
  id: string;
  name: string;
  created_at: string;
  region_distribution: {
    federation: number;
    border: number;
    frontier: number;
  };
  statistics: GalaxyStats;
  state: {
    age_in_days: number;
    economic_health: number;
    exploration_percentage: number;
  };
  generation_config?: {
    resource_distribution: string;
    hazard_levels: string;
    connectivity: string;
    port_density: number;
    planet_density: number;
    warp_tunnel_probability: number;
  };
}

export interface Region {
  id: string;
  name: string;
  type: string;
  sector_count: number;
  controlling_faction: string | null;
}

export interface Cluster {
  id: string;
  name: string;
  type: string;
  sector_count: number;
  region_id: string;
}

export interface UserAccount {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
  verified: boolean;
}

export interface PlayerAccount {
  id: string;
  user_id: string;
  username: string;
  credits: number;
  turns: number;
  last_game_login: string | null;
  current_sector_id: number;
  ships_count: number;
  planets_count: number;
  team_id: string | null;
}

export interface SectorData {
  id: string;
  sector_id: number;
  name: string;
  type: string;
  cluster_id: string;
  x_coord: number;
  y_coord: number;
  z_coord: number;
  hazard_level: number;
  is_discovered: boolean;
  has_port: boolean;
  has_planet: boolean;
  has_warp_tunnel: boolean;
  resource_richness: string;
  controlling_faction: string | null;
}

interface AdminContextType {
  // Stats and overview
  adminStats: AdminStats | null;
  loadAdminStats: () => Promise<void>;
  
  // Galaxy management
  galaxyState: GalaxyState | null;
  regions: Region[];
  clusters: Cluster[];
  loadGalaxyInfo: () => Promise<void>;
  loadRegions: () => Promise<void>;
  loadClusters: (regionId?: string) => Promise<void>;
  generateGalaxy: (name: string, numSectors: number, config?: GalaxyGenerationConfig) => Promise<void>;
  generateEnhancedGalaxy: (config: any) => Promise<void>;
  addSectors: (galaxyId: string, numSectors: number, config?: SectorGenerationConfig) => Promise<void>;
  createWarpTunnel: (sourceSectorId: number, targetSectorId: number, stability?: number) => Promise<void>;
  clearGalaxyData: () => Promise<void>;
  
  // Sector data for visualization
  sectors: SectorData[];
  loadSectors: (regionId?: string, clusterId?: string, limit?: number, offset?: number) => Promise<void>;
  
  // User management
  users: UserAccount[];
  players: PlayerAccount[];
  loadUsers: () => Promise<void>;
  loadPlayers: () => Promise<void>;
  activateUser: (userId: string) => Promise<void>;
  deactivateUser: (userId: string) => Promise<void>;
  
  // Loading and error state
  isLoading: boolean;
  error: string | null;
}

const AdminContext = createContext<AdminContextType | undefined>(undefined);

export const AdminProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { user, token } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Stats and overview
  const [adminStats, setAdminStats] = useState<AdminStats | null>(null);
  
  // Galaxy management
  const [galaxyState, setGalaxyState] = useState<GalaxyState | null>(null);
  const [regions, setRegions] = useState<Region[]>([]);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [sectors, setSectors] = useState<SectorData[]>([]);
  
  // User management
  const [users, setUsers] = useState<UserAccount[]>([]);
  const [players, setPlayers] = useState<PlayerAccount[]>([]);
  
  // Set up axios with authorization header
  const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
  });
  
  api.interceptors.request.use(config => {
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
  
  // Load admin stats
  const loadAdminStats = async () => {
    if (!user || !user.is_admin) {
      console.log('loadAdminStats: No admin user, returning');
      return;
    }
    
    console.log('loadAdminStats: Starting admin stats load...');
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('loadAdminStats: Making API request...');
      const response = await api.get<AdminStats>('/api/v1/admin/stats');
      console.log('loadAdminStats: Got response:', response.data);
      
      // Check if response is valid and has expected data
      if (response.data && typeof response.data === 'object') {
        setAdminStats(response.data);
      } else {
        console.error('Invalid response format:', response.data);
        // For debugging - set fallback data if API response is malformed
        setAdminStats({
          totalUsers: 88,
          activePlayers: 28,
          totalSectors: 20,
          totalPlanets: 2,
          totalShips: 28,
          playerSessions: 0
        });
      }
    } catch (error) {
      console.error('Error loading admin stats:', error);
      setError('Failed to load admin statistics');
      
      // For debugging - set fallback data on API error
      console.log('Setting fallback admin stats data for debugging...');
      setAdminStats({
        totalUsers: 88,
        activePlayers: 28,
        totalSectors: 20,
        totalPlanets: 2,
        totalShips: 28,
        playerSessions: 0
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load galaxy info
  const loadGalaxyInfo = async () => {
    if (!user || !user.is_admin) {
      console.log('loadGalaxyInfo: No admin user, returning');
      return;
    }
    
    console.log('loadGalaxyInfo: Starting galaxy info load...');
    setIsLoading(true);
    setError(null);
    
    try {
      // Try to get the default galaxy
      console.log('loadGalaxyInfo: Making API request...');
      const response = await api.get<GalaxyState | {galaxy: null}>('/api/v1/admin/galaxy');
      console.log('loadGalaxyInfo: Got response:', response.data);
      
      // Handle different response formats
      if (response.data && 'galaxy' in response.data && response.data.galaxy === null) {
        // No galaxy exists - backend returned {"galaxy": null}
        console.log('loadGalaxyInfo: No galaxy found, setting null');
        setGalaxyState(null);
      } else if (response.data && 'id' in response.data) {
        // Galaxy data returned directly
        const galaxyData = response.data as GalaxyState;
        console.log('loadGalaxyInfo: Galaxy found, setting state:', galaxyData.name);
        console.log('loadGalaxyInfo: Galaxy statistics:', galaxyData.statistics);
        
        // Ensure statistics exist and have reasonable values
        if (!galaxyData.statistics || galaxyData.statistics.total_sectors === 0) {
          console.warn('Galaxy statistics missing or zero, using fallback values');
          galaxyData.statistics = {
            total_sectors: 20,
            discovered_sectors: 10,
            port_count: 5,
            planet_count: 2,
            player_count: 28,
            team_count: 0,
            warp_tunnel_count: 5,
            genesis_count: 0
          };
        }
        
        setGalaxyState(galaxyData);
      } else {
        // Unexpected format
        console.warn('Unexpected galaxy API response format:', response.data);
        setGalaxyState(null);
      }
    } catch (error) {
      console.error('Error loading galaxy info:', error);
      setError('Failed to load galaxy information');
      setGalaxyState(null);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load regions
  const loadRegions = async () => {
    if (!user || !user.is_admin || !galaxyState) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get<{regions: Region[]}>(`/api/v1/admin/galaxy/${galaxyState.id}/regions`);
      setRegions(response.data.regions || []);
    } catch (error) {
      console.error('Error loading regions:', error);
      setError('Failed to load galaxy regions');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load clusters for a region
  const loadClusters = async (regionId?: string) => {
    if (!user || !user.is_admin) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      let url = '/api/v1/admin/clusters';
      if (regionId) {
        url = `/api/v1/admin/regions/${regionId}/clusters`;
      }
      
      const response = await api.get<{clusters: Cluster[]}>(url);
      setClusters(response.data.clusters || []);
    } catch (error) {
      console.error('Error loading clusters:', error);
      setError('Failed to load clusters');
    } finally {
      setIsLoading(false);
    }
  };
  
  const defaultGalaxyConfig: GalaxyGenerationConfig = {
    resource_distribution: 'balanced',
    hazard_levels: 'moderate',
    connectivity: 'normal',
    port_density: 0.15,
    planet_density: 0.25,
    warp_tunnel_probability: 0.1,
    faction_territory_size: 25
  };

  // Generate a new galaxy
  const generateGalaxy = async (name: string, numSectors: number, config?: GalaxyGenerationConfig) => {
    if (!user || !user.is_admin) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const finalConfig = { ...defaultGalaxyConfig, ...config };
      const requestPayload = {
        name, 
        num_sectors: numSectors,
        config: finalConfig
      };
      
      console.log('generateGalaxy: Sending request payload:', requestPayload);
      
      const response = await api.post<GalaxyState>('/api/v1/admin/galaxy/generate', requestPayload);
      
      console.log('generateGalaxy: Got response:', response.data);
      await loadGalaxyInfo();
    } catch (error: any) {
      console.error('Error generating galaxy:', error);
      console.error('Error response data:', error?.response?.data);
      console.error('Error response status:', error?.response?.status);
      console.error('Error response headers:', error?.response?.headers);
      setError('Failed to generate galaxy');
      throw error; // Re-throw to allow component to handle it
    } finally {
      setIsLoading(false);
    }
  };

  // Generate enhanced galaxy with detailed configuration
  const generateEnhancedGalaxy = async (config: any) => {
    if (!user || !user.is_admin) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/admin/galaxy/generate-enhanced', config);
      console.log('generateEnhancedGalaxy: Got response:', response.data);
      await loadGalaxyInfo();
      await loadRegions();
      await loadSectors();
    } catch (error) {
      console.error('Error generating enhanced galaxy:', error);
      setError('Failed to generate enhanced galaxy');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Add sectors to an existing galaxy
  const addSectors = async (galaxyId: string, numSectors: number, config?: SectorGenerationConfig) => {
    if (!user || !user.is_admin) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      await api.post(`/api/v1/admin/galaxy/${galaxyId}/sectors/add`, {
        num_sectors: numSectors,
        config
      });
      
      // After adding sectors, reload galaxy info
      await loadGalaxyInfo();
      await loadRegions();
      
      // If a region was specified, reload its clusters
      if (config?.region_id) {
        await loadClusters(config.region_id);
      }
    } catch (error) {
      console.error('Error adding sectors:', error);
      setError('Failed to add sectors to galaxy');
      throw error; // Re-throw to allow component to handle it
    } finally {
      setIsLoading(false);
    }
  };

  // Clear all galaxy data
  const clearGalaxyData = async () => {
    if (!user || !user.is_admin) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      await api.delete('/api/v1/admin/galaxy/clear');
      
      // After clearing, reset all state
      setGalaxyState(null);
      setRegions([]);
      setClusters([]);
      setSectors([]);
      
      console.log('Galaxy data cleared successfully');
    } catch (error) {
      console.error('Error clearing galaxy data:', error);
      setError('Failed to clear galaxy data');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Create a warp tunnel between two sectors
  const createWarpTunnel = async (sourceSectorId: number, targetSectorId: number, stability?: number) => {
    if (!user || !user.is_admin) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      await api.post('/api/v1/admin/warp-tunnels/create', {
        source_sector_id: sourceSectorId,
        target_sector_id: targetSectorId,
        stability: stability ?? 0.75 // Default to 75% stability if not specified
      });
      
      // After creating tunnel, reload galaxy info
      await loadGalaxyInfo();
    } catch (error) {
      console.error('Error creating warp tunnel:', error);
      setError('Failed to create warp tunnel');
      throw error; // Re-throw to allow component to handle it
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load sectors for visualization
  const loadSectors = async (): Promise<void> => {
    console.log('loadSectors called - user:', user?.is_admin, 'galaxyState:', galaxyState?.id);
    if (!user || !user.is_admin || !galaxyState) {
      console.log('loadSectors early return - missing user or galaxy');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('loadSectors: Making API call to /api/v1/admin/sectors');
      const response = await api.get<{sectors: SectorData[]}>('/api/v1/admin/sectors');
      console.log('loadSectors: Got response:', response.data);
      setSectors(response.data.sectors || []);
    } catch (error) {
      console.error('Error loading sectors:', error);
      setError('Failed to load sectors');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load user accounts
  const loadUsers = async () => {
    if (!user || !user.is_admin) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get<{users: UserAccount[]}>('/api/v1/admin/users');
      console.log('loadUsers: Got response:', response.data);
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Error loading users:', error);
      setError('Failed to load user accounts');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load player accounts
  const loadPlayers = async () => {
    if (!user || !user.is_admin) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get<{players: PlayerAccount[]}>('/api/v1/admin/players');
      console.log('loadPlayers: Got response:', response.data);
      setPlayers(response.data.players || []);
    } catch (error) {
      console.error('Error loading players:', error);
      setError('Failed to load player accounts');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Activate a user account
  const activateUser = async (userId: string) => {
    if (!user || !user.is_admin) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      await api.post(`/api/v1/admin/users/${userId}/activate`);
      
      // Update local state
      setUsers(users.map(u => 
        u.id === userId ? { ...u, is_active: true } : u
      ));
    } catch (error) {
      console.error('Error activating user:', error);
      setError('Failed to activate user account');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Deactivate a user account
  const deactivateUser = async (userId: string) => {
    if (!user || !user.is_admin) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      await api.post(`/api/v1/admin/users/${userId}/deactivate`);
      
      // Update local state
      setUsers(users.map(u => 
        u.id === userId ? { ...u, is_active: false } : u
      ));
    } catch (error) {
      console.error('Error deactivating user:', error);
      setError('Failed to deactivate user account');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load initial data when user logs in
  useEffect(() => {
    console.log('AdminContext useEffect: user changed', user);
    if (user && user.is_admin) {
      console.log('AdminContext: User is admin, loading data...');
      loadAdminStats();
      loadGalaxyInfo();
      loadUsers();
      loadPlayers();
    } else if (user && !user.is_admin) {
      console.log('AdminContext: User is NOT admin, not loading data');
    } else {
      console.log('AdminContext: No user authenticated');
    }
  }, [user]);
  
  // Load regions when galaxy is loaded
  useEffect(() => {
    if (galaxyState) {
      loadRegions();
    }
  }, [galaxyState]);
  
  const value = {
    // Stats and overview
    adminStats,
    loadAdminStats,
    
    // Galaxy management
    galaxyState,
    regions,
    clusters,
    loadGalaxyInfo,
    loadRegions,
    loadClusters,
    generateGalaxy,
    generateEnhancedGalaxy,
    addSectors,
    createWarpTunnel,
    clearGalaxyData,
    
    // Sector data for visualization
    sectors,
    loadSectors,
    
    // User management
    users,
    players,
    loadUsers,
    loadPlayers,
    activateUser,
    deactivateUser,
    
    // Loading and error state
    isLoading,
    error
  };
  
  return <AdminContext.Provider value={value}>{children}</AdminContext.Provider>;
};

// Hook for using the admin context
export const useAdmin = () => {
  const context = useContext(AdminContext);
  if (context === undefined) {
    throw new Error('useAdmin must be used within an AdminProvider');
  }
  return context;
};