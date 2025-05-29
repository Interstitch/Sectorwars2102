// Team-related type definitions
export interface Team {
  id: string;
  name: string;
  tag: string; // 3-5 character team tag
  description: string;
  leaderId: string;
  leaderName: string;
  memberCount: number;
  maxMembers: number;
  reputation: number;
  founded: string;
  isPublic: boolean;
  recruitmentStatus: 'open' | 'invite-only' | 'closed';
  treasury: {
    credits: number;
    fuel: number;
    organics: number;
    equipment: number;
  };
}

export interface TeamMember {
  id: string;
  playerId: string;
  playerName: string;
  role: 'leader' | 'officer' | 'member';
  joinedAt: string;
  contributions: {
    credits: number;
    resources: number;
    combatKills: number;
  };
  online: boolean;
  location: {
    sectorId: string;
    sectorName: string;
  };
  shipType: string;
  combatRating: number;
}

export interface TeamInvitation {
  id: string;
  teamId: string;
  teamName: string;
  teamTag: string;
  invitedBy: string;
  invitedAt: string;
  expiresAt: string;
  message?: string;
}

export interface TeamApplication {
  id: string;
  playerId: string;
  playerName: string;
  teamId: string;
  message: string;
  appliedAt: string;
  status: 'pending' | 'accepted' | 'rejected';
}

export interface TeamMessage {
  id: string;
  teamId: string;
  senderId: string;
  senderName: string;
  senderRole: 'leader' | 'officer' | 'member';
  content: string;
  timestamp: string;
  type: 'message' | 'system' | 'alert';
  readBy: string[]; // Array of player IDs who have read the message
}

export interface ResourceTransfer {
  id: string;
  teamId: string;
  fromPlayerId: string;
  fromPlayerName: string;
  toPlayerId: string;
  toPlayerName: string;
  resources: {
    credits?: number;
    fuel?: number;
    organics?: number;
    equipment?: number;
  };
  reason?: string;
  timestamp: string;
  status: 'pending' | 'completed' | 'cancelled';
}

export interface TeamMission {
  id: string;
  teamId: string;
  name: string;
  description: string;
  type: 'combat' | 'trading' | 'exploration' | 'defense' | 'siege';
  status: 'planning' | 'active' | 'completed' | 'failed';
  createdBy: string;
  createdAt: string;
  startTime?: string;
  endTime?: string;
  objectives: MissionObjective[];
  participants: string[]; // Player IDs
  rewards?: {
    credits?: number;
    reputation?: number;
    resources?: Record<string, number>;
  };
}

export interface MissionObjective {
  id: string;
  description: string;
  type: 'destroy' | 'capture' | 'deliver' | 'defend' | 'explore';
  targetId?: string;
  targetType?: 'sector' | 'ship' | 'planet' | 'port';
  requiredAmount?: number;
  currentAmount?: number;
  completed: boolean;
}

export interface Alliance {
  id: string;
  name: string;
  teams: {
    teamId: string;
    teamName: string;
    teamTag: string;
    joinedAt: string;
  }[];
  type: 'mutual-defense' | 'trade' | 'non-aggression';
  createdAt: string;
  expiresAt?: string;
  terms: string[];
}

export interface DiplomaticRelation {
  id: string;
  fromTeamId: string;
  fromTeamName: string;
  toTeamId: string;
  toTeamName: string;
  type: 'ally' | 'neutral' | 'hostile' | 'war';
  establishedAt: string;
  treaty?: {
    type: 'peace' | 'trade' | 'defense' | 'non-aggression';
    terms: string[];
    expiresAt?: string;
  };
}

export interface TeamAnalytics {
  teamId: string;
  period: 'day' | 'week' | 'month' | 'all-time';
  metrics: {
    combatStats: {
      kills: number;
      deaths: number;
      kdRatio: number;
      damageDealt: number;
      damageTaken: number;
    };
    economicStats: {
      creditsEarned: number;
      creditsSpent: number;
      resourcesGathered: number;
      resourcesTraded: number;
      profitMargin: number;
    };
    territoryStats: {
      sectorsControlled: number;
      planetsOwned: number;
      portsVisited: number;
      territoriesLost: number;
      territoriesGained: number;
    };
    memberStats: {
      averageOnlineTime: number;
      activeMembers: number;
      newRecruits: number;
      membersLost: number;
    };
  };
  topPerformers: {
    combat: TeamMember[];
    trading: TeamMember[];
    exploration: TeamMember[];
  };
}

export interface TeamPermissions {
  canInvite: boolean;
  canKick: boolean;
  canPromote: boolean;
  canManageTreasury: boolean;
  canStartMissions: boolean;
  canEditTeamInfo: boolean;
  canManageAlliances: boolean;
  canDeclareWar: boolean;
}