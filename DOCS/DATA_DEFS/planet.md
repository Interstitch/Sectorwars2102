// Sector Wars 2102 Planet Data Model

export enum PlanetType {
  TERRA = "TERRA",
  M_CLASS = "M_CLASS",
  L_CLASS = "L_CLASS",
  O_CLASS = "O_CLASS",
  K_CLASS = "K_CLASS",
  H_CLASS = "H_CLASS",
  U_CLASS = "U_CLASS",
  C_CLASS = "C_CLASS"
}

export interface PlanetColonists {
  fuel: number;
  organics: number;
  equipment: number;
  total: number;
}

export interface PlanetProductionRates {
  ore: number;
  organics: number;
  equipment: number;
}

export interface PlanetCommodities {
  ore: number;
  organics: number;
  equipment: number;
}

export interface PlanetModel {
  id: string;
  name: string;
  sectorId: number;
  ownerId: string | null;
  ownerName?: string;
  teamId?: string | null;
  created: boolean;
  createdAt: Date;
  lastUpdated: Date;
  lastColonistUpdate: Date;
  type: PlanetType;
  colonists: PlanetColonists;
  colonistCapacity: {
    fuel: number;
    organics: number;
    equipment: number;
  };
  breedingRate: number; // 0-100, percent per day
  commodities: PlanetCommodities;
  productionRates: PlanetProductionRates;
  citadelLevel: number;
  shieldLevel: number;
  fighters: number;
  productionUpgrades: {
    ore: number;
    organics: number;
    equipment: number;
  };
  buildings: {
    id: string;
    name: string;
    level: number;
    effect: string;
  }[];
  atmosphere?: string;
  description?: string;
  isHidden?: boolean;
  occupiedCount: number;
  occupants?: {
    playerId: string;
    playerName: string;
    landed: Date;
  }[];
  landingRights?: {
    allowTeam: boolean;
    allowedPlayers: string[];
    denyList: string[];
  };
}

export interface PlanetTypeConfig {
  type: PlanetType;
  typeDescription: string;
  fuelProduction: number;
  organicsProduction: number;
  equipmentProduction: number;
  maxColonists: {
    fuel: number;
    organics: number;
    equipment: number;
  };
  breeding: number; // 0-100, percent per day
}
