// Real API service for gameserver endpoints
import { getAuthToken } from '../utils/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Helper function for API requests
async function apiRequest(
  endpoint: string, 
  options: RequestInit = {}
): Promise<any> {
  const token = getAuthToken();
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// Combat APIs
export const combatAPI = {
  engage: (targetType: 'ship' | 'planet' | 'port', targetId: string) =>
    apiRequest('/api/combat/engage', {
      method: 'POST',
      body: JSON.stringify({ targetType, targetId })
    }),

  getStatus: (combatId: string) =>
    apiRequest(`/api/combat/${combatId}/status`),

  // Drone management
  deployDrones: (sectorId: string, droneCount: number) =>
    apiRequest('/api/drones/deploy', {
      method: 'POST',
      body: JSON.stringify({ sectorId, droneCount })
    }),

  getDeployedDrones: () =>
    apiRequest('/api/drones/deployed'),

  recallDrones: (deploymentId: string) =>
    apiRequest(`/api/drones/${deploymentId}/recall`, {
      method: 'DELETE'
    })
};

// Planetary Management APIs
export const planetaryAPI = {
  getOwnedPlanets: () =>
    apiRequest('/api/planets/owned'),

  getPlanet: (planetId: string) =>
    apiRequest(`/api/planets/${planetId}`),

  allocateColonists: (planetId: string, allocations: { fuel: number, organics: number, equipment: number }) =>
    apiRequest(`/api/planets/${planetId}/allocate`, {
      method: 'PUT',
      body: JSON.stringify(allocations)
    }),

  upgradeBuilding: (planetId: string, buildingType: string, targetLevel: number) =>
    apiRequest(`/api/planets/${planetId}/buildings/upgrade`, {
      method: 'POST',
      body: JSON.stringify({ buildingType, targetLevel })
    }),

  updateDefenses: (planetId: string, defenses: { turrets?: number, shields?: number, drones?: number }) =>
    apiRequest(`/api/planets/${planetId}/defenses`, {
      method: 'PUT',
      body: JSON.stringify(defenses)
    }),

  deployGenesis: (sectorId: string, planetName: string, planetType: string) =>
    apiRequest('/api/planets/genesis/deploy', {
      method: 'POST',
      body: JSON.stringify({ sectorId, planetName, planetType })
    }),

  specializePlanet: (planetId: string, specialization: string) =>
    apiRequest(`/api/planets/${planetId}/specialize`, {
      method: 'PUT',
      body: JSON.stringify({ specialization })
    }),

  getSiegeStatus: (planetId: string) =>
    apiRequest(`/api/planets/${planetId}/siege-status`)
};

// Team Management APIs
export const teamAPI = {
  // Team operations
  getTeam: (teamId: string) =>
    apiRequest(`/api/teams/${teamId}`),

  createTeam: (data: { name: string, tag: string, description: string, isPublic: boolean, recruitmentStatus: string }) =>
    apiRequest('/api/teams/create', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  updateTeam: (teamId: string, updates: any) =>
    apiRequest(`/api/teams/${teamId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    }),

  disbandTeam: (teamId: string) =>
    apiRequest(`/api/teams/${teamId}`, {
      method: 'DELETE'
    }),

  // Member management
  getMembers: (teamId: string) =>
    apiRequest(`/api/teams/${teamId}/members`),

  inviteMember: (teamId: string, playerId: string, message?: string) =>
    apiRequest(`/api/teams/${teamId}/invite`, {
      method: 'POST',
      body: JSON.stringify({ playerId, message })
    }),

  kickMember: (teamId: string, memberId: string, reason?: string) =>
    apiRequest(`/api/teams/${teamId}/members/${memberId}`, {
      method: 'DELETE',
      body: JSON.stringify({ reason })
    }),

  promoteMember: (teamId: string, memberId: string, role: 'officer' | 'member') =>
    apiRequest(`/api/teams/${teamId}/members/${memberId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role })
    }),

  // Team chat
  getMessages: (teamId: string, limit?: number, before?: string) => {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (before) params.append('before', before);
    return apiRequest(`/api/teams/${teamId}/messages?${params}`);
  },

  sendMessage: (teamId: string, content: string) =>
    apiRequest(`/api/teams/${teamId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content })
    }),

  // Resource management
  depositToTreasury: (teamId: string, resources: any) =>
    apiRequest(`/api/teams/${teamId}/treasury/deposit`, {
      method: 'POST',
      body: JSON.stringify(resources)
    }),

  withdrawFromTreasury: (teamId: string, resources: any) =>
    apiRequest(`/api/teams/${teamId}/treasury/withdraw`, {
      method: 'POST',
      body: JSON.stringify(resources)
    }),

  transferResources: (teamId: string, transfer: any) =>
    apiRequest(`/api/teams/${teamId}/transfer`, {
      method: 'POST',
      body: JSON.stringify(transfer)
    }),

  // Mission management
  getMissions: (teamId: string) =>
    apiRequest(`/api/teams/${teamId}/missions`),

  createMission: (teamId: string, mission: any) =>
    apiRequest(`/api/teams/${teamId}/missions`, {
      method: 'POST',
      body: JSON.stringify(mission)
    }),

  updateMission: (teamId: string, missionId: string, updates: any) =>
    apiRequest(`/api/teams/${teamId}/missions/${missionId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    }),

  joinMission: (teamId: string, missionId: string) =>
    apiRequest(`/api/teams/${teamId}/missions/${missionId}/join`, {
      method: 'POST'
    }),

  leaveMission: (teamId: string, missionId: string) =>
    apiRequest(`/api/teams/${teamId}/missions/${missionId}/leave`, {
      method: 'DELETE'
    }),

  // Alliance & Diplomacy (Phase 3 - may not be implemented yet)
  getAlliances: (teamId: string) =>
    apiRequest(`/api/teams/${teamId}/alliances`),

  getDiplomaticRelations: (teamId: string) =>
    apiRequest(`/api/teams/${teamId}/relations`),

  proposeAlliance: (teamId: string, data: any) =>
    apiRequest(`/api/teams/${teamId}/alliances/propose`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  proposeTreaty: (teamId: string, data: any) =>
    apiRequest(`/api/teams/${teamId}/treaties/propose`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  changeDiplomaticRelation: (teamId: string, targetTeamId: string, type: string) =>
    apiRequest(`/api/teams/${teamId}/relations/${targetTeamId}`, {
      method: 'PUT',
      body: JSON.stringify({ type })
    }),

  leaveAlliance: (teamId: string, allianceId: string) =>
    apiRequest(`/api/teams/${teamId}/alliances/${allianceId}`, {
      method: 'DELETE'
    }),

  // Analytics
  getTeamAnalytics: (teamId: string, period: 'day' | 'week' | 'month' | 'all-time') =>
    apiRequest(`/api/teams/${teamId}/analytics?period=${period}`),

  // Permissions
  getPermissions: (teamId: string) =>
    apiRequest(`/api/teams/${teamId}/permissions`),

  // Utility function to get available teams (may need a different endpoint)
  getAvailableTeams: () =>
    apiRequest('/api/teams') // This endpoint might need to be implemented
};

// Fleet Management APIs
export const fleetAPI = {
  createFleet: (name: string, formation?: string, commanderId?: string) =>
    apiRequest('/api/fleets', {
      method: 'POST',
      body: JSON.stringify({ name, formation, commander_id: commanderId })
    }),

  getFleets: () =>
    apiRequest('/api/fleets'),

  getFleet: (fleetId: string) =>
    apiRequest(`/api/fleets/${fleetId}`),

  addShipToFleet: (fleetId: string, shipId: string, role?: string) =>
    apiRequest(`/api/fleets/${fleetId}/add-ship`, {
      method: 'POST',
      body: JSON.stringify({ ship_id: shipId, role })
    }),

  removeShipFromFleet: (fleetId: string, shipId: string) =>
    apiRequest(`/api/fleets/${fleetId}/remove-ship/${shipId}`, {
      method: 'DELETE'
    }),

  updateFormation: (fleetId: string, formation: string) =>
    apiRequest(`/api/fleets/${fleetId}/formation?formation=${formation}`, {
      method: 'PATCH'
    }),

  disbandFleet: (fleetId: string) =>
    apiRequest(`/api/fleets/${fleetId}`, {
      method: 'DELETE'
    }),

  initiateBattle: (fleetId: string, defenderFleetId: string) =>
    apiRequest(`/api/fleets/${fleetId}/initiate-battle`, {
      method: 'POST',
      body: JSON.stringify({ defender_fleet_id: defenderFleetId })
    }),

  simulateBattleRound: (battleId: string) =>
    apiRequest(`/api/fleets/battles/${battleId}/simulate-round`, {
      method: 'POST'
    }),

  getBattles: (activeOnly?: boolean) => {
    const params = activeOnly ? '?active_only=true' : '';
    return apiRequest(`/api/fleets/battles${params}`);
  }
};

// Faction APIs
export const factionAPI = {
  getFactions: () =>
    apiRequest('/api/factions/'),

  getReputation: () =>
    apiRequest('/api/factions/reputation'),

  getFactionReputation: (factionId: string) =>
    apiRequest(`/api/factions/${factionId}/reputation`),

  getMissions: (factionId?: string) => {
    const params = factionId ? `?faction_id=${factionId}` : '';
    return apiRequest(`/api/factions/missions${params}`);
  },

  getTerritory: (factionId: string) =>
    apiRequest(`/api/factions/${factionId}/territory`),

  getPricingModifier: (factionId: string) =>
    apiRequest(`/api/factions/${factionId}/pricing-modifier`)
};

// Message APIs
export const messageAPI = {
  sendMessage: (recipientId: string, content: string, subject?: string) =>
    apiRequest('/api/messages/send', {
      method: 'POST',
      body: JSON.stringify({ recipientId, subject, content })
    }),

  getInbox: (page: number = 1, unreadOnly?: boolean) => {
    const params = new URLSearchParams({ page: page.toString() });
    if (unreadOnly) params.append('unreadOnly', 'true');
    return apiRequest(`/api/messages/inbox?${params}`);
  },

  markAsRead: (messageId: string) =>
    apiRequest(`/api/messages/${messageId}/read`, {
      method: 'PUT'
    }),

  deleteMessage: (messageId: string) =>
    apiRequest(`/api/messages/${messageId}`, {
      method: 'DELETE'
    }),

  getTeamMessages: (teamId: string, page: number = 1) =>
    apiRequest(`/api/messages/team/${teamId}?page=${page}`)
};

// Ship APIs (partial - may need enhancement)
export const shipAPI = {
  getShips: () =>
    apiRequest('/api/ships'), // Endpoint may vary

  getShip: (shipId: string) =>
    apiRequest(`/api/ships/${shipId}`),

  updateShip: (shipId: string, updates: any) =>
    apiRequest(`/api/ships/${shipId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    }),

  // These may need different endpoints
  getMaintenanceStatus: (shipId: string) =>
    apiRequest(`/api/ships/${shipId}/maintenance`),

  scheduleMainenance: (shipId: string, components: any[]) =>
    apiRequest(`/api/ships/${shipId}/maintenance`, {
      method: 'POST',
      body: JSON.stringify({ components })
    }),

  getInsurance: (shipId: string) =>
    apiRequest(`/api/ships/${shipId}/insurance`),

  purchaseInsurance: (shipId: string, coverage: string) =>
    apiRequest(`/api/ships/${shipId}/insurance`, {
      method: 'POST',
      body: JSON.stringify({ coverage })
    }),

  fileInsuranceClaim: (shipId: string, details: any) =>
    apiRequest(`/api/ships/${shipId}/insurance/claim`, {
      method: 'POST',
      body: JSON.stringify(details)
    }),

  getUpgrades: (shipId: string) =>
    apiRequest(`/api/ships/${shipId}/upgrades`),

  installUpgrade: (shipId: string, upgradeId: string) =>
    apiRequest(`/api/ships/${shipId}/upgrades`, {
      method: 'POST',
      body: JSON.stringify({ upgradeId })
    })
};

// Trading Intelligence APIs
export const tradingAPI = {
  getMarketData: (sectorId: number | null, range: number) =>
    apiRequest('/api/trading/market-data', {
      method: 'POST',
      body: JSON.stringify({ sectorId, range })
    }),

  getPricePredictions: (params: any) =>
    apiRequest('/api/trading/predictions', {
      method: 'POST',
      body: JSON.stringify(params)
    }),

  optimizeRoutes: (params: any) =>
    apiRequest('/api/trading/optimize-routes', {
      method: 'POST',
      body: JSON.stringify(params)
    }),

  getCompetitionAnalysis: (params: any) =>
    apiRequest('/api/trading/competition', {
      method: 'POST',
      body: JSON.stringify(params)
    })
};

// Player Analytics APIs
export const playerAPI = {
  getAnalytics: (playerId: string, params: any) =>
    apiRequest(`/api/players/${playerId}/analytics`, {
      method: 'POST',
      body: JSON.stringify(params)
    }),

  getAchievements: (playerId: string) =>
    apiRequest(`/api/players/${playerId}/achievements`),

  getProgressData: (playerId: string, timeRange: string) =>
    apiRequest(`/api/players/${playerId}/progress?timeRange=${timeRange}`),

  getGoals: (playerId: string) =>
    apiRequest(`/api/players/${playerId}/goals`),

  getGoalTemplates: () =>
    apiRequest('/api/players/goal-templates'),

  createGoal: (playerId: string, goal: any) =>
    apiRequest(`/api/players/${playerId}/goals`, {
      method: 'POST',
      body: JSON.stringify(goal)
    }),

  updateGoal: (playerId: string, goalId: string, updates: any) =>
    apiRequest(`/api/players/${playerId}/goals/${goalId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    }),

  deleteGoal: (playerId: string, goalId: string) =>
    apiRequest(`/api/players/${playerId}/goals/${goalId}`, {
      method: 'DELETE'
    }),

  getLeaderboards: (category: string, params: any) => {
    const queryParams = new URLSearchParams();
    if (params.subcategory) queryParams.append('subcategory', params.subcategory);
    if (params.timeRange) queryParams.append('timeRange', params.timeRange);
    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value) queryParams.append(key, String(value));
      });
    }
    return apiRequest(`/api/leaderboards/${category}?${queryParams}`);
  }
};

// Export all APIs
export const gameAPI = {
  combat: combatAPI,
  planetary: planetaryAPI,
  team: teamAPI,
  fleet: fleetAPI,
  faction: factionAPI,
  message: messageAPI,
  ship: shipAPI,
  trading: tradingAPI,
  player: playerAPI
};